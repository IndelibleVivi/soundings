import { useRef, useState, type CSSProperties, type PointerEvent } from 'react';
import { Compass, Maximize2, MousePointer2, Pause, Play, X } from 'lucide-react';
import { MethodGlyph } from './garden-architecture';
import { assetUrl } from '@/lib/base';

/* Hotspots are calibrated against the r5 painting (1536x1024). Each place
   names the structure it points to and the working semantic that structure
   carries, so the garden and the four method panels stay the same place. */
const places = [
  {
    id: 'search', name: '访求', english: 'Search', x: 22, y: 58,
    landmark: ['门外展开的书', 'The open book outside the gate'],
    question: ['证据在材料之外？', 'Need evidence from beyond?'],
    action: ['出园，读回完整条件', 'Go outward, read the conditions back'],
    path: 'M 150 806 C 214 782 259 748 296 706 L 336 596'
  },
  {
    id: 'study', name: '会通', english: 'Study', x: 44, y: 28,
    landmark: ['对读的两座书斋', 'Two facing reading galleries'],
    question: ['对读，何处仍不相通？', 'Read across — where do they still not meet?'],
    action: ['对读材料，追到关系', 'Read across the material and trace the relationship'],
    path: 'M 548 250 L 576 286 L 704 322 L 805 298'
  },
  {
    id: 'explore', name: '营造', english: 'Explore', x: 84, y: 34,
    landmark: ['生长的花架与未来的印子', 'A growing pergola and its sketched extension'],
    question: ['这里还能长出什么？', 'What could still grow here?'],
    action: ['沿着铅笔线，再造一段', 'Follow the pencilled line and build on'],
    path: 'M 1310 300 C 1350 274 1388 250 1404 214 M 1300 336 C 1331 345 1361 353 1390 348'
  },
  {
    id: 'shape', name: '辨定', english: 'Shape', x: 77, y: 66,
    landmark: ['两孔月洞与可移的屏', 'Twin moon apertures and a movable screen'],
    question: ['两处所见，差在哪里？', 'Two framed views — where is the difference?'],
    action: ['并置两解，再定其一', 'Set the alternatives together, then decide'],
    path: 'M 1144 664 L 1237 617 M 1122 704 L 1240 664'
  },
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
        <img className="terrain-painting" src={assetUrl('assets/garden-watercolor-r5.webp')} width="1536" height="1024" fetchPriority="high" alt={zh ? '一幅淡水彩的斜俯园林：园外一本摊开的书铺成入门石径，两座书斋在水上相对而读，一段木廊架向右生长，末端停在铅笔勾出的未成之架上；前院白墙并开两孔月洞，各取一景。' : 'A watercolor garden in oblique view: an open book outside the gate becomes a stepping-stone path in; two facing reading galleries sit across the water; a timber pergola grows to the right, its far end sketched in pencil; the front wall opens two circular apertures onto different views.'} />
        <svg className="terrain-traces" viewBox="0 0 1536 1024" fill="none" aria-hidden="true">
          <g className="terrain-water-movement"><ellipse cx="700" cy="560" rx="30" ry="10" /><ellipse cx="700" cy="560" rx="54" ry="18" /><ellipse cx="980" cy="470" rx="26" ry="9" /></g>
          {current && <path className={'terrain-active-trace trace-' + current.id} d={current.path} key={current.id} />}
        </svg>
        {places.map(place => <button key={place.id} className={'terrain-landmark landmark-' + place.id + (selected === place.id ? ' is-selected' : '')} style={{ left: place.x + '%', top: place.y + '%' } as CSSProperties} onClick={() => setSelected(selected === place.id ? null : place.id)} aria-pressed={selected === place.id} aria-label={(zh ? '走近' + place.name + ' · ' + place.landmark[0] : 'Look closer: ' + place.english + ' · ' + place.landmark[1])}>
          <span className="landmark-target" aria-hidden="true"><i /></span><span className="landmark-name"><span>{place.name}</span><small>{place.english}</small></span>
        </button>)}
      </div>
    </div>
    <div className="terrain-intro">
      {current ? <div className="terrain-place-note" key={current.id}><span className="terrain-place-kind">{current.landmark[zh ? 0 : 1]}</span><h2>{current.question[zh ? 0 : 1]}</h2><button className="terrain-enter" onClick={() => onEnter(current.id)}><MethodGlyph method={current.id} /><span>{current.action[zh ? 0 : 1]}</span></button><button className="terrain-return" onClick={() => setSelected(null)}><X size={14} />{zh ? '回看全园' : 'Back to the garden'}</button></div> : <><p>{zh ? '一份材料，一处疑问，或一个尚未成形的念头。沿着它，走得更远一点。' : 'A piece of material. An open question. An idea still taking shape. Follow it a little further.'}</p><a className="terrain-enter" href="#methods"><span className="tiny-door" aria-hidden="true"><i /></span><span>{zh ? '入园，走一走' : 'Step into the garden'}</span></a><span className="terrain-product">{zh ? '四个独立 skill · 随处开始' : 'Four independent skills · Begin anywhere'}</span></>}
    </div>
    <div className="terrain-tools"><button onClick={() => setSelected(null)} disabled={!selected}><Maximize2 size={15} />{zh ? '全园' : 'Overview'}</button><button aria-pressed={still} onClick={() => { setStill(!still); resetMotion(); }}>{still ? <Play size={14} /> : <Pause size={14} />}{still ? (zh ? '游观' : 'Motion') : (zh ? '静观' : 'Still view')}</button></div>
    <div className="terrain-compass" aria-hidden="true"><Compass strokeWidth={1} /><span>{zh ? '一园 · 四境' : 'ONE GARDEN'}</span></div>
    <div className="terrain-foot">
      <span className="terrain-hint"><MousePointer2 size={15} aria-hidden="true" />{zh ? '点园中题签，走近一处。' : 'Select a place to look closer.'}</span>
      <nav aria-label={zh ? '园中四处' : 'Four places in the garden'}>{places.map(place => <button key={place.id} onClick={() => setSelected(place.id)} aria-pressed={selected === place.id}><span>{zh ? place.name : place.english}</span><small>{zh ? place.english : place.name}</small></button>)}</nav>
    </div>
  </section>;
}
