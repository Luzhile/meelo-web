"""Shared asset helpers; the legacy study Diffuse CLI is archived.

The active AO-only entry is meal_ao.py / run-ao.ps1. The old CLI requires
--allow-archived-diffuse and must never be used implicitly as an AO fallback.

Never saves over source, never deletes source images, bakes studyWork only.
Each run is immutable: an existing output directory is rejected.
"""
import argparse
import base64
import collections
import hashlib
import json
import math
import pathlib
import re
import shutil
import struct
import sys
import time

import bpy
import numpy as np
from mathutils import Vector

ROOMS = ['meal', 'sleep', 'studyWork', 'entertainment', 'commute', 'home', 'outdoor', 'social']
INTER = {
    'studyWork': r'(keyboard|_screen$|_monitor$|mug|wclock|anim_Cursor|DeskLampShade)',
    'meal': r'(FridgeDoor|PotLid|meal_tap)',
    'sleep': r'(PullCord|sleep_clock|curt[LR]\d|cloud_|moon_r|crater|sleep_milk|sleep_plush|sleep_mask)',
    'entertainment': r'(tv_screen|entertainment_pad|entertainment_spk|toy_ball)',
    'commute': r'(commute_door|routeDot|route_line)',
    'home': r'(wash_|home_chk|home_vac)',
    'outdoor': r'(_bf|apple)',
    'social': r'(disco|dj_led|mixer|turntable|record|social_spk)',
}
LEGACY = re.compile(r'^(LM_|LMBAKE|LMUV|BAKED_)|lightmap|baked_illumination', re.I)
LM_UV = 'UV_Lightmap'


def log(*args):
    print('PIPELINE', *args, flush=True)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def ancestry(o):
    while o:
        yield o
        o = o.parent


def owner(o):
    hits = {p.name[5:] for p in ancestry(o) if p.name.startswith('Unit_') and p.name[5:] in ROOMS}
    if len(hits) == 1:
        return next(iter(hits)), 'parent'
    if len(hits) > 1:
        return None, 'ambiguous-parent'
    hits = {r for r in ROOMS if o.name.startswith(r + '_')}
    return (next(iter(hits)), 'name-fallback') if len(hits) == 1 else (None, 'unassigned')


def excluded(o):
    for p in ancestry(o):
        if p.get('meelo_old'):
            return 'old-furniture'
        if p.hide_render:
            return 'hidden-render'
        if any(c.name.startswith('旧家具_') or c.hide_render for c in p.users_collection):
            return 'old-or-hidden-collection'
    return None


def classify(o, room):
    skip = excluded(o)
    if skip:
        return skip
    if not room:
        return 'unassigned'
    chain = list(ancestry(o))
    if any('Cat_main' in p.name or p.name.startswith(('CAT_', 'CAT_main')) for p in chain):
        return 'dynamic-cat'
    if any(re.search(INTER[room], p.name) for p in chain):
        return 'dynamic-interaction'
    if any(p.animation_data and (p.animation_data.action or p.animation_data.drivers) for p in chain):
        return 'dynamic-animation'
    if o.data.shape_keys:
        return 'dynamic-shape-keys'
    return 'static'


def json_value(v):
    try:
        if isinstance(v, (int, float, bool, str)):
            return v
        return list(v)
    except Exception:
        return str(v)


def node_snapshot(tree, visited=None):
    visited = set() if visited is None else visited
    if tree.as_pointer() in visited:
        return {'recursive': tree.name}
    visited.add(tree.as_pointer())
    nodes = []
    for n in tree.nodes:
        row = {'name': n.name, 'type': n.type, 'active': n == tree.nodes.active}
        if n.type == 'TEX_IMAGE':
            row.update(image=n.image.name if n.image else None, uv_interpolation=n.interpolation)
        if n.type == 'UVMAP':
            row['uv_map'] = n.uv_map
        if n.type in {'BSDF_PRINCIPLED', 'EMISSION'}:
            row['defaults'] = {s.name: json_value(s.default_value) for s in n.inputs
                               if hasattr(s, 'default_value') and any(k in s.name for k in ['Color', 'Emission', 'Strength', 'Metallic', 'Roughness'])}
        if n.type == 'GROUP' and n.node_tree:
            row['group'] = node_snapshot(n.node_tree, visited)
        nodes.append(row)
    return {'name': tree.name, 'nodes': nodes, 'links': [
        {'from': [l.from_node.name, l.from_socket.name], 'to': [l.to_node.name, l.to_socket.name]}
        for l in tree.links]}


def legacy_nodes(tree, visited=None):
    visited = set() if visited is None else visited
    if tree.as_pointer() in visited:
        return []
    visited.add(tree.as_pointer())
    found = []
    for n in tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and (LEGACY.search(n.image.name) or n.name == 'LMBAKE'):
            found.append(n)
        if n.type == 'GROUP' and n.node_tree:
            found.extend(legacy_nodes(n.node_tree, visited))
    return found


