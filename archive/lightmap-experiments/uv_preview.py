import bpy,json,pathlib,sys,hashlib
import numpy as np
run=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(run/'blends/prepared-eight-rooms.blend'))
size=1024;image=np.full((size,size,4),(.035,.035,.045,1),np.float32)
for o in bpy.data.objects:
    if o.type!='MESH' or not o.get('lightmap_static') or o.get('lightmap_room')!='studyWork':continue
    color=np.frombuffer(hashlib.sha256(o.name.encode()).digest()[:3],np.uint8).astype(float)/255*.65+.25
    me=o.data;me.calc_loop_triangles();uv=me.uv_layers['UV_Lightmap']
    for tri in me.loop_triangles:
        pts=np.array([uv.data[i].uv[:] for i in tri.loops])*size;a,b,c=pts
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8:continue
        lo=np.maximum(0,np.floor(pts.min(0)).astype(int));hi=np.minimum(size,np.ceil(pts.max(0)).astype(int))
        if (hi<=lo).any():continue
        yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];xx=xx+.5;yy=yy+.5
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        mask=(u>0)&(v>0)&(1-u-v>0)
        image[lo[1]:hi[1],lo[0]:hi[0],:3][mask]=color
im=bpy.data.images.new('UV_Lightmap_DIAGNOSTIC',width=size,height=size,alpha=True)
im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(image.ravel());im.update()
im.filepath_raw=str(run/'renders/study-uv-atlas.png');im.file_format='PNG';im.save()
print('UV_PREVIEW_SAVED',im.filepath_raw,flush=True)
