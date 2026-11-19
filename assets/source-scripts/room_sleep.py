# 卧室：床头靠窗、两侧床头柜、窗帘、云朵壁灯、月亮灯、衣柜、梳妆台、拉绳灯
from mathutils import Matrix
room('sleep'); clear_new('sleep'); window()
r = 'sleep'; F = FLOOR; Y = BACK
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fff6ea', emit=4), bevel=.02)
# 拉绳（挂在灯条一端）
pc = cyl(f'{r}_PullCord', .006, .75, 1.45, -0.4, CEIL - .8, 'white', seg=6)
sph(f'{r}_PullCord_bead', .035, 1.45, -0.4, CEIL - .82, 'accent', seg=10, parent=pc)

# --- 窗帘 ---
cyl(f'{r}_win_rod', .018, 3.7, 0, Y - .16, 2.86, 'white', seg=10, ry=math.pi / 2, origin='center')
for s in (-1, 1): sph(f'{r}_win_rodend{s}', .035, s * 1.86, Y - .16, 2.86, 'white', seg=10)
for side, s in (('L', -1), ('R', 1)):
    curtain(f'{r}_curt{side}1', s * 1.42, .62, F + .35, 2.83, Y - .16, 'fabric', waves=4)
    curtain(f'{r}_curt{side}2', s * 1.72, .52, F + .35, 2.83, Y - .22, 'fabric2', waves=3)
# --- 床 ---
bw, bl = 1.95, 2.15; by0 = Y - .06; byc = by0 - bl / 2
box(f'{r}_headboard', bw + .2, .12, 1.0, 0, by0 - .02, F, 'fabric2', bevel=.05, seg=3)
for j in range(4): box(f'{r}_headboard_tuft{j}', .02, .02, .7, -.75 + j * .5, by0 - .085, F + .22, 'fabric2', bevel=0)
box(f'{r}_bedframe', bw + .06, bl, .28, 0, byc, F + .06, 'wood', bevel=.02)
for j, (sx, sy) in enumerate([(-1, -1), (1, -1)]):
    box(f'{r}_bedleg{j}', .06, .06, .07, sx * (bw / 2 - .02), by0 - bl + .04, F, 'woodD', bevel=.01)
box(f'{r}_mattress', bw, bl - .06, .2, 0, byc, F + .34, 'white', bevel=.06, seg=3)
MT = F + .54
box(f'{r}_duvet', bw + .08, bl * .68, .1, 0, byc - bl * .16, MT - .07, 'fabric', bevel=.05, seg=3)
box(f'{r}_duvet_fold', bw + .09, .3, .12, 0, byc + bl * .17, MT - .06, 'white', bevel=.05, seg=3)
box(f'{r}_throw', bw + .12, .5, .11, 0, byc - bl * .38, MT - .06, 'fabric2', bevel=.04, seg=3)
for j, s in enumerate((-1, 1)):
    box(f'{r}_pillow{j}', .7, .38, .18, s * .47, by0 - .3, MT - .02, 'white', bevel=.08, seg=3, rx=-.25)
box(f'{r}_cushion', .42, .14, .34, -.15, by0 - .52, MT - .02, 'fabric2', bevel=.06, seg=3, rx=-.3, rz=.1)
# 眼罩
mk = box(f'{r}_sleep_mask', .26, .1, .03, .5, by0 - .62, MT + .05, 'accent', bevel=.012, rz=-.25)
# 玩偶（小熊）
px, py = -.62, by0 - .62
pl = sph(f'{r}_sleep_plush', .13, px, py, MT + .1, 'cream', seg=14, sc=(1, .9, 1.1))
sph(f'{r}_sleep_plush_head', .1, px, py - .02, MT + .3, 'cream', seg=14, parent=pl)
for s in (-1, 1): sph(f'{r}_sleep_plush_ear{s}', .04, px + s * .075, py - .02, MT + .39, 'cream', seg=8, parent=pl)
sph(f'{r}_sleep_plush_snout', .04, px, py - .11, MT + .28, 'white', seg=8, parent=pl)
# 猫坐在床上
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (.35, byc - .35, MT - .02); cat.rotation_euler = (0, 0, 0)
# --- 床头柜 ---
for j, s in enumerate((-1, 1)):
    nx = s * 1.5
    cabinet(f'{r}_nstand{j}', nx, Y - .27, .55, .45, .55, drawers=2, m='white', top='wood')
