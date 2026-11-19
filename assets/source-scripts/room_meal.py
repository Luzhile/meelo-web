# 餐厅：后墙一字橱柜（水槽在窗下）、灶台+油烟机、冰箱、中岛+高脚凳、圆餐桌+吊灯
from mathutils import Matrix
room('meal'); clear_new('meal'); window()
r = 'meal'; F = FLOOR; Y = BACK
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (-0.55, -1.05, F - 0.0)
cat.rotation_euler = (0, 0, 0)

# 吸顶灯条（每个房间同款，跟天花一起动）
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fff6ea', emit=4), bevel=.02)

# --- 后墙橱柜 x -3.86..3.0 ---
D = .62; yc = Y - D / 2; H = .88
segs = [(-3.86, -2.95, 'drawers'), (-2.95, -1.75, 'stove'), (-1.75, -1.15, 'doors1'), (-1.15, 1.15, 'sink'), (1.15, 2.1, 'drawers'), (2.1, 3.0, 'doors2')]
for i, (a, b, kind) in enumerate(segs):
    w = b - a; x = (a + b) / 2
    if kind == 'drawers': cabinet(f'{r}_base{i}', x, yc, w, D, H, drawers=3, m='cream')
    elif kind == 'doors1': cabinet(f'{r}_base{i}', x, yc, w, D, H, doors=1, m='cream')
    elif kind == 'stove':
        cabinet(f'{r}_base{i}', x, yc, w, D, H, drawers=2, m='cream')
    else: cabinet(f'{r}_base{i}', x, yc, w, D, H, doors=2, m='cream')
box(f'{r}_counter', 6.88, D + .04, .05, (-3.86 + 3.0) / 2, yc - .02, F + H, 'wood', bevel=.008)
box(f'{r}_backsplash', 6.86, .02, .5, (-3.86 + 3.0) / 2, Y - .01, F + H + .05, 'white', bevel=0)
ct = F + H + .05
# 灶台 + 锅
box(f'{r}_hob', .62, .5, .012, -2.35, yc, ct, 'dark_keep', bevel=.004)
for i, (dx, dy) in enumerate([(-.15, -.1), (.15, -.1), (-.15, .12), (.15, .12)]):
    tor(f'{r}_burner{i}', .07, .008, -2.35 + dx, yc + dy, ct + .014, 'metal', seg=16, sseg=5)
cyl(f'{r}_pot', .15, .17, -2.5, yc - .1, ct + .015, 'white', seg=28)
tor(f'{r}_pot_rim', .15, .012, -2.5, yc - .1, ct + .185, 'white', seg=28, sseg=6)
box(f'{r}_pot_hL', .06, .03, .025, -2.68, yc - .1, ct + .14, 'woodD', bevel=.008)
box(f'{r}_pot_hR', .06, .03, .025, -2.32, yc - .1, ct + .14, 'woodD', bevel=.008)
lid = cyl(f'{r}_PotLid', .155, .035, -2.5, yc - .1, ct + .18, 'white', seg=28, r2=.06)
sph(f'{r}_PotLid_knob', .025, -2.5, yc - .1, ct + .225, 'woodD', seg=10, parent=lid)
cyl(f'{r}_kettle', .09, .16, -2.16, yc + .12, ct + .015, 'white', seg=20, r2=.06)
box(f'{r}_kettle_spout', .1, .025, .025, -2.06, yc + .12, ct + .11, 'white', bevel=.008, ry=-.6)
# 油烟机
box(f'{r}_hood', .82, .5, .14, -2.35, Y - .25, 1.95, 'white', bevel=.02)
cyl(f'{r}_hood_cone', .3, .22, -2.35, Y - .22, 2.09, 'white', seg=4, r2=.15, rz=math.pi / 4)
box(f'{r}_hood_chim', .3, .3, 1.2, -2.35, Y - .16, 2.3, 'white', bevel=.01)
box(f'{r}_hood_lamp', .5, .05, .01, -2.35, Y - .32, 1.945, M('glow', color='#fff2dc', emit=3), bevel=0)
add_light(f'{r}_HoodLight', 'POINT', (-2.35, Y - .32, 1.85), 22, '#ffd8a8', radius=.2)
# 吊柜（左）+ 挂杆（右）
cabinet(f'{r}_upper0', -3.42, Y - .18, .86, .34, .78, z=1.62, doors=2, m='cream', kick=0)
box(f'{r}_rail', .55, .02, .02, -1.47, Y - .06, 1.72, 'metal', bevel=.005, rx=0)
for i, (dx, kind) in enumerate([(-.18, 'pan'), (0, 'ladle'), (.18, 'pan2')]):
    x = -1.47 + dx
    cyl(f'{r}_hook{i}', .004, .07, x, Y - .07, 1.65, 'metal', seg=6)
    if kind == 'ladle':
        box(f'{r}_ladle', .015, .01, .3, x, Y - .08, 1.36, 'woodD', bevel=.004)
        sph(f'{r}_ladle_cup', .045, x, Y - .09, 1.36, 'white', seg=10, sc=(1, 1, .6))
    else:
        rr = .11 if kind == 'pan' else .085
        cyl(f'{r}_{kind}', rr, .02, x, Y - .08, 1.62 - .1 - rr, 'woodD' if kind == 'pan' else 'white', seg=20, rx=math.pi / 2, origin='center')
        box(f'{r}_{kind}_h', .022, .012, .1, x, Y - .08, 1.55 - .1, 'woodD', bevel=.005)