def reachable_legacy(tree):
    # Conservatively checks every legacy texture, even disconnected targets.
    return len(legacy_nodes(tree))


def image_audit(im):
    return {'name': im.name, 'size': list(im.size), 'filepath': im.filepath,
            'packed': bool(im.packed_file), 'color_space': im.colorspace_settings.name,
            'float': im.is_float, 'legacy_candidate': bool(LEGACY.search(im.name))}


def audit_scene():
    objects, materials, material_users = [], {}, collections.defaultdict(list)
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        room, method = owner(o)
        row = {'name': o.name, 'mesh': o.data.name, 'parent': o.parent.name if o.parent else None,
               'room': room, 'ownership_method': method, 'role': classify(o, room),
               'hide_render': o.hide_render, 'hide_viewport': o.hide_viewport,
               'hide_set': o.hide_get(), 'collections': [c.name for c in o.users_collection],
               'uvs': [{'name': u.name, 'active_render': u.active_render,
                        'active': u == o.data.uv_layers.active, 'loops': len(u.data)} for u in o.data.uv_layers],
               'materials': [s.material.name if s.material else None for s in o.material_slots],
               'polygons': len(o.data.polygons),
               'modifiers': [{'name': m.name, 'type': m.type, 'render': m.show_render} for m in o.modifiers],
               'matrix_world': [list(v) for v in o.matrix_world]}
        objects.append(row)
        for slot in o.material_slots:
            m = slot.material
            if not m:
                continue
            material_users[m.name].append({'object': o.name, 'room': room, 'role': row['role']})
            if m.name not in materials:
                materials[m.name] = {'name': m.name, 'users': m.users,
                                      'nodes': node_snapshot(m.node_tree) if m.use_nodes else None}
    shared = {n: users for n, users in material_users.items()
              if len({u['room'] for u in users if u['room']}) > 1}
    return {'objects': objects, 'materials': materials, 'images': [image_audit(i) for i in bpy.data.images],
            'shared_between_rooms': shared,
            'unassigned': [o for o in objects if not o['room']],
            'summary': {r: dict(collections.Counter(o['role'] for o in objects if o['room'] == r)) for r in ROOMS},
            'render': {'engine': bpy.context.scene.render.engine,
                       'view': bpy.context.scene.view_settings.view_transform,
                       'look': bpy.context.scene.view_settings.look, 'exposure': bpy.context.scene.view_settings.exposure}}


def sanitize_tree(tree, room, role, changes):
    # Tree belongs to a copied material; groups are copied before touching their nodes.
    for n in list(tree.nodes):
        if n.type == 'GROUP' and n.node_tree and reachable_legacy(n.node_tree):
            n.node_tree = n.node_tree.copy()
            n.node_tree.name += '__isolated_' + room + '_' + role
            sanitize_tree(n.node_tree, room, role, changes)
        if n.type == 'TEX_IMAGE' and n.image and (LEGACY.search(n.image.name) or n.name == 'LMBAKE'):
            changes.append({'room': room, 'role': role, 'tree': tree.name, 'node': n.name,
                            'image': n.image.name,
                            'removed_links': [{'to': l.to_node.name, 'socket': l.to_socket.name} for l in n.outputs['Color'].links]})
            tree.nodes.remove(n)


def prepare_materials(audit):
    cache, changes = {}, []
    for row in audit['objects']:
        room = row['room']
        if not room:
            continue
        o = bpy.data.objects[row['name']]
        role = 'static' if row['role'] == 'static' else 'dynamic' if row['role'].startswith('dynamic') else 'excluded'
        # Keep all original material data blocks intact, including excluded/old assets.
        if role == 'excluded':
            continue
        for slot in o.material_slots:
            original = slot.material
            if not original:
                continue
            key = (room, role, original.name)
            if key not in cache:
                m = original.copy()
                m.name = original.name + '__' + room + '_' + role
                m['source_material'] = original.name
                m['bake_room'] = room
                m['bake_role'] = role
                if m.use_nodes:
                    sanitize_tree(m.node_tree, room, role, changes)
                    assert reachable_legacy(m.node_tree) == 0, m.name
                cache[key] = m
            # Object-linked slots avoid propagating through shared mesh data.
            slot.link = 'OBJECT'
            slot.material = cache[key]
        o['lightmap_role'] = role
        o['source_object'] = o.name
    return {'material_copies': len(cache), 'removed_legacy_nodes': changes,
            'source_images_retained': [i.name for i in bpy.data.images if LEGACY.search(i.name)]}


