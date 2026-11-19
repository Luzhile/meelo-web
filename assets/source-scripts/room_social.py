# 社交：派对小酒吧——左卡座、中间 DJ 台（唱盘可转）、右吧台+高脚凳、迪斯科球、音箱、串灯
from mathutils import Matrix
room('social'); clear_new('social'); window()
r = 'social'; F = FLOOR; Y = BACK
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#fff2f6', emit=3), bevel=.02)
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (-.2, .9, F); cat.rotation_euler = (0, 0, 0)
# --- DJ 台（窗前，猫站在台后）---
dx, dy = -.2, .2
box(f'{r}_djdesk', 1.7, .6, .9, dx, dy, F, 'white', bevel=.02)
box(f'{r}_djdesk_front', 1.6, .02, .5, dx, dy - .31, F + .25, M('djface', color='#f4e4ec'), bevel=.005)
for j in range(3):
    box(f'{r}_dj_led{j}', .4, .01, .05, dx - .5 + j * .5, dy - .325, F + .5, M(f'led{j}', color=['#ff9ccc', '#9fe4ff', '#ffe08a'][j], emit=2.5), bevel=0)
T = F + .9
for j, s in enumerate((-1, 1)):
    tt = box(f'{r}_turntable{j}', .44, .38, .06, dx + s * .52, dy, T, 'cream', bevel=.015) if False else None
    box(f'{r}_deck{j}', .44, .38, .06, dx + s * .52, dy, T, 'cream', bevel=.015)
    cyl(f'{r}_record{j}', .16, .012, dx + s * .52, dy, T + .06, 'dark_keep', seg=28)
    cyl(f'{r}_record{j}_label', .05, .004, dx + s * .52, dy, T + .072, 'accent', seg=16, parent=bpy.data.objects[f'{r}_record{j}'])
    box(f'{r}_tonearm{j}', .02, .2, .015, dx + s * .52 + .15, dy + .05, T + .08, 'metal', bevel=.004, rz=.4)
