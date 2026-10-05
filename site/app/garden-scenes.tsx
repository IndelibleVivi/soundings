import { useEffect, useState } from 'react';
import { copyTextToClipboard } from '@/lib/copy-text';
import { BookOpen, Copy, Check, RotateCcw } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Lattice } from './garden-architecture';
import { StudyScene } from './study-evidence';

type Language = 'zh' | 'en';
const repo = 'https://github.com/IndelibleVivi/soundings';
function DemoHeading({ title, subtitle }: { title: string; subtitle: string }) { return <div className="demo-heading"><h4>{title}</h4><p>{subtitle}</p></div>; }
function DemoSource({ children, href }: { children: React.ReactNode; href: string }) { return <a className="demo-source" href={href} target="_blank" rel="noreferrer"><BookOpen size={14} />{children}</a>; }

function SearchScene({ zh }: { zh: boolean }) {
  const [representation, setRepresentation] = useState('object');
  const [expanded, setExpanded] = useState(false);
  const raw = representation === 'raw';
  return <div className={'skill-demo search-demo' + (expanded ? ' source-is-open' : '')}>
    <DemoHeading title={zh ? '窗外的依据，带着条件入内。' : 'Let the evidence in, with its conditions.'} subtitle={zh ? '动手开窗 · GitHub Contents API 的固定示例' : 'Open the window · A fixed GitHub Contents API example'} />
    <p className="question-line"><span>{zh ? '案上之问' : 'THE QUESTION'}</span>{zh ? '80 MB 的文件，能读到正文吗？' : 'Can we read the body of an 80 MB file?'}</p>
    <div className="search-chamber">
      <div className="source-wall">
        <div className="source-reveal"><span className="source-overline">{zh ? '窗外 · 官方文档' : 'OUTSIDE · THE SOURCE'}</span><div className="source-inside"><strong className="source-range">1–100 <small>MB</small></strong><p>{zh ? '文件大小在支持范围内。' : 'The file is within the supported range.'}</p><div className="source-condition" aria-hidden={!expanded}><span>{zh ? '还要看这一句' : 'THE ADJACENT CONDITION'}</span><p>{zh ? <>这个区间的 <code>object</code> 正文为空。读取正文，要用 <code>raw</code>。</> : <>Here, <code>object</code> leaves the body empty. Retrieve the body with <code>raw</code>.</>}</p></div></div><button className="source-shutter" onClick={() => setExpanded(!expanded)} aria-expanded={expanded} aria-label={expanded ? (zh ? '收起来源条件' : 'Fold the source conditions') : (zh ? '打开来源条件' : 'Open the source conditions')}><Lattice /><span>{zh ? '推窗' : 'OPEN'}</span></button></div>
        <button className="window-ledge-action" onClick={() => setExpanded(!expanded)} aria-expanded={expanded}>{expanded ? (zh ? '合上窗扇' : 'Close the shutter') : (zh ? '推开窗扇，读相邻条件' : 'Open the shutter. Read the conditions.')}<span aria-hidden="true">{expanded ? '−' : '+'}</span></button>
      </div>
      <div className="receiving-desk"><div className="desk-label"><span>{zh ? '窗内 · 返回材料' : 'INSIDE · WHAT RETURNS'}</span><span className={'receipt-status ' + (raw ? 'filled' : '')}>{raw ? (zh ? '有正文' : 'Body received') : (zh ? '正文为空' : 'Empty body')}</span></div><div className={'retrieved-paper ' + (raw ? 'has-content' : '')} key={representation}><div className="paper-fold" aria-hidden="true" /><div className="paper-body">{raw ? <><span className="body-stroke long" /><span className="body-stroke" /><span className="body-stroke medium" /><strong>{zh ? '文件正文' : 'FILE BODY'}</strong><div className="source-attached">1–100 MB · raw<br />{zh ? '条件与来处，随正文留下。' : 'The condition stays with the answer.'}</div></> : <><code>content: &quot;&quot;</code><code>encoding: &quot;none&quot;</code><span className="empty-paper-space" /><strong>{zh ? '范围正确，还没有读到。' : 'Within range. Still unread.'}</strong></>}</div></div><div className="representation-row"><span>{zh ? '选择读取方式' : 'READ AS'}</span><Tabs value={representation} onValueChange={value => { setRepresentation(value); if(value === 'raw') setExpanded(true); }}><TabsList className="small-tabs"><TabsTrigger value="object">object</TabsTrigger><TabsTrigger value="raw">raw</TabsTrigger></TabsList></Tabs></div></div>
    </div>
    <p className="demo-insight" aria-live="polite">{raw ? (zh ? '可以读取这个大小的文件，但需要 raw 表示。依据的条件，决定了可用的建议。' : 'This file size can be read using the raw representation. The condition determines the useful recommendation.') : (zh ? '只截取“大小在范围内”，会漏掉决定用法的条件。' : 'Taking only the size range misses the condition that determines how to read it.')}</p><DemoSource href="https://docs.github.com/en/rest/repos/contents#get-repository-content">{zh ? '外部依据 · GitHub 官方文档' : 'External evidence · GitHub documentation'}</DemoSource>
  </div>;
}

