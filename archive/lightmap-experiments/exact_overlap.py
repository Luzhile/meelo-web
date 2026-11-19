"""Check positive-area intersections for UV triangles flagged by Blender's native checker."""
import bpy,json,pathlib,sys,math,collections

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))))/2 if len(poly)>2 else 0
def intersect(a,b):
    if cross(*b)<0:b=list(reversed(b))
    poly=list(a)
    for i in range(3):
        e0,e1=b[i],b[(i+1)%3];new=[]
        if not poly:break
        for j,p in enumerate(poly):
            q=poly[(j+1)%len(poly)];cp,cq=cross(e0,e1,p),cross(e0,e1,q)
            if cp>=-1e-15:new.append(p)
            if (cp>0 and cq<0) or (cp<0 and cq>0):
                t=cp/(cp-cq);new.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
        poly=new
    return area(poly)

run=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(run/'blends/prepared-eight-rooms.blend'))
native=json.loads((run/'reports/native-uv-verification.json').read_text(encoding='utf8'))
report={}
for room,info in native.items():
    hits=[];zero_triangles=0;triangle_count=0;largest=0;collapsed_surface_area=0.;zero_geometry=0
    # Check all static triangles in a shared spatial grid, including cross-object overlaps.
    objs=[o for o in bpy.data.objects if o.type=='MESH' and o.get('lightmap_static') and o.get('lightmap_room')==room]
    triangles=[];grid=collections.defaultdict(list);seen=set()
    for o in objs:
        me=o.data;me.calc_loop_triangles();uv=me.uv_layers['UV_Lightmap']
        for tri in me.loop_triangles:
            pts=[tuple(uv.data[i].uv) for i in tri.loops];a=area(pts);triangle_count+=1
            if a<1e-14:
                zero_triangles+=1
                p0,p1,p2=[o.matrix_world@me.vertices[i].co for i in tri.vertices]
                surface=(p1-p0).cross(p2-p0).length/2
                collapsed_surface_area+=surface
                if surface<1e-12:zero_geometry+=1
                continue
            low=[max(0,min(63,math.floor(min(p[k] for p in pts)*64))) for k in [0,1]]
            high=[max(0,min(63,math.floor(max(p[k] for p in pts)*64))) for k in [0,1]]
            idx=len(triangles);triangles.append((o.name,tri.polygon_index,pts))
            candidates=set()
            for y in range(low[1],high[1]+1):
                for x in range(low[0],high[0]+1):candidates.update(grid[x,y]);grid[x,y].append(idx)
            for other in candidates:
                name,face,points=triangles[other]
                if name==o.name and face==tri.polygon_index:continue
                overlap=intersect(pts,points)
                if overlap>1e-12:
                    largest=max(largest,overlap)
                    if len(hits)<100:hits.append({'a':[o.name,tri.polygon_index],'b':[name,face],'uv_area':overlap})
    report[room]={'positive_area_overlaps':hits,'largest_uv_overlap_area':largest,'zero_area_triangles':zero_triangles,'triangles':triangle_count,'epsilon_uv_area':1e-12,'collapsed_uv_surface_area':collapsed_surface_area,'zero_geometry_triangles':zero_geometry}
    print('EXACT_OVERLAP',room,len(hits),largest,zero_triangles,flush=True)
(run/'reports/exact-uv-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if any(v['positive_area_overlaps'] for v in report.values()):raise RuntimeError('Positive-area UV intersections found')
