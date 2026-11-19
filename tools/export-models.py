"""blender --background --python tools/export-models.py [-- --blend FILE --out DIR]"""
import argparse,sys,json,bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--blend',default=str(root/'assets/blender/meelo_unit_rooms_realtime-clean.blend'))
parser.add_argument('--out',default=str(root/'app/models'))
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path(args.blend).resolve()))
legacy={'LM_'+x for x in ['studyWork','sleep','meal','home','commute','outdoor','social','entertainment']}
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image and n.image.name in legacy and any(s.is_linked for s in n.outputs):
                raise RuntimeError('Legacy Lightmap connected: '+m.name+'. Clean a separate Blender copy first.')
if not (out/'rooms.json').exists():
    (out/'rooms.json').write_bytes((root/'assets/export/rooms-template.json').read_bytes())
script=(root/'assets/export/export-unit.py').read_text(encoding='utf-8-sig')
ns={};exec(compile(script,'export-unit.py','exec'),ns);ns['APP']=str(out)
report=[]
for cat in ['meal','sleep','studyWork','entertainment','commute','home','outdoor','social']:
    result=ns['export_unit'](cat);report.append(result);print('EXPORTED',result,flush=True)
(out/'export-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
