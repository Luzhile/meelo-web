# 居家：右洗衣角（洗衣机可转）、晾衣架、左待办板、吸尘器、窗下矮柜、扶手椅+落地灯、阳光从窗射进来
from mathutils import Matrix
room('home'); clear_new('home'); window()
r = 'home'; F = FLOOR; Y = BACK
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fff6ea', emit=4), bevel=.02)
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (-.35, -.9, F); cat.rotation_euler = (0, 0, 0)
# 窗下矮柜 + 植物
cabinet(f'{r}_sideboard', 0, Y - .24, 2.2, .46, .7, doors=3, m='white', top='wood')
ST = F + .735
plant(f'{r}_sbplant0', -.75, Y - .25, z=ST, h=.4, pot_r=.09, kind='bush')
cyl(f'{r}_vase', .06, .26, .1, Y - .25, ST, 'cream', seg=16, r2=.04)
for j in range(3): cyl(f'{r}_twig{j}', .006, .3, .1, Y - .25, ST + .2, 'woodD', seg=5, rx=(j - 1) * .25)
box(f'{r}_basket', .4, .3, .2, .7, Y - .25, ST, 'wood', bevel=.03)
box(f'{r}_folded0', .32, .24, .06, .7, Y - .25, ST + .2, 'fabric', bevel=.02)
box(f'{r}_folded1', .3, .22, .06, .7, Y - .25, ST + .26, 'white', bevel=.02)
# 阳光
add_light(f'{r}_SunBeam', 'SPOT', (-.6, Y + 1.2, 3.1), 420, '#ffc070', angle=.9, blend=.4, rot=(math.radians(-48), math.radians(-10), 0))
# --- 洗衣角（右后）---
wx = 3.3
box(f'{r}_wash_body', .72, .66, .9, wx, Y - .36, F, 'white', bevel=.03)
box(f'{r}_wash_panel', .7, .02, .14, wx, Y - .7, F + .74, 'cream', bevel=.006)
cyl(f'{r}_wash_knob', .04, .02, wx + .2, Y - .72, F + .81, 'metal', seg=12, rx=math.pi / 2, origin='center')
dz = F + .4
cyl(f'{r}_wash_ring', .25, .04, wx, Y - .7, dz, 'metal', seg=28, rx=math.pi / 2, origin='center')
cyl(f'{r}_wash_glass', .2, .02, wx, Y - .73, dz, M('Glass_wash', color='#9fb6c8', rough=.15), seg=28, rx=math.pi / 2, origin='center')
cl = sph(f'{r}_wash_cloth', .12, wx, Y - .62, dz, 'fabric', seg=12, sc=(1.3, .5, .7))
box(f'{r}_wash_cloth_b', .1, .06, .08, wx + .06, Y - .62, dz - .1, 'accent', bevel=.03, parent=cl)
# 洗衣机上的搁板 + 洗衣液
box(f'{r}_lshelf', .9, .28, .035, wx, Y - .14, 1.55, 'wood', bevel=.006)
for j, (dx, c, h) in enumerate([(-.3, 'white', .22), (-.12, 'fabric', .18), (.08, 'cream', .25)]):
    box(f'{r}_bottle{j}', .12, .1, h, wx + dx, Y - .15, 1.585, c, bevel=.03)
plant(f'{r}_lplant', wx + .3, Y - .15, z=1.585, h=.3, pot_r=.06, kind='hang')
cyl(f'{r}_lbasket', .25, .4, 2.55, Y - .45, F, 'wood', seg=20, r2=.28)
for j in range(3): sph(f'{r}_lcloth{j}', .12, 2.5 + j * .06, Y - .45, F + .42, ['fabric', 'white', 'fabric2'][j], seg=10, sc=(1.2, 1, .5))
# --- 晾衣架（右前）---
rx0 = 2.4; ry0 = -.7
for j, s in enumerate((-1, 1)):
    box(f'{r}_rack_leg{j}a', .025, .025, 1.3, rx0 + s * .55, ry0 - .2, F, 'metal', bevel=0, rx=.15)
    box(f'{r}_rack_leg{j}b', .025, .025, 1.3, rx0 + s * .55, ry0 + .2, F, 'metal', bevel=0, rx=-.15)
cyl(f'{r}_rack_top', .015, 1.15, rx0, ry0, F + 1.27, 'metal', seg=8, ry=math.pi / 2, origin='center')
for j, (dx, w, h, c) in enumerate([(-.38, .3, .45, 'fabric'), (-.02, .32, .55, 'white'), (.33, .26, .38, 'fabric2')]):
    box(f'{r}_hangcloth{j}', w, .015, h, rx0 + dx, ry0, F + 1.27 - h, c, bevel=.005)
