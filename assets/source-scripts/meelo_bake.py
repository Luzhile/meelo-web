# 咪楼烘焙：把房间的全局光照（含墙面颜色反弹）烤进一张 lightmap，网页里当 lightMap 用
import bpy, bmesh, os, time
import numpy as np

LM_SIZE = 2048
SCALE = 0.5          # 存图前把辐照度 ×0.5，避免 8 位图在灯下截断；网页 lightMapIntensity 乘回来
OUT = os.path.join(os.environ.get('TEMP', '.'), 'meelo_lm')

def _is_old(o):
    p = o
    while p:
        if p.get('meelo_old'): return True
        p = p.parent
    return False

def room_meshes(r):
    u = bpy.data.objects['Unit_' + r]
    cat = bpy.data.objects[r + '_Cat_main']; cs = set(cat.children_recursive) | {cat}
    out = []
    for o in u.children_recursive:
        if o.type != 'MESH' or o in cs or _is_old(o) or o.hide_render: continue
        out.append(o)
    return out

def _apply_mods(o):
    if not o.modifiers: return
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    old = o.data; o.modifiers.clear(); o.data = me
    if old.users == 0: bpy.data.meshes.remove(old)

def prep_uv(r):
    objs = room_meshes(r)
    for o in objs:
        if o.data.users > 1: o.data = o.data.copy()
        _apply_mods(o)
        me = o.data
        for uv in list(me.uv_layers):
            if uv.name != 'LM': me.uv_layers.remove(uv)
        if 'LM' not in me.uv_layers: me.uv_layers.new(name='LM')
        me.uv_layers.active = me.uv_layers['LM']
    vl = bpy.context.view_layer
    for o in vl.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    try:
        bpy.ops.uv.pack_islands(rotate=True, margin=0.004)
    except Exception as e:
        print('pack_islands', e)
    bpy.ops.object.mode_set(mode='OBJECT')
    return objs

def _materials(objs):
    ms = []
    for o in objs:
        for s in o.material_slots:
            if s.material and s.material not in ms: ms.append(s.material)
    return ms

def _is_glow(m):
    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.use_nodes else None
    return bool(b and b.inputs['Emission Strength'].default_value > 0.01)

def _smooth(a, sigma=2.2):
    """只在有内容的像素里做高斯模糊（掩码归一化），去掉采样噪点又不把黑底混进来"""
    m = (a.max(2) > 1e-6).astype(np.float32)
    rad = int(sigma * 3); ks = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2); ks /= ks.sum()
    def blur(x):
        for ax in (0, 1):
            acc = np.zeros_like(x)
            for i, w in zip(range(-rad, rad + 1), ks): acc += w * np.roll(x, i, axis=ax)
            x = acc
        return x
    num = blur(a * m[..., None]); den = blur(m)[..., None]
    out = np.where(m[..., None] > 0, num / np.maximum(den, 1e-4), 0)
    return out.astype(np.float32)

def bake(r, samples=96):
    t0 = time.time()
    objs = prep_uv(r)
    name = 'LM_' + r
    img = bpy.data.images.get(name)
    if img: bpy.data.images.remove(img)
    img = bpy.data.images.new(name, LM_SIZE, LM_SIZE, float_buffer=True)
    for m in _materials(objs):
        if not m.use_nodes: m.use_nodes = True
        nt = m.node_tree
        for n in [n for n in nt.nodes if n.name in ('LMBAKE', 'LMUV')]: nt.nodes.remove(n)
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.name = 'LMBAKE'; tex.image = img; tex.location = (-700, -400)
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.name = 'LMUV'; uvn.uv_map = 'LM'; uvn.location = (-900, -400)
        nt.links.new(uvn.outputs['UV'], tex.inputs['Vector'])
        for n in nt.nodes: n.select = False
        tex.select = True; nt.nodes.active = tex
    sc = bpy.context.scene
    try: sc.render.engine = 'CYCLES'
    except TypeError as e: print(e)
    sc.cycles.samples = samples
    try: sc.cycles.device = 'GPU'
    except Exception: pass
    sc.render.bake.margin = 6
    sc.render.bake.use_pass_direct = True; sc.render.bake.use_pass_indirect = True; sc.render.bake.use_pass_color = False
    vl = bpy.context.view_layer
    for o in vl.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=6, use_clear=True)
    # 存成 8 位 jpg
    px = np.empty(LM_SIZE * LM_SIZE * 4, dtype=np.float32); img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    px[:, :3] = _smooth(px[:, :3].reshape(LM_SIZE, LM_SIZE, 3)).reshape(-1, 3)
    px[:, :3] *= SCALE; px[:, 3] = 1
    img.pixels.foreach_set(px.ravel()); img.update()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f'LM_{r}.jpg')
    img.filepath_raw = path; img.file_format = 'JPEG'
    sc.render.image_settings.quality = 88
    img.save()
    img.pack()
    print(f'bake {r}: {len(objs)} objs, {time.time() - t0:.1f}s -> {path}')
    return path

def link_for_export(r, on=True):
    """导出时把 lightmap 接到 Emission Color（glTF 里就是 emissiveTexture），网页再挪到 lightMap"""
    objs = room_meshes(r); saved = []
    for m in _materials(objs):
        if not m.use_nodes or _is_glow(m): continue
        nt = m.node_tree; tex = nt.nodes.get('LMBAKE')
        b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not tex or not b: continue
        ec = b.inputs['Emission Color'] if 'Emission Color' in b.inputs else b.inputs['Emission']
        if on:
            tex.image = bpy.data.images.get('LM_' + r)
            nt.links.new(tex.outputs['Color'], ec); b.inputs['Emission Strength'].default_value = 1.0
        else:
            for l in list(nt.links):
                if l.to_socket == ec: nt.links.remove(l)
            b.inputs['Emission Strength'].default_value = 0.0
