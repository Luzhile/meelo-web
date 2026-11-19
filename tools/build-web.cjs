const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'dist');
const input=path.join(root,'app');
if(!fs.existsSync(path.join(input,'index.html')))throw Error('Missing app/index.html');
fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(out,{recursive:true});
for(const name of ['index.html','models','vendor','fonts','board']){
  fs.cpSync(path.join(input,name),path.join(out,name),{recursive:true});
}
console.log('Web build complete: dist/');
