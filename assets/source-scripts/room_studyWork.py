# 学习/工作：大书桌在窗前，猫坐桌后面朝镜头；左书架+画架，右软木板+矮柜+落地灯
from mathutils import Matrix
room('studyWork'); clear_new('studyWork'); window()
r = 'studyWork'; F = FLOOR; Y = BACK
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (0.0, 1.45, F); cat.rotation_euler = (0, 0, 0)
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fff6ea', emit=4), bevel=.02)
blinds('blind', drop=.42)

# --- 大书桌 ---
dx, dy, dw, dd, dh = 0.0, 0.62, 2.5, .86, .76
box(f'{r}_desk_top', dw, dd, .05, dx, dy, F + dh - .05, 'wood', bevel=.012)
for i, sx in enumerate([-1, 1]):
    box(f'{r}_desk_leg{i}', .06, dd - .1, dh - .05, dx + sx * (dw / 2 - .08), dy, F, 'white', bevel=.01)
box(f'{r}_desk_drw', .5, dd - .12, .5, dx + dw / 2 - .4, dy, F + dh - .55, 'white', bevel=.01)
for j in range(2): box(f'{r}_desk_drw_f{j}', .46, .012, .2, dx + dw / 2 - .4, dy - dd / 2 + .055, F + dh - .52 + j * .24, 'white', bevel=.004)
box(f'{r}_desk_modesty', dw - .2, .02, .35, dx, dy - dd / 2 + .08, F + dh - .4, 'white', bevel=.005)
T = F + dh
# 笔记本（屏幕朝猫，背面猫头 logo 朝镜头）
kb = box(f'{r}_keyboard', .5, .34, .022, -.15, dy + .02, T, 'metal', bevel=.008)
box(f'{r}_keyboard_keys', .42, .14, .004, -.15, dy + .08, T + .022, 'dark_keep', bevel=0, parent=kb)
lid = box(f'{r}_laptop_lid', .5, .018, .34, -.15, dy - .15, T + .01, 'metal', bevel=.008, rx=-.28)
sph(f'{r}_laptop_logo', .045, -.15, dy - .2, T + .2, 'white', seg=12, sc=(1, .2, .9))
for s in (-1, 1): cyl(f'{r}_laptop_logoear{s}', .02, .03, -.15 + s * .03, dy - .21, T + .24, 'white', seg=3, r2=.002)
# 外接显示器（斜放，屏幕能被镜头看到）
mx, my = .78, dy + .12
cyl(f'{r}_mon_base', .11, .015, mx, my, T, 'white', seg=20)
box(f'{r}_mon_neck', .04, .03, .3, mx, my + .02, T + .01, 'white', bevel=.008)
mon = box(f'{r}_monitor', .62, .04, .38, mx, my, T + .22, 'white', bevel=.012, rz=math.radians(-28))
scr = box(f'{r}_screen', .56, .006, .32, mx - .01, my - .03, T + .25, M('Screen', color='#cfe6ff', emit=1.4, ecol='#bcdcff'), bevel=0, rz=math.radians(-28))
cur = box(f'{r}_anim_Cursor', .012, .004, .04, mx - .17, my - .1, T + .48, M('cursor', color='#ffffff', emit=3), bevel=0, rz=math.radians(-28))
# 台灯（左）
lx, ly = -.95, dy + .2
cyl(f'{r}_lamp_base', .09, .03, lx, ly, T, 'white', seg=20)
box(f'{r}_lamp_arm1', .025, .025, .42, lx, ly, T + .02, 'white', bevel=.008, rx=.25)
box(f'{r}_lamp_arm2', .025, .025, .32, lx, ly - .1, T + .42, 'white', bevel=.008, rx=-1.15)
sh = cyl(f'{r}_DeskLampShade', .1, .14, lx, ly - .38, T + .46, 'white', seg=20, r2=.04, rx=0.35)
cyl(f'{r}_DeskLampBulb', .075, .01, lx, ly - .37, T + .455, M('bulb', color='#fff4e0', emit=6, ecol='#ffd9a0'), seg=16, rx=.35, parent=sh)
add_light(f'{r}_DeskLamp.001', 'POINT', (lx, ly - .4, T + .38), 30, '#ffd9a0', radius=.1)
# 桌面小物
mug = cyl(f'{r}_mug', .045, .1, .35, dy - .12, T, 'fabric', seg=16)
tor(f'{r}_mug_h', .032, .009, .4, dy - .12, T + .05, 'fabric', seg=12, sseg=5, rx=math.pi / 2, parent=mug)
for j, (h, c) in enumerate([(.05, 'white'), (.045, 'fabric'), (.04, 'cream')]):
    box(f'{r}_deskbook{j}', .3 - j * .02, .22, h, -.75, dy - .15, T + sum([.05, .045, .04][:j]), c, bevel=.006, rz=.1 * j)
