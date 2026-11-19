# 户外：室内露营角——草地毯、苹果树（苹果可摘）、帐篷、营灯、折叠椅、背包、蝴蝶
from mathutils import Matrix
room('outdoor'); clear_new('outdoor'); window()
r = 'outdoor'; F = FLOOR; Y = BACK
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fffbea', emit=4), bevel=.02)
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (.1, -.85, F); cat.rotation_euler = (0, 0, 0)
# 草地毯
box(f'{r}_grass', 6.4, 3.4, .03, .2, .3, F, 'leaf2_keep', bevel=.02)
for j in range(14):
    a = j * 2.39; rr = 1.2 + (j % 5) * .45
    x = .2 + math.cos(a) * rr * 1.4; y = .3 + math.sin(a) * rr * .55
    for k in range(3): box(f'{r}_tuft{j}_{k}', .02, .01, .08 + k * .02, x + (k - 1) * .025, y, F + .03, 'leaf_keep', bevel=0, ry=(k - 1) * .35)
# --- 苹果树（右后，大花盆）---
tx, ty = 2.6, 1.3
box(f'{r}_planter', .9, .9, .5, tx, ty, F, 'wood', bevel=.03)
box(f'{r}_planter_soil', .82, .82, .02, tx, ty, F + .48, 'woodD', bevel=0)
cyl(f'{r}_trunk', .08, 1.3, tx, ty, F + .5, 'woodD', seg=10, r2=.05)
cyl(f'{r}_branch0', .035, .55, tx, ty, F + 1.3, 'woodD', seg=8, ry=.7)
cyl(f'{r}_branch1', .035, .5, tx, ty, F + 1.4, 'woodD', seg=8, ry=-.6)
crowns = [(0, 0, 2.15, .55), (-.45, -.05, 1.95, .4), (.45, .05, 1.95, .42), (-.2, -.15, 2.45, .35), (.25, .1, 2.4, .36)]
for j, (dx, dy, z, rr) in enumerate(crowns):
    sph(f'{r}_canopy{j}', rr, tx + dx, ty + dy, z, 'leaf_keep' if j % 2 == 0 else 'leaf2_keep', seg=14)
for j, (dx, dz) in enumerate([(-.4, 1.75), (.3, 1.82), (-.05, 1.72), (.55, 2.05), (-.6, 2.0)]):
    sph(f'{r}_apple{j}', .065, tx + dx, ty - .45 + (j % 2) * .05, dz, M('apple_keep', color='#d9837a'), seg=12)
# 窗台和窗下：小盆栽一排
for j, (x, k) in enumerate([(-.8, 'bush'), (-.25, 'snake'), (.35, 'bush'), (.85, 'snake')]):
    plant(f'{r}_sill{j}', x, Y - .08, z=WIN_B, h=.3, pot_r=.065, kind=k)
# --- 帐篷（左）---
px, py = -2.35, .55
p = empty_parent(f'{r}_tent', px, py, F); p.rotation_euler = (0, 0, .25)
for j, s in enumerate((-1, 1)):
    o = box(f'{r}_tent_side{j}', 1.05, 1.5, .03, 0, 0, 0, 'fabric', bevel=.01, origin='center'); o.parent = p
    o.location = (s * .37, 0, .52); o.rotation_euler = (0, s * .95, 0)
o = poly(f'{r}_tent_back', [(-.8, 0), (.8, 0), (0, 1.12)], .02, 0, 0, 0, 'fabric2', rx=math.pi / 2); o.parent = p; o.location = (0, .76, 0); o.rotation_euler = (math.pi / 2, 0, 0)
for j, s in enumerate((-1, 1)):
    o = poly(f'{r}_tent_flap{j}', [(0, 0), (s * .5, 0), (0, 1.0)], .015, 0, 0, 0, 'fabric2'); o.parent = p; o.location = (s * .25, -.74, 0); o.rotation_euler = (math.pi / 2, 0, s * .5)