export type ExploreChoices = { crossing: 'through' | 'around'; view: 'shelter' | 'view'; ending: 'bridge' | 'close' };
export function exploreOutcome(choices: ExploreChoices, zh: boolean) {
  const through = choices.crossing === 'through', view = choices.view === 'view', bridge = choices.ending === 'bridge';
  const response = through ? (zh ? '铃铛果园' : 'Bell orchard') : (zh ? '守光庭' : 'Starlight court');
  const destination = view ? (through ? (zh ? '鱼背眺望台' : 'Fishback overlook') : (zh ? '星海眺望台' : 'Star-sea overlook')) : (through ? (zh ? '栖声亭' : 'Sound shelter') : (zh ? '护星廊' : 'Starlight shelter'));
  const title = through ? (view ? (bridge ? '鱼背上相连的国度' : '隔岸的铃铛国') : (bridge ? '循声可归的庭院' : '留声的隐园')) : (view ? (bridge ? '星光之间的一座桥' : '不可抵达的星岸') : (bridge ? '护星人的归路' : '闭园之后仍有微光'));
  const titleEn = through ? (view ? (bridge ? 'A country joined on a sleeping fish' : 'Bells across the water') : (bridge ? 'A way home by sound' : 'The hidden garden of echoes')) : (view ? (bridge ? 'A bridge between the stars' : 'The unreachable starlit shore') : (bridge ? 'The keeper’s way home' : 'Light after the gate closes'));
  const first = through ? (zh ? '路径穿过倒流瀑布，水流变成声波，下一位营造出回应它的铃铛果园。' : 'The route passes through the upfall. Water becomes sound, and the next player responds with a bell orchard.') : (zh ? '路径绕过瀑布，保护了一池未醒的星光。下一位围绕这份保护，营造出守光庭。' : 'The route goes around the waterfall, protecting a pool of sleeping stars. The next player builds a court around what was protected.');
  const second = view ? (through ? (zh ? '登高之后才发现，整片土地原来伏在一条沉睡的大鱼背上。' : 'The overlook reveals that the whole country rests on a sleeping fish.') : (zh ? '登高之后才发现，池中的微光连着园外的一整片星海。' : 'The overlook reveals that the protected pool is connected to a whole sea of stars.')) : (through ? (zh ? '人们在栖声亭里停下来歇息，屋檐收拢并保留了果园里传来的铃声。' : 'People pause in the sound shelter, where the eaves gather and preserve the bells from the orchard.') : (zh ? '护星廊为微光遮住了风，人们在廊下歇息，守着那池尚未醒来的星光。' : 'The starlight shelter keeps the wind away. People rest beneath its roof and watch over the sleeping stars.'));
  const last = bridge ? (zh ? '最后一笔架起一座桥，两处终于可以互相抵达。' : 'The final mark builds a bridge, making the two places reachable from each other.') : (zh ? '最后一笔封住连接，仍可看见彼岸，路线却必须在此折返。' : 'The final mark closes the connection. The far side remains visible, but the route turns back.');
  return { title: zh ? title : titleEn, response, destination, body: first + (zh ? '' : ' ') + second + (zh ? '' : ' ') + last, through, view, bridge };
}

