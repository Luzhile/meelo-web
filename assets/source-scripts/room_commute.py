# 通勤：地铁车厢——左后滑门、沿后墙长座椅、扶杆吊环、窗上方线路图
from mathutils import Matrix
room('commute'); clear_new('commute'); window()
r = 'commute'; F = FLOOR; Y = BACK
box(f'{r}_ceil_strip', 3.2, .16, .05, 0, -0.4, CEIL - .05, M('strip', color='#f4f8ff', emit=4), bevel=.02)
cat = bpy.data.objects[r + '_Cat_main']; cat.location = (.75, -.95, F); cat.rotation_euler = (0, 0, 0)
# --- 滑门（左后）---
dc = -2.75; dw = .5
box(f'{r}_dframe', 1.2, .08, 2.18, dc, Y - .04, F, 'metal', bevel=.02)
box(f'{r}_drecess', 1.04, .02, 2.05, dc, Y - .085, F, 'dark_keep', bevel=0)
for nm, s in (('L', -1), ('R', 1)):
    d = box(f'{r}_door{nm}', dw, .05, 2.0, dc + s * dw / 2, Y - .12, F + .02, 'white', bevel=.012)
    box(f'{r}_door{nm}_glass', dw - .16, .01, .75, dc + s * dw / 2, Y - .15, F + 1.0, M('Glass_door', color='#2a3550', rough=.2), bevel=0, parent=d)
    box(f'{r}_door{nm}_edge', .03, .06, 1.9, dc + s * .02, Y - .12, F + .07, 'dark_keep', bevel=.008, parent=d)
box(f'{r}_dsign', .5, .02, .14, dc, Y - .09, F + 2.22, M('sign', color='#e9f2ff', emit=1.5, ecol='#bfd8ff'), bevel=.01)
box(f'{r}_floorline', 1.1, .14, .006, dc, Y - .5, F, M('yline', color='#f2d36b'), bevel=0)
# --- 长座椅（沿后墙，窗下开始）---
x0, x1 = -1.95, 3.86
box(f'{r}_bench_base', x1 - x0, .5, .32, (x0 + x1) / 2, Y - .3, F + .06, 'white', bevel=.02)
box(f'{r}_bench_kick', x1 - x0 - .06, .44, .06, (x0 + x1) / 2, Y - .27, F, 'dark_keep', bevel=0)
n = 7; sw = (x1 - x0) / n
for j in range(n):
    xx = x0 + sw * (j + .5)
    box(f'{r}_seat{j}', sw - .05, .48, .1, xx, Y - .32, F + .38, 'fabric', bevel=.04, seg=3)
    box(f'{r}_seatback{j}', sw - .05, .1, .5, xx, Y - .1, F + .5, 'fabric', bevel=.04, seg=3, rx=.08)
for j in (2, 5):
    xx = x0 + sw * j
    box(f'{r}_divider{j}', .03, .45, .55, xx, Y - .3, F + .38, 'metal', bevel=.01)
# --- 行李架 ---
box(f'{r}_rack', x1 - x0 - .1, .32, .03, (x0 + x1) / 2 + .05, Y - .2, 2.32, 'metal', bevel=.006)
for j in range(4): box(f'{r}_rack_br{j}', .03, .3, .12, x0 + .3 + j * 1.75, Y - .18, 2.2, 'metal', bevel=.006)
box(f'{r}_suitcase_up', .5, .28, .32, 2.8, Y - .2, 2.35, 'fabric2', bevel=.04)
box(f'{r}_bag_up', .4, .26, .2, -1.4, Y - .2, 2.35, 'cream', bevel=.06)
# --- 扶杆 + 横杆 + 吊环 ---
for j, xx in enumerate([-1.0, 1.4]):
    cyl(f'{r}_pole{j}', .025, CEIL - F, xx, -.1, F, 'metal', seg=12)
cyl(f'{r}_ceil_bar', .02, 6.6, 0, -.1, 3.05, 'metal', seg=10, ry=math.pi / 2, origin='center')
for j in range(8):
    xx = -3.0 + j * .85
    if abs(xx + 1.0) < .2 or abs(xx - 1.4) < .2: continue
    cyl(f'{r}_ceil_strap{j}', .012, .28, xx, -.1, 2.77, 'fabric', seg=6)
    tor(f'{r}_ceil_ring{j}', .07, .014, xx, -.1, 2.7, 'white', seg=16, sseg=6, rx=math.pi / 2)
# --- 线路图（窗上方，可点）---
box(f'{r}_mapboard', 2.6, .03, .42, 0, Y - .015, 2.82, 'white', bevel=.01)
box(f'{r}_route_line', 2.2, .01, .03, 0, Y - .035, 3.02, M('route', color='#9fc2ff', emit=1.2), bevel=0)
for j in range(6):
    xx = -1.0 + j * .4
    cyl(f'{r}_routeDot{j}', .045, .02, xx, Y - .045, 3.035, M('dot', color='#ffffff', emit=1.0, ecol='#ffe9a8'), seg=14, rx=math.pi / 2, origin='center')
    box(f'{r}_station{j}', .2, .006, .03, xx, Y - .035, 2.88, 'dark_keep', bevel=0)
# --- 广告框（右墙）+ 车厢小物 ---
frame_pic(f'{r}_ad0', XR, -.4, 1.3, .9, .6, art='fabric2', wall='right')
frame_pic(f'{r}_ad1', XR, .7, 1.3, .9, .6, art='accent', wall='right')
box(f'{r}_seatbag', .35, .2, .28, 2.25, Y - .35, F + .48, 'cream', bevel=.06)
cyl(f'{r}_umbrella', .02, .8, 3.5, Y - .6, F, 'dark_keep', seg=8, rx=.2)
tor(f'{r}_umbrella_h', .04, .01, 3.5, Y - .62 - .16, F + .8, 'dark_keep', seg=12, sseg=5, rx=math.pi / 2, arc=.5)
box(f'{r}_suitcase', .42, .26, .62, -1.45, -.6, F + .04, 'fabric2', bevel=.05)
for j, s in enumerate((-1, 1)): sph(f'{r}_suitcase_wh{j}', .03, -1.45 + s * .15, -.6, F + .03, 'dark_keep', seg=8)
box(f'{r}_suitcase_h', .2, .03, .2, -1.45, -.6, F + .66, 'metal', bevel=.008)
cyl(f'{r}_coffee', .04, .14, 1.6, Y - .32, F + .48, 'cream', seg=12, r2=.05)
box(f'{r}_newspaper', .3, .22, .015, -.6, Y - .3, F + .48, 'paper', bevel=.003, rz=.2)
# 地面防滑纹
for j in range(6): box(f'{r}_floorstripe{j}', 7.5, .02, .004, 0, -1.8 + j * .35, F, 'white', bevel=0)
box(f'{r}_mat_door', .9, .5, .012, -3.35, -.8, F, 'fabric2', bevel=.008)
