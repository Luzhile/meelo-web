const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const MIME = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.txt':'text/plain; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2','.glb':'model/gltf-binary','.wasm':'application/wasm','.ico':'image/x-icon'};
function startStaticServer(root, port=4173) {
  root=path.resolve(root);
  const server=http.createServer((req,res)=>{
    let file;
    try {
      const url=new URL(req.url,'http://localhost');
      const rel=decodeURIComponent(url.pathname);
      file=path.resolve(root,'.'+(rel.endsWith('/')?rel+'index.html':rel));
      if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end('Forbidden');return;}
    } catch {res.writeHead(400);res.end('Bad request');return;}
    fs.stat(file,(err,st)=>{
      if(err||!st.isFile()){res.writeHead(404);res.end('Not found');return;}
      res.writeHead(200,{'Content-Type':MIME[path.extname(file).toLowerCase()]||'application/octet-stream','Content-Length':st.size,'Cache-Control':'no-store'});
      if(req.method==='HEAD'){res.end();return;}
      const stream=fs.createReadStream(file);stream.on('error',()=>res.destroy());stream.pipe(res);
    });
  });
  return new Promise((resolve,reject)=>{
    server.once('error',reject);
    server.listen(port,'127.0.0.1',()=>resolve({server,url:`http://127.0.0.1:${server.address().port}/`}));
  });
}
module.exports={startStaticServer};
if(require.main===module){
  const root=path.resolve(__dirname,'..',process.argv[2]||'app');
  startStaticServer(root,Number(process.env.PORT||process.argv[3]||4173))
    .then(({url})=>console.log(`MEELO: ${url} (${root})`))
    .catch(err=>{console.error(err.message);process.exitCode=1;});
}
