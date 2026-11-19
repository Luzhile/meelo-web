# 咪楼房间建模小工具：在 Blender 里 exec 本文件后用 room('meal') 再调用各函数
# 所有坐标是房间单元局部坐标：x -3.88..3.88，y 前 -2.2 → 后墙 2.08，地面 z=0.12，天花 3.48
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

FLOOR = 0.12; CEIL = 3.48; BACK = 2.08; XL = -3.88; XR = 3.88
WIN_W = 2.3; WIN_B = 1.25; WIN_T = 2.65; WIN_X = 0.0   # 每个房间同一位置的窗洞
S = {'r': None, 'u': None}

HUE = {'studyWork': '#d8ab2f', 'sleep': '#8f84d0', 'meal': '#e2665d', 'home': '#e8873a',
       'commute': '#4f8fd6', 'outdoor': '#5fae3e', 'social': '#e07fa3', 'entertainment': '#2ba3b5'}

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c)

def mix(a, b, t): return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))

def room(r):
    S['r'] = r; S['u'] = bpy.data.objects['Unit_' + r]; DONE.clear()
    return S['u']

def tint(t=0.18, base='#f3efe9'):
    return mix(srgb(base), srgb(HUE[S['r']]), t)

PAL = {
    # 明度要拉开层次：大件浅、台面中、软装偏深，远看才有轮廓
    'white': lambda: srgb('#f0ebe4'), 'cream': lambda: tint(.12, '#e6d9c6'), 'wood': lambda: srgb('#c49a6c'),
    'woodD': lambda: srgb('#8c6448'), 'fabric': lambda: tint(.55, '#c9bcb0'), 'fabric2': lambda: tint(.7, '#9c8c82'),
    'metal': lambda: srgb('#a9a9b0'), 'dark_keep': lambda: srgb('#3a3a42'), 'leaf_keep': lambda: srgb('#6f9a6a'),
    'leaf2_keep': lambda: srgb('#93b884'), 'pot': lambda: srgb('#d8cfc2'), 'clay': lambda: srgb('#c98e6e'),
    'accent': lambda: tint(.85, '#c8a898'), 'paper': lambda: srgb('#faf7f0'),
}

def mat(key, color=None, emit=0.0, ecol=None, rough=0.75, metal=0.0):
    name = f'F_{S["r"]}_{key}'
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    col = color if color is not None else (PAL[key]() if key in PAL else (0.9, 0.9, 0.9))
    if isinstance(col, str): col = srgb(col)
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    ec = ecol if ecol is not None else col
    if isinstance(ec, str): ec = srgb(ec)
    for nm in ('Emission Color', 'Emission'):
        if nm in b.inputs: b.inputs[nm].default_value = (*ec, 1); break
    b.inputs['Emission Strength'].default_value = emit
    m.diffuse_color = (*col, 1)
    return m

def M(key, **kw):
    m = bpy.data.materials.get(f'F_{S["r"]}_{key}')
    if m and not kw and (S['r'], key) in DONE: return m
    DONE.add((S['r'], key))
    return mat(key, **kw)
DONE = set()
THICK = ('leg', 'pole', 'post', 'stick', 'stem', 'stand')

def _finish(name, bm, m, loc, rot, bevel, seg, parent, smooth=False):
    old = bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    bpy.data.collections['U_' + S['r']].objects.link(o)
    par = parent or S['u']
    o.parent = par; o.matrix_parent_inverse = Matrix()
    if parent is not None and not isinstance(loc, Vector) and parent != S['u']:
        # loc 是房间坐标 → 转成父物件局部
        w = S['u'].matrix_world @ Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4()
        o.matrix_basis = parent.matrix_world.inverted() @ w
    else:
        o.location = loc; o.rotation_euler = rot
    me.materials.append(m if not isinstance(m, str) else M(m))
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg; bv.limit_method = 'ANGLE'
    o['meelo_new'] = 1
    return o

def box(name, sx, sy, sz, x, y, z, m='white', bevel=0.015, seg=2, rz=0.0, rx=0.0, ry=0.0, parent=None, origin='bottom'):
    if any(k in name for k in THICK) and sz > .25: sx = max(sx, .045); sy = max(sy, .045)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    oz = sz / 2 if origin == 'bottom' else (0 if origin == 'center' else -sz / 2)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz + oz))
    return _finish(name, bm, m, (x, y, z), (rx, ry, rz), min(bevel, sx / 2.2, sy / 2.2, sz / 2.2) if bevel else 0, seg, parent)

