
import bpy,re,base64,json,os
from mathutils import Matrix,Vector
APP=r'C:\Users\86173\Documents\ChatGPT\meelo咪楼\交接包_1116\app\models'
# 可点的物件（名字要和网页 index.html 里 INTER 规则对上）
INTER={'studyWork':r'(keyboard|_screen$|_monitor$|mug|wclock|anim_Cursor|DeskLampShade)',
       'meal':r'(FridgeDoor|PotLid|meal_tap)',
       'sleep':r'(PullCord|sleep_clock|curt[LR]\d|cloud_|moon_r|crater|sleep_milk|sleep_plush|sleep_mask)',
       'entertainment':r'(tv_screen|entertainment_pad|entertainment_spk|toy_ball)',
       'commute':r'(commute_door|routeDot|route_line)',
       'home':r'(wash_|home_chk|home_vac)',
       'outdoor':r'(_bf|apple)',
       'social':r'(disco|dj_led|mixer|turntable|record|social_spk)'}
SHELL=re.compile(r'_(BackWall|Frame_L|Frame_R|LeftWall_back|LeftWall_front|LeftWall_lintel|RightWall)$')
CEIL=re.compile(r'_ceil_|_(Ceiling|Frame_T|crown\w*|ceil_strip|new_pend_\w+)$')
NOCEIL=re.compile(r'_win|BackWin')
def is_old(o):
    p=o
    while p:
        if p.get('meelo_old'):return True
        p=p.parent
    return False
def export_unit(U):
    unit=bpy.data.objects['Unit_'+U];inv=unit.matrix_world.inverted();dg=bpy.context.evaluated_depsgraph_get()
    cat=bpy.data.objects[U+'_Cat_main'];catset=set(cat.children_recursive)
    tmp=bpy.data.scenes.new('MEELO_EXPORT')
    def new(name,data=None):
        o=bpy.data.objects.new(name,data);tmp.collection.objects.link(o);return o
    root=new('Unit_'+U);stat=[];ceil=[];imap={};shell=0
    ire=re.compile(INTER[U]);oldc=bpy.data.collections.get('旧家具_'+U)
    for o in unit.children_recursive:
        if o.type not in('MESH','FONT') or is_old(o) or o in catset or o.hide_render:continue
        if oldc and o.name in oldc.objects:continue
        me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));rel=inv@o.matrix_world
        if ire.search(o.name):
            x=new('I_'+o.name,me);x.parent=root;x.matrix_world=rel;imap[o]=x
        elif SHELL.search(o.name):
            x=new('SHELL_'+o.name,me);x.parent=root;x.matrix_world=rel;shell+=1
        else:
            me.transform(rel);x=new('tmp_'+o.name,me)
            zmin=min((v.co.z for v in me.vertices),default=0)
            # 新家具只按名字（_ceil_）进天花组；旧家具才用高度猜
            guess=(zmin>2.45 and not NOCEIL.search(o.name) and not o.get('meelo_new'))
            (ceil if (CEIL.search(o.name) or guess) else stat).append(x)
    for o,x in imap.items():
        p=o.parent
        while p and p not in imap:p=p.parent
        if p:
            w=x.matrix_world.copy();x.parent=imap[p];x.matrix_parent_inverse=Matrix();x.matrix_basis=imap[p].matrix_world.inverted()@w
            x.name=x.name[2:]  # 子物件不单独可点，跟着父物件动
    def join(name,objs):
        if not objs:return
        with bpy.context.temp_override(scene=tmp,active_object=objs[0],selected_editable_objects=objs,selected_objects=objs):
            bpy.ops.object.join()
        objs[0].name=name;objs[0].parent=root
    join('G_static',stat);join('G_ceiling',ceil)
    ce=new('CAT_main');ce.parent=root;ce.matrix_world=inv@cat.matrix_world;cinv=cat.matrix_world.inverted()
    for c in cat.children_recursive:
        if c.type!='MESH':continue
        x=new(c.name,bpy.data.meshes.new_from_object(c.evaluated_get(dg)));x.parent=ce;x.matrix_parent_inverse=Matrix();x.matrix_basis=cinv@c.matrix_world
    win=bpy.context.window;prev=win.scene;win.scene=tmp
    glb=os.path.join(os.environ.get('TEMP','.'),f'meelo_{U}.glb')
    MB=bpy.app.driver_namespace.get('MBAKE');baked=bool(MB and bpy.data.images.get('LM_'+U))
    try:
        if baked:MB['link_for_export'](U,True)
        bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=False,use_active_scene=True,export_yup=True,export_apply=False,export_lights=False,export_cameras=False,export_materials='EXPORT',export_image_format='JPEG',export_jpeg_quality=86)
    finally:
        if baked:MB['link_for_export'](U,False)
        win.scene=prev
        for o in list(tmp.objects):
            d=o.data;bpy.data.objects.remove(o,do_unlink=True)
            if d and d.users==0:bpy.data.meshes.remove(d)
        bpy.data.scenes.remove(tmp)
    raw=open(glb,'rb').read()
    open(os.path.join(APP,U+'.txt'),'w').write(base64.b64encode(raw).decode('ascii'))
    # 灯：按 Blender 里房间下的灯整表重建（网页每间最多 1 面光 / 6 点光 / 4 聚光）
    rj=os.path.join(APP,'rooms.json');R=json.load(open(rj,encoding='utf8'))
    lights=[]
    for o in unit.children_recursive:
        if o.type!='LIGHT' or is_old(o) or o.hide_render:continue
        m=inv@o.matrix_world;p=m.translation;d=(m.to_3x3()@Vector((0,0,-1))).normalized();L=o.data
        e={'name':o.name,'type':L.type,'energy':L.energy,'color':list(L.color),'pos':[round(p.x,4),round(p.z,4),round(-p.y,4)],'dir':[round(d.x,4),round(d.z,4),round(-d.y,4)]}
        if L.type in('POINT','SPOT'):e['radius']=L.shadow_soft_size
        if L.type=='SPOT':e['angle']=L.spot_size;e['blend']=L.spot_blend
        if L.type=='AREA':e['size']=[L.size,L.size_y if L.shape in('RECTANGLE','ELLIPSE') else L.size];e['shape']=L.shape
        lights.append(e)
    lights.sort(key=lambda e:(e['type']!='AREA',e['name']))
    R[U]['lights']=lights;R[U]['kept']=[]
    json.dump(R,open(rj,'w',encoding='utf8'),ensure_ascii=False)
    return {'unit':U,'bytes':len(raw),'static':len(stat),'ceiling':len(ceil),'interactive':sum(1 for x in imap.values()),'shell':shell,'lights':len(lights)}

# 用法：在 Blender 的脚本编辑器里运行本文件，然后 export_unit("studyWork")