cyl(f'{r}_pencup', .04, .1, .6, dy - .2, T, 'white', seg=14)
for j in range(3): cyl(f'{r}_pencil{j}', .006, .16, .6 + (j - 1) * .015, dy - .2, T + .02, ['woodD', 'accent', 'dark_keep'][j], seg=6, rx=(j - 1) * .15)
plant(f'{r}_deskplant', -.45, dy + .3, z=T, h=.28, pot_r=.06)
box(f'{r}_notebook', .22, .28, .015, .2, dy - .05, T, 'paper', bevel=.004, rz=-.2)
# --- 墙钟（窗上方） ---
cz = 3.05
wc = cyl(f'{r}_wclock', .22, .04, 0, Y - .02, cz, 'white', seg=32, rx=math.pi / 2, origin='center')
cyl(f'{r}_wclock_face', .19, .005, 0, Y - .045, cz, 'paper', seg=32, rx=math.pi / 2, origin='center', parent=wc)
for k in range(12):
    a = k / 12 * 2 * math.pi
    box(f'{r}_wclock_tick{k}', .012, .006, .03, math.sin(a) * .16, Y - .05, cz + math.cos(a) * .16, 'dark_keep', bevel=0, origin='center', ry=a, parent=wc)
hh = box(f'{r}_wclock_h', .022, .008, .1, 0, Y - .06, cz, 'dark_keep', bevel=0)
mm = box(f'{r}_wclock_m', .016, .008, .15, 0, Y - .066, cz, 'dark_keep', bevel=0)
# --- 左：高书架 + 矮抽屉柜 + 画架 ---
zs = shelf_unit(f'{r}_bookshelf', -3.3, Y - .2, 1.1, .38, 2.3, rows=5)
for k, z in enumerate(zs):
    if k == 2:
        sph(f'{r}_globe', .11, -3.55, Y - .2, z + .13, 'fabric', seg=16)
        cyl(f'{r}_globe_base', .06, .02, -3.55, Y - .2, z, 'woodD', seg=12)
        books(f'{r}_bk{k}_', -3.35, Y - .22, z, .45, h=.26)
    elif k == 4:
        plant(f'{r}_shelfplant', -3.3, Y - .2, z=z, h=.3, pot_r=.07, kind='hang')
    else:
        books(f'{r}_bk{k}_', -3.82, Y - .22, z, .9 - (k % 2) * .25, h=.28)
box(f'{r}_boxes', .3, .3, .2, -3.5, Y - .2, zs[0] + .29 if False else zs[0], 'cream', bevel=.01)
cabinet(f'{r}_drawers', -2.2, Y - .26, .7, .5, .72, drawers=4, m='white')
box(f'{r}_printer', .5, .36, .16, -2.2, Y - .28, F + .74, 'white', bevel=.02)
box(f'{r}_printer_paper', .28, .2, .005, -2.2, Y - .36, F + .9, 'paper', bevel=0)
# 画架（左前）
ex, ey = -2.7, -0.75
pe = empty_parent(f'{r}_easel', ex, ey, F); pe.rotation_euler = (0, 0, .35)
for j, (lx2, ry2) in enumerate([(-.28, .14), (.28, -.14)]):
    o = box(f'{r}_easel_leg{j}', .035, .035, 1.55, 0, 0, 0, 'wood', bevel=.008); o.parent = pe; o.location = (lx2, 0, 0); o.rotation_euler = (-.12, ry2, 0)
o = box(f'{r}_easel_back', .035, .035, 1.45, 0, 0, 0, 'wood', bevel=.008); o.parent = pe; o.location = (0, .45, 0); o.rotation_euler = (.3, 0, 0)
o = box(f'{r}_easel_bar', .62, .05, .035, 0, 0, 0, 'wood', bevel=.008); o.parent = pe; o.location = (0, -.08, .62)
o = box(f'{r}_canvas', .62, .03, .75, 0, 0, 0, 'paper', bevel=.006); o.parent = pe; o.location = (0, -.1, .65); o.rotation_euler = (-.12, 0, 0)
for j, (cx, cz2, rr, c) in enumerate([(-.1, .95, .12, 'fabric2'), (.12, .85, .09, 'accent'), (0, 1.12, .07, 'leaf2_keep')]):
    o = cyl(f'{r}_paint{j}', rr, .006, 0, 0, 0, c, seg=16, rx=math.pi / 2, origin='center'); o.parent = pe; o.location = (cx, -.13, cz2 - .01); o.rotation_euler = (math.pi / 2 - .12, 0, 0)
