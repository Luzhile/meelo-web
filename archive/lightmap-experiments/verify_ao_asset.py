"""Read-only verification of the saved meal AO working asset."""
import bpy,json,pathlib,sys,hashlib
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from meal_ao import uv_state,packed_image_state,material_defaults
import pipeline as shared
run=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(run/'blends/meal-ao-working.blend'))
before=json.loads((run/'reports/input-uv-state.json').read_text(encoding='utf8'))
assert uv_state()==before,'Saved working file changed prepared UVs/hierarchy'
images=json.loads((run/'reports/input-image-state.json').read_text(encoding='utf8'))
current=packed_image_state()
assert all(current[n]==v for n,v in images.items()),'Saved working file changed old packed images'
static=[o for o in bpy.data.objects if o.type=='MESH' and o.get('lightmap_room')=='meal' and o.get('lightmap_static')]
materials={s.material for o in static for s in o.material_slots if s.material}
for m in materials:
    assert shared.reachable_legacy(m.node_tree)==0,m.name
    target=m.node_tree.nodes.get('NEW_AO_TARGET')
    assert target and target.image.name=='NEW_AO_meal_1024'
    assert not target.outputs['Color'].links and not target.outputs['Alpha'].links,'AO target connected to source shading'
    assert m.node_tree.nodes.active==target,m.name
im=bpy.data.images.load(str(run/'assets/meal-ao.png'),check_existing=False);im.colorspace_settings.name='Non-Color'
png=np.array(im.pixels[:],np.float32).reshape(-1,4)
exr=bpy.data.images.load(str(run/'assets/meal-ao-linear.exr'),check_existing=False)
raw=np.array(exr.pixels[:],np.float32).reshape(-1,4)
diff=abs(png[:,:3]-raw[:,:3])
assert im.size[:]==(1024,1024)
assert np.isfinite(png).all() and png[:,:3].min()>=0 and png[:,:3].max()<=1
assert float(diff.max())<=1/255+.00001,'PNG contains an unexpected display transform'
result={'all_prepared_mesh_uvs_and_parents_match':True,'mesh_count':len(before),
        'old_packed_images_unchanged':len(images),'static_material_targets_checked':len(materials),
        'old_lightmaps_on_participating_materials':0,'ao_target_not_connected_to_source_shading':True,
        'saved_ao_distance':bpy.context.scene.world.light_settings.distance,
        'png_exr_max_numeric_error':float(diff.max()),'png_exr_mean_numeric_error':float(diff.mean()),
        'texture_is_non_color_numeric_data':True}
shared.write(run/'reports/saved-asset-verification.json',result)
print('AO_ASSET_CHECKS_PASS',json.dumps(result),flush=True)
