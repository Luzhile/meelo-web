const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const files=[];
function walk(dir){for(const item of fs.readdirSync(dir,{withFileTypes:true})){
  if(item.name==='.git'||(dir===root&&item.name==='dist'))continue;
  const p=path.join(dir,item.name);if(item.isDirectory())walk(p);
  else if(item.name!=='SHA256SUMS.json')files.push(p);
}}
walk(root);
const manifest=files.sort().map(p=>({file:path.relative(root,p).split(path.sep).join('/'),bytes:fs.statSync(p).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')}));
fs.writeFileSync(path.join(root,'SHA256SUMS.json'),JSON.stringify(manifest,null,2));
console.log('Manifest files:',manifest.length);