def cyl(name, r, h, x, y, z, m='white', seg=24, r2=None, rx=0.0, ry=0.0, rz=0.0, bevel=0.0, parent=None, origin='bottom'):
    if any(k in name for k in THICK) and h > .25 and r < .03: r = .03; r2 = None if r2 is None else max(r2, .025)
    if 'cord' in name and r < .01: r = .01
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    oz = h / 2 if origin == 'bottom' else 0
    for v in bm.verts: v.co.z += oz
    return _finish(name, bm, m, (x, y, z), (rx, ry, rz), bevel, 2, parent, smooth=seg >= 10)

def sph(name, r, x, y, z, m='white', seg=16, sc=(1, 1, 1), parent=None, rx=0.0, ry=0.0, rz=0.0):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sc[0], v.co.y * sc[1], v.co.z * sc[2]))
    return _finish(name, bm, m, (x, y, z), (rx, ry, rz), 0, 2, parent, smooth=True)

def tor(name, R, r, x, y, z, m='white', seg=24, sseg=8, rx=0.0, ry=0.0, rz=0.0, parent=None, arc=1.0):
    bm = bmesh.new(); rings = []
    n = seg if arc >= 1 else seg + 1
    for i in range(n):
        a = 2 * math.pi * arc * i / seg
        c = Vector((math.cos(a) * R, math.sin(a) * R, 0))
        ring = []
        for j in range(sseg):
            b = 2 * math.pi * j / sseg
            d = Vector((math.cos(a), math.sin(a), 0)) * math.cos(b) * r + Vector((0, 0, math.sin(b) * r))
            ring.append(bm.verts.new(c + d))
        rings.append(ring)
    for i in range(n if arc >= 1 else n - 1):
        a, b2 = rings[i], rings[(i + 1) % n]
        for j in range(sseg):
            bm.faces.new((a[j], a[(j + 1) % sseg], b2[(j + 1) % sseg], b2[j]))
    return _finish(name, bm, m, (x, y, z), (rx, ry, rz), 0, 2, parent, smooth=True)

def poly(name, pts2d, h, x, y, z, m='white', rx=0.0, ry=0.0, rz=0.0, parent=None, bevel=0.0):
    """在 XY 平面画多边形再沿 Z 挤出 h"""
    bm = bmesh.new()
    vs = [bm.verts.new((p[0], p[1], 0)) for p in pts2d]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in ext['geom']:
        if isinstance(v, bmesh.types.BMVert): v.co.z += h
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, m, (x, y, z), (rx, ry, rz), bevel, 2, parent)

def empty_parent(name, x, y, z, parent=None):
    old = bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    o = bpy.data.objects.new(name, None)
    bpy.data.collections['U_' + S['r']].objects.link(o)
    o.parent = parent or S['u']; o.matrix_parent_inverse = Matrix(); o.location = (x, y, z); o['meelo_new'] = 1
    return o

# ---------- 复合家具 ----------
def plant(name, x, y, z=FLOOR, h=0.9, pot_r=0.16, kind='bush', potm='pot'):
    cyl(name + '_pot', pot_r, pot_r * 1.5, x, y, z, potm, seg=20, r2=pot_r * 0.8)
    top = z + pot_r * 1.5
    if kind == 'bush':
        for i, (dx, dy, dz, rr) in enumerate([(0, 0, .55, .30), (-.13, .04, .38, .22), (.14, -.03, .42, .22), (.03, -.1, .72, .18), (-.05, .08, .78, .16)]):
            sph(f'{name}_leaf{i}', rr * h / .9 * pot_r / .16, x + dx * pot_r / .16, y + dy, top + (dz - .25) * h / .9, 'leaf_keep' if i % 2 == 0 else 'leaf2_keep', seg=10)
    elif kind == 'tall':
        cyl(name + '_stem', .015, h, x, y, top, 'woodD', seg=6)
        for i in range(7):
            a = i * 2.4; zz = top + h * (.35 + .09 * i)
            sph(f'{name}_leaf{i}', .13, x + math.cos(a) * .15, y + math.sin(a) * .1, zz, 'leaf_keep' if i % 2 else 'leaf2_keep', seg=8, sc=(1.4, .5, .55), rz=a)
    elif kind == 'snake':
        for i in range(6):
            a = i * 1.05
            box(f'{name}_leaf{i}', .06, .02, h * (.6 + .07 * (i % 3)), x + math.cos(a) * .06, y + math.sin(a) * .05, top, 'leaf_keep', bevel=.008, rz=a, rx=math.cos(a) * .12)
    elif kind == 'hang':
        for i in range(6):
            a = i * 1.05
            sph(f'{name}_leaf{i}', .1, x + math.cos(a) * .12, y + math.sin(a) * .08, top - .02 - .12 * (i % 3), 'leaf_keep' if i % 2 else 'leaf2_keep', seg=8, sc=(1, .8, 1.6))

