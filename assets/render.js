const {chromium}=require('playwright');
(async()=>{const [,,html,out,dur]=process.argv;const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+html);await p.waitForTimeout(800);
const fps=30,n=Math.round(dur*fps);
for(let i=0;i<n;i++){const t=i*1000/fps;
 await p.evaluate(t=>{for(const a of document.getAnimations()){a.pause();a.currentTime=t;}},t);
 await p.screenshot({path:`${out}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:88});}
await b.close();})();
