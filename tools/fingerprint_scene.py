import bpy, hashlib, json, struct
h=hashlib.sha256()
for o in sorted(bpy.data.objects,key=lambda x:x.name):
    h.update(json.dumps([o.name,o.type,o.parent.name if o.parent else None,list(o.matrix_basis),[c.name for c in o.users_collection]],default=list).encode())
    if o.type=='MESH':
        h.update(o.data.name.encode())
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for p in o.data.polygons:h.update(struct.pack('<%di'%len(p.vertices),*p.vertices))
        for uv in o.data.uv_layers:
            h.update(uv.name.encode())
            for v in uv.data:h.update(struct.pack('<2f',*v.uv))
lights=[(o.name,o.data.type,o.data.energy,list(o.data.color)) for o in bpy.data.objects if o.type=='LIGHT']
print('SCENE_FINGERPRINT',h.hexdigest(),'LIGHTS',hashlib.sha256(json.dumps(sorted(lights)).encode()).hexdigest())
