import bpy, json, collections, math

mesh_objects=[o for o in bpy.data.objects if o.type=='MESH']
uv_counts=collections.Counter()
uv_names=collections.Counter()
bad=[]
for o in mesh_objects:
    uv_counts[len(o.data.uv_layers)]+=1
    for layer in o.data.uv_layers:
        uv_names[layer.name]+=1
        if any(not math.isfinite(v) for loop in layer.data for v in loop.uv):
            bad.append(o.name+':'+layer.name)
rooms={}
for cat in ['studyWork','sleep','meal','home','commute','outdoor','social','entertainment']:
    unit=bpy.data.objects.get('Unit_'+cat)
    def old(o):
        p=o
        while p:
            if p.get('meelo_old'):return True
            p=p.parent
        return any(c.name.startswith('旧家具_') for c in o.users_collection)
    objs=[o for o in unit.children_recursive if o.type=='MESH' and not o.hide_render and not old(o)] if unit else []
    rooms[cat]={'meshes':len(objs),'no_uv':sum(not len(o.data.uv_layers) for o in objs),
      'uv_names':dict(collections.Counter(u.name for o in objs for u in o.data.uv_layers)),
      'lightmap_uv_objects':[o.name for o in objs if o.data.uv_layers.get('UV_Lightmap')]}
images=[{'name':i.name,'path':i.filepath,'size':list(i.size)} for i in bpy.data.images]
links=[]
for m in bpy.data.materials:
    if not m.use_nodes:continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image and n.outputs[0].is_linked:
            links.append({'material':m.name,'image':n.image.name,'destinations':[l.to_socket.name for s in n.outputs for l in s.links]})
print('UV_AUDIT_JSON '+json.dumps({'blend':bpy.data.filepath,'mesh_objects':len(mesh_objects),
 'uv_counts':dict(uv_counts),'uv_names':dict(uv_names),'nonfinite_uv':bad,'rooms':rooms,
 'images':images,'linked_image_nodes':links,
 'pipeline_material_names':[m.name for m in bpy.data.materials if any(x in m.name for x in ['__LM','LM_','__meal','__study','BAKE','AO_'])]},ensure_ascii=False))
