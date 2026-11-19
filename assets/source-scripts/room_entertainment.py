# 娱乐：右后电视柜+电视+落地音箱，左侧沙发（侧放），中间茶几+手柄，懒人沙发，街机，霓虹，星球灯
from mathutils import Matrix
room('entertainment'); clear_new('entertainment'); window()
r = 'entertainment'; F = FLOOR; Y = BACK
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fff6ea', emit=4), bevel=.02)
blinds('blind', drop=.3)
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (1.55, -.75, F + .3); cat.rotation_euler = (0, 0, 0)
# --- 电视柜 + 电视 ---
tx = 2.5
cabinet(f'{r}_console', tx, Y - .25, 2.0, .46, .48, doors=0, drawers=2, m='white', top='wood') if False else None
box(f'{r}_console', 2.0, .46, .42, tx, Y - .25, F + .08, 'white', bevel=.015)
for j in range(3): box(f'{r}_console_dr{j}', .62, .012, .34, tx - .66 + j * .66, Y - .485, F + .12, 'white', bevel=.004)
for j, s in enumerate((-1, 1)): box(f'{r}_console_leg{j}', .04, .4, .08, tx + s * .9, Y - .25, F, 'woodD', bevel=.008)
CT = F + .5
box(f'{r}_tv', 1.5, .06, .86, tx, Y - .1, 1.0, 'dark_keep', bevel=.012)
box(f'{r}_tv_screen', 1.42, .01, .78, tx, Y - .135, 1.04, M('Screen_tv', color='#6fd6e6', emit=1.3, ecol='#5ccbe0'), bevel=0)
add_light(f'{r}_TVGlow', 'POINT', (tx, Y - .7, 1.4), 40, '#6fd0ff', radius=.6)
# 游戏机 + 星球灯 + 手办
box(f'{r}_gamebox', .36, .3, .08, tx - .5, Y - .25, CT, 'white', bevel=.02)
box(f'{r}_gamebox_led', .1, .005, .008, tx - .5, Y - .405, CT + .04, M('led', color='#99ffff', emit=4), bevel=0)
pl = sph(f'{r}_planet', .13, tx + .62, Y - .25, CT + .19, M('planet', color='#ffe3b8', emit=1.5, ecol='#ffcf8a'), seg=24)
tor(f'{r}_planet_ring', .21, .012, tx + .62, Y - .25, CT + .19, 'cream', seg=32, sseg=5, rx=.35, ry=.25)
cyl(f'{r}_planet_stand', .06, .06, tx + .62, Y - .25, CT, 'woodD', seg=14)
add_light(f'{r}_PlanetLamp', 'POINT', (tx + .62, Y - .5, CT + .25), 20, '#ffcf8a', radius=.2)
cyl(f'{r}_figure', .04, .12, tx + .2, Y - .25, CT, 'fabric', seg=10)
sph(f'{r}_figure_h', .05, tx + .2, Y - .25, CT + .16, 'fabric', seg=10)
# 落地音箱
for s, nm in ((-1, 'L'), (1, 'R')):
    sx = tx + s * 1.18
    sp = box(f'{r}_spk{nm}', .3, .3, 1.05, sx, Y - .25, F, 'white', bevel=.02)
    cyl(f'{r}_spk{nm}_cone', .1, .02, sx, Y - .4, F + .7, 'dark_keep', seg=20, rx=math.pi / 2, origin='center', parent=sp)
    cyl(f'{r}_spk{nm}_tw', .045, .02, sx, Y - .4, F + .92, 'dark_keep', seg=14, rx=math.pi / 2, origin='center', parent=sp)
    cyl(f'{r}_spk{nm}_cone2', .1, .02, sx, Y - .4, F + .38, 'dark_keep', seg=20, rx=math.pi / 2, origin='center', parent=sp)
# 电视上方搁板
for k, z in enumerate([2.2]):
    box(f'{r}_tvshelf', 1.6, .24, .035, tx, Y - .12, z, 'wood', bevel=.006)
books(f'{r}_tvbk', tx - .7, Y - .14, 2.235, .45, h=.24)
plant(f'{r}_tvplant', tx + .55, Y - .13, z=2.235, h=.3, pot_r=.07, kind='hang')
box(f'{r}_tvframe', .32, .03, .24, tx + .05, Y - .1, 2.235, 'white', bevel=.006)
# --- 左：沙发（侧放，面向右）---
sx0, sy0 = -1.55, 0.25; sl = 2.1
box(f'{r}_sofa_base', .9, sl, .3, sx0, sy0, F + .08, 'fabric', bevel=.06, seg=3)
box(f'{r}_sofa_back', .25, sl, .45, sx0 - .33, sy0, F + .38, 'fabric', bevel=.1, seg=3)
for j, s in enumerate((-1, 1)): box(f'{r}_sofa_arm{j}', .9, .22, .55, sx0, sy0 + s * (sl / 2 - .11), F + .08, 'fabric', bevel=.09, seg=3)
for j in range(2): box(f'{r}_sofa_seat{j}', .66, (sl - .44) / 2 - .02, .14, sx0 + .08, sy0 - (sl - .44) / 4 + j * (sl - .44) / 2, F + .38, 'fabric', bevel=.06, seg=3)
for j, (dy, c) in enumerate([(-.45, 'fabric2'), (.45, 'cream')]):
    box(f'{r}_sofa_pillow{j}', .14, .42, .38, sx0 - .14, sy0 + dy, F + .5, c, bevel=.07, seg=3, ry=-.2)
for j, s in enumerate((-1, 1)):
    for k in (-1, 1): box(f'{r}_sofa_foot{j}{k}', .05, .05, .08, sx0 + k * .38, sy0 + s * (sl / 2 - .08), F, 'woodD', bevel=.01)
