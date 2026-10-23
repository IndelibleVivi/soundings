(async()=>{
const sources=await (await fetch('sources.json')).json();
for(const source of sources){const article=document.createElement('article');article.textContent=source.title+' — '+source.text;document.querySelector('#sources').append(article)}
document.querySelector('#export').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([document.querySelector('#argument').value]));a.download='argument.txt';a.click()};

})().catch(error=>{console.error(error);throw error});