function Pavilion({ view }: { view: boolean }) {
  return <g className="pavilion" transform={view ? 'translate(505 76)' : 'translate(505 102)'}><path className="pavilion-base" d="M -27 77 L 56 58 L 100 76 L 16 99 Z M -27 77 V 85 L 16 107 L 100 84 V 76 M 16 99 V 107" />{view && <path className="pavilion-base" d="M -35 86 L 16 112 L 108 87 V 95 L 16 120 L -35 93 Z" />}<path d="M -6 24 V 75 M 29 39 V 89 M 77 17 V 68 M -6 60 L 29 76 L 77 56 M -6 64 L 29 80 L 77 60" /><path className="pavilion-roof" d="M -28 22 Q -14 21 -8 12 L 39 -3 Q 57 10 98 11 L 72 22 L 25 40 Z" /><path d="M -28 22 L -27 28 L 25 47 L 99 17 L 98 11 M 25 40 V 47 M 25 35 L 39 3" />{!view && <path className="pavilion-screen" d="M -4 28 L 27 42 V 75 L -4 61 Z M 0 35 L 22 45 M 0 45 L 22 55 M 0 55 L 22 65" />}</g>;
}

function ExploreScene({ zh }: { zh: boolean }) {
  const [choices, setChoices] = useState<ExploreChoices>({ crossing: 'through', view: 'view', ending: 'bridge' });
  const [copyState, setCopyState] = useState<'idle' | 'success' | 'failed'>('idle');
  useEffect(() => setCopyState('idle'), [zh]);
  const outcome = exploreOutcome(choices, zh);
  async function copyOutcome() { setCopyState(await copyTextToClipboard(outcome.title + '\n\n' + outcome.body) ? 'success' : 'failed'); }
  function change(key: keyof ExploreChoices, value: string) { setChoices(c => ({ ...c, [key]: value })); setCopyState('idle'); }
  const route = outcome.through ? 'M 65 285 C 135 276 128 179 192 163 S 235 248 307 232' : 'M 65 285 C 77 168 107 75 206 78 S 370 148 307 232';
  const bridge = 'M 307 232 C 382 224 405 147 534 151';
  return <div className="skill-demo explore-demo"><DemoHeading title={zh ? '落一笔，后来便有了不同的路。' : 'Make a mark. Change what comes next.'} subtitle={zh ? '公开纸笔活动的预设分支 · 三处选择，八种展开' : 'Preset branches from the paper activity · Three choices, eight unfoldings'} />
    <div className="play-map"><svg viewBox="0 0 700 360" role="img" aria-label={outcome.title + '. ' + outcome.body}>
      <path className="map-water" d="M 122 239 C 185 204 212 131 307 117 S 447 219 568 210 Q 649 232 562 285 C 462 328 363 281 293 313 S 180 302 122 239 Z" />
      <path className="water-line" d="M 181 258 Q 244 232 281 243 M 401 267 Q 462 281 515 264 M 341 134 Q 369 141 387 160" />
      {outcome.bridge && <g className="map-corridor return-corridor"><path className="corridor-depth" d="M 534 151 C 602 248 489 320 347 325 S 119 337 65 285" /><path className="corridor-floor" d="M 534 151 C 602 248 489 320 347 325 S 119 337 65 285" /></g>}
      <g className="map-corridor"><path className="corridor-depth" d={route} /><path className="corridor-floor" d={route} /><path className="corridor-roof-line" d={route} /><path className="corridor-guide" d={route} key={choices.crossing} /></g>
      <g className="upfall" transform="translate(173 115)"><path d="M -22 45 Q -10 16 -15 -17 M -7 42 Q 8 15 0 -19 M 8 37 Q 23 13 15 -22" /><path d="M -17 -18 L 0 -23 L 17 -22" />{outcome.through && <><ellipse cx="3" cy="22" rx="38" ry="9" /><ellipse cx="3" cy="22" rx="47" ry="13" /></>}</g>
      <text x="154" y="207" className="map-label">{outcome.through ? (zh ? '声纹之瀑' : 'Ringing falls') : (zh ? '倒流瀑布' : 'The upfall')}</text>
      <g className="response-court" transform="translate(293 202)"><path className="pavilion-base" d="M -35 24 L 10 8 L 58 27 L 10 46 Z M -35 24 V 30 L 10 52 L 58 33 V 27 M 10 46 V 52" />{outcome.through ? <><path d="M 0 22 V -15 M -20 -6 Q 0 -22 20 -6 M -14 -5 V 1 M 0 -10 V -3 M 14 -5 V 1" /><path className="map-bell" d="M -19 5 Q -18 -6 -13 -1 L -10 8 Z M -4 0 Q 0 -9 4 0 L 6 7 H -6 Z M 12 8 Q 11 -3 17 -1 L 21 5 Z" /></> : <><path d="M -16 18 L 7 -14 L 36 14 M -11 19 L 10 28 L 32 18" /><circle cx="7" cy="9" r="3" /><circle cx="19" cy="17" r="2" /></>}</g>
      <text x="262" y="280" className="map-label">{outcome.response}</text>
      {outcome.bridge ? <g className="map-corridor bridge-corridor"><path className="corridor-depth" d={bridge} /><path className="corridor-floor" d={bridge} /><path className="corridor-guide" d={bridge} key={choices.ending} /><path className="bridge-rail" d="M 365 200 Q 425 143 486 146 M 365 208 Q 425 151 486 154 M 382 190 V 204 M 404 171 V 185 M 429 160 V 174 M 456 152 V 166" /></g> : <><path className="line-of-sight" d={bridge} /><g className="closed-route" transform="translate(382 192)"><path d="M -8 -27 V 12 M 9 -33 V 6 M -10 -26 L 11 -33 L 11 -11 L -10 -4 Z" /><text x="2" y="41" textAnchor="middle">{zh ? '折返' : 'Turn back'}</text></g></>}
      <Pavilion view={outcome.view} /><text x="562" y={outcome.view ? 48 : 74} textAnchor="middle" className="map-label">{outcome.destination}</text>
      <path className="arrival-gate" d="M 51 282 V 251 Q 65 230 79 244 V 271 M 48 249 Q 61 224 82 241 M 51 258 L 79 248" /><text x="66" y="336" textAnchor="middle" className="map-label">{zh ? '抵达' : 'Arrival'}</text>
    </svg><span className="map-view-note">{zh ? '廊道会随选择改变' : 'THE ROUTE CHANGES WITH YOUR CHOICES'}</span></div>
    <div className="branch-choices"><Tabs value={choices.crossing} onValueChange={v => change('crossing', v)}><span>{zh ? '遇到瀑布' : 'AT THE FALLS'}</span><TabsList className="small-tabs"><TabsTrigger value="through">{zh ? '穿过' : 'Through'}</TabsTrigger><TabsTrigger value="around">{zh ? '绕行' : 'Around'}</TabsTrigger></TabsList></Tabs><Tabs value={choices.view} onValueChange={v => change('view', v)}><span>{zh ? '下一处' : 'NEXT PLACE'}</span><TabsList className="small-tabs"><TabsTrigger value="view">{zh ? '眺望' : 'A view'}</TabsTrigger><TabsTrigger value="shelter">{zh ? '庇护' : 'Shelter'}</TabsTrigger></TabsList></Tabs><Tabs value={choices.ending} onValueChange={v => change('ending', v)}><span>{zh ? '两岸之间' : 'BETWEEN BANKS'}</span><TabsList className="small-tabs"><TabsTrigger value="bridge">{zh ? '架桥' : 'Bridge'}</TabsTrigger><TabsTrigger value="close">{zh ? '封路' : 'Close'}</TabsTrigger></TabsList></Tabs></div>
    <div className="created-work" aria-live="polite"><h5>{outcome.title}</h5><p>{outcome.body}</p><button className="demo-copy" onClick={copyOutcome}>{copyState === 'success' ? <Check size={14} /> : <Copy size={14} />}{copyState === 'success' ? (zh ? '已复制' : 'Copied') : copyState === 'failed' ? (zh ? '请手动选择复制' : 'Select and copy the text') : (zh ? '带走这段展开' : 'Keep this unfolding')}</button></div><DemoSource href={repo + '/blob/main/docs/examples/six-minutes-to-elsewhere.md'}>{zh ? '原活动与完整玩法' : 'The source activity and complete rules'}</DemoSource>
  </div>;
}

