// Independent checks over actual outputs, not just pipeline completion flags.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const run=path.resolve(process.argv[2]);
const read=f=>JSON.parse(fs.readFileSync(path.join(run,f),'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex').toUpperCase();
const results=[];
function check(name,fn){try{const value=fn();results.push({name,pass:true,detail:value});}catch(e){results.push({name,pass:false,error:String(e)});}}
const provenance=read('reports/provenance.json');
check('Original source and byte-identical backup unchanged',()=>{
  assert.equal(hash(provenance.source),provenance.sha256.toUpperCase());
  assert.equal(hash(provenance.backup),provenance.sha256.toUpperCase());return provenance.sha256;
});
check('Production HTML and all production model files unchanged',()=>{
  const local=path.join(run,'reports/production-hashes-before.json');
  const protectedFiles=JSON.parse(fs.readFileSync(fs.existsSync(local)?local:new URL('./production-hashes-before.json',import.meta.url),'utf8').replace(/^\uFEFF/,''));
  for(const p of protectedFiles)assert.equal(hash(p.Path),p.Hash);return protectedFiles.length;
});
const before=read('reports/audit-original.json'),after=read('reports/audit-repaired.json');
check('All original mesh object names and parent names preserved',()=>{
  assert.deepEqual(after.objects.map(o=>[o.name,o.parent]).sort(),before.objects.map(o=>[o.name,o.parent]).sort());return before.objects.length;
});
check('Original UV layer names retained on all room meshes',()=>{
  const next=new Map(after.objects.map(o=>[o.name,o]));
  for(const o of before.objects){const n=next.get(o.name);for(const uv of o.uvs)assert(n.uvs.some(v=>v.name===uv.name),`${o.name}:${uv.name}`);}
  return true;
});
check('No materials shared across different active rooms after isolation',()=>{
  const unexpected=Object.entries(after.shared_between_rooms).filter(([name,users])=>new Set(users.filter(u=>u.role==='static'||u.role.startsWith('dynamic')).map(u=>u.room)).size>1);
  assert.equal(unexpected.length,0);return true;
});
check('New static UVs are room-wide, in bounds, no raster overlap',()=>{
  const rooms=['meal','sleep','studyWork','entertainment','commute','home','outdoor','social'];
  return rooms.map(room=>{const uv=read(`reports/uv-${room}.json`);assert.equal(uv.overlap_pixels,0);assert.equal(uv.out_of_bounds_objects.length,0);assert(uv.objects>0);return {room,objects:uv.objects,occupancy:uv.occupancy_ratio,margin:uv.actual_island_margin_pixels};});
});
check('Exact triangle clipping finds no positive-area overlap in all eight atlases',()=>{
  const exact=read('reports/exact-uv-verification.json');
  for(const [room,info] of Object.entries(exact))assert.equal(info.positive_area_overlaps.length,0,room);
  return Object.fromEntries(Object.entries(exact).map(([r,v])=>[r,{degenerateUVTriangles:v.zero_area_triangles,collapsedSurfaceArea:v.collapsed_uv_surface_area}]));
});
check('Original genuine emission defaults retained in copied active materials',()=>{
  let count=0;
  for(const [name,mat] of Object.entries(after.materials)){
    const original=name.replace(/__(meal|sleep|studyWork|entertainment|commute|home|outdoor|social)_(static|dynamic)$/, '');
    if(original===name||!before.materials[original]?.nodes)continue;
    const extract=nodes=>nodes.filter(n=>n.type==='BSDF_PRINCIPLED'||n.type==='EMISSION').map(({name,type,defaults})=>({name,type,defaults}));
    const a=extract(before.materials[original].nodes.nodes);
    const b=extract(mat.nodes.nodes);
    assert.deepEqual(b,a, name);count++;
  }return count;
});
check('Only studyWork baked; nonblack finite diffuse-only float output',()=>{
  const result=read('reports/result.json'),bake=read('reports/study-bake.json');
  assert.deepEqual(result.baked_rooms,['studyWork']);assert.equal(result.other_rooms_baked,false);
  assert.deepEqual(bake.passes,['DIRECT','INDIRECT']);assert.equal(bake.color_pass,false);
  assert.equal(bake.legacy_nodes_in_bake_materials,0);assert(bake.finite&&bake.pixel_max>.01);
  assert(fs.statSync(path.join(run,'assets/studyWork-lightmap.hdr')).size>1000);
  assert(fs.statSync(path.join(run,'assets/studyWork-lightmap.exr')).size>1000);return bake;
});
check('Actual GLB: every static primitive has secondary UV and its carrier references it',()=>{
  const b=fs.readFileSync(path.join(run,'assets/studyWork.glb'));
  assert.equal(b.toString('ascii',0,4),'glTF');assert.equal(b.readUInt32LE(8),b.length);
  const g=JSON.parse(b.toString('utf8',20,20+b.readUInt32LE(12)));let count=0;
  for(const node of g.nodes){if(!node.extras?.is_static_lightmap||node.mesh==null)continue;
    for(const p of g.meshes[node.mesh].primitives){const m=g.materials[p.material],ch=m.occlusionTexture?.texCoord??0;assert(ch>=1,node.name);assert(p.attributes[`TEXCOORD_${ch}`]!=null,node.name);count++;}}
  const sources=g.nodes.filter(n=>n.extras?.source_object).map(n=>n.extras.source_object);assert.equal(new Set(sources).size,sources.length);
  const activeSources=before.objects.filter(o=>o.room==='studyWork'&&(o.role==='static'||o.role.startsWith('dynamic'))).map(o=>o.name);
  for(const name of activeSources)assert(sources.includes(name),'Missing active/dynamic mesh: '+name);
  const expected=read('reports/gltf-validation.json');assert.equal(expected.missing_source_objects.length,0);return count;
});
fs.writeFileSync(path.join(run,'reports/independent-verification.json'),JSON.stringify(results,null,2));
for(const r of results)console.log(`${r.pass?'PASS':'FAIL'} ${r.name}${r.pass?'':': '+r.error}`);
if(results.some(r=>!r.pass))process.exitCode=1;
