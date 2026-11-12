const { chromium } = require('playwright');const http=require('http'),path=require('path'),fs=require('fs');
const MIME={'.html':'text/html','.js':'text/javascript','.json':'application/json'};
(async()=>{const [html,...ts]=process.argv.slice(2);const srv=http.createServer((q,r)=>{const f=path.join(process.cwd(),decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end()}r.writeHead(200,{'Content-Type':MIME[path.extname(f)]||'application/octet-stream'});r.end(d)})}).listen(0);
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});const pg=await b.newPage({viewport:{width:1080,height:1920}});
pg.on('pageerror',e=>console.log('EXC',e.message));pg.on('console',m=>{if(m.type()==='error')console.log('C',m.text())});
await pg.goto(`http://localhost:${srv.address().port}/${html}`);await pg.waitForFunction(()=>window.ready===true,null,{timeout:60000});
for(const t of ts){await pg.evaluate(x=>setT(x),Number(t));await pg.screenshot({path:`s_${t}.png`});}
await b.close();srv.close();})();
