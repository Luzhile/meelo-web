"""Measure display and scene-linear differences from actual saved same-camera images."""
import bpy,numpy as np,json,pathlib,sys
run=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
def load(name):
    im=bpy.data.images.load(str(run/'renders'/name),check_existing=False)
    return np.array(im.pixels[:],np.float32).reshape(im.size[1],im.size[0],4)[:,:,:3]
def linear(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def compare(a,b):
    assert a.shape==b.shape,(a.shape,b.shape)
    # Room aperture in bottom-up Blender pixel coordinates, excluding World background.
    crop=(slice(115,445),slice(83,817))
    d=abs(a[crop]-b[crop]);dl=abs(linear(a[crop])-linear(b[crop]))
    return {'mae_srgb_room_crop':float(d.mean()),'rmse_srgb_room_crop':float(np.sqrt((d*d).mean())),
            'mae_linear_room_crop':float(dl.mean()),'p95_srgb_error':float(np.percentile(d,95)),
            'crop_top_left_pixels':{'x0':83,'x1':817,'y0':155,'y1':485},'resolution':[a.shape[1],a.shape[0]]}
ref=load('study-reference.png');baked=load('study-baked-reconstruction.png');web=load('three-baked.png');real=load('three-realtime.png')
report={'blender_diffuse_bake_vs_clean_pbr':compare(ref,baked),'web_lightmap_vs_blender_baked':compare(baked,web),
        'web_lightmap_vs_blender_reference':compare(ref,web),'web_realtime_vs_blender_reference':compare(ref,real),
        'notes':['All four images use the same orthographic position/target and 900x600 framing.',
                 'Metrics exclude the differing World/canvas backdrop.',
                 'Blender Medium High Contrast Look is absent in Three.js; procedural bump/roughness are not exported by core glTF.',
                 'Diffuse bake excludes view-dependent specular; 1024 atlas / 32 samples is a test, not a final-quality asset.']}
(run/'reports/image-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False),flush=True)