function ShapeScene({ zh }: { zh: boolean }) {
  const [preview, setPreview] = useState('scene');
  const [applied, setApplied] = useState('score');
  const [action, setAction] = useState<'wait' | 'enter' | null>(null);
  const [score, setScore] = useState(3);
  const scene = preview === 'scene';
  return <div className="skill-demo shape-demo"><DemoHeading title={zh ? '在门外试看，把判断带入工作。' : 'Try it at the threshold. Carry the decision in.'} subtitle={zh ? '构造小样 · 保留六轮体验与丰富反思' : 'Constructed example · Keep six rounds and rich reflection'} />
    <div className="shape-brief"><span>{zh ? '仍然保留' : 'KEEP'}</span><strong>{zh ? '六轮' : 'Six rounds'}</strong><span>·</span><strong>{zh ? '丰富反思' : 'Rich reflection'}</strong></div>
    <Tabs value={preview} onValueChange={setPreview}><TabsList className="small-tabs shape-options"><TabsTrigger value="score">{zh ? '特质评分' : 'Trait rating'}</TabsTrigger><TabsTrigger value="scene">{zh ? '在场景中行动' : 'Act in a scene'}</TabsTrigger></TabsList></Tabs>
    <div className={'judgement-court ' + (applied === 'scene' ? 'threshold-crossed' : '')}>
      <div className={'interpretation-window ' + (scene ? 'scene-view' : 'score-view')}><div className="window-caption"><span>{zh ? '门外 · 试看' : 'OUTSIDE · PREVIEW'}</span><span>1 / 6</span></div><h5>{scene ? (zh ? '隔着院墙，听见一阵雨声。' : 'Behind the courtyard wall, you hear rain.') : (zh ? '我喜欢探索不熟悉的地方。' : 'I enjoy exploring unfamiliar places.')}</h5>{scene ? <><p>{zh ? '门半掩着。一册书，被留在石阶上。' : 'The gate is half open. A book has been left on the stone step.'}</p><div className="scene-actions"><button aria-pressed={action === 'wait'} onClick={() => setAction('wait')}>{zh ? '在门外听一会儿' : 'Stay and listen'}</button><button aria-pressed={action === 'enter'} onClick={() => setAction('enter')}>{zh ? '拾起书，走进去' : 'Take the book inside'}</button></div>{action && <p className="scene-consequence">{action === 'wait' ? (zh ? '雨声渐近；你注意到书页里夹着一张尚未展开的地图。' : 'The rain draws closer. You notice a folded map between the pages.') : (zh ? '檐下的人认出了那册书，指给你一条通向内院的小路。' : 'Someone under the eaves recognizes the book and points to a path into the inner court.')}</p>}</> : <><p>{zh ? '选择与你相符的程度。' : 'Choose how strongly you agree.'}</p><div className="rating-preview"><Slider value={[score]} onValueChange={v => setScore(v[0])} min={1} max={5} step={1} aria-label={zh ? '特质评分' : 'Trait rating'} /><span>{score} / 5</span></div></>}</div>
      <div className="decision-threshold" aria-hidden="true"><span className="threshold-lintel" /><div className="threshold-door"><Lattice /></div><span className="threshold-step" /></div>
      <div className="inner-court"><p className="inner-court-label">{zh ? '门内 · 当前采用' : 'INSIDE · CURRENTLY APPLIED'}</p><div className="propagation" aria-live="polite"><div><span>{zh ? '说明' : 'INSTRUCTIONS'}</span><strong>{applied === 'scene' ? (zh ? '六轮场景中的选择' : 'Choices across six scenes') : (zh ? '六轮特质的自评分' : 'Self-ratings across six rounds')}</strong></div><div><span>{zh ? '交互' : 'INTERACTION'}</span><strong>{applied === 'scene' ? (zh ? '动作留下后果' : 'Actions have consequences') : (zh ? '为陈述选择分值' : 'Assign a score to a statement')}</strong></div><div><span>{zh ? '反思' : 'REFLECTION'}</span><strong>{applied === 'scene' ? (zh ? '回到实际发生的事' : 'Return to what happened') : (zh ? '汇总与解释评分' : 'Summarize the ratings')}</strong></div></div></div>
    </div><div className="shape-apply-row"><button className="apply-interpretation" onClick={() => setApplied(preview)} disabled={applied === preview}>{applied === preview ? (zh ? '这一解释已在工作中' : 'This interpretation is applied') : (zh ? '采用这个纠正' : 'Apply this correction')}</button>{applied === 'scene' && <button className="undo-interpretation" onClick={() => setApplied('score')}><RotateCcw size={14} />{zh ? '撤回' : 'Undo'}</button>}</div><p className="demo-insight">{zh ? '门外可以反复试看。采用以后，说明、交互与反思才一起改变。' : 'Try either version outside. Adoption changes the instructions, interaction and reflection together.'}</p>
  </div>;
}

export function SkillScene({ method, language }: { method: string; language: Language }) {
  const zh = language === 'zh';
  if (method === 'search') return <SearchScene zh={zh} />;
  if (method === 'study') return <StudyScene zh={zh} />;
  if (method === 'explore') return <ExploreScene zh={zh} />;
  return <ShapeScene zh={zh} />;
}
