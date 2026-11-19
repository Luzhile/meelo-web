import bpy,numpy as np,json,pathlib,sys
run=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
def load(name):
    im=bpy.data.images.load(str(run/'renders'/name),check_existing=False)
    return np.array(im.pixels[:],np.float32).reshape(im.size[1],im.size[0],4)[:,:,:3][::-1]
a=load('meal-pbr.png');zero=load('meal-pbr-ao-000.png');half=load('meal-pbr-ao-050.png');full=load('meal-pbr-ao-100.png')
assert a.shape==(600,900,3)
assert np.array_equal(a,zero),'Saved A and zero-strength B screenshots differ'
def metrics(b,box):
    x0,y0,x1,y1=box;x=a[y0:y1,x0:x1];y=b[y0:y1,x0:x1];d=y-x
    return {'rect_top_left':box,'mean_abs_channel_delta_0_255':float(abs(d).mean()*255),
            'max_abs_channel_delta_0_255':float(abs(d).max()*255),
            'mean_srgb_change_percent':float((y.mean()-x.mean())/x.mean()*100),
            'changed_pixels':int(np.any(abs(d)>1e-7,axis=2).sum())}
rois={'room':[83,155,817,480],'table_chair_floor':[155,380,345,475],
      'cabinet_floor':[355,420,740,470],'upper_wall':[300,157,540,190]}
report={'resolution':[900,600],'saved_zero_A_exact_pixel_match':True,
        'half':{name:metrics(half,box) for name,box in rois.items()},
        'full':{name:metrics(full,box) for name,box in rois.items()},
        'new_near_black_pixels_half':int(((half.max(2)<8/255)&(a.max(2)>32/255)).sum()),
        'new_near_black_pixels_full':int(((full.max(2)<8/255)&(a.max(2)>32/255)).sum()),
        'interpretation':'AO is technically working but subtle; no strong overall visual improvement is claimed.',
        'measure':'Display sRGB pixel differences, not a photometric brightness or aesthetic score.'}
(run/'reports/screenshot-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
delta=np.minimum(abs(a-half)*8,1)[::-1]
rgba=np.ones((600,900,4),np.float32);rgba[:,:,:3]=delta
im=bpy.data.images.new('AO_DIFFERENCE_X8',width=900,height=600,alpha=True)
im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.ravel());im.update()
im.filepath_raw=str(run/'renders/meal-ao-difference-x8.png');im.file_format='PNG';im.save()
print(json.dumps(report,ensure_ascii=False),flush=True)
