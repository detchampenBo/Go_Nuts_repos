import {outcome,bestDefence} from './rules.mjs';
const $=id=>document.getElementById(id), NS='http://www.w3.org/2000/svg';
const motionQuery=matchMedia('(prefers-reduced-motion: reduce)');
let missions=[], index=0, selected=new Set(), phase='loading', solution, lastResult, graphNodes=[], graphEdges=[], timer;
let reduced=motionQuery.matches;
function setMotion(value){reduced=value;document.body.classList.toggle('reduced',value);$('motion').setAttribute('aria-pressed',String(value));$('motion').textContent=value?'Motion reduced':'Reduce motion';}
setMotion(reduced);$('motion').addEventListener('click',()=>setMotion(!reduced));
motionQuery.addEventListener('change',e=>setMotion(e.matches));
function svg(tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
function shortName(name){return name.replace(/ \([^)]*\)/g,'');}
function start(){
 clearTimeout(timer);selected=new Set();phase='plan';lastResult=null;document.body.classList.remove('snapping','victory');
 const m=missions[index];solution=bestDefence(m);
 $('mission-count').textContent=`MISSION ${String(index+1).padStart(2,'0')} / 03`;
 $('mission-title').textContent=m.title;$('phase').textContent='PLAN YOUR DEFENCE';
 $('results').hidden=true;$('best-copy').textContent='';$('best').disabled=false;$('best').textContent='Show best defence';
 $('witch-line').textContent='I can protect three. You choose who matters.';
 $('thanos-line').textContent="You know my targets. It still won't be enough.";
 $('next').textContent=index===missions.length-1?'Back to mission 1 →':'Next mission →';
 $('network').replaceChildren();$('targets').replaceChildren();
 $('network').append(svg('title',{},`${m.title}: 24 articles, 10 targets. Choose shields using the buttons below.`));
 graphEdges=m.edges.map(([a,b])=>{const e=svg('line',{x1:m.nodes[a].x,y1:m.nodes[a].y,x2:m.nodes[b].x,y2:m.nodes[b].y,class:'edge'});$('network').append(e);return e;});
 graphNodes=m.nodes.map((n,i)=>{
  const g=svg('g',{class:`node${m.targets.includes(i)?' target':''}`,'data-node':i});
  g.append(svg('title',{},n.name+(m.targets.includes(i)?' — targeted':' — safe this round')));
  g.append(svg('circle',{cx:n.x,cy:n.y,r:23,class:'shield-ring'}));
  g.append(svg('circle',{cx:n.x,cy:n.y,r:12,class:'core'}));
  g.append(svg('text',{x:n.x,y:n.y+36,'text-anchor':'middle'},shortName(n.name)));
  g.addEventListener('click',()=>{if(m.targets.includes(i)) choose(i);else if(phase==='plan')$('status').textContent=`${n.name} is already safe. Shield an orange target.`;});
  $('network').append(g);return g;
 });
 for(const i of m.targets){const b=document.createElement('button');b.type='button';b.className='target-card';b.dataset.node=i;b.setAttribute('aria-pressed','false');b.setAttribute('aria-label',`Shield ${m.nodes[i].name}`);const tag=document.createElement('span');tag.textContent='TARGETED';b.append(tag,document.createTextNode(shortName(m.nodes[i].name)));b.addEventListener('click',()=>choose(i));$('targets').append(b);}
 update();
}
function choose(i){if(phase!=='plan')return;if(selected.has(i))selected.delete(i);else if(selected.size<3)selected.add(i);else{$('status').textContent='All three shields are placed. Unselect one to change your defence.';return;}update();}
function update(){
 const count=selected.size;$('shield-count').textContent=`${count} / 3 SELECTED`;$('snap').disabled=phase!=='plan'||count!==3;
 for(const b of $('targets').children){const active=selected.has(Number(b.dataset.node));b.setAttribute('aria-pressed',String(active));b.querySelector('span').textContent=active?'◉ SHIELDED':'TARGETED';b.disabled=phase!=='plan';}
 graphNodes.forEach((g,i)=>g.classList.toggle('shielded',selected.has(i)));
 $('status').textContent=count===3?'Your defence is ready. Seven targets will disappear.':`Place ${3-count} more shield${3-count===1?'':'s'} on the orange targets.`;
}
function finish(){
 const m=missions[index], result=outcome(m,[...selected]);lastResult=result;phase='result';
 const removed=new Set(result.removed), largest=new Set(result.components[0]);
 graphEdges.forEach((e,i)=>e.classList.toggle('removed',m.edges[i].some(n=>removed.has(n))));
 graphNodes.forEach((g,i)=>{g.classList.toggle('removed',removed.has(i));g.classList.toggle('outside',!removed.has(i)&&!largest.has(i));g.classList.toggle('largest',largest.has(i));});
 if(!reduced)for(const i of result.removed)for(let k=0;k<12;k++){
  const n=m.nodes[i],p=svg('rect',{x:n.x+(k%4)*5-8,y:n.y+Math.floor(k/4)*5-8,width:4,height:4,fill:k%2?'#ffb45f':'#d0b992',class:'dust'});
  p.style.setProperty('--dx',`${30+k*7}px`);p.style.setProperty('--dy',`${-25-k*6}px`);p.addEventListener('animationend',()=>p.remove(),{once:true});$('network').append(p);
 }
 const perfect=result.score===solution.score;document.body.classList.toggle('victory',perfect);
 $('phase').textContent='SNAP COMPLETE';$('results').hidden=false;
 $('result-kicker').textContent=perfect?'PERFECT DEFENCE':'THE UNIVERSE SURVIVED. MOSTLY.';
 $('result-title').textContent=`${result.score} / 17 survivors connected`;
 $('result-copy').textContent=`Your largest group has ${result.score} articles. ${17-result.score} survivors sit outside it. ${perfect?'You found an optimal defence.':'Try a different three shields, or reveal an optimal defence.'}`;
 $('witch-line').textContent=perfect?'Together. Every one of them.':`${result.score} stayed together. We can learn from this.`;
 $('thanos-line').textContent=perfect?'Impossible. You held them together.':'A shield is only as good as where you place it.';
 $('status').textContent='Snap complete. Your shield choices are locked for this result.';
 $('best').focus({preventScroll:true});
}
$('snap').addEventListener('click',()=>{if(phase!=='plan'||selected.size!==3)return;phase='snap';update();$('phase').textContent='THE SNAP';$('status').textContent='Thanos is snapping…';document.body.classList.add('snapping');timer=setTimeout(finish,reduced?0:650);});
$('retry').addEventListener('click',()=>{start();$('targets').firstElementChild.focus({preventScroll:true});});
$('next').addEventListener('click',()=>{index=(index+1)%missions.length;start();$('targets').firstElementChild.focus({preventScroll:true});});
$('best').addEventListener('click',()=>{
 if(phase!=='result')return;const m=missions[index],best=outcome(m,solution.shields),removed=new Set(best.removed),largest=new Set(best.components[0]);
 graphNodes.forEach((g,i)=>{g.classList.toggle('best',solution.shields.includes(i));g.classList.toggle('shielded',solution.shields.includes(i));g.classList.toggle('removed',removed.has(i));g.classList.toggle('outside',!removed.has(i)&&!largest.has(i));g.classList.toggle('largest',largest.has(i));});
 graphEdges.forEach((e,i)=>e.classList.toggle('removed',m.edges[i].some(n=>removed.has(n))));
 for(const b of $('targets').children)b.classList.toggle('best-choice',solution.shields.includes(Number(b.dataset.node)));
 $('phase').textContent='BEST DEFENCE REPLAY';$('result-kicker').textContent='YOUR SCORE ABOVE · BEST DEFENCE ON THE MAP';
 $('best-copy').textContent=`Best possible: ${solution.score}/17. Shield ${solution.shields.map(i=>shortName(m.nodes[i].name)).join(', ')}. The map now shows that outcome; your score remains ${lastResult.score}/17. Checked all 120 combinations; other choices may tie.`;
 $('best').disabled=true;
});
try{const response=await fetch('missions.json');if(!response.ok)throw new Error('Mission data unavailable');missions=await response.json();start();}
catch(error){$('mission-title').textContent='Mission unavailable';$('status').textContent='Could not load missions. Open this page through the local preview server and refresh.';console.error(error);}
