"""Independent read-only Blender verification of a prepared working copy."""
import bpy, json, pathlib, sys, hashlib, collections
import numpy as np

run=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
audit=json.loads((run/'reports/audit-original.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(run/'blends/prepared-eight-rooms.blend'))
checks={}
for room in ['meal','sleep','studyWork','entertainment','commute','home','outdoor','social']:
    names=[r['name'] for r in audit['objects'] if r['room']==room and r['role']=='static']
    for o in bpy.context.view_layer.objects:o.select_set(False)
    objs=[bpy.data.objects[n] for n in names]
    for o in objs:o.hide_set(False);o.hide_viewport=False;o.select_set(True);o.data.uv_layers.active=o.data.uv_layers['UV_Lightmap']
    bpy.context.view_layer.objects.active=objs[0]
    bpy.context.scene.tool_settings.use_uv_select_sync=False
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='DESELECT')
    bpy.ops.uv.select_overlap(extend=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    overlaps=[]
    for o in objs:
        uv=o.data.uv_layers['UV_Lightmap']
        selections=o.data.attributes.get('.uv_select_face')
        selected=sum(v.value for v in selections.data) if selections else 0
        if selected:overlaps.append({'object':o.name,'faces':selected})
    checks[room]={'blender_native_overlap_selected_faces':overlaps,'static_objects':len(objs)}
    print('NATIVE_OVERLAP',room,len(overlaps),flush=True)
(run/'reports/native-uv-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
if any(v['blender_native_overlap_selected_faces'] for v in checks.values()):
    # Blender also flags collapsed/zero-area bevel triangles. Resolve these
    # candidates with positive-area clipping rather than silently discarding them.
    exact_path=run/'reports/exact-uv-verification.json'
    if '--candidates-only' in sys.argv:
        print('NATIVE_CANDIDATES_RECORDED: run exact_overlap.py next',flush=True)
    elif not exact_path.exists():
        raise RuntimeError('Native UV candidates require exact_overlap.py follow-up')
    else:
        exact=json.loads(exact_path.read_text(encoding='utf8'))
        assert not any(v['positive_area_overlaps'] for v in exact.values())
        print('NATIVE_CANDIDATES_RESOLVED_BY_EXACT_CLIPPING: degenerate/subpixel bevel triangles; see exact report',flush=True)