def books(name, x0, y, z, width, h=0.24, depth=0.18, m_cycle=('white', 'fabric', 'cream', 'fabric2'), lean_last=True):
    x = x0; i = 0
    while x < x0 + width - .03:
        w = .03 + (i * 37 % 5) * .006; hh = h * (.78 + (i * 53 % 7) * .035)
        box(f'{name}{i}', w, depth, hh, x + w / 2, y, z, m_cycle[i % len(m_cycle)], bevel=.004)
        x += w + .004; i += 1

def rug(name, x, y, sx, sy, m='fabric', round_=False):
    if round_:
        return cyl(name, sx / 2, .015, x, y, FLOOR, m, seg=40)
    return box(name, sx, sy, .015, x, y, FLOOR, m, bevel=.01)

def pendant(name, x, y, drop=1.0, r=0.22, m='white', light=True, energy=30, col='#ffd9a8', shape='dome'):
    """吊灯：名字带 _ceil_ 让导出器放进 G_ceiling（房间长高时一起上移）"""
    zc = CEIL - drop
    cyl(f'{S["r"]}_ceil_{name}_cord', .006, drop, x, y, zc, 'dark_keep', seg=6)
    cyl(f'{S["r"]}_ceil_{name}_cap', .05, .03, x, y, CEIL - .03, m, seg=12)
    if shape == 'dome':
        cyl(f'{S["r"]}_ceil_{name}_shade', r, r * .55, x, y, zc - r * .5, m, seg=28, r2=r * .22)
        cyl(f'{S["r"]}_ceil_{name}_bulb', r * .8, .015, x, y, zc - r * .51, M('bulb', color='#fff4e0', emit=6, ecol=col), seg=24)
    else:
        cyl(f'{S["r"]}_ceil_{name}_shade', r * .45, r * .9, x, y, zc - r * .2, m, seg=20, r2=r * .3)
        cyl(f'{S["r"]}_ceil_{name}_bulb', r * .4, .02, x, y, zc - r * .21, M('bulb', color='#fff4e0', emit=6, ecol=col), seg=16)
    if light:
        return add_light(f'{S["r"]}_{name}', 'POINT', (x, y, zc - r * .4), energy, col, radius=.15)

def add_light(name, kind, loc, energy, col, radius=.2, size=(1, 1), angle=1.0, blend=.4, rot=(0, 0, 0)):
    o = bpy.data.objects.get(name)
    if o and o.type != 'LIGHT': bpy.data.objects.remove(o, do_unlink=True); o = None
    if o is None:
        ld = bpy.data.lights.new(name, kind); o = bpy.data.objects.new(name, ld)
        bpy.data.collections['U_' + S['r']].objects.link(o)
    o.data.energy = energy; o.data.color = srgb(col)
    if kind in ('POINT', 'SPOT'): o.data.shadow_soft_size = radius
    if kind == 'SPOT': o.data.spot_size = angle; o.data.spot_blend = blend
    if kind == 'AREA':
        o.data.shape = 'RECTANGLE'; o.data.size = size[0]; o.data.size_y = size[1]
    o.parent = S['u']; o.matrix_parent_inverse = Matrix(); o.location = loc; o.rotation_euler = rot
    o['meelo_new'] = 1
    if 'meelo_old' in o: del o['meelo_old']
    col = bpy.data.collections['U_' + S['r']]
    for c in list(o.users_collection):
        if c != col: c.objects.unlink(o)
    if o.name not in col.objects: col.objects.link(o)
    return o

