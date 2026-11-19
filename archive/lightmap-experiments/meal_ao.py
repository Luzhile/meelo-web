"""AO-only experiment using the already prepared eight-room asset.

Run with Blender --background --python-exit-code 1 --python meal_ao.py --
  --prepared FILE --out NEW_DIR --samples 256 --distance .25 --margin 8
No UV unwrap, Diffuse bake, GI bake, color bake, or source save is performed.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import time

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pipeline as shared


def uv_state():
    result = {}
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        layers = []
        for uv in o.data.uv_layers:
            values = np.empty(len(uv.data)*2, np.float32)
            uv.data.foreach_get('uv', values)
            layers.append({'name': uv.name, 'hash': hashlib.sha256(values.tobytes()).hexdigest(),
                           'loops': len(uv.data), 'active_render': uv.active_render})
        result[o.name] = {'parent': o.parent.name if o.parent else None, 'layers': layers,
                          'room': shared.owner(o)[0], 'role': o.get('lightmap_role')}
    return result


def packed_image_state():
    return {i.name: {'filepath': i.filepath, 'size': list(i.size),
                      'packed_sha256': hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None}
            for i in bpy.data.images}


def material_defaults(materials):
    result = {}
    for m in materials:
        result[m.name] = {'source_material': m.get('source_material'),
                           'nodes': [n for n in shared.node_snapshot(m.node_tree)['nodes']
                                     if n['type'] in {'BSDF_PRINCIPLED', 'EMISSION'}]}
        for n in result[m.name]['nodes']:
            n.pop('active', None)
    return result


def dynamic_evaluation(dynamic, static):
    def bounds(o):
        points = [o.matrix_world@Vector(v) for v in o.bound_box]
        return np.min([p[:] for p in points], 0), np.max([p[:] for p in points], 0)
    boxes = [(o.name, bounds(o)) for o in static]
    rows = []
    for o in dynamic:
        lo, hi = bounds(o)
        distances = []
        for name, (a, b) in boxes:
            delta = np.maximum(0, np.maximum(a-hi, lo-b))
            distances.append((float(np.linalg.norm(delta)), name))
        rows.append({'object': o.name, 'role': o.get('lightmap_role'),
                     'nearest_static_bounds': sorted(distances)[:3],
                     'policy': 'excluded from baked receivers and occluders; remains real-time PBR in both web modes'})
    return {'objects': rows,
            'evaluation': 'AABB distances only; not a penetration test. Cat/doors/lid/tap cannot leave fixed AO on static surfaces.',
            'limitation': 'No static AO shadow is baked under a moving cat or opened door. Real-time shadow behavior is identical in both modes.'}


def coverage_mask(objs, size):
    mask = np.zeros((size, size), bool)
    for o in objs:
        me = o.data; me.calc_loop_triangles(); uv = me.uv_layers[shared.LM_UV]
        for tri in me.loop_triangles:
            pts = np.array([uv.data[i].uv[:] for i in tri.loops])*size
            a, b, c = pts
            den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-10:
                continue
            lo = np.maximum(0, np.floor(pts.min(0)).astype(int))
            hi = np.minimum(size, np.ceil(pts.max(0)).astype(int))
            if (hi<=lo).any():
                continue
            yy, xx = np.mgrid[lo[1]:hi[1], lo[0]:hi[0]]; xx=xx+.5; yy=yy+.5
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
            mask[lo[1]:hi[1],lo[0]:hi[0]] |= (u>0)&(v>0)&(1-u-v>0)
    return mask


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepared',required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--samples',type=int,default=256)
    parser.add_argument('--distance',type=float,default=.25)
    parser.add_argument('--margin',type=int,choices=range(8,17),default=8)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=pathlib.Path(args.prepared).resolve();out=pathlib.Path(args.out).resolve()
    assert source.is_file() and not out.exists(), 'Use the prepared input and a completely new output directory'
    assert .05<=args.distance<=.5, 'Distance must stay within the contact-AO test range'
    out.mkdir(parents=True)
    for d in ['assets','reports','blends','renders']:(out/d).mkdir()
    source_hash=shared.sha(source)
    backup=out/'blends/prepared-input-snapshot.blend';shutil.copy2(source,backup)
    bpy.ops.wm.open_mainfile(filepath=str(backup))
    before_uv=uv_state();images_before=packed_image_state()
    shared.write(out/'reports/input-uv-state.json',before_uv)
    shared.write(out/'reports/input-image-state.json',images_before)
    audit=shared.audit_scene();shared.write(out/'reports/prepared-asset-audit.json',audit)
    static=[o for o in bpy.data.objects if o.type=='MESH' and shared.owner(o)[0]=='meal'
            and o.get('lightmap_static') and not shared.excluded(o)]
    dynamic=[o for o in bpy.data.objects if o.type=='MESH' and shared.owner(o)[0]=='meal'
             and o.get('lightmap_role')=='dynamic' and not shared.excluded(o)]
    assert static and dynamic
    assert all(o.data.uv_layers.get(shared.LM_UV) for o in static)
    materials={s.material for o in static for s in o.material_slots if s.material}
    assert all(m.get('bake_room')=='meal' and m.get('bake_role')=='static' for m in materials)
    assert all(shared.reachable_legacy(m.node_tree)==0 for m in materials)
    uv_validation=shared.uv_validation(static,1024)
    assert not uv_validation['out_of_bounds_objects'] and uv_validation['overlap_pixels']==0
    shared.write(out/'reports/reused-meal-uv-validation.json',uv_validation)
    shared.write(out/'reports/dynamic-occlusion-evaluation.json',dynamic_evaluation(dynamic,static))
    defaults_before=material_defaults(materials)
    visibility={o:(o.hide_render,o.hide_viewport,o.hide_get()) for o in bpy.context.scene.objects}
    original_active_uv={o:o.data.uv_layers.active_index for o in static}
    for o in bpy.context.scene.objects:
        if o.type in {'MESH','FONT'}:o.hide_render=o not in static
    scene=bpy.context.scene;device=shared.configure_cycles(scene,args.samples)
    # The dedicated Cycles AO pass does not evaluate direct/indirect/color passes.
    scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=False
    scene.cycles.diffuse_bounces=0
    scene.world.light_settings.distance=args.distance
    scene.world.light_settings.ao_factor=1
    target=bpy.data.images.new('NEW_AO_meal_1024',width=1024,height=1024,alpha=True,float_buffer=True)
    target.colorspace_settings.name='Non-Color';target.generated_color=(1,1,1,1)
    target.pixels.foreach_set(np.ones(1024*1024*4,np.float32));target.update()
    for m in materials:
        nt=m.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.name='NEW_AO_TARGET';tex.image=target
        tex.label='AO ONLY: disconnected bake target; not a Base Color or Emission input'
        uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=shared.LM_UV
        nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
        for n in nt.nodes:n.select=False
        tex.select=True;nt.nodes.active=tex
    shared.select_objects(static)
    for o in static:o.data.uv_layers.active=o.data.uv_layers[shared.LM_UV]
    assert all(m.node_tree.nodes.active.image==target for m in materials)
    shared.log('MEAL_AO_START',len(static),'static',len(dynamic),'dynamic excluded','distance',args.distance,device)
    started=time.time()
    bpy.ops.object.bake(type='AO',uv_layer=shared.LM_UV,margin=args.margin,margin_type='EXTEND',use_clear=False)
    seconds=time.time()-started
    px=np.empty(1024*1024*4,np.float32);target.pixels.foreach_get(px);px=px.reshape(1024,1024,4)
    assert np.isfinite(px).all()
    assert px[:,:,:3].min()>=-1e-5 and px[:,:,:3].max()<=1.0001
    mask=coverage_mask(static,1024);valid=px[:,:,0][mask]
    assert valid.max()>.5 and valid.min()<.99, 'AO is empty, black or uniformly white'
    # Raw output is archived; PNG uses the same linear/non-color AO values, without AgX.
    shared.save_float_image(target,out/'assets/meal-ao-linear.exr','OPEN_EXR')
    png=bpy.data.images.new('NEW_AO_meal_png',width=1024,height=1024,alpha=True,float_buffer=False)
    png.colorspace_settings.name='Non-Color';png.pixels.foreach_set(np.clip(px,0,1).ravel());png.update()
    shared.save_float_image(png,out/'assets/meal-ao.png','PNG')
    png.pack();target.pack()
    for o,index in original_active_uv.items():o.data.uv_layers.active_index=index
    for o,(render,viewport,hidden) in visibility.items():o.hide_render=render;o.hide_viewport=viewport;o.hide_set(hidden)
    assert uv_state()==before_uv, 'Prepared UV coordinates/layers/hierarchy changed'
    assert material_defaults(materials)==defaults_before, 'Base PBR/emission defaults changed'
    after_images=packed_image_state()
    assert all(after_images[name]==state for name,state in images_before.items()), 'An old image was modified'
    assert shared.sha(source)==source_hash
    camera,camera_data=shared.make_camera('meal');shared.write(out/'assets/camera.json',camera_data)
    export=shared.export_room(audit,{'meal':static},png,out,camera_data,room='meal',texture_kind='ao')
    manifest=json.loads((out/'assets/manifest.json').read_text(encoding='utf8'))
    manifest.update(aoDistance=args.distance,aoMargin=args.margin,aoSamples=args.samples,
                    worldApproximation={'ambientColorLinear':[.8,.8,.8],'ambientIntensity':.3,
                                        'note':'Same baseline as the previous independent viewer; unchanged by AO switch/slider'},
                    defaultMode='ao',defaultAOIntensity=.5)
    shared.write(out/'assets/manifest.json',manifest)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'blends/meal-ao-working.blend'))
    result={'bake_type':'AO','room':'meal','resolution':1024,'samples':args.samples,'margin':args.margin,
            'distance':args.distance,'distance_property':'scene.world.light_settings.distance',
            'distance_property_description':scene.world.light_settings.bl_rna.properties['distance'].description,
            'device':device,'seconds':seconds,'static_objects':len(static),'excluded_dynamic_objects':len(dynamic),
            'material_targets':len(materials),'uv_regenerated':False,'uv_layer_explicit':shared.LM_UV,
            'all_eight_uvs_unchanged':True,'old_images_unchanged':True,'material_defaults_unchanged':True,
            'prepared_input_unchanged':True,'prepared_sha256':source_hash,
            'old_lightmap_nodes_in_participating_materials':0,'direct_pass':False,'indirect_pass':False,'color_pass':False,
            'global_min':float(px[:,:,:3].min()),'global_max':float(px[:,:,:3].max()),
            'surface_min':float(valid.min()),'surface_mean':float(valid.mean()),
            'surface_p05':float(np.percentile(valid,5)),'surface_p50':float(np.percentile(valid,50)),
            'surface_p95':float(np.percentile(valid,95)),'surface_pixels':int(mask.sum()),
            'exported_room_meshes':export['source_meshes'],'exported_static_meshes':len(static),'gltf_uv_errors':export['errors']}
    shared.write(out/'reports/ao-result.json',result)
    shared.write(out/'reports/output-uv-state.json',uv_state())
    shared.write(out/'reports/provenance.json',{'prepared':str(source),'prepared_sha256':source_hash,
                 'input_snapshot':str(backup),'reuse':'No preparation, material-isolation or UV generation functions were executed',
                 'shared_functions':['audit_scene','uv_validation','configure_cycles','select_objects','make_camera','export_room'],
                 'archived_diffuse':'study-04 remains untouched and is not loaded by this experiment'})
    shared.log('MEAL_AO_COMPLETE',json.dumps(result))


if __name__=='__main__':main()