mx = box(f'{r}_mixer', .34, .34, .08, dx, dy, T, 'white', bevel=.015)
for j in range(4): cyl(f'{r}_mixer_knob{j}', .018, .03, dx - .1 + (j % 2) * .2, dy + .08 - (j // 2) * .12, T + .08, 'dark_keep', seg=8, parent=mx)
box(f'{r}_mixer_fader', .14, .02, .02, dx, dy - .12, T + .08, 'accent', bevel=.004, parent=mx)
cyl(f'{r}_headphone', .1, .03, dx + .3, dy - .2, T, 'dark_keep', seg=16) if False else tor(f'{r}_headphone', .1, .018, dx + .1, dy + .22, T + .1, 'dark_keep', seg=16, sseg=6, rx=math.pi / 2, arc=.5)
# 音箱（台两侧）
for j, s in enumerate((-1, 1)):
    sx = dx + s * 1.3
    sp = box(f'{r}_social_spk{j}', .4, .38, .9, sx, dy + .1, F, 'white', bevel=.02)
    cyl(f'{r}_social_spk{j}_c', .14, .02, sx, dy - .1, F + .55, 'dark_keep', seg=20, rx=math.pi / 2, origin='center', parent=sp)
    cyl(f'{r}_social_spk{j}_t', .06, .02, sx, dy - .1, F + .78, 'dark_keep', seg=14, rx=math.pi / 2, origin='center', parent=sp)
    cyl(f'{r}_social_spk{j}_c2', .1, .02, sx, dy - .1, F + .25, 'dark_keep', seg=18, rx=math.pi / 2, origin='center', parent=sp)
# 迪斯科球（可转）
cyl(f'{r}_ceil_dcord', .006, .5, -.2, -.3, CEIL - .5, 'metal', seg=6)
db = sph(f'{r}_disco0', .22, -.2, -.3, CEIL - .72, M('discoball', color='#e8e8f0', metal=.8, rough=.25), seg=14)
# --- 左：卡座沙发 + 小圆桌 ---
bx = -3.0
box(f'{r}_booth_seat', 1.0, 2.2, .42, bx, .45, F, 'fabric', bevel=.06, seg=3)
box(f'{r}_booth_back', .3, 2.2, .65, bx - .5, .45, F + .42, 'fabric', bevel=.1, seg=3)
for j in range(3): box(f'{r}_booth_tuft{j}', .02, .02, .5, bx - .34, -.2 + j * .65, F + .5, 'fabric2', bevel=0)
for j, (dy2, c) in enumerate([(-.2, 'fabric2'), (.9, 'cream')]):
    box(f'{r}_booth_pillow{j}', .14, .42, .36, bx - .28, .45 + dy2, F + .45, c, bevel=.07, seg=3, ry=-.2)
cyl(f'{r}_btable', .38, .04, -1.95, .3, F + .68, 'wood', seg=30)
cyl(f'{r}_btable_leg', .04, .68, -1.95, .3, F, 'white', seg=10)
cyl(f'{r}_btable_foot', .22, .03, -1.95, .3, F, 'white', seg=20)
for j, (x, y, c) in enumerate([(-2.05, .2, 'accent'), (-1.85, .4, 'fabric2'), (-1.8, .15, 'cream')]):
    cyl(f'{r}_glass{j}', .035, .12, x, y, F + .72, c, seg=12, r2=.045)
cyl(f'{r}_cake', .12, .1, -2.1, .45, F + .72, 'cream', seg=20)
cyl(f'{r}_cake_top', .12, .02, -2.1, .45, F + .82, 'accent', seg=20)
cyl(f'{r}_candle', .008, .08, -2.1, .45, F + .84, 'white', seg=6)
# --- 右：吧台 + 高脚凳 + 酒架 ---
ox = 2.75
box(f'{r}_bar', 1.9, .62, 1.0, ox, .55, F, 'white', bevel=.02)
box(f'{r}_bar_top', 2.0, .75, .05, ox, .52, F + 1.0, 'wood', bevel=.01)
box(f'{r}_bar_rail', 1.85, .04, .04, ox, .2, F + .25, 'metal', bevel=.01)
for j in range(3): box(f'{r}_bar_p{j}', .02, .006, .75, ox - .6 + j * .6, .237, F + .15, 'fabric2', bevel=0)
for j in range(3): stool(f'{r}_stool{j}', ox - .65 + j * .65, -.15, h=.75)
BT = F + 1.05
for j, (x, c, h) in enumerate([(2.2, 'accent', .28), (2.35, 'fabric', .32), (3.3, 'cream', .25)]):
    cyl(f'{r}_bottle{j}', .04, h, x, .6, BT, c, seg=12, r2=.025)
cyl(f'{r}_shaker', .05, .2, 2.95, .55, BT, 'metal', seg=14, r2=.04)
cyl(f'{r}_lemonbowl', .1, .06, 3.15, .45, BT, 'white', seg=16, r2=.12)
for j in range(3): sph(f'{r}_lemon{j}', .04, 3.12 + j * .04, .45, BT + .07, M('lemon', color='#f2e3a0'), seg=8)
# 酒架（右后墙）
for k, z in enumerate([1.45, 1.85, 2.25]):
    box(f'{r}_bshelf{k}', 1.6, .24, .03, 2.85, Y - .12, z, 'wood', bevel=.006)
    for j in range(6):
        cyl(f'{r}_bs{k}_{j}', .035, .2 + (j % 3) * .04, 2.2 + j * .26, Y - .12, z + .03, ['white', 'fabric', 'cream', 'accent'][(j + k) % 4], seg=10, r2=.02)
add_light(f'{r}_BarGlow', 'POINT', (2.85, .55, 1.9), 30, '#ffaad2', radius=.4)
# 霓虹（左墙后墙：爱心）
nm = M('neon', color='#ff9cc8', emit=5, ecol='#ff6fb0')
hx, hz = -2.35, 2.35
for j in range(56):
    t = j / 56 * 2 * math.pi
    x = 16 * math.sin(t) ** 3; z = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    sph(f'{r}_neon_h{j}', .024, hx + x * .022, Y - .04, hz + z * .022, nm, seg=6)
add_light(f'{r}_NeonGlow', 'POINT', (hx, Y - .45, hz), 25, '#ff6fb0', radius=.6)
# 串灯（前沿）
for j in range(15):
    t = j / 14; x = -3.6 + 7.2 * t; z = 3.25 - math.sin(t * math.pi * 3) ** 2 * .18
    sph(f'{r}_ceil_bulb{j}', .035, x, -1.9, z, M('bulbs', color='#fff1c4', emit=3), seg=8)
# 彩色派对聚光（迪斯科时会转亮）
for j, (x, col) in enumerate([(-2.4, '#ff3a8a'), (-.8, '#3abfff'), (.8, '#ffbf2a'), (2.4, '#8a5aff')]):
    add_light(f'{r}_Spot{j}', 'SPOT', (x, -.9, 3.3), 220, col, angle=.65, blend=.5, rot=(math.radians(10), math.radians(-x * 6), 0))
# 气球
for j, (x, y, z, c) in enumerate([(-3.5, 1.6, 2.5, 'accent'), (-3.3, 1.75, 2.35, 'fabric2'), (-3.6, 1.8, 2.2, 'cream')]):
    sph(f'{r}_balloon{j}', .14, x, y, z, c, seg=14, sc=(1, 1, 1.2))
    cyl(f'{r}_balloon{j}_s', .003, z - .2 - F - 1.1, x, y, F + 1.1, 'white', seg=4)
rug(f'{r}_rug', -.2, -.5, 2.6, 2.6, 'fabric2', round_=True)
plant(f'{r}_bigplant', 1.5, -1.6, h=1.0, pot_r=.17, kind='tall')
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