box(f'{r}_blanket', .6, .5, .04, sx0 + .05, sy0 + .55, F + .52, 'fabric2', bevel=.02, rz=.1)
# 茶几 + 手柄 + 零食
cx, cy = 0.35, 0.15
cyl(f'{r}_ctable', .5, .05, cx, cy, F + .36, 'wood', seg=36, bevel=.01)
cyl(f'{r}_ctable_base', .35, .36, cx, cy, F, 'white', seg=30, r2=.42)
CTT = F + .41
pad = box(f'{r}_pad', .2, .12, .04, cx - .12, cy - .1, CTT, 'white', bevel=.02, rz=.3)
for j, (dx, dy) in enumerate([(-.06, 0), (.06, 0)]): cyl(f'{r}_pad_stick{j}', .016, .02, cx - .12 + dx, cy - .1 + dy, CTT + .04, 'dark_keep', seg=8, parent=pad)
pad2 = box(f'{r}_pad2', .2, .12, .04, cx + .15, cy + .12, CTT, 'fabric2', bevel=.02, rz=-.5)
cyl(f'{r}_snackbowl', .12, .07, cx + .15, cy - .15, CTT, 'cream', seg=20, r2=.14)
for j in range(5): sph(f'{r}_snack{j}', .03, cx + .1 + (j % 3) * .045, cy - .15 + (j // 3) * .05 - .02, CTT + .07, 'clay', seg=8)
cyl(f'{r}_soda', .033, .12, cx - .25, cy + .2, CTT, 'accent', seg=12)
# 懒人沙发
sph(f'{r}_beanbag', .45, 1.65, -.55, F + .3, 'fabric2', seg=24, sc=(1, 1, .7), rz=.5)
sph(f'{r}_beanbag_top', .3, 1.75, -.4, F + .55, 'fabric2', seg=20, sc=(1, .7, .9), rz=.5)
# 球
ball = sph(f'{r}_toy_ball', .11, -.55, -1.35, F + .11, 'accent', seg=16)
# 地毯
rug(f'{r}_rug', .3, .0, 3.2, 3.2, 'fabric', round_=True)
# --- 左后：街机 + 游戏柜 ---
ax = -3.3
box(f'{r}_arcade_body', .75, .7, 1.75, ax, Y - .4, F, 'white', bevel=.02)
box(f'{r}_arcade_top', .78, .62, .22, ax, Y - .43, F + 1.75, 'white', bevel=.02)
box(f'{r}_arcade_marq', .7, .01, .16, ax, Y - .745, F + 1.78, M('marq', color='#ffe0ef', emit=2.2, ecol='#ff9ccc'), bevel=0)
box(f'{r}_arcade_screen', .6, .01, .5, ax, Y - .78, F + 1.15, M('Screen_arc', color='#bdf3ff', emit=1.2, ecol='#8fe8ff'), bevel=0, rx=-.2)
box(f'{r}_arcade_deck', .75, .32, .08, ax, Y - .84, F + .92, 'cream', bevel=.02, rx=.25)
cyl(f'{r}_arcade_stick', .012, .08, ax - .18, Y - .86, F + 1.0, 'dark_keep', seg=8)
sph(f'{r}_arcade_knob', .03, ax - .18, Y - .86, F + 1.09, 'accent', seg=10)
for j in range(3): cyl(f'{r}_arcade_btn{j}', .025, .02, ax + .02 + j * .09, Y - .88 + j * .0, F + 1.0, ['accent', 'fabric', 'white'][j], seg=10)
add_light(f'{r}_ArcadeGlow', 'POINT', (ax, Y - 1.0, F + 1.4), 18, '#ff9ccc', radius=.2)
cabinet(f'{r}_gamecab', -2.25, Y - .22, .9, .42, .9, doors=0, drawers=0, m='white') if False else None
zs = shelf_unit(f'{r}_gamecab', -2.3, Y - .22, .95, .4, 1.2, rows=3)
for k, z in enumerate(zs):
    if k == 1: cyl(f'{r}_trophy', .05, .18, -2.5, Y - .22, z, 'cream', seg=12, r2=.07); books(f'{r}_gc{k}_', -2.3, Y - .24, z, .45, h=.22, depth=.16)
    else: books(f'{r}_gc{k}_', -2.75, Y - .24, z, .7, h=.24, depth=.16)
# --- 霓虹灯（左墙上方：手柄图形）---
nm = M('neon', color='#ff8fc8', emit=5, ecol='#ff6fb5')
nx, nz = -2.4, 2.55
for j, (w, h, x, z) in enumerate([(.7, .035, 0, .18), (.7, .035, 0, -.18), (.035, .36, -.35, 0), (.035, .36, .35, 0)]):
    box(f'{r}_neon{j}', w, .03, h, nx + x, Y - .03, nz + z - h / 2, nm, bevel=.012)
for j, s in enumerate((-1, 1)): tor(f'{r}_neon_btn{j}', .05, .012, nx + s * .17, Y - .03, nz, nm, seg=16, sseg=5, rx=math.pi / 2)
add_light(f'{r}_NeonGlow', 'POINT', (nx, Y - .4, nz), 20, '#ff6fb5', radius=.4)
# 角落植物 + 挂画
plant(f'{r}_bigplant', 3.5, -1.45, h=1.2, pot_r=.2, kind='tall')
frame_pic(f'{r}_pic0', XR, 0.0, 1.35, .9, .6, art='fabric2', wall='right')
frame_pic(f'{r}_poster', XL, 1.25, 1.35, .55, .75, art='accent', wall='left')
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
