"""Remove only the eight legacy baked-light images in a separate .blend copy.
Run: blender --background SOURCE.blend --python clean_legacy_lightmaps.py -- OUTPUT.blend
"""
import bpy, sys, json
from pathlib import Path

cats=['studyWork','sleep','meal','home','commute','outdoor','social','entertainment']
legacy={'LM_'+c for c in cats}
args=sys.argv[sys.argv.index('--')+1:]
target=Path(args[0])
if target.resolve()==Path(bpy.data.filepath).resolve():
    raise RuntimeError('Output must be different from source')
before={o.name:[u.name for u in o.data.uv_layers] for o in bpy.data.objects if o.type=='MESH'}
changes=[]
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    nodes=mat.node_tree.nodes
    for node in list(nodes):
        if node.type!='TEX_IMAGE' or not node.image or node.image.name not in legacy:continue
        destinations=[]
        for output in node.outputs:
            for link in list(output.links):
                destinations.append(link.to_node.name+':'+link.to_socket.name)
                # Restore the socket's authored constant; do not zero actual lamp materials.
                mat.node_tree.links.remove(link)
        changes.append({'material':mat.name,'image':node.image.name,'destinations':destinations})
        nodes.remove(node)
for image in list(bpy.data.images):
    if image.name in legacy:
        bpy.data.images.remove(image,do_unlink=True)
assert before=={o.name:[u.name for u in o.data.uv_layers] for o in bpy.data.objects if o.type=='MESH'}
target.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(target))
report={'output':str(target),'removed_image_nodes':changes,'uv_names_preserved':True,'objects':len(bpy.data.objects)}
target.with_suffix('.cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('CLEANED_LEGACY_LIGHTMAPS',len(changes),str(target))