# 小推车（画具）
for k, z in enumerate([.12, .42, .72]):
    box(f'{r}_cart_t{k}', .44, .34, .03, -1.75, -1.3, F + z, 'white', bevel=.01)
for j, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
    cyl(f'{r}_cart_post{j}', .012, .72, -1.75 + sx * .2, -1.3 + sy * .15, F + .06, 'metal', seg=8)
    sph(f'{r}_cart_wheel{j}', .03, -1.75 + sx * .2, -1.3 + sy * .15, F + .03, 'dark_keep', seg=8)
for j in range(4): cyl(f'{r}_cart_jar{j}', .04, .12, -1.88 + j * .09, -1.3, F + .75, ['fabric', 'white', 'accent', 'cream'][j], seg=12)
for j in range(3): box(f'{r}_cart_pad{j}', .3, .22, .02, -1.75, -1.3, F + .45 + j * .022, ['paper', 'fabric2', 'cream'][j], bevel=.004, rz=j * .15)
# --- 右：软木板 + 矮柜 + 梯形书架 + 落地灯 ---
box(f'{r}_cork', 1.25, .025, .85, 2.2, Y - .013, 1.35, 'clay', bevel=.008)
box(f'{r}_cork_frame', 1.31, .02, .91, 2.2, Y - .005, 1.32, 'white', bevel=.006)
for j, (px, pz, c, rz2) in enumerate([(1.85, 1.9, 'paper', .08), (2.15, 1.75, 'fabric', -.05), (2.5, 1.95, 'paper', .04), (2.0, 1.48, 'accent', -.1), (2.5, 1.5, 'paper', .06)]):
    box(f'{r}_note{j}', .22, .006, .2, px, Y - .03, pz, c, bevel=0, ry=rz2)
    sph(f'{r}_pin{j}', .012, px, Y - .04, pz + .17, 'accent', seg=6)
cabinet(f'{r}_lowcab', 2.2, Y - .22, 1.4, .44, .78, doors=2, m='white', top='wood')
plant(f'{r}_cabplant', 1.75, Y - .25, z=F + .815, h=.38, pot_r=.08, kind='snake')
box(f'{r}_radio', .3, .14, .18, 2.45, Y - .25, F + .815, 'cream', bevel=.03)
cyl(f'{r}_radio_dial', .04, .01, 2.52, Y - .32, F + .9, 'white', seg=12, rx=math.pi / 2, origin='center')
for j in range(3): box(f'{r}_binder{j}', .07, .26, .3, 2.75 + j * .08, Y - .22, F + .815, ['fabric', 'white', 'fabric2'][j], bevel=.006)
zs2 = shelf_unit(f'{r}_rshelf', XR - .2, 0.35, .8, .36, 1.6, rows=3, back=False) if False else None
for k in range(4):
    zz = F + .3 + k * .42
    box(f'{r}_wshelf{k}', .3, .9, .03, XR - .15, .4, zz, 'white', bevel=.006)
box(f'{r}_wshelf_side', .03, .03, 1.7, XR - .02, .4, F + .1, 'white', bevel=.006)
books(f'{r}_rb0_', 0, 0, 0, 0) if False else None
for k in range(4):
    zz = F + .33 + k * .42
    for j in range(5 - k % 2):
        box(f'{r}_rbook{k}_{j}', .2, .035, .24 - (j % 3) * .02, XR - .16, .05 + j * .045, zz, ['white', 'fabric', 'cream', 'fabric2'][(j + k) % 4], bevel=.004)
    if k % 2 == 0: cyl(f'{r}_rvase{k}', .05, .14, XR - .16, .7, zz, 'white', seg=14)
    else: box(f'{r}_rbox{k}', .18, .2, .14, XR - .16, .7, zz, 'cream', bevel=.01)
# 落地灯
fx, fy = 3.15, -1.1
cyl(f'{r}_flamp_base', .15, .03, fx, fy, F, 'white', seg=20)
cyl(f'{r}_flamp_pole', .015, 1.45, fx, fy, F + .03, 'white', seg=8)
cyl(f'{r}_flamp_shade', .2, .26, fx, fy, F + 1.42, 'paper', seg=24, r2=.15)
add_light(f'{r}_FloorLamp', 'POINT', (fx, fy, F + 1.5), 24, '#ffd4a0', radius=.2)
plant(f'{r}_bigplant', 2.55, -1.6, h=1.3, pot_r=.17, kind='tall')
rug(f'{r}_rug', 0, 0.5, 3.4, 2.1, 'fabric')
box(f'{r}_pouf', .5, .5, .34, 1.15, -.45, F + .015, 'fabric2', bevel=.12, seg=4)
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
