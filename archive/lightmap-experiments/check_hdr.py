import bpy,numpy as np,pathlib
r=pathlib.Path(r'D:\MEELO_交接_1119\lightmap-pipeline\runs\study-04')
a=bpy.data.images.load(str(r/'assets/studyWork-lightmap.exr')); b=bpy.data.images.load(str(r/'assets/studyWork-lightmap.hdr'))
x=np.array(a.pixels[:]).reshape(-1,4)[:,:3];y=np.array(b.pixels[:]).reshape(-1,4)[:,:3]
print('HDR_READBACK',a.size[:],b.size[:],np.mean(abs(x-y)),np.max(abs(x-y)),np.mean(x),np.mean(y),flush=True)
for f in ['three-baked.png','three-flip-true.png','study-baked-reconstruction.png']:
 im=bpy.data.images.load(str(r/'renders'/f));print('IMAGE',f,im.size[:],im.pixels[0:4],flush=True)