# 水槽 + 龙头（窗下）
box(f'{r}_sink', .7, .42, .012, 0, yc - .02, ct - .002, 'metal', bevel=0)
box(f'{r}_sink_in', .62, .34, .013, 0, yc - .02, ct, M('sinkin', color='#9a9aa2', rough=.4), bevel=0)
tap = cyl(f'{r}_tap', .025, .26, 0, Y - .12, ct, 'metal', seg=12)
box(f'{r}_tap_arm', .03, .2, .03, 0, Y - .2, ct + .24, 'metal', bevel=.01, parent=tap)
box(f'{r}_tap_lever', .1, .02, .02, .06, Y - .12, ct + .18, 'metal', bevel=.006, parent=tap)
sp = cyl(f'{r}_tap_spout', .014, .05, 0, Y - .29, ct + .21, 'metal', seg=10)
# 窗台小物：小盆栽 + 皂液
plant(f'{r}_herb0', -.75, Y - .08, z=WIN_B, h=.32, pot_r=.07)
plant(f'{r}_herb1', .78, Y - .08, z=WIN_B, h=.28, pot_r=.06, kind='snake')
cyl(f'{r}_soap', .035, .14, .45, Y - .2, ct, 'white', seg=12)
# 右侧开放搁板 + 罐子盘子
for k, zz in enumerate([1.62, 2.02]):
    box(f'{r}_shelf{k}', 1.7, .26, .035, 2.0, Y - .13, zz, 'wood', bevel=.006)
    for j in range(2): box(f'{r}_shelf{k}_br{j}', .025, .2, .1, 1.3 + j * 1.4, Y - .1, zz - .1, 'white', bevel=.004)
for j, (x, rr, hh) in enumerate([(1.3, .07, .2), (1.48, .06, .16), (1.64, .07, .22)]):
    cyl(f'{r}_jar{j}', rr, hh, x, Y - .14, 1.655, 'white', seg=16)
    cyl(f'{r}_jar{j}_lid', rr * .85, .03, x, Y - .14, 1.655 + hh, 'woodD', seg=16)
for j in range(4):
    cyl(f'{r}_plate{j}', .11, .015, 2.1 + j * .055, Y - .14, 1.66 + .11, 'white', seg=20, ry=math.pi / 2 - .15, origin='center')
cyl(f'{r}_bowlstack', .1, .12, 2.55, Y - .13, 1.655, 'fabric', seg=18, r2=.12)
plant(f'{r}_shelfplant', 2.2, Y - .13, z=2.055, h=.3, pot_r=.06, kind='hang')
cyl(f'{r}_cup0', .04, .09, 1.9, Y - .14, 2.055, 'fabric', seg=12)
cyl(f'{r}_cup1', .04, .09, 2.65, Y - .14, 2.055, 'white', seg=12)
# 砧板 + 刀架
box(f'{r}_board', .4, .26, .025, -1.35, yc - .05, ct, 'woodD', bevel=.008)
box(f'{r}_bread', .2, .1, .08, -1.35, yc - .05, ct + .025, 'clay', bevel=.03)
# 冰箱（门绕左边铰链转）
fx0, fx1 = 3.05, 3.86; fw = fx1 - fx0; fd = .7; fy = Y - fd / 2
box(f'{r}_fridge', fw, fd, 1.98, (fx0 + fx1) / 2, fy, F, 'white', bevel=.03)
door = box(f'{r}_FridgeDoor', fw - .02, .05, 1.2, 0, 0, 0, 'white', bevel=.02)
door.data.transform(Matrix.Translation((fw / 2 - .01, 0, 0))); door.location = (fx0 + .01, fy - fd / 2 - .025, F + .74)
box(f'{r}_FridgeDoor_h', .025, .04, .5, fx0 + .1, fy - fd / 2 - .07, F + 1.1, 'metal', bevel=.008, parent=door)
box(f'{r}_freezer', fw - .02, .05, .7, (fx0 + fx1) / 2, fy - fd / 2 - .025, F + .02, 'white', bevel=.02)
box(f'{r}_freezer_h', .3, .04, .025, fx0 + .3, fy - fd / 2 - .07, F + .62, 'metal', bevel=.008)
for j, (dx, c) in enumerate([(.2, 'fabric'), (.45, 'accent'), (.62, 'white')]):
    box(f'{r}_magnet{j}', .08, .01, .08, fx0 + dx, fy - fd / 2 - .056, F + 1.6 - j * .12, c, bevel=.004, parent=door)