NT = F + .585
# 左：闹钟 + 小台灯
ck = cyl(f'{r}_sleep_clock', .1, .06, -1.6, Y - .32, NT + .12, 'fabric', seg=24, rx=math.pi / 2, origin='center')
cyl(f'{r}_sleep_clock_face', .085, .005, -1.6, Y - .355, NT + .12, 'paper', seg=24, rx=math.pi / 2, origin='center', parent=ck)
for s in (-1, 1):
    sph(f'{r}_sleep_clock_bell{s}', .04, -1.6 + s * .065, Y - .32, NT + .22, 'metal', seg=10, sc=(1, 1, .7), parent=ck)
    box(f'{r}_sleep_clock_foot{s}', .015, .015, .05, -1.6 + s * .06, Y - .32, NT, 'metal', bevel=0, parent=ck)
box(f'{r}_sleep_clock_hand', .006, .004, .06, -1.6, Y - .36, NT + .12, 'dark_keep', bevel=0, parent=ck, ry=.8)
cyl(f'{r}_nlamp_base', .06, .2, -1.32, Y - .2, NT, 'white', seg=16, r2=.04)
cyl(f'{r}_nlamp_shade', .13, .16, -1.32, Y - .2, NT + .2, 'paper', seg=24, r2=.09)
add_light(f'{r}_BedLamp', 'POINT', (-1.32, Y - .25, NT + .25), 22, '#ffcf96', radius=.15)
# 右：牛奶 + 书 + 月亮灯
mk2 = cyl(f'{r}_sleep_milk', .04, .13, 1.32, Y - .38, NT, M('milk', color='#fbf8f1'), seg=14)
for j, c in enumerate(['fabric', 'white']):
    box(f'{r}_nbook{j}', .22, .16, .035, 1.55, Y - .3, NT + j * .035, c, bevel=.005, rz=.15 * j)
mo = sph(f'{r}_moon_r', .13, 1.6, Y - .2, NT + .33, M('moon', color='#fff2cf', emit=1.2, ecol='#ffe1a3'), seg=24)
for j, (dx, dz, rr) in enumerate([(-.05, .04, .03), (.04, -.03, .025), (.01, .07, .018)]):
    sph(f'{r}_crater{j}', rr, 1.6 + dx, Y - .325, NT + .33 + dz, M('moon'), seg=8, sc=(1, .4, 1), parent=mo)
cyl(f'{r}_moon_stand', .05, .2, 1.6, Y - .2, NT + .07, 'woodD', seg=12, r2=.012)
cyl(f'{r}_moon_base', .07, .07, 1.6, Y - .2, NT + .07 - .07, 'woodD', seg=14)
add_light(f'{r}_MoonGlow', 'POINT', (1.6, Y - .45, NT + .35), 40, '#ffdca0', radius=.3)
# --- 云朵壁灯（左右墙上方） ---
for j, (cx, cz) in enumerate([(-2.6, 2.55), (2.55, 2.75)]):
    c0 = sph(f'{r}_cloud_{j}', .16, cx, Y - .1, cz, M('cloud', color='#fffaf0', emit=1.8, ecol='#fff0d8'), seg=16, sc=(1, .45, 1))
    for k, (dx, dz, rr) in enumerate([(-.18, -.05, .12), (.18, -.04, .13), (.33, -.08, .08), (-.32, -.08, .08)]):
        sph(f'{r}_cloud_{j}_p{k}', rr, cx + dx, Y - .1, cz + dz, M('cloud'), seg=12, sc=(1, .45, 1), parent=c0)
