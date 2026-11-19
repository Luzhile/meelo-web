import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';
const run=path.resolve(process.argv[2]),base=path.resolve('lightmap-pipeline');
const read=p=>JSON.parse(fs.readFileSync(path.join(run,p),'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex').toUpperCase();
const results=[];const check=(name,fn)=>{try{results.push({name,pass:true,detail:fn()});}catch(e){results.push({name,pass:false,error:String(e)});}};
const local=path.join(run,'reports/protected-inputs.json');
check('Production app/models, original source, prepared asset and complete study archive unchanged',()=>{
  let files;
  if(fs.existsSync(local))files=JSON.parse(fs.readFileSync(local,'utf8').replace(/^\uFEFF/,''));
  else files=['production-protected-before-ao.json','study-04-protected-before-ao.json','study-viewer-protected-before-ao.json'].flatMap(f=>JSON.parse(fs.readFileSync(path.join(base,f),'utf8').replace(/^\uFEFF/,'')));
  for(const file of files)assert.equal(hash(file.Path),file.Hash,file.Path);return files.length;
});
const result=read('reports/ao-result.json'),asset=read('reports/saved-asset-verification.json'),provenance=read('reports/provenance.json');
check('Prepared input and its new snapshot are byte-identical',()=>{assert.equal(hash(provenance.prepared),provenance.prepared_sha256.toUpperCase());assert.equal(hash(provenance.input_snapshot),provenance.prepared_sha256.toUpperCase());return true;});
check('All eight rooms UV coordinate hashes, layer names and mesh parents retained',()=>{const a=read('reports/input-uv-state.json'),b=read('reports/output-uv-state.json');assert.deepEqual(a,b);assert(asset.all_prepared_mesh_uvs_and_parents_match);return Object.keys(a).length;});
check('AO bake only: 1024, 8–16px margin, finite bounded data, explicit distance and UV',()=>{
  assert.equal(result.bake_type,'AO');assert.equal(result.room,'meal');assert.equal(result.resolution,1024);assert(result.margin>=8&&result.margin<=16);
  assert.equal(result.direct_pass,false);assert.equal(result.indirect_pass,false);assert.equal(result.color_pass,false);assert.equal(result.uv_regenerated,false);
  assert(result.distance>0&&result.distance<=.5);assert.equal(result.uv_layer_explicit,'UV_Lightmap');assert(result.global_min>=0&&result.global_max<=1);assert(result.surface_min<.99&&result.surface_p95>.5);return {samples:result.samples,distance:result.distance,margin:result.margin};
});
check('Old image blocks preserved; no legacy Lightmap participates or feeds source shading',()=>{
  assert(asset.old_packed_images_unchanged>=8);assert.equal(asset.old_lightmaps_on_participating_materials,0);assert(asset.ao_target_not_connected_to_source_shading);assert(result.material_defaults_unchanged);return asset.old_packed_images_unchanged;
});
check('AO PNG is non-color data, not AgX / base-color baked output',()=>{
  assert(asset.texture_is_non_color_numeric_data);assert(asset.png_exr_max_numeric_error<=1/255+.00001);return asset.png_exr_max_numeric_error;
});
check('Actual exported GLB has real AO textures on secondary UVs and none on dynamics',()=>{
  const b=fs.readFileSync(path.join(run,'assets/meal.glb'));assert.equal(b.toString('ascii',0,4),'glTF');assert.equal(b.readUInt32LE(8),b.length);
  const g=JSON.parse(b.toString('utf8',20,20+b.readUInt32LE(12)));let staticCount=0,dynamicCount=0,primitives=0;
  for(const n of g.nodes){if(n.mesh==null)continue;const isStatic=n.extras?.is_static_ao===true;if(isStatic)staticCount++;else dynamicCount++;
    assert(!n.extras?.is_static_lightmap,n.name);
    for(const p of g.meshes[n.mesh].primitives){const m=g.materials[p.material];if(isStatic){const ch=m.occlusionTexture?.texCoord??0;assert(ch>=1,n.name);assert(p.attributes[`TEXCOORD_${ch}`]!=null,n.name);assert.equal(m.extras?.roomAO,'meal');primitives++;}else assert(!m.occlusionTexture,n.name);}}
  assert.equal(staticCount,result.static_objects);assert.equal(dynamicCount,result.excluded_dynamic_objects);
  const aliases=g.nodes.map(n=>n.extras?.interaction_alias);for(const a of ['CAT_main','I_meal_FridgeDoor','I_meal_PotLid','I_meal_tap'])assert(aliases.includes(a),a);
  const audit=read('reports/prepared-asset-audit.json');const expected=audit.objects.filter(o=>o.room==='meal'&&(o.role==='static'||o.role.startsWith('dynamic')));
  const actual=new Set(g.nodes.filter(n=>n.mesh!=null).map(n=>n.extras.source_object));for(const o of expected)assert(actual.has(o.name),o.name);
  return {staticCount,dynamicCount,primitives};
});
const browserFile=path.join(run,'reports/browser-ab-validation.json');
if(fs.existsSync(browserFile)){
  const browser=read('reports/browser-ab-validation.json');
  check('Browser binding: uv1, NoColorSpace, no Lightmap or load errors',()=>{assert(browser.state.errors.length===0&&browser.state.uvErrors.length===0);assert.equal(browser.state.lightMapCount,0);assert(browser.bindings.every(b=>b.channel===1&&b.colorSpace===''&&b.flipY===false));return browser.bindings.length;});
  check('Strict A/B invariants and zero-strength pixel equivalence',()=>{assert(browser.checks.abOnlyAOChanges);assert(browser.checks.cmfCameraLightsBackgroundAndModelsUnchanged);assert.equal(browser.checks.aVsAOZero.differingPixels,0);assert.equal(browser.checks.aVsAOZero.maxChannelDifference,0);return browser.checks.aVsAOZero.totalPixels;});
  check('AO slider has a measurable, monotonic effect without raising lights/exposure',()=>{assert(browser.checks.aVsAOHalf.differingPixels>0);assert(browser.checks.aVsAOFull.meanAbsoluteChannelDifference>browser.checks.aVsAOHalf.meanAbsoluteChannelDifference);assert(browser.checks.aVsAOHalf.brightnessChangePercent<=0&&browser.checks.aVsAOHalf.brightnessChangePercent>-.5);return browser.checks.aVsAOHalf;});
}
fs.writeFileSync(path.join(run,'reports/independent-ao-verification.json'),JSON.stringify(results,null,2));
for(const c of results)console.log(`${c.pass?'PASS':'FAIL'} ${c.name}${c.pass?'':': '+c.error}`);
if(results.some(c=>!c.pass))process.exitCode=1;