cyl(f'{r}_fridge_basket', .14, .12, fx0 + .35, fy + .05, F + 1.98, 'wood', seg=16)
# --- 中岛 + 高脚凳 ---
ix, iy, iw, idp = 1.35, 0.25, 1.9, .7
box(f'{r}_island', iw, idp, .86, ix, iy, F, 'cream', bevel=.015)
box(f'{r}_island_top', iw + .14, idp + .12, .05, ix, iy - .04, F + .86, 'wood', bevel=.01)
for j in range(3): box(f'{r}_island_p{j}', .02, .006, .7, ix - .6 + j * .6, iy - idp / 2 - .003, F + .08, 'white', bevel=0)
it = F + .91
cyl(f'{r}_fruitbowl', .17, .07, ix - .4, iy, it, 'white', seg=24, r2=.2)
for j, (dx, dy, c) in enumerate([(-.05, 0, 'clay'), (.06, .03, 'accent'), (0, .07, 'clay'), (.04, -.06, 'leaf2_keep')]):
    sph(f'{r}_fruit{j}', .055, ix - .4 + dx, iy + dy, it + .09, c, seg=12)
cyl(f'{r}_vase', .05, .2, ix + .5, iy + .05, it, 'white', seg=16, r2=.035)
for j in range(3): sph(f'{r}_vflower{j}', .035, ix + .48 + j * .03, iy + .05, it + .24 + j * .03, 'accent', seg=8)
box(f'{r}_tray', .3, .2, .02, ix + .1, iy - .05, it, 'woodD', bevel=.006)
cyl(f'{r}_teacup', .04, .07, ix + .05, iy - .05, it + .02, 'white', seg=12)
for j in range(2): stool(f'{r}_stool{j}', ix - .45 + j * .9, iy - .7, h=.66)
# --- 圆餐桌 + 椅子 ---
tx, ty = -2.15, 0.05
cyl(f'{r}_table_top', .58, .04, tx, ty, F + .72, 'wood', seg=40, bevel=.01)
cyl(f'{r}_table_leg', .05, .68, tx, ty, F + .04, 'white', seg=16)
cyl(f'{r}_table_foot', .3, .04, tx, ty, F, 'white', seg=32, r2=.25)
for j, a in enumerate([math.pi, math.pi / 2 + .2, -.15]):
    chair(f'{r}_chair{j}', tx + math.cos(a) * .72, ty + math.sin(a) * .72, rz=a - math.pi / 2, m='white', seat='fabric')
rug(f'{r}_rug', tx, ty, 1.9, 1.9, 'fabric', round_=True)
tt = F + .76
cyl(f'{r}_tplate0', .12, .015, tx - .2, ty - .1, tt, 'white', seg=20)
cyl(f'{r}_tplate1', .12, .015, tx + .22, ty + .05, tt, 'white', seg=20)
cyl(f'{r}_tbowl', .08, .06, tx - .2, ty - .1, tt + .015, 'fabric', seg=16, r2=.1)
cyl(f'{r}_tglass', .035, .11, tx + .05, ty + .22, tt, 'white', seg=12)
cyl(f'{r}_tcandle', .03, .12, tx, ty + .02, tt, 'cream', seg=12)
pendant('Pend0', tx, ty, drop=1.15, r=.26, energy=40, col='#ffcf8f')
pendant('Pend1', ix - .5, iy, drop=1.25, r=.15, energy=26, col='#ffd29a', shape='cone')
pendant('Pend2', ix + .5, iy, drop=1.25, r=.15, energy=26, col='#ffd29a', shape='cone')
# 角落：大盆栽 + 挂画 + 墙钟
plant(f'{r}_bigplant', 3.45, -1.55, h=1.3, pot_r=.22, kind='tall')
frame_pic(f'{r}_pic0', -3.86, 0.4, 1.45, .55, .7, wall='left')
frame_pic(f'{r}_pic1', -3.86, 1.05, 1.62, .4, .5, art='accent', wall='left')
box(f'{r}_mat', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