add_light(f'{r}_CloudLight', 'POINT', (-2.6, Y - .4, 2.45), 30, '#ffe6c2', radius=.3)
# 月光：从窗外斜射进来
add_light(f'{r}_Moonlight', 'SPOT', (0, Y + .9, 2.9), 140, '#8fa6ff', angle=.75, blend=.6, rot=(math.radians(-52), 0, 0))
# --- 衣柜（左后） ---
cabinet(f'{r}_wardrobe', -3.3, Y - .32, 1.1, .6, 2.35, doors=2, m='white', kick=.06)
box(f'{r}_wardrobe_box', .5, .4, .25, -3.45, Y - .35, F + 2.35, 'cream', bevel=.02)
box(f'{r}_wardrobe_box2', .4, .35, .18, -3.1, Y - .35, F + 2.35, 'fabric2', bevel=.02)
# 挂衣杆 + 帽子
cyl(f'{r}_coatstand', .02, 1.6, -2.45, Y - .3, F, 'woodD', seg=8)
cyl(f'{r}_coatstand_foot', .18, .02, -2.45, Y - .3, F, 'woodD', seg=3)
sph(f'{r}_coat', .18, -2.45, Y - .36, F + 1.2, 'fabric2', seg=12, sc=(1, .5, 1.6))
cyl(f'{r}_hat', .1, .08, -2.45, Y - .3, F + 1.6, 'cream', seg=16, r2=.07)
cyl(f'{r}_hat_brim', .17, .012, -2.45, Y - .3, F + 1.6, 'cream', seg=20)
# --- 右：梳妆台 + 镜子 + 凳子 ---
cabinet(f'{r}_dresser', 2.95, Y - .25, 1.3, .48, .8, drawers=3, m='white', top='wood')
DT = F + .835
cyl(f'{r}_mirror', .38, .025, 2.95, Y - .03, 1.55, 'white', seg=32, rx=math.pi / 2, origin='center')
cyl(f'{r}_mirror_glass', .33, .005, 2.95, Y - .045, 1.55, M('Glass', color='#dfe6ee', rough=.1, metal=.3), seg=32, rx=math.pi / 2, origin='center')
cyl(f'{r}_perfume', .035, .1, 2.6, Y - .3, DT, 'accent', seg=10)
cyl(f'{r}_jewel', .07, .06, 2.82, Y - .3, DT, 'cream', seg=16)
plant(f'{r}_dresserplant', 3.35, Y - .25, z=DT, h=.4, pot_r=.07, kind='snake')
box(f'{r}_bench', .9, .38, .42, 0, byc - bl / 2 - .3, F, 'fabric2', bevel=.06, seg=3)
for j, s in enumerate((-1, 1)): box(f'{r}_bench_leg{j}', .04, .3, .05, s * .38, byc - bl / 2 - .3, F, 'woodD', bevel=.01)
# 拖鞋
for j, s in enumerate((-1, 1)):
    box(f'{r}_slipper{j}', .1, .25, .05, -1.05 + s * .07, -.15, F + .015, 'fabric2', bevel=.025, rz=.15 * s)
# 地毯 + 大植物 + 挂画
rug(f'{r}_rug', 0, -0.25, 3.0, 2.0, 'fabric2', round_=False)
plant(f'{r}_bigplant', 3.45, -1.55, h=1.2, pot_r=.2, kind='tall')
frame_pic(f'{r}_pic0', XR, 0.2, 1.3, .7, .55, wall='right')
frame_pic(f'{r}_pic1', XR, 1.0, 1.45, .45, .6, art='fabric2', wall='right')
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
# 墙上星星串灯
for j in range(9):
    t = j / 8; x = -2.0 + 4.0 * t; z = 3.2 - math.sin(t * math.pi) * .25
    sph(f'{r}_star{j}', .025, x, Y - .04, z, M('starled', color='#fff2c8', emit=3), seg=8)