o = cyl(f'{r}_tent_pole', .015, 1.25, 0, 0, 0, 'woodD', seg=6); o.parent = p; o.location = (0, -.76, 0)
box(f'{r}_tent_mat', 1.4, 1.6, .04, px, py, F + .03, 'cream', bevel=.015, rz=.25)
cyl(f'{r}_tent_flag', .006, .25, px - .18, py - .72, F + 1.2, 'woodD', seg=5)
poly(f'{r}_tent_flagc', [(0, 0), (.14, -.04), (0, -.09)], .005, px - .18, py - .72, F + 1.45, 'accent', rx=math.pi / 2)
# 营灯（帐篷前）
lx, ly = -1.35, -.5
cyl(f'{r}_lantern_base', .08, .04, lx, ly, F + .03, 'dark_keep', seg=14)
cyl(f'{r}_lantern_glass', .06, .16, lx, ly, F + .07, M('lanternglow', color='#fff0c8', emit=3, ecol='#ffc56e'), seg=14)
cyl(f'{r}_lantern_top', .07, .05, lx, ly, F + .23, 'dark_keep', seg=14, r2=.03)
tor(f'{r}_lantern_h', .05, .008, lx, ly, F + .3, 'dark_keep', seg=12, sseg=5, rx=math.pi / 2, arc=.5)
add_light(f'{r}_Lantern', 'POINT', (lx, ly, F + .2), 25, '#ffc56e', radius=.15)
# 折叠椅 + 背包 + 靴子
cx, cy = 1.25, .05
p2 = empty_parent(f'{r}_campchair', cx, cy, F); p2.rotation_euler = (0, 0, -.5)
for j, s in enumerate((-1, 1)):
    o = box(f'{r}_campchair_x{j}a', .025, .55, .025, 0, 0, 0, 'metal', bevel=0, origin='center'); o.parent = p2; o.location = (s * .25, 0, .2); o.rotation_euler = (.7, 0, 0)
    o = box(f'{r}_campchair_x{j}b', .025, .55, .025, 0, 0, 0, 'metal', bevel=0, origin='center'); o.parent = p2; o.location = (s * .25, 0, .2); o.rotation_euler = (-.7, 0, 0)
o = box(f'{r}_campchair_seat', .5, .42, .03, 0, 0, 0, 'fabric2', bevel=.01); o.parent = p2; o.location = (0, 0, .38)
o = box(f'{r}_campchair_back', .5, .03, .42, 0, 0, 0, 'fabric2', bevel=.01); o.parent = p2; o.location = (0, .22, .4); o.rotation_euler = (-.2, 0, 0)
box(f'{r}_backpack', .36, .22, .48, -.55, .95, F + .03, 'fabric2', bevel=.08, seg=3, rz=-.2)
box(f'{r}_backpack_pocket', .26, .06, .2, -.57, .82, F + .1, 'fabric', bevel=.04, rz=-.2)
cyl(f'{r}_bedroll', .1, .4, -.55, .95, F + .51, 'cream', seg=14, ry=math.pi / 2, origin='center', rz=-.2)
for j, s in enumerate((-1, 1)):
    box(f'{r}_boot{j}', .11, .24, .08, 2.0 + s * .09, -1.1, F + .03, 'woodD', bevel=.03, rz=.1 * s)
    box(f'{r}_boot{j}_up', .11, .1, .16, 2.0 + s * .09, -1.03, F + .1, 'woodD', bevel=.03, rz=.1 * s)
# 野餐垫 + 篮子 + 保温壶
box(f'{r}_picnic', 1.1, .8, .012, .9, -.95, F + .03, 'fabric', bevel=.005, rz=.1)
for j in range(4): box(f'{r}_picnic_stripe{j}', 1.1, .06, .004, .9, -1.25 + j * .2, F + .043, 'white', bevel=0, rz=.1)
box(f'{r}_hamper', .38, .26, .22, .7, -.85, F + .045, 'wood', bevel=.02)
tor(f'{r}_hamper_h', .14, .012, .7, -.85, F + .27, 'woodD', seg=14, sseg=5, rx=math.pi / 2, arc=.5)
cyl(f'{r}_flask', .05, .24, 1.15, -.95, F + .045, 'accent', seg=12)
# 墙上：登山绳+地图
frame_pic(f'{r}_map', XR, -.3, 1.25, 1.0, .7, art='cream', wall='right')
tor(f'{r}_rope', .16, .025, XR - .05, .8, 1.6, 'clay', seg=20, sseg=6, ry=math.pi / 2)
frame_pic(f'{r}_pic0', -1.95, Y, 1.35, .5, .65, art='leaf2_keep', wall='back')
# 蝴蝶（身体 + 两片翅膀，各自独立好扇动）
for j, (bx, by, bz) in enumerate([(1.9, .4, 2.0), (-1.0, .1, 2.25), (.9, .9, 1.7)]):
    sph(f'{r}_bf{j}', .02, bx, by, bz, 'dark_keep', seg=8, sc=(1, 1, 2.5))
    for nm, s in (('L', -1), ('R', 1)):
        w = poly(f'{r}_bf{j}{nm}', [(0, 0), (s * .11, .04), (s * .1, -.06), (s * .04, -.08)], .004, bx, by, bz, M('wing', color='#fff1c8') if j != 1 else 'accent', rx=math.pi / 2 - .3)
add_light(f'{r}_SunBeam', 'SPOT', (.4, Y + 1.2, 3.1), 380, '#ffe2a8', angle=.9, blend=.45, rot=(math.radians(-50), math.radians(8), 0))
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
