import { useRef, useState } from 'react';
import { assetUrl } from '@/lib/base';

export function Lattice({ quiet = false }: { quiet?: boolean }) {
  return <svg viewBox="0 0 100 220" preserveAspectRatio="none" aria-hidden="true" className={'lattice-lines' + (quiet ? ' quiet' : '')}>
    <rect x="5" y="5" width="90" height="210" />
    <path d="M 12 12 H 88 V 208 H 12 Z M 12 47 H 88 M 12 174 H 88 M 28 12 V 47 M 72 12 V 47 M 28 174 V 208 M 72 174 V 208 M 50 12 V 47 M 50 174 V 208" />
    <path d="M 12 110 L 50 65 L 88 110 L 50 155 Z M 12 86 L 32 62 M 12 134 L 32 158 M 88 86 L 68 62 M 88 134 L 68 158 M 12 62 H 32 V 47 M 68 47 V 62 H 88 M 12 158 H 32 V 174 M 68 174 V 158 H 88" />
    <path d="M 35 110 L 50 92 L 65 110 L 50 128 Z" />
  </svg>;
}

export function MethodGlyph({ method }: { method: string }) {
  return <svg viewBox="0 0 42 42" fill="none" aria-hidden="true" className="method-glyph">
    {method === 'search' ? <><path d="M 7 35 V 10 Q 21 -2 35 10 V 35 M 11 35 V 12 Q 21 4 31 12 V 35 M 5 35 H 37" /><path d="M 13 15 L 20 18 V 34 L 13 31 Z M 29 15 L 22 18 V 34 L 29 31 Z" /></> : method === 'study' ? <><path d="M 5 8 L 16 5 L 27 8 L 38 5 V 34 L 27 37 L 16 34 L 5 37 Z M 16 5 V 34 M 27 8 V 37" /><path d="M 8 16 L 13 15 M 19 15 L 24 16 M 30 16 L 35 15 M 8 24 L 13 23 M 19 23 L 24 24 M 30 24 L 35 23" /></> : method === 'explore' ? <><path d="M 4 33 C 16 33 10 12 21 12 S 27 29 38 29 M 4 28 C 11 28 7 6 21 6 S 30 24 38 24 M 8 28 V 19 M 14 13 V 5 M 28 18 V 10 M 35 27 V 18" /><path d="M 6 17 C 15 17 11 1 21 1 S 28 16 38 16" /></> : <><path d="M 8 35 V 8 H 34 V 35 M 12 35 V 12 H 30 V 35 M 4 35 H 38 M 5 38 H 37" /><path d="M 13 13 L 21 17 V 34 L 13 31 Z M 24 23 H 28" /></>}
  </svg>;
}

export function BookWindow({ variant }: { variant: 'elsewhere' | 'evidence' }) {
  return <svg viewBox="0 0 56 74" aria-hidden="true">
    <path d="M3 70V28C3-2 53-2 53 28V70ZM7 66V29C7 4 49 4 49 29V66Z" />
    {variant === 'elsewhere' ? <>
      <path d="M8 43Q17 34 25 40T48 38M8 49Q19 43 28 49T48 45M9 58Q20 51 29 55T48 54M16 40V29M12 30Q16 22 21 30M35 39V24M29 27Q35 16 41 27M21 53Q29 46 38 51Q29 61 21 53ZM37 51L43 47V56Z" />
      <circle cx="31" cy="52" r=".7" /><path d="M12 62H22M31 63H44" />
    </> : <>
      <path d="M8 31H48M8 57H48M18 18V31M28 13V31M38 18V31M18 57V66M38 57V66M8 44L28 32L48 44L28 56Z M20 44L28 39L36 44L28 49Z" />
      <path d="M11 28H15M22 25H25M32 25H35M41 28H45" />
    </>}
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
        <div className="window-view"><img src={assetUrl('assets/flowering-bird-r3.webp')} width="1536" height="1024" alt={zh ? '淡墨疏枝上，一只小禽停在白花与嫩叶之间。' : 'A small bird rests among white blossoms and pale new leaves on a finely painted branch.'} fetchPriority="high" /></div>
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