# --- 待办板（左墙后方的后墙上）---
bx = -1.95
box(f'{r}_home_chk', .85, .03, 1.0, bx, Y - .015, 1.35, 'white', bevel=.01)
for j in range(4):
    box(f'{r}_home_chk_box{j}', .07, .01, .07, bx - .3, Y - .035, 2.15 - j * .2, 'cream', bevel=0)
    box(f'{r}_home_chk_line{j}', .45, .01, .025, bx + .05, Y - .035, 2.17 - j * .2, 'dark_keep' if j < 2 else 'fabric2', bevel=0)
box(f'{r}_home_chk_tick', .06, .012, .02, bx - .3, Y - .04, 2.18, 'accent', bevel=0, ry=.6)
box(f'{r}_home_chk_tick2', .06, .012, .02, bx - .3, Y - .04, 1.98, 'accent', bevel=0, ry=.6)
# --- 吸尘器（立着）---
vx, vy = -1.95, Y - .45
box(f'{r}_home_vac_head', .3, .16, .07, vx, vy, F, 'cream', bevel=.03)
cyl(f'{r}_home_vac_stick', .02, 1.0, vx, vy + .02, F + .07, 'metal', seg=10)
cyl(f'{r}_home_vac_body', .07, .3, vx, vy + .06, F + .55, 'fabric', seg=14)
box(f'{r}_home_vac_grip', .04, .1, .12, vx, vy + .02, F + 1.05, 'dark_keep', bevel=.015)
# --- 左：扶手椅 + 落地灯 + 边几 ---
ax, ay = -2.65, -.1
p = empty_parent(f'{r}_armchair', ax, ay, F); p.rotation_euler = (0, 0, -.45)
for nm2, (sx, sy, sz, x, y, z) in {'base': (.85, .8, .32, 0, 0, .1), 'back': (.85, .2, .45, 0, .32, .42), 'armL': (.16, .8, .3, -.37, 0, .42), 'armR': (.16, .8, .3, .37, 0, .42), 'cush': (.55, .58, .12, 0, -.06, .42)}.items():
    o = box(f'{r}_armchair_{nm2}', sx, sy, sz, 0, 0, 0, 'fabric', bevel=.07, seg=3); o.parent = p; o.location = (x, y, z)
for j, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
    o = box(f'{r}_armchair_leg{j}', .05, .05, .1, 0, 0, 0, 'woodD', bevel=.01); o.parent = p; o.location = (sx * .35, sy * .32, 0)
cyl(f'{r}_sidetable', .25, .03, -1.85, .55, F + .55, 'wood', seg=24)
cyl(f'{r}_sidetable_leg', .03, .55, -1.85, .55, F, 'white', seg=10)
cyl(f'{r}_teacup', .045, .07, -1.85, .5, F + .58, 'white', seg=12)
box(f'{r}_book', .2, .14, .03, -1.78, .62, F + .58, 'fabric2', bevel=.004, rz=.3)
cyl(f'{r}_flamp_base', .15, .03, -3.45, .75, F, 'white', seg=20)
cyl(f'{r}_flamp_pole', .015, 1.5, -3.45, .75, F + .03, 'white', seg=8)
cyl(f'{r}_flamp_shade', .22, .28, -3.45, .75, F + 1.48, 'paper', seg=24, r2=.16)
add_light(f'{r}_FloorLamp', 'POINT', (-3.45, .75, F + 1.55), 26, '#ffcf90', radius=.2)
rug(f'{r}_rug', -2.4, .0, 2.0, 1.6, 'fabric2', round_=True)
# 挂钟 + 挂画
frame_pic(f'{r}_pic0', XL, .5, 1.55, .5, .65, art='fabric', wall='left')
frame_pic(f'{r}_pic1', XR, -.6, 1.45, .7, .5, art='fabric2', wall='right')
plant(f'{r}_bigplant', 1.25, -1.55, h=1.0, pot_r=.18, kind='snake')
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
# 地上的小拖鞋 + 猫碗
for j, s in enumerate((-1, 1)): box(f'{r}_slipper{j}', .1, .25, .05, .55 + s * .07, -1.35, F + .015, 'fabric', bevel=.025, rz=.2 * s)
cyl(f'{r}_catbowl', .11, .06, -.95, -1.45, F, 'cream', seg=20, r2=.13)
cyl(f'{r}_catbowl_food', .1, .01, -.95, -1.45, F + .05, 'clay', seg=16)