def frame_pic(name, x, y, z, w, h, m='white', art='fabric', depth=.03, wall='back'):
    if wall == 'back':
        box(name, w, depth, h, x, y - depth / 2, z, m, bevel=.006)
        box(name + '_art', w * .78, .006, h * .78, x, y - depth - .002, z + h * .11, art, bevel=0)
    elif wall == 'right':
        box(name, depth, w, h, x - depth / 2, y, z, m, bevel=.006)
        box(name + '_art', .006, w * .78, h * .78, x - depth - .002, y, z + h * .11, art, bevel=0)
    else:
        box(name, depth, w, h, x + depth / 2, y, z, m, bevel=.006)
        box(name + '_art', .006, w * .78, h * .78, x + depth + .002, y, z + h * .11, art, bevel=0)

def shelf_unit(name, x, y, w, d, h, rows=4, m='white', z=FLOOR, back=True):
    t = .03
    box(name + '_sL', t, d, h, x - w / 2 + t / 2, y, z, m, bevel=.005)
    box(name + '_sR', t, d, h, x + w / 2 - t / 2, y, z, m, bevel=.005)
    if back: box(name + '_bk', w, .015, h, x, y + d / 2 - .008, z, m, bevel=0)
    for i in range(rows + 1):
        zz = z + (h - t) * i / rows
        box(f'{name}_b{i}', w, d, t, x, y, zz, m, bevel=.005)
    return [z + (h - t) * i / rows + t for i in range(rows)]

def cabinet(name, x, y, w, d, h, z=FLOOR, m='white', doors=2, drawers=0, handle='metal', top=None, face='-y', kick=.06):
    """前脸朝 -y（面向镜头）"""
    box(name, w, d, h - kick, x, y, z + kick, m, bevel=.008)
    box(name + '_kick', w - .04, d - .06, kick, x, y + .02, z, 'dark_keep' if kick > .02 else m, bevel=0)
    fy = y - d / 2 - .006
    n = max(1, doors + drawers)
    if drawers and not doors:
        hh = (h - kick - .02) / drawers
        for i in range(drawers):
            zz = z + kick + .01 + i * hh
            box(f'{name}_dr{i}', w - .03, .012, hh - .02, x, fy, zz + .01, m, bevel=.004)
            box(f'{name}_hd{i}', min(.18, w * .4), .02, .015, x, fy - .012, zz + hh - .06, handle, bevel=.004)
    else:
        dw = (w - .02) / max(1, doors)
        for i in range(doors):
            xx = x - w / 2 + .01 + dw * (i + .5)
            box(f'{name}_dr{i}', dw - .015, .012, h - kick - .03, xx, fy, z + kick + .015, m, bevel=.004)
            hx = xx + (dw / 2 - .06) * (1 if i % 2 == 0 else -1) * (-1 if doors > 1 else 1)
            box(f'{name}_hd{i}', .015, .02, .14, hx, fy - .012, z + h - .26, handle, bevel=.004)
    if top:
        box(name + '_top', w + .03, d + .03, .035, x, y - .01, z + h, top, bevel=.006)