def select_objects(objs):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.hide_set(False)
        o.hide_viewport = False
        o.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def uv_validation(objs, resolution=1024):
    occupancy = np.zeros((resolution, resolution), dtype=np.uint16)
    out_bounds, degenerate, triangles = [], 0, 0
    for o in objs:
        me = o.data
        layer = me.uv_layers.get(LM_UV)
        assert layer, o.name
        uv = np.array([v.uv[:] for v in layer.data], dtype=np.float64)
        if not np.isfinite(uv).all() or (uv < -1e-5).any() or (uv > 1.00001).any():
            out_bounds.append(o.name)
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
            pts = uv[list(tri.loops)] * resolution
            a, b, c = pts
            den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            triangles += 1
            if abs(den) < 1e-8:
                degenerate += 1
                continue
            low = np.maximum(0, np.floor(pts.min(0)).astype(int))
            high = np.minimum(resolution, np.ceil(pts.max(0)).astype(int))
            if (high <= low).any():
                continue
            yy, xx = np.mgrid[low[1]:high[1], low[0]:high[0]]
            xx = xx + .5
            yy = yy + .5
            u = ((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v = ((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
            w = 1-u-v
            # Strict triangle interior prevents counting shared edges twice.
            mask = (u > 1e-5) & (v > 1e-5) & (w > 1e-5)
            occupancy[low[1]:high[1], low[0]:high[0]] += mask.astype(np.uint16)
    occupied = int((occupancy > 0).sum())
    overlapping = int((occupancy > 1).sum())
    return {'resolution': resolution, 'triangles': triangles, 'degenerate_triangles': degenerate,
            'out_of_bounds_objects': out_bounds, 'occupied_pixels': occupied,
            'overlap_pixels': overlapping, 'overlap_ratio': overlapping/max(1, occupied),
            'occupancy_ratio': occupied/(resolution*resolution),
            'method': 'strict triangle interior at pixel centers, entire room jointly; not a proof against subpixel overlap'}


def prepare_uv(room, objs, out):
    original_uvs = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        original_uvs[o.name] = [u.name for u in o.data.uv_layers]
        # Evaluate the exact current modifier shape into independent working mesh data.
        # The input .blend and original mesh datablocks remain archived and untouched.
        old_mats = [s.material for s in o.material_slots]
        if o.modifiers:
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        else:
            me = o.data.copy()
        o.data = me
        o.modifiers.clear()
        for i, m in enumerate(old_mats):
            if i < len(o.material_slots):
                o.material_slots[i].link = 'OBJECT'
                o.material_slots[i].material = m
        me['source_mesh_uvs'] = json.dumps(original_uvs[o.name])
        if not me.uv_layers:
            me.uv_layers.new(name='UV_Original')
        original_render = next((u.name for u in me.uv_layers if u.active_render), me.uv_layers[0].name)
        layer = me.uv_layers.get(LM_UV) or me.uv_layers.new(name=LM_UV)
        me.uv_layers.active = layer
        me.uv_layers[original_render].active_render = True
    select_objects(objs)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.object.mode_set(mode='OBJECT')
    weights = {}
    for o in objs:
        importance = 1.35 if re.search(r'BackWall|Floor$|_floor|Frame_', o.name) else 1.15 if re.search(r'desk|shelf|cab|chair|bed|sofa', o.name, re.I) else 1.0
        weights[o.name] = importance
        for uv in o.data.uv_layers[LM_UV].data:
            uv.uv *= math.sqrt(importance)
    used_margin = None
    for pixels in ([2, 1] if room == 'studyWork' else [8, 4, 2, 1]):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(udim_source='ACTIVE_UDIM', rotate=True, scale=True, margin_method='FRACTION', margin=pixels/1024)
        bpy.ops.object.mode_set(mode='OBJECT')
        packed = np.array([v.uv[:] for o in objs for v in o.data.uv_layers[LM_UV].data])
        if (packed.max(0)-packed.min(0) <= 1.0001).all():
            used_margin = pixels
            break
    assert used_margin is not None, room+' cannot fit atlas even at one pixel margin'
    # Background Blender has no Image Editor active tile. Translate the complete
    # packed atlas as one block into tile 1001; never wrap objects independently.
    all_uvs = np.array([v.uv[:] for o in objs for v in o.data.uv_layers[LM_UV].data])
    lo, hi = all_uvs.min(0), all_uvs.max(0)
    assert (hi-lo <= 1.0001).all(), (room, lo, hi)
    shift = (lo+hi)/2 - .5
    for o in objs:
        for v in o.data.uv_layers[LM_UV].data:
            v.uv.x -= float(shift[0]); v.uv.y -= float(shift[1])
    for o in objs:
        old = original_uvs[o.name]
        assert all(o.data.uv_layers.get(n) for n in old), o.name
        o['lightmap_room'] = room
        o['lightmap_static'] = True
        o['lightmap_uv'] = LM_UV
    result = uv_validation(objs)
    result.update(objects=len(objs), original_uvs_preserved=original_uvs, importance_weights=weights,
                  texel_allocation='surface area normalized, multiplied by importance weight', requested_island_margin_pixels=8,
                  actual_island_margin_pixels=used_margin,
                  note='Test-only reduced margin where chart count prevents packing; final resolution must be reevaluated')
    write(out/'reports'/f'uv-{room}.json', result)
    assert not result['out_of_bounds_objects'], room
    assert result['overlap_pixels'] == 0, f'{room}: UV overlaps: {result["overlap_pixels"]}'
    return result


def configure_cycles(scene, samples=32):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.cycles.diffuse_bounces = 4
    scene.cycles.device = 'CPU'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'CUDA'
        prefs.get_devices()
        gpu = [d for d in prefs.devices if d.type == 'CUDA']
        if gpu:
            for d in prefs.devices:
                d.use = d.type == 'CUDA'
            scene.cycles.device = 'GPU'
    except Exception as e:
        log('GPU_UNAVAILABLE', str(e))
    scene.render.resolution_x = 900
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    return scene.cycles.device


def save_float_image(image, path, fmt):
    image.filepath_raw = str(path)
    image.file_format = fmt
    image.save()


def write_rgb(pixels, path, colorspace='Non-Color', fmt='HDR'):
    h, w = pixels.shape[:2]
    im = bpy.data.images.new(path.stem, width=w, height=h, alpha=True, float_buffer=True)
    im.colorspace_settings.name = colorspace
    rgba = np.ones((h, w, 4), np.float32)
    rgba[:, :, :3] = pixels[:, :, :3]
    im.pixels.foreach_set(rgba.ravel())
    im.update()
    save_float_image(im, path, fmt)
    return im


def make_preview(image, scene, path):
    image.save_render(str(path), scene=scene)


def make_camera(room):
    unit = bpy.data.objects['Unit_'+room]
    cam = bpy.data.objects.new('LM_ValidationCamera', bpy.data.cameras.new('LM_ValidationCamera'))
    bpy.context.scene.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 9.5
    cam.location = unit.matrix_world @ Vector((0, -10, 2.6))
    target = unit.matrix_world @ Vector((0, 0, 1.75))
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam, {'position_blender_local': [0, -10, 2.6], 'target_blender_local': [0, 0, 1.75],
                 'position_web': [0, 2.6, 10], 'target_web': [0, 1.75, 0],
                 'ortho_width': 9.5, 'ortho_height': 9.5/1.5, 'width': 900, 'height': 600}


def render_to(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def room_isolation(audit, room):
    rows = {o['name']: o for o in audit['objects']}
    log_rows = []
    for o in bpy.context.scene.objects:
        if o.type not in {'MESH', 'LIGHT', 'FONT'}:
            continue
        r, _ = owner(o)
        enabled = r == room and not excluded(o)
        row = rows.get(o.name)
        if row and row['role'].startswith('dynamic'):
            enabled = False
        o.hide_render = not enabled
        log_rows.append({'name': o.name, 'room': r, 'enabled_for_test': enabled})
    return log_rows


def bake_study(audit, static, out, size, samples):
    room = 'studyWork'
    scene = bpy.context.scene
    isolation = room_isolation(audit, room)
    write(out/'reports'/'study-isolation.json', isolation)
    device = configure_cycles(scene, samples)
    camera, camera_data = make_camera(room)
    write(out/'assets'/'camera.json', camera_data)
    # Cycles reference uses exactly the cleaned original materials and original room lights/world.
    render_to(scene, out/'renders'/'study-reference.png')
    objs = static[room]
    target = bpy.data.images.new('NEW_LM_studyWork_test', width=size, height=size, alpha=True, float_buffer=True)
    target.colorspace_settings.name = 'Non-Color'
    materials = {s.material for o in objs for s in o.material_slots if s.material}
    for m in materials:
        assert m.use_nodes, m.name
        assert reachable_legacy(m.node_tree) == 0, m.name
        nt = m.node_tree
        node = nt.nodes.new('ShaderNodeTexImage')
        node.name = 'NEW_LIGHTMAP_TARGET'
        node.label = 'NEW studyWork diffuse direct+indirect; never source emission'
        node.image = target
        uvn = nt.nodes.new('ShaderNodeUVMap')
        uvn.uv_map = LM_UV
        nt.links.new(uvn.outputs['UV'], node.inputs['Vector'])
        for n in nt.nodes:
            n.select = False
        node.select = True
        nt.nodes.active = node
    for o in objs:
        o.data.uv_layers.active = o.data.uv_layers[LM_UV]
    select_objects(objs)
    uv_report = json.loads((out/'reports'/'uv-studyWork.json').read_text(encoding='utf8'))
    bake_margin = max(1, uv_report['actual_island_margin_pixels']//2)
    scene.render.bake.margin = bake_margin
    scene.render.bake.use_clear = True
    scene.render.bake.use_pass_color = False
    scene.render.bake.use_pass_direct = True
    scene.render.bake.use_pass_indirect = True
    assert all(s.material.node_tree.nodes.active.image == target for o in objs for s in o.material_slots if s.material)
    started = time.time()
    log('BAKE_STUDY_START', len(objs), size, device)
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, uv_layer=LM_UV,
                        margin=bake_margin, use_clear=True)
    px = np.empty(size*size*4, np.float32)
    target.pixels.foreach_get(px)
    px = px.reshape(size, size, 4)
    assert np.isfinite(px).all(), 'Non-finite bake pixels'
    assert float(px[:, :, :3].max()) > .01, 'Black bake'
    save_float_image(target, out/'assets'/'studyWork-lightmap.exr', 'OPEN_EXR')
    save_float_image(target, out/'assets'/'studyWork-lightmap.hdr', 'HDR')
    make_preview(target, scene, out/'renders'/'study-lightmap-preview.png')
    # PNG is only a transport marker for the UV channel in glTF occlusionTexture.
    # The viewer discards it and loads the linear HDR above instead.
    carrier = write_rgb(np.clip(px[:, :, :3], 0, 1), out/'assets'/'uv-channel-carrier.png', fmt='PNG')
    stats = {'room': room, 'resolution': size, 'samples': samples, 'device': device,
             'seconds': time.time()-started, 'type': 'DIFFUSE', 'passes': ['DIRECT', 'INDIRECT'], 'color_pass': False,
             'bake_margin_pixels': bake_margin,
             'bake_uv_layer_explicit': LM_UV,
             'pixel_min': float(px[:, :, :3].min()), 'pixel_max': float(px[:, :, :3].max()),
             'pixel_mean': float(px[:, :, :3].mean()), 'finite': bool(np.isfinite(px).all()),
             'target_materials': len(materials), 'static_objects': len(objs),
             'legacy_nodes_in_bake_materials': sum(reachable_legacy(m.node_tree) for m in materials)}
    write(out/'reports'/'study-bake.json', stats)
    # Bake only one room, then save all repair work in a distinct .blend.
    target.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'blends'/'study-baked.blend'))
    return target, carrier, camera_data


def render_baked_comparison(target, static, out):
    # Reconstruct diffuse appearance as base color * baked diffuse irradiance,
    # then add the preserved genuine design emission. No real lights hit these shaders.
    objs = static['studyWork']
    original = {o: [s.material for s in o.material_slots] for o in objs}
    cache = {}
    for o in objs:
        for slot in o.material_slots:
            m = slot.material
            if not m:
                continue
            if m not in cache:
                n = m.copy()
                n.name += '__COMPARE_BAKED'
                nt = n.node_tree
                bs = next((x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'), None)
                output = next(x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL' and x.is_active_output)
                if not bs:
                    raise RuntimeError('Unsupported comparison shader '+m.name)
                tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = target
                uv = nt.nodes.new('ShaderNodeUVMap'); uv.uv_map = LM_UV
                nt.links.new(uv.outputs['UV'], tex.inputs['Vector'])
                mul = nt.nodes.new('ShaderNodeMixRGB'); mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
                base = bs.inputs['Base Color']
                if base.is_linked:
                    nt.links.new(base.links[0].from_socket, mul.inputs[1])
                else:
                    mul.inputs[1].default_value = base.default_value
                nt.links.new(tex.outputs['Color'], mul.inputs[2])
                add = nt.nodes.new('ShaderNodeMixRGB'); add.blend_type = 'ADD'; add.inputs[0].default_value = 1
                nt.links.new(mul.outputs[0], add.inputs[1])
                em = bs.inputs['Emission Color']; strength = bs.inputs['Emission Strength'].default_value
                if em.is_linked:
                    scale = nt.nodes.new('ShaderNodeMixRGB'); scale.blend_type = 'MULTIPLY'; scale.inputs[0].default_value = 1
                    scale.inputs[2].default_value = (strength, strength, strength, 1)
                    nt.links.new(em.links[0].from_socket, scale.inputs[1]); nt.links.new(scale.outputs[0], add.inputs[2])
                else:
                    add.inputs[2].default_value = tuple(float(c)*strength for c in em.default_value[:3])+(1,)
                emit = nt.nodes.new('ShaderNodeEmission')
                nt.links.new(add.outputs[0], emit.inputs['Color'])
                nt.links.new(emit.outputs[0], output.inputs['Surface'])
                cache[m] = n
            slot.material = cache[m]
    render_to(bpy.context.scene, out/'renders'/'study-baked-reconstruction.png')
    for o, mats in original.items():
        for slot, m in zip(o.material_slots, mats):
            slot.material = m
    # Image metrics in the same display transform. Background is excluded approximately by alpha.
    ref = bpy.data.images.load(str(out/'renders'/'study-reference.png'), check_existing=False)
    baked = bpy.data.images.load(str(out/'renders'/'study-baked-reconstruction.png'), check_existing=False)
    a, b = np.array(ref.pixels[:], np.float32).reshape(-1, 4), np.array(baked.pixels[:], np.float32).reshape(-1, 4)
    diff = abs(a[:, :3]-b[:, :3])
    metrics = {'mae_srgb_rgb_all_pixels': float(diff.mean()), 'rmse_srgb_rgb_all_pixels': float(np.sqrt((diff**2).mean())),
               'p95_abs_srgb_error': float(np.percentile(diff, 95)),
               'comparison': 'same Cycles camera, same AgX view; reference full PBR versus diffuse-only lightmap reconstruction',
               'known_difference': 'view-dependent specular is intentionally not baked; dynamic objects excluded from both'}
    write(out/'reports'/'blender-comparison.json', metrics)
    write_rgb(np.minimum(diff.reshape(600, 900, 3)*4, 1), out/'renders'/'study-difference-x4.png', colorspace='sRGB', fmt='PNG')
    return metrics


def export_study(audit, static, carrier, out, camera_data):
    """Archived Diffuse adapter. New experiments use export_room directly."""
    return export_room(audit, static, carrier, out, camera_data, room='studyWork', texture_kind='lightmap')


def export_room(audit, static, carrier, out, camera_data, room, texture_kind='lightmap'):
    """Shared named-mesh/secondary-UV exporter. Never alters the source scene."""
    assert room in ROOMS and texture_kind in {'lightmap', 'ao'}
    source_scene = bpy.context.scene
    src_unit = bpy.data.objects['Unit_'+room]
    rows = {r['name']: r for r in audit['objects']}
    # Baking temporarily hides dynamics. Decide export eligibility from the original
    # audit, not those temporary render flags, so every interaction is retained.
    keep = [o for o in src_unit.children_recursive
            if (o.type == 'MESH' and rows[o.name]['role'] in {'static', 'dynamic-cat', 'dynamic-interaction', 'dynamic-animation', 'dynamic-shape-keys'})
            or (o.type != 'MESH' and not excluded(o))]
    # Export on detached scene copies; original names/hierarchy remain intact in saved repair files.
    tmp = bpy.data.scenes.new('BAKE_EXPORT_'+room)
    root = bpy.data.objects.new('Unit_'+room+'__EXPORT', None); tmp.collection.objects.link(root)
    copies, material_cache = {}, {}
    source_world = {o: o.matrix_world.copy() for o in keep}
    inv = src_unit.matrix_world.inverted()
    static_names = {o.name for o in static[room]}
    from io_scene_gltf2.blender.com.material_helpers import create_settings_group
    settings = create_settings_group('glTF Material Output')
    for o in keep:
        if o.type not in {'MESH', 'EMPTY'}:
            continue
        cp = o.copy()
        cp.name = o.name+'__EXPORT'
        if o.type == 'MESH':
            cp.data = o.data.copy()
        tmp.collection.objects.link(cp); cp.hide_render = False; cp.hide_viewport = False
        copies[o] = cp
    for o, cp in copies.items():
        cp.parent = copies.get(o.parent, root)
        parent_world = source_world[o.parent] if o.parent in copies else src_unit.matrix_world
        cp.matrix_parent_inverse.identity()
        cp.matrix_basis = parent_world.inverted() @ source_world[o]
        cp['source_object'] = o.name
        cp['is_static_lightmap'] = o.name in static_names and texture_kind == 'lightmap'
        cp['is_static_ao'] = o.name in static_names and texture_kind == 'ao'
        # Preserve existing Three.js interaction aliases while retaining source names in extras.
        dyn_parent = any(re.search(INTER[room], p.name) for p in ancestry(o.parent) if p != src_unit)
        if o.name == room+'_Cat_main':
            alias = 'CAT_main'
        elif re.search(INTER[room], o.name) and not dyn_parent:
            alias = 'I_'+o.name
        elif re.search(r'_(BackWall|Frame_L|Frame_R|LeftWall_back|LeftWall_front|LeftWall_lintel|RightWall)$', o.name):
            alias = 'SHELL_'+o.name
        else:
            alias = o.name
        cp['interaction_alias'] = alias
        if cp.type != 'MESH':
            continue
        for slot in cp.material_slots:
            original = slot.material
            if not original:
                continue
            key = (original, o.name in static_names)
            if key not in material_cache:
                m = original.copy();m.name += '__EXPORT'
                if o.name in static_names:
                    m['roomLightmap' if texture_kind == 'lightmap' else 'roomAO'] = room
                    m['lightmapUV' if texture_kind == 'lightmap' else 'aoUV'] = LM_UV
                    tex = m.node_tree.nodes.new('ShaderNodeTexImage');tex.image = carrier
                    uv = m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map = LM_UV
                    group = m.node_tree.nodes.new('ShaderNodeGroup');group.node_tree = settings
                    m.node_tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
                    m.node_tree.links.new(tex.outputs['Color'], group.inputs['Occlusion'])
                material_cache[key] = m
            slot.link = 'OBJECT';slot.material = material_cache[key]
        # Restore UV0 as active-render; UV_Lightmap is explicitly referenced by carrier UV node.
        uv0 = next(u for u in cp.data.uv_layers if u.name != LM_UV) if len(cp.data.uv_layers)>1 else None
        if uv0:
            uv0.active_render = True
    previous = bpy.context.window.scene
    bpy.context.window.scene = tmp
    raw_path = out/'assets'/f'{room}-export-raw.glb'
    bpy.ops.export_scene.gltf(filepath=str(raw_path), export_format='GLB', use_active_scene=True,
                              export_extras=True, export_lights=False, export_cameras=False,
                              export_yup=True, export_apply=False, export_materials='EXPORT')
    bpy.context.window.scene = previous
    # Remove Blender suffixes deterministically in glTF JSON, without touching original Blender names.
    data = raw_path.read_bytes();json_len = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20+json_len])
    binary = data[20+json_len:]
    for node in gltf.get('nodes', []):
        source = node.get('extras', {}).get('source_object')
        if source:
            node['name'] = node['extras'].get('interaction_alias', source)
        elif node.get('name', '').startswith('Unit_'+room):
            node['name'] = 'Unit_'+room
    for m in gltf.get('materials', []):
        m['name'] = m.get('name', '').removesuffix('__EXPORT')
    encoded = json.dumps(gltf, separators=(',', ':'), ensure_ascii=False).encode()
    encoded += b' '*((-len(encoded)) % 4)
    final = struct.pack('<4sII', b'glTF', 2, 12+8+len(encoded)+len(binary))+struct.pack('<I4s', len(encoded), b'JSON')+encoded+binary
    (out/'assets'/f'{room}.glb').write_bytes(final)
    static_nodes = [n for n in gltf['nodes'] if n.get('extras', {}).get('is_static_'+('lightmap' if texture_kind == 'lightmap' else 'ao'))]
    errors, uv_bindings = [], []
    for node in static_nodes:
        if 'mesh' not in node:
            continue
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            m = gltf['materials'][prim['material']]
            texcoord = m.get('occlusionTexture', {}).get('texCoord', 0)
            if f'TEXCOORD_{texcoord}' not in prim['attributes'] or texcoord < 1:
                errors.append({'node': node['name'], 'texcoord': texcoord, 'attributes': list(prim['attributes'])})
            uv_bindings.append({'node': node['name'], 'material': m['name'], 'channel': texcoord})
    source_meshes = {o.name for o in keep if o.type=='MESH'}
    exported_sources = {n.get('extras', {}).get('source_object') for n in gltf['nodes'] if 'mesh' in n}
    result = {'static_nodes': len(static_nodes), 'uv_bindings': uv_bindings, 'errors': errors,
              'source_meshes': len(source_meshes), 'exported_meshes': len(exported_sources),
              'missing_source_objects': sorted(source_meshes-exported_sources),
              'interaction_aliases': [n['name'] for n in gltf['nodes'] if n.get('name','').startswith(('I_', 'CAT_main', 'SHELL_'))],
              'original_hierarchy_preserved_in_blend': True, 'gltf_preserves_parent_relationships': True,
              'uv_transport': 'occlusionTexture is the actual non-color AO map' if texture_kind == 'ao' else 'occlusionTexture carries UV channel; viewer removes carrier and loads linear HDR as lightMap',
              'texture_kind': texture_kind, 'uvChannel': 1,
              'colorSpace': 'NoColorSpace', 'flipY': False}
    if texture_kind == 'lightmap':
        result['lightMapIntensity'] = math.pi
    else:
        result['aoMapIntensity'] = .5
    write(out/'reports'/'gltf-validation.json', result)
    assert not errors, errors[:3]
    assert not result['missing_source_objects'], result['missing_source_objects']
    manifest = {'room': room, 'glb': f'{room}.glb',
                'uvChannel': 1, 'colorSpace': 'linear',
                'camera': camera_data, 'staticObjects': sorted(static_names),
                'dynamicPolicy': 'PBR with identical real lights in A/B; only static meshes receive AO' if texture_kind == 'ao' else 'PBR, real lights; static diffuse direct+indirect lightmap must not receive duplicate direct diffuse',
                'toneMapping': 'AgX once; Blender Medium High Contrast is not identical to Three.js AgX',
                'blenderLights': [{'name':o.name, 'type':o.data.type, 'energy':o.data.energy,
                                   'color':list(o.data.color),
                                   'position':list(inv@o.matrix_world.translation),
                                   'direction':list((inv.to_3x3()@o.matrix_world.to_3x3())@Vector((0,0,-1))),
                                   'size':getattr(o.data,'size',None),'size_y':getattr(o.data,'size_y',None),
                                   'angle':getattr(o.data,'spot_size',None),'blend':getattr(o.data,'spot_blend',None),
                                   'castShadow':getattr(o.data,'use_shadow',True),'radius':getattr(o.data,'shadow_soft_size',None)}
                                  for o in src_unit.children_recursive if o.type=='LIGHT' and not excluded(o)]}
    if texture_kind == 'lightmap':
        manifest.update(lightmap=f'{room}-lightmap.hdr', lightMapIntensity=math.pi)
    else:
        manifest.update(ao=f'{room}-ao.png', aoMapIntensity=.5, experiment='AO_ONLY',
                        abContract='Only aoMap and aoMapIntensity may differ; lights/camera/CMF/model/background fixed')
    write(out/'assets'/'manifest.json', manifest)
    # Detached export proxies are temporary, not part of the repaired Blender asset.
    for cp in list(copies.values()):
        data = cp.data if cp.type == 'MESH' else None
        bpy.data.objects.remove(cp, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)
    bpy.data.objects.remove(root, do_unlink=True)
    bpy.data.scenes.remove(tmp)
    for m in material_cache.values():
        if m.users == 0:
            bpy.data.materials.remove(m)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--size', type=int, choices=[512, 1024], default=1024)
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--allow-archived-diffuse', action='store_true', help='Explicit opt-in to the archived study Diffuse experiment')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.allow_archived_diffuse:
        parser.error('Study Diffuse experiment is archived. Use meal_ao.py for the active AO-only workflow.')
    source, out = pathlib.Path(args.source).resolve(), pathlib.Path(args.out).resolve()
    assert source.is_file()
    assert not out.exists(), 'Refusing to overwrite a previous run'
    assert source not in out.parents
    out.mkdir(parents=True)
    for d in ['blends', 'reports', 'assets', 'renders']:
        (out/d).mkdir()
    original_hash = sha(source)
    backup = out/'blends'/'original-backup.blend'
    shutil.copy2(source, backup)
    assert sha(backup) == original_hash
    write(out/'reports'/'provenance.json', {'source':str(source),'sha256':original_hash,'backup':str(backup),'arguments':vars(args)})
    bpy.ops.wm.open_mainfile(filepath=str(backup))
    audit = audit_scene()
    write(out/'reports'/'audit-original.json', audit)
    log('AUDIT', len(audit['objects']), len(audit['shared_between_rooms']), 'shared', len(audit['unassigned']), 'unassigned')
    expected = {o.name:(o.parent.name if o.parent else None) for o in bpy.data.objects}
    isolation = prepare_materials(audit)
    write(out/'reports'/'material-isolation.json', isolation)
    static = {r:[bpy.data.objects[row['name']] for row in audit['objects'] if row['room']==r and row['role']=='static'] for r in ROOMS}
    uvs = {}
    for room, objs in static.items():
        log('PREPARE_UV', room, len(objs))
        uvs[room] = prepare_uv(room, objs, out)
        log('UV_OK', room, uvs[room]['occupancy_ratio'])
    actual = {o.name:(o.parent.name if o.parent else None) for o in bpy.data.objects}
    assert expected == actual, 'Names or hierarchy changed during preparation'
    write(out/'reports'/'audit-repaired.json', audit_scene())
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'blends'/'prepared-eight-rooms.blend'))
    target, carrier, camera = bake_study(audit, static, out, args.size, args.samples)
    comparison = render_baked_comparison(target, static, out)
    export = export_study(audit, static, carrier, out, camera)
    assert sha(source) == original_hash, 'SOURCE WAS MODIFIED'
    result = {'completed': True, 'source_hash_unchanged': True, 'baked_rooms': ['studyWork'],
              'other_rooms_baked': False, 'uv_rooms': list(uvs), 'comparison': comparison,
              'gltf_errors': len(export['errors']), 'production_app_modified': False}
    write(out/'reports'/'result.json', result)
    log('COMPLETE', json.dumps(result))


if __name__ == '__main__':
    main()
