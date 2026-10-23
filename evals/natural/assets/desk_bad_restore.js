(async()=>{
const sources=await (await fetch('sources.json')).json();
const reopened=!!localStorage.getItem('desk')&&!sessionStorage.getItem('desk-session');sessionStorage.setItem('desk-session','1');
let state;try{state=JSON.parse(localStorage.getItem('desk'))}catch{}state=state||{argument:'',clips:[]};
if(reopened)state.clips=[];
const argument=document.querySelector('#argument');argument.value=state.argument;
function save(){state.argument=argument.value;localStorage.setItem('desk',JSON.stringify(state))}
function render(){document.querySelector('#sources').replaceChildren();for(const s of sources){const article=document.createElement('article');const text=document.createElement('p');text.textContent=s.title+' — '+s.author+' — '+s.text;article.append(text);const button=document.createElement('button');button.dataset.source=s.id;button.textContent='Use '+s.title;button.onclick=()=>{state.clips.push({...s});save();render()};article.append(button);document.querySelector('#sources').append(article)}let list=document.querySelector('#clips');if(!list){list=document.createElement('section');list.id='clips';document.querySelector('#sources').after(list)}list.replaceChildren();for(const c of state.clips){const p=document.createElement('p');p.textContent=c.title+' | '+c.author+' | '+c.url+' | '+c.text;list.append(p)}}
argument.oninput=save;render();document.querySelector('#export').onclick=()=>{save();const content=state.argument+'\n\n'+state.clips.map(c=>c.title+' | '+c.author+' | '+c.url+'\n'+c.text).join('\n\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([content],{type:'text/plain'}));a.download='argument.txt';a.click()};

})().catch(error=>{console.error(error);throw error});
