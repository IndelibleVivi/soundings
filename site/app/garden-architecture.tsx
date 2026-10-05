import { useRef, useState } from 'react';
import { assetUrl } from '@/lib/base';

/* Line-drawing joinery: a few pen strokes and a wash of watercolor, never a
   dense or antiquarian ornament. Each mark has to earn its place as either a
   wall, an opening or a piece of working furniture. */
export function Lattice({ quiet = false }: { quiet?: boolean }) {
  return <svg viewBox="0 0 100 220" preserveAspectRatio="none" aria-hidden="true" className={'lattice-lines' + (quiet ? ' quiet' : '')}>
    <rect x="5" y="5" width="90" height="210" />
    <path d="M 12 12 H 88 V 208 H 12 Z M 12 47 H 88 M 12 174 H 88 M 28 12 V 47 M 72 12 V 47 M 28 174 V 208 M 72 174 V 208 M 50 12 V 47 M 50 174 V 208" />
    <path d="M 12 110 L 50 65 L 88 110 L 50 155 Z M 12 86 L 32 62 M 12 134 L 32 158 M 88 86 L 68 62 M 88 134 L 68 158 M 12 62 H 32 V 47 M 68 47 V 62 H 88 M 12 158 H 32 V 174 M 68 174 V 158 H 88" />
    <path d="M 35 110 L 50 92 L 65 110 L 50 128 Z" />
  </svg>;
}

/* Each method keeps a different working object: an open book read outside,
   two facing leaves read across, a route that grows, and two frames set
   beside each other. The same four forms appear in the garden painting. */
export function MethodGlyph({ method }: { method: string }) {
  return <svg viewBox="0 0 42 42" fill="none" aria-hidden="true" className="method-glyph">
    {method === 'search'
      ? <><path d="M 23 23 V 7 H 37 V 23 M 26 23 V 10 H 34 V 23" /><path d="M 4 27 Q 11 23 19 27 Q 26 23 34 27 V 36 Q 26 32 19 36 Q 11 32 4 36 Z M 19 27 V 36 M 21 24 L 28 18" /></>
      : method === 'study'
        ? <><path d="M 4 8 L 10 5 L 16 8 V 27 L 10 24 L 4 27 Z M 10 5 V 24 M 26 8 L 32 5 L 38 8 V 27 L 32 24 L 26 27 Z M 32 5 V 24" /><path d="M 12 31 H 30 M 16 27 V 35 M 26 27 V 35" /></>
        : method === 'explore'
          ? <><path d="M 5 34 V 14 M 14 34 V 14 M 23 34 V 14 M 3 14 L 12 6 L 25 14 M 5 11 H 22 M 5 34 H 25" /><path d="M 25 14 H 38 M 33 14 V 34 M 25 34 H 38 M 25 10 H 38" strokeDasharray="3 3" /></>
          : <><path d="M 2 35 V 8 H 40 V 35 Z M 20 13 L 24 15 V 35 L 20 33 Z" /><circle cx="11" cy="23" r="7" /><circle cx="31" cy="23" r="7" /></>}
  </svg>;
}

export function GardenPorch({ zh }: { zh: boolean }) {
  const [open, setOpen] = useState(true);
  const [still, setStill] = useState(false);
  const porch = useRef<HTMLDivElement>(null);
  function look(event: React.PointerEvent<HTMLDivElement>) {
    if (still || event.pointerType !== 'mouse' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const box = event.currentTarget.getBoundingClientRect();
    porch.current?.style.setProperty('--look', ((event.clientX - box.left) / box.width - .5) * 12 + 'px');
  }
  return <figure className={'porch-figure' + (open ? ' window-open' : '') + (still ? ' is-still' : '')}>
    <div ref={porch} className="garden-porch" onPointerMove={look} onPointerLeave={() => porch.current?.style.setProperty('--look', '0px')}>
      <div className="porch-horizon" aria-hidden="true" />
      <div className="far-wall" aria-hidden="true"><div className="far-wall-cap" /><div className="far-window"><Lattice quiet /></div></div>
      <div className="water-court" aria-hidden="true"><span /><span /><span /></div>
      <div className="garden-wall" aria-hidden="true"><span className="wall-title">{zh ? '小窗听枝' : 'A VIEW WITHIN'}</span></div>
      <div className="moon-window">
        <div className="window-view"><img src={assetUrl('assets/magnolia-bird-watercolor.webp')} width="1024" height="1536" alt={zh ? '疏朗水彩玉兰枝上，一只蓝灰色小鸟停在白花之间。' : 'A blue-grey songbird rests among white magnolias, drawn in airy watercolor.'} loading="lazy" /></div>
        <div className="moon-window-depth" aria-hidden="true" />
        <button className="moon-window-control" onClick={() => setOpen(!open)} aria-expanded={open} aria-label={open ? (zh ? '合上花窗' : 'Close the garden window') : (zh ? '推开花窗' : 'Open the garden window')}>
          <span className="moon-shutter shutter-left"><Lattice /><i /></span>
          <span className="moon-shutter shutter-right"><Lattice /><i /></span>
        </button>
      </div>
      <svg className="porch-eaves" viewBox="0 0 800 140" fill="none" aria-hidden="true">
        <path className="roof-plane" d="M 22 42 Q 52 62 158 66 L 721 25 Q 756 22 788 5 L 780 18 Q 755 39 718 42 L 158 84 Q 56 83 22 58 Z" />
        <path d="M 22 42 Q 52 62 158 66 L 721 25 Q 756 22 788 5 M 22 58 Q 62 78 160 78 L 724 36 Q 765 31 784 15 M 70 75 L 70 87 L 730 40 M 70 94 L 730 47 M 85 86 V 113 H 107 V 99 M 647 48 V 74 H 667 V 57" />
        {Array.from({length: 26}, (_,i) => <path key={i} d={'M ' + (160 + i*21) + ' ' + (66-i*1.54) + ' l 7 10'} />)}
        <path d="M 108 90 L 134 114 M 617 64 L 648 88 M 129 113 H 139 M 644 87 H 655" />
      </svg>
      <div className="porch-post near-post" aria-hidden="true"><i /><span /></div><div className="porch-post side-post" aria-hidden="true"><i /><span /></div>
      <div className="porch-walk" aria-hidden="true"><div /><span /><i /></div>
      <div className="porch-step step-one" aria-hidden="true" /><div className="porch-step step-two" aria-hidden="true" />
      <span className="porch-inscription" aria-hidden="true">{zh ? '有风过处，便有来路。' : 'ROOM FOR WHAT COMES NEXT.'}</span>
    </div>
    <figcaption className="porch-caption"><div><span className="caption-dot" /><span>{zh ? '借一扇窗，见一处天地。' : 'A window opens onto another possibility.'}</span></div><div><button onClick={() => setOpen(!open)}>{open ? (zh ? '合扇' : 'Close window') : (zh ? '开窗' : 'Open window')}</button><button className="still-control" onClick={() => setStill(!still)} aria-pressed={still}>{still ? (zh ? '随目而移' : 'Enable parallax') : (zh ? '静观' : 'Still view')}</button></div></figcaption>
  </figure>;
}