def chair(name, x, y, rz=0.0, m='white', seat='fabric', h=.46, z=FLOOR, back=True, w=.44):
    p = empty_parent(name, x, y, z); p.rotation_euler = (0, 0, rz)
    for i, (dx, dy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        o = cyl(f'{name}_leg{i}', .018, h - .04, 0, 0, 0, m, seg=8)
        o.parent = p; o.location = (dx * (w / 2 - .04), dy * (w / 2 - .04), 0)
    o = box(name + '_seat', w, w, .05, 0, 0, 0, seat, bevel=.02); o.parent = p; o.location = (0, 0, h - .05)
    if back:
        o = box(name + '_back', w * .92, .04, .36, 0, 0, 0, m, bevel=.015); o.parent = p; o.location = (0, w / 2 - .03, h)
    return p

def stool(name, x, y, h=.68, m='white', seat='fabric', z=FLOOR):
    cyl(name + '_leg', .025, h - .05, x, y, z + .02, 'metal', seg=10)
    cyl(name + '_base', .16, .02, x, y, z, 'metal', seg=20)
    tor(name + '_ring', .12, .01, x, y, z + h * .35, 'metal', seg=20, sseg=6)
    cyl(name + '_seat', .18, .06, x, y, z + h - .06, seat, seg=24, bevel=.02)

def window(extra=True):
    """把后墙切出同位置的窗洞：后墙拆成「窗以下+两侧」(静态) 和「窗以上」(SHELL，房间长高时拉伸)"""
    r = S['r']; u = S['u']
    bw = bpy.data.objects[r + '_BackWall']
    wm = bw.data.materials[0]
    y0, y1 = 2.08, 2.2
    def setbox(o, x0, x1, z0, z1):
        inv = o.matrix_world.inverted() @ u.matrix_world
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
        for v in bm.verts:
            p = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
            v.co = inv @ p
        bm.to_mesh(o.data); bm.free(); o.data.update()
    setbox(bw, -4.0, 4.0, WIN_T, 3.48)
    xa, xb = WIN_X - WIN_W / 2, WIN_X + WIN_W / 2
    parts = []
    for nm, (x0, x1, z0, z1) in {'lo': (-4.0, 4.0, 0.12, WIN_B), 'L': (-4.0, xa, WIN_B, WIN_T), 'R': (xb, 4.0, WIN_B, WIN_T)}.items():
        o = box(f'{r}_BackWin_{nm}', x1 - x0, y1 - y0, z1 - z0, (x0 + x1) / 2, (y0 + y1) / 2, z0, wm, bevel=0)
        parts.append(o)
    # 窗框（白色）：四边内衬 + 中梃 + 窗台
    fm = 'white'; t = .06; d = y1 - y0 + .04; yc = (y0 + y1) / 2
    box(f'{r}_win_fT', WIN_W + .16, d, t, WIN_X, yc, WIN_T - t + .03, fm, bevel=.008)
    box(f'{r}_win_fB', WIN_W + .16, d, t, WIN_X, yc, WIN_B - .03, fm, bevel=.008)
    box(f'{r}_win_fL', t, d, WIN_T - WIN_B, xa - t / 2 + .03, yc, WIN_B, fm, bevel=.008)
    box(f'{r}_win_fR', t, d, WIN_T - WIN_B, xb + t / 2 - .03, yc, WIN_B, fm, bevel=.008)
    box(f'{r}_win_mull', .035, .05, WIN_T - WIN_B, WIN_X, y1 - .05, WIN_B, fm, bevel=.006)
    box(f'{r}_win_tran', WIN_W, .05, .035, WIN_X, y1 - .05, WIN_B + (WIN_T - WIN_B) * .68, fm, bevel=.006)
    box(f'{r}_win_sill', WIN_W + .34, .2, .045, WIN_X, y0 - .07, WIN_B - .045, fm, bevel=.01)
    return parts

def blinds(name='blind', drop=.55, slats=None):
    """百叶帘，收在窗上部"""
    r = S['r']; n = slats or int(drop / .045)
    box(f'{r}_win_{name}_head', WIN_W - .02, .08, .06, WIN_X, BACK - .07, WIN_T - .08, 'white', bevel=.01)
    for i in range(n):
        box(f'{r}_win_{name}{i}', WIN_W - .06, .07, .008, WIN_X, BACK - .07, WIN_T - .1 - (i + 1) * .045, 'white', bevel=0, rx=.25)
    box(f'{r}_win_{name}_bar', WIN_W - .04, .07, .02, WIN_X, BACK - .07, WIN_T - .12 - (n + 1) * .045, 'white', bevel=.005)

def curtain(name, xc, width, z0, z1, y, m='fabric', waves=5, amp=.035, th=.02):
    """波浪窗帘片：原点在片子中心底部"""
    n = waves * 8; front = []; back = []
    for i in range(n + 1):
        t = i / n; x = -width / 2 + width * t; dy = math.sin(t * waves * 2 * math.pi) * amp
        front.append((x, dy - th / 2)); back.append((x, dy + th / 2))
    pts = front + back[::-1]
    return poly(name, pts, z1 - z0, xc, y, z0, m)

def clear_new(r):
    for o in list(bpy.data.objects):
        if o.get('meelo_new') and o.parent and (o.parent.name == 'Unit_' + r or any(p.name == 'Unit_' + r for p in [o.parent] + list(_ancestors(o)))):
            pass
    u = bpy.data.objects['Unit_' + r]
    for o in list(u.children_recursive):
        if o.get('meelo_new') and not o.name.startswith(r + '_BackWin'):
            bpy.data.objects.remove(o, do_unlink=True)

def _ancestors(o):
    p = o.parent
    while p:
        yield p; p = p.parent
