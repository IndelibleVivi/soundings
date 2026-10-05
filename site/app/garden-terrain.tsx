import { useRef, useState, type CSSProperties, type PointerEvent } from 'react';
import { Compass, Maximize2, MousePointer2, Pause, Play, X } from 'lucide-react';
import { MethodGlyph } from './garden-architecture';
import { assetUrl } from '@/lib/base';

const places = [
  { id: 'search', name: '访求', english: 'Search', x: 23.5, y: 57, landmark: ['向外的门', 'The outward gate'], question: ['事实还在材料之外？', 'Need evidence from outside?'], action: ['推窗，读到完整条件', 'Open the source window'], path: 'M 112 783 C 156 754 195 721 225 698 L 357 594' },
  { id: 'study', name: '会通', english: 'Study', x: 49, y: 23, landmark: ['对读的书斋', 'The reading gallery'], question: ['找到了，为何仍然用错？', 'Found, but still misunderstood?'], action: ['找出名字消失的位置', 'Find where the name was lost'], path: 'M 582 289 L 884 215 M 605 268 L 899 198 M 626 247 L 911 182' },
  { id: 'explore', name: '营造', english: 'Explore', x: 78, y: 36, landmark: ['继续生长的廊', 'The branching corridor'], question: ['想法还能怎样展开？', 'Where could this idea lead?'], action: ['进入营造，试着改变路线', 'Enter Explore. Try changing the route.'], path: 'M 1020 426 C 1040 413 1110 433 1168 391 C 1200 372 1199 328 1184 311 C 1200 286 1238 272 1280 257 L 1360 251' },
  { id: 'shape', name: '辨定', english: 'Shape', x: 68.5, y: 63, landmark: ['试看与采用之间', 'The threshold of a decision'], question: ['做出来，却偏离了原意？', 'Does the work feel off course?'], action: ['在门前试看一个纠正', 'Try a correction at the threshold'], path: 'M 1169 787 L 1043 738 L 1073 681 L 1071 634' },
];

export function GardenTerrain({ zh, onEnter }: { zh: boolean; onEnter: (id: string) => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [still, setStill] = useState(false);
  const world = useRef<HTMLDivElement>(null);
  const current = places.find(p => p.id === selected);
  function look(event: PointerEvent<HTMLElement>) {
    if (still || event.pointerType !== 'mouse' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const rect = event.currentTarget.getBoundingClientRect();
    world.current?.style.setProperty('--drift-x', ((event.clientX - rect.left) / rect.width - .5) * 12 + 'px');
    world.current?.style.setProperty('--drift-y', ((event.clientY - rect.top) / rect.height - .5) * 7 + 'px');
  }
  function resetMotion() {
    world.current?.style.setProperty('--drift-x', '0px');
    world.current?.style.setProperty('--drift-y', '0px');
  }
  const camera = {
    '--focus-x': (current?.x ?? 50) + '%', '--focus-y': (current?.y ?? 50) + '%',
    '--mobile-pan-x': current ? ((50 - current.x) * 1.75) + '%' : '0%',
    '--mobile-pan-y': current ? ((50 - current.y) * 1.75) + '%' : '0%',
  } as CSSProperties;

  return <section className={'terrain-hero' + (current ? ' terrain-focused focus-' + current.id : '') + (still ? ' terrain-still' : '')} id="top" aria-labelledby="hero-title" onPointerMove={look} onPointerLeave={resetMotion}>
    <div className="terrain-margin-note" aria-hidden="true"><span>见地</span><i /><span>A GARDEN OF INQUIRY</span></div>
    <div className="terrain-headline">
      <p className="terrain-kicker">{zh ? '见地 · 与你的 agent 一起探问' : 'SOUNDINGS · INQUIRY WITH YOUR AGENT'}</p>
      <h1 id="hero-title">{zh ? <><span>于未明处，</span><span>渐见其地。</span></> : <><span>A little further,</span><span>a new way <br />through.</span></>}</h1>
      <p className="terrain-translation">{zh ? 'A little further, a new way through.' : '于未明处，渐见其地。'}</p>
    </div>
    <div className="terrain-canvas" aria-label={zh ? '可探索的园林地形图' : 'An explorable garden terrain'}>
      <div className="terrain-world" ref={world} style={camera}>
        <img className="terrain-painting" src={assetUrl('assets/garden-terrain-r4.webp')} width="1536" height="1024" fetchPriority="high" alt={zh ? '斜俯视的一园清水。书页接入门外的路，书斋在后，曲廊向右伸展，前院以月门相隔。白花与树叶疏落在浅浅的地层上。' : 'A garden seen from above: an open book becomes a path through the entrance, a reading gallery stands at the back, a curved corridor extends over water, and a moon gate divides the front court.'} />
        <svg className="terrain-traces" viewBox="0 0 1536 1024" fill="none" aria-hidden="true">
          <g className="terrain-water-movement"><ellipse cx="673" cy="596" rx="29" ry="10" /><ellipse cx="673" cy="596" rx="52" ry="17" /><ellipse cx="933" cy="425" rx="28" ry="9" /></g>
          {current && <path className={'terrain-active-trace trace-' + current.id} d={current.path} key={current.id} />}
        </svg>
        {places.map(place => <button key={place.id} className={'terrain-landmark landmark-' + place.id + (selected === place.id ? ' is-selected' : '')} style={{left:place.x + '%',top:place.y + '%'} as CSSProperties} onClick={() => setSelected(selected === place.id ? null : place.id)} aria-pressed={selected === place.id} aria-label={(zh ? '走近' + place.name + ' · ' + place.landmark[0] : 'Look closer: ' + place.english + ' · ' + place.landmark[1])}>
          <span className="landmark-target" aria-hidden="true"><i /></span><span className="landmark-name"><span>{place.name}</span><small>{place.english}</small></span>
        </button>)}
      </div>
    </div>
    <div className="terrain-intro">
      {current ? <div className="terrain-place-note" key={current.id}><span className="terrain-place-kind">{current.landmark[zh ? 0 : 1]}</span><h2>{current.question[zh ? 0 : 1]}</h2><button className="terrain-enter" onClick={() => onEnter(current.id)}><MethodGlyph method={current.id} /><span>{current.action[zh ? 0 : 1]}</span></button><button className="terrain-return" onClick={() => setSelected(null)}><X size={14} />{zh ? '回看全园' : 'Back to the garden'}</button></div> : <><p>{zh ? '一份材料，一处疑问，或一个尚未成形的念头。沿着它，走得更远一点。' : 'A piece of material. An open question. An idea still taking shape. Follow it a little further.'}</p><a className="terrain-enter" href="#methods"><span className="tiny-door" aria-hidden="true"><i /></span><span>{zh ? '入园，走一走' : 'Step into the garden'}</span></a><span className="terrain-product">{zh ? '四个独立 skill · 随处开始' : 'Four independent skills · Begin anywhere'}</span></>}
    </div>
    <div className="terrain-tools"><button onClick={() => setSelected(null)} disabled={!selected}><Maximize2 size={15} />{zh ? '全园' : 'Overview'}</button><button aria-pressed={still} onClick={() => {setStill(!still);resetMotion();}}>{still ? <Play size={14} /> : <Pause size={14} />}{still ? (zh ? '游观' : 'Motion') : (zh ? '静观' : 'Still view')}</button></div>
    <div className="terrain-compass" aria-hidden="true"><Compass strokeWidth={1} /><span>{zh ? '一园 · 四境' : 'ONE GARDEN'}</span></div>
    <div className="terrain-foot">
      <span className="terrain-hint"><MousePointer2 size={15} aria-hidden="true" />{zh ? '点园中题签，走近一处。' : 'Select a place to look closer.'}</span>
      <nav aria-label={zh ? '园中四处' : 'Four places in the garden'}>{places.map(place => <button key={place.id} onClick={() => setSelected(place.id)} aria-pressed={selected === place.id}><span>{zh ? place.name : place.english}</span><small>{zh ? place.english : place.name}</small></button>)}</nav>
    </div>
  </section>;
}
