import { copyTextToClipboard } from '@/lib/copy-text';

import { useEffect, useRef, useState } from 'react';
import { SkillScene } from './garden-scenes';
import { BookWindow, GardenPorch, MethodGlyph } from './garden-architecture';
import { GardenTerrain } from './garden-terrain';
import { Check, Copy, GitFork, Menu, X, BookOpen } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog';

type Language = 'zh' | 'en';
type Bilingual = { zh: string; en: string };
type CaseId = 'elsewhere' | 'evidence';
const repo = 'https://github.com/IndelibleVivi/soundings';
const installation = 'codex plugin marketplace add IndelibleVivi/soundings\ncodex plugin add soundings@soundings';

const methods = [
  {
    id: 'search', name: '访求', english: 'Search',
    title: { zh: '向外寻找，让回答有来处。', en: 'Go outward. Bring back an answer with roots.' },
    description: { zh: '当需要的事实、机制或参考还在当前材料之外，向外调查，找到足以回答问题的依据。', en: 'When the facts, mechanisms or references you need are outside the current material, investigate them and bring back a supported answer.' },
    result: { zh: '有出处的回答或比较，以及结论成立的条件。', en: 'A supported answer or comparison, with the conditions that make it true.' },
    prompt: { zh: '$search 调查这个交互机制有哪些值得借鉴的做法。读原始来源，说明它在什么条件下有效，再带回对当前作品有用的建议。', en: '$search Investigate useful precedents for this interaction. Read primary sources, explain the conditions under which it works, and bring back a recommendation for our project.' },
    note: { zh: '材料之外，仍有值得遇见的东西。', en: 'There is more to meet beyond the material at hand.' }
  },
  {
    id: 'study', name: '会通', english: 'Study',
    title: { zh: '把材料放在关系里理解。', en: 'Understand what the material means together.' },
    description: { zh: '对照已有材料，解释它们之间的关系。问题尚未清楚时，找到最影响当前目标的一处，并继续追到可用的解释或结果。', en: 'Explain the relationships across the material. When the question is still unclear, find what matters most to the current goal and pursue it to a useful explanation or result.' },
    result: { zh: '综合解释、机制或新的判断；真实分歧依然清楚。', en: 'An integrated explanation, mechanism or new judgment, with real disagreements intact.' },
    prompt: { zh: '$study 这些报告对同一个机制有不同结论。解释它们实际证明了什么，区分条件差异与真正分歧，并判断这对我们的项目意味着什么。', en: '$study These reports reach different conclusions about the same mechanism. Explain what they establish, distinguish conditions from real disagreements, and work out what this means for our project.' },
    note: { zh: '会通，也包括看清哪里尚不相通。', en: 'Understanding includes seeing where things do not yet connect.' }
  },
  {
    id: 'explore', name: '营造', english: 'Explore',
    title: { zh: '让一个想法，成为能遇见的作品。', en: 'Develop an idea into something you can experience.' },
    description: { zh: '方向可以粗略，也可以已经很清楚。接着它往下做，让场景、规则或体验发展到足够完整，真正显出自己的性格。', en: 'The direction may be rough or already clear. Carry it further, developing a scene, set of rules or experience until its character can actually be felt.' },
    result: { zh: '可读、可玩、可体验的创作，或足够完整的候选作品。', en: 'A substantial scene, playable experience or developed candidate someone can react to.' },
    prompt: { zh: '$explore 做一个六分钟、三人参与的纸笔活动。让每次选择改变后来的人能做什么，交付完整玩法和一段实际展开的示例。', en: '$explore Make a six-minute paper activity for three people. Let each choice change what the next person can do. Deliver the complete activity and a worked playthrough.' },
    note: { zh: '一小处，也值得被认真营造。', en: 'Even a small place deserves to be made with care.' }
  },
  {
    id: 'shape', name: '辨定', english: 'Shape',
    title: { zh: '让重要的差异，变得可以判断。', en: 'Make the consequential difference visible.' },
    description: { zh: '当一种解释会改变整件作品，或反馈说明方向已经偏离，做出能看见、能比较的材料，让判断与纠正真正抵达工作。', en: 'When an interpretation changes the work, or feedback reveals that it has drifted, make the difference perceptible and carry the correction into the work.' },
    result: { zh: '可判断的材料或有依据的决定；需要纠正时，继续完成已授权的改动。', en: 'Representative material or a grounded decision; authorized corrections carried through when needed.' },
    prompt: { zh: '$shape 原型做出来了，但体验偏离了最初的目标。保留已经认可的部分，让两种关键解释产生的差别可以被感受，再完成已授权的纠正。', en: '$shape The prototype works, but its experience has drifted from the intended goal. Preserve accepted qualities, make the consequential alternatives tangible, and carry through the authorized correction.' },
    note: { zh: '看清这一步，继续眼前的事。', en: 'See this choice clearly, then continue the work.' }
  }
];

const cases = [
  {
    id: 'elsewhere' as CaseId, category: 'EXPLORE · 营造', label: { zh: '一处被共同创造的地方', en: 'A place made together' },
    title: { zh: '六分钟，去往别处', en: 'Six Minutes to Elsewhere' },
    description: { zh: '一张纸，三个人。每一次落笔，都改变后来的人能创造什么。', en: 'One sheet of paper. Three people. Each mark changes what the next person can make.' },
    meta: { zh: '纸笔活动 · 构造示例', en: 'Paper activity · Constructed example' },
    source: repo + '/blob/main/docs/examples/six-minutes-to-elsewhere.md',
    className: 'case-elsewhere'
  },
  {
    id: 'evidence' as CaseId, category: 'STUDY · 会通', label: { zh: '从一段材料，追到真正的问题', en: 'From material to the question that matters' },
    title: { zh: '找到了，为何仍然用错？', en: 'Found, but still misunderstood' },
    description: { zh: '材料已经存过，也已经返回。决定答案的那层关系，是在哪里消失的？', en: 'The evidence was saved and retrieved. Where did the distinction needed by the answer disappear?' },
    meta: { zh: '研究摘读 · 问题与证据', en: 'Research reading · Question and evidence' },
    source: repo + '/blob/main/docs/examples/diagnosing-evidence-loss.md',
    className: 'case-evidence'
  }
];

const playthrough: Bilingual[] = [
  { zh: '先在纸中央写下“抵达”。第一位画出一座倒着流的瀑布；第二位选择让路径穿过它，把水流改成一圈圈声波。', en: 'Begin with ARRIVAL. The first player draws an upside-down waterfall. The second sends a route through it, changing the falling lines into rings of sound.' },
  { zh: '第三位必须回应这个变化：声波唤醒了一片钟形树木，成为“铃铛果园”。后来的人不能任意忽略前面的选择。', en: 'The third player responds to the change: the ringing awakens an orchard of bell-shaped trees. Later choices have to take the earlier ones seriously.' },
  { zh: '路径接着分成两条，一条去往庇护所，另一条通向眺望处。参与者选了眺望，于是必须揭示一个一直藏在地图里的东西：原来整片土地都在一条沉睡的大鱼背上。', en: 'The route splits toward shelter and a view. Choosing the view reveals something that has been inside the map all along: the whole country rests on a sleeping fish.' },
  { zh: '最后一位在果园与眺望处之间架桥，为这片地方题名。所有人留下桥两侧的足迹、涟漪与飞鸟，再用手指从“抵达”走一遍如今真正能走的路。', en: 'The last player bridges the orchard and viewpoint, then names the place. Everyone leaves traces on both sides, and one finger follows the route that the accumulated choices now allow.' }
];

export default function Soundings() {
  const [language, setLanguage] = useState<Language>('zh');
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeMethod, setActiveMethod] = useState('search');
  const [activeCase, setActiveCase] = useState<CaseId | null>(null);
  const [copyState, setCopyState] = useState({ key: '', success: false });
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const openedBook = useRef<HTMLButtonElement | null>(null);
  const t = (value: Bilingual) => value[language];
  const zh = language === 'zh';
  const currentCase = cases.find(item => item.id === activeCase);

  useEffect(() => {
    document.documentElement.lang = zh ? 'zh-CN' : 'en';
    document.title = zh ? '见地 Soundings · 与你的 agent 一起探问' : 'Soundings · Inquire with your agent';
    setCopyState({ key: '', success: false });
  }, [zh]);

  useEffect(() => () => { if (copyTimer.current) clearTimeout(copyTimer.current); }, []);

  async function copyText(value: string, key: string) {
    const success = await copyTextToClipboard(value);
    setCopyState({ key, success });
    if (copyTimer.current) clearTimeout(copyTimer.current);
    copyTimer.current = setTimeout(() => setCopyState({ key: '', success: false }), 2800);
  }

  const copyLabel = (key: string) => copyState.key === key
    ? (copyState.success ? (zh ? '已复制' : 'Copied') : (zh ? '请手动选择复制' : 'Select and copy'))
    : (zh ? '复制' : 'Copy');

  return (
    <div className={'site language-' + language}>
      <a href="#main" className="skip-link">{zh ? '跳到正文' : 'Skip to content'}</a>
      <header className="site-header">
        <div className="header-inner">
          <a className="brand-lockup" href="#top" aria-label={zh ? '见地 Soundings 首页' : 'Soundings home'} onClick={() => setMenuOpen(false)}>
            <span className="brand-seal" aria-hidden="true">
              <svg viewBox="0 0 40 40" fill="none">
                <rect x="4.5" y="4.5" width="31" height="31" rx="3" />
                <path d="M12 27.5V13.5L16 9.5H27" />
                <path d="M16.5 32V18l4-4h11" />
                <path d="M7 30.5c12.5 0 12.5-8 23.5-8" />
              </svg>
            </span>
            <span className="brand-name">见地</span>
            <span className="brand-english">soundings</span>
          </a>
          <nav className={'main-nav' + (menuOpen ? ' is-open' : '')} aria-label={zh ? '主导航' : 'Main navigation'}>
            <a href="#methods" onClick={() => setMenuOpen(false)}>{zh ? '四处探问' : 'Ways of inquiry'}</a>
            <a href="#library" onClick={() => setMenuOpen(false)}>{zh ? '书房' : 'Reading room'}</a>
            <a href="#about" onClick={() => setMenuOpen(false)}>{zh ? '题记' : 'A note'}</a>
          </nav>
          <div className="header-actions">
            <button className="language-toggle" onClick={() => setLanguage(zh ? 'en' : 'zh')} aria-label={zh ? 'Switch to English' : '切换为中文'}>{zh ? 'EN' : '中文'}</button>
            <a href="#start" className="header-start">{zh ? '开始使用' : 'Get started'}</a>
            <button className="mobile-menu" aria-label={menuOpen ? (zh ? '关闭菜单' : 'Close menu') : (zh ? '打开菜单' : 'Open menu')} aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}>
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </header>

      <main id="main">
        <GardenTerrain zh={zh} onEnter={id => {
          setActiveMethod(id);
          requestAnimationFrame(() => {
            (document.querySelector('.method-trigger[data-state="active"]') as HTMLElement | null)?.focus({ preventScroll: true });
            document.getElementById('methods')?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
          });
        }} />

        <section className="methods-section" id="methods" aria-labelledby="methods-title">
          <span className="motif motif-roofline" aria-hidden="true"><i /><i /><i /><i /><i /></span>
          <div className="section-width">
            <div className="section-heading"><div><p className="eyebrow">{zh ? '园中 · 各有一境' : 'WITHIN THE GARDEN'}</p><h2 id="methods-title">{zh ? '从你需要的那一处，进去。' : 'Enter where the work needs you.'}</h2></div><p className="section-intro">{zh ? '向外寻，向内读，动手做，看清再定。每一种方法，都可以独立开始。' : 'Look outward. Read across. Make something. See the difference. Each method is its own beginning.'}</p></div>
            <Tabs className="method-tabs" value={activeMethod} onValueChange={setActiveMethod}>
              <TabsList className="method-list" variant="line" aria-label={zh ? '选择一种探问方式' : 'Choose an inquiry method'}>
                {methods.map(method => <TabsTrigger key={method.id} value={method.id} className="method-trigger" data-method={method.id}><span className="method-joinery" aria-hidden="true" /><span className="method-glyph-panel" aria-hidden="true"><MethodGlyph method={method.id} /></span><span className="method-names"><span className="method-slip">{method.name}</span><small>{method.english}</small></span></TabsTrigger>)}
              </TabsList>
              {methods.map(method => <TabsContent className="method-panel" key={method.id} value={method.id}>
                <aside className="method-commentary"><div className="method-explanation"><span className="method-category">{method.english.toUpperCase()} · {method.name}</span><h3>{t(method.title)}</h3><p>{t(method.description)}</p><div className="method-result"><span>{zh ? '这一程，可以带走' : 'WHAT YOU TAKE WITH YOU'}</span><p>{t(method.result)}</p></div></div>
                  <details className="prompt-sheet"><summary><span className="prompt-tab" aria-hidden="true" />{zh ? '把它带到我的工作里' : 'Bring it to my work'}</summary><div className="prompt-inside"><span className="prompt-fold" aria-hidden="true" /><p className="sample-prompt">{t(method.prompt)}</p><div className="prompt-bottom"><button className="copy-button" onClick={() => copyText(t(method.prompt), method.id)} aria-label={(zh ? '复制' : 'Copy ') + method.english + (zh ? '示例提示词' : ' example prompt')}>{copyState.key === method.id && copyState.success ? <Check size={15} /> : <Copy size={15} />}<span>{copyLabel(method.id)}</span></button></div></div></details>
                  <p className="method-small-poem">{t(method.note)}</p>
                </aside>
                <div className="method-artpage"><SkillScene method={method.id} language={language} /></div>
              </TabsContent>)}
            </Tabs>
          </div>
        </section>

        <section className="library-section section-width" id="library" aria-labelledby="library-title">
          <div className="section-heading"><div><p className="eyebrow">{zh ? '书房 · 展卷有得' : 'THE READING ROOM'}</p><h2 id="library-title">{zh ? '有些理解，长成了作品。' : 'Some understanding grows into a work.'}</h2></div><p className="section-intro">{zh ? '两份具体的工作，留在这里。翻开，看它们如何一步步有了自己的样子。' : 'Two pieces of work, kept here to read. Open one and see how it found its own form.'}</p></div>
          <div className="case-shelf">
            {cases.map((item,index) => <button key={item.id} className={'case-book ' + item.className} onClick={event => { openedBook.current = event.currentTarget; setActiveCase(item.id); }} aria-haspopup="dialog"><span className="book-binding" aria-hidden="true">{Array.from({length:5},(_,i)=><i key={i} />)}</span><span className="book-page-edges" aria-hidden="true" /><span className="case-cover"><span className="case-window" aria-hidden="true"><BookWindow variant={item.id} /></span><span className="case-label">{item.category}</span><span className="case-title">{t(item.title)}</span><span className="case-description">{t(item.description)}</span><span className="case-book-bottom"><span>{t(item.meta)}</span><span className="read-case"><BookOpen size={17} />{zh ? '展卷' : 'Open the leaf'}</span></span></span><span className="book-corner-mark" aria-hidden="true">{index === 0 ? '游' : '读'}</span></button>)}
          </div><p className="library-source-note">{zh ? '来自 Soundings 的公开示例；册页内附完整原文。' : 'From the public Soundings examples. Each leaf keeps its complete source.'}</p>
        </section>

        <section className="about-section" id="about" aria-labelledby="about-title">
          <span className="motif motif-water" aria-hidden="true"><i /><i /><i /></span>
          <div className="section-width about-layout"><div className="about-window"><GardenPorch zh={zh} /><span className="about-window-note">{zh ? '推窗见枝' : 'AN OPEN WINDOW'}</span></div><div className="about-copy"><p className="eyebrow">{zh ? '见地题记' : 'A NOTE ON SOUNDINGS'}</p><h2 id="about-title">{zh ? <>见其所从来，<br />亦见其可往。</> : <>See where it comes from.<br />Leave room for where it goes.</>}</h2><p>{zh ? '窗框取一段景，游廊带来另一个视角。走过一重遮挡，眼前材料的关系也会改变。我们借园林来表达探问：每次看见，都与正在做的事相连。' : 'A window frames a view; a corridor offers another position. Beyond an obstruction, the relationship between things changes. The garden gives inquiry a form: each act of seeing belongs to the work at hand.'}</p><p>{zh ? 'Soundings 让 agent 继续追问、理解、营造与辨定。成果可以是有来处的回答、一种更准确的解释，也可以是一件足够完整、能被亲自感受的新作品。' : 'Soundings helps an agent investigate, understand, develop and discern. The result can be a supported answer, a clearer explanation, or a substantial new work someone can experience.'}</p><a href={repo + '/blob/main/plugins/soundings/docs/design.md'} target="_blank" rel="noreferrer" className="text-link">{zh ? '读完整的设计主张' : 'Read the design principles'}</a></div></div>
        </section>

        <section className="start-section section-width" id="start" aria-labelledby="start-title">
          <span className="motif motif-botanical" aria-hidden="true"><i /><i /><i /><i /><i /></span>
          <div className="start-copy"><p className="eyebrow">{zh ? '入园 · 从手边开始' : 'BRING IT TO YOUR WORK'}</p><h2 id="start-title">{zh ? <>下一次探问，<br />就从手边开始。</> : <>Bring your next question.<br />Start with the work at hand.</>}</h2><p>{zh ? '在 Codex 中安装 Soundings，新开一次任务，即可使用四个独立的 skill。' : 'Install Soundings in Codex, then start a new task to use the four independent skills.'}</p><a className="github-link" href={repo} target="_blank" rel="noreferrer"><GitFork size={18} />{zh ? '在 GitHub 查看项目' : 'View the project on GitHub'}</a></div>
          <div className="install-desk"><div className="desk-rail" aria-hidden="true" /><div className="install-card"><div className="install-heading"><span>CODEX · {zh ? '安装' : 'INSTALL'}</span><button className="copy-button" onClick={() => copyText(installation, 'install')} aria-label={zh ? '复制安装命令' : 'Copy installation commands'}>{copyState.key === 'install' && copyState.success ? <Check size={15} /> : <Copy size={15} />}<span>{copyLabel('install')}</span></button></div><pre><code>{installation}</code></pre><p>{zh ? '直接描述你的任务，或用 $search、$study、$explore、$shape 指定方法。' : 'Describe your task naturally, or choose a method with $search, $study, $explore or $shape.'}</p><a href={repo + (zh ? '/blob/main/README.zh-CN.md#安装与升级' : '/blob/main/README.md#install-and-upgrade')} target="_blank" rel="noreferrer" className="text-link">{zh ? '安装与升级说明' : 'Installation and upgrade guide'}</a></div><div className="desk-legs" aria-hidden="true"><i /><i /></div></div>
        </section>
      </main>
      <footer className="site-footer section-width"><a href="#top" className="footer-brand"><span>见地</span><em>soundings</em></a><p>{zh ? '一项由 Faye 发起的探问。' : 'A project by Faye.'}</p><div><a href={repo + '/tree/main/site/public'} target="_blank" rel="noreferrer">{zh ? '页面视觉资源' : 'Page visual resources'}</a><a href={repo} target="_blank" rel="noreferrer">GitHub</a></div></footer>
      <span className="sr-only" role="status" aria-live="polite">{copyState.key ? (copyState.success ? (zh ? '已复制到剪贴板' : 'Copied to clipboard') : (zh ? '复制未成功，请选择文字手动复制' : 'Copy did not succeed. Please select the text and copy it.')) : ''}</span>

      <Dialog open={activeCase !== null} onOpenChange={open => { if (!open) setActiveCase(null); }}>
        <DialogContent className="reading-sheet" showCloseButton={false} onCloseAutoFocus={event => { event.preventDefault(); openedBook.current?.focus({ preventScroll: true }); }}>
          <div className="reading-toolbar"><span className="reading-running-head"><i aria-hidden="true" />{currentCase?.category}</span><DialogClose className="reading-close" aria-label={zh ? '合上案例' : 'Close reading'}><X size={20} /></DialogClose></div>
          <DialogTitle className="reading-title">{currentCase ? t(currentCase.title) : ''}</DialogTitle>
          <DialogDescription className="reading-description">{currentCase ? t(currentCase.description) : ''}</DialogDescription>
          {activeCase === 'elsewhere' ? (
            <div className="reading-body"><div className="reading-meta"><span>{zh ? '3 位参与者' : '3 participants'}</span><span>{zh ? '一张纸与三支笔' : 'Paper and three pencils'}</span><span>{zh ? '设计时长 6 分钟' : 'Designed for 6 minutes'}</span></div>
              <h3>{zh ? '让选择留下后果' : 'Choices that leave a trace'}</h3>
              <p>{zh ? '这份活动的核心，是让每次落笔都进入后来者必须面对的世界。路径从地标里穿过，地标就要改变；选择绕行，就必须保护某样东西。最后得到的地方，由这些具体选择共同决定。' : 'Every mark becomes part of the world the next player encounters. Passing through a landmark changes it; going around protects something. The final place emerges from those consequential choices.'}</p>
              <h3>{zh ? '一次完整的展开' : 'One complete unfolding'}</h3>
              <ol className="playthrough">{playthrough.map((step, index) => <li key={index}><span aria-hidden="true">{String(index + 1).padStart(2, '0')}</span><p>{t(step)}</p></li>)}</ol>
              <div className="reading-takeaway">{zh ? '《沉睡巨鱼上的国度》不是预先写好的结局。它能出现，是因为前面的选择一直在影响后来可以发生什么。' : 'The Country on a Sleeping Fish was not a predetermined ending. It became possible because earlier choices kept changing what could happen next.'}</div>
              <p className="reading-qualification">{zh ? '这是构造的活动与展开示例。六分钟时长及游玩体验尚待真人试玩检验。完整原文附逐步玩法。' : 'This is a constructed activity and playthrough. Timing and enjoyment have not yet been tested with human players. The full source includes the complete schedule and rules.'}</p>
            </div>
          ) : (
            <div className="reading-body"><div className="reading-meta"><span>{zh ? '研究摘读' : 'Research reading'}</span><span>{zh ? '证据如何抵达回答' : 'How evidence reaches an answer'}</span></div>
              <h3>{zh ? '把大问题，追到一个可以区分的地方' : 'Find the distinction inside the broad question'}</h3>
              <p>{zh ? '“系统是否记得”太宽了。这份研究追问：当前任务需要的区别，在哪个可观察的边界消失，或者不再影响最后的结果？' : '“Does the system remember?” is too broad. This inquiry asks where the distinction required by the current task disappears, or stops governing the result.'}</p>
              <h3>{zh ? '两种构造的处理，可以产生相同的最终输入' : 'Two constructed transformations can produce the same final input'}</h3>
              <div className="evidence-comparison"><div><span>{zh ? '情形 A' : 'CASE A'}</span><p>{zh ? '存储前就去掉了说话者信息。' : 'Speaker identity is removed before storage.'}</p><small>{zh ? '材料入库时，区别已经丢失。' : 'The distinction is already gone when the material is stored.'}</small></div><div><span>{zh ? '情形 B' : 'CASE B'}</span><p>{zh ? '保存和检索时都保留了说话者，装配输入时才删掉。' : 'Storage and retrieval preserve the speaker, but input assembly removes it.'}</p><small>{zh ? '区别曾经还在，却没有进入阅读者的输入。' : 'The distinction survived until the context handed to the reader.'}</small></div></div>
              <p>{zh ? '两种情形的最终输入可能完全一样。只观察最后的输入或回答，就无法定位丢失发生在哪里；需要比较存储、返回与实际装配的相邻表示。' : 'The final assembled inputs can be identical. Looking only at those inputs or answers cannot locate the loss. Comparing adjacent stored, returned and assembled representations can.'}</p>
              <div className="reading-takeaway">{zh ? '新的见地，是让“找到了却用错”分解成几个能够被证据区分的解释，进而设计下一次有意义的观察。' : 'The useful finding is a set of explanations that evidence can distinguish, and a concrete observation that could test them.'}</div>
              <p className="reading-qualification">{zh ? '这组对照检查的是公开合成输入的离线变换，没有运行检索引擎或模型；原文另含限定范围的源码检查与明确标出的推断。' : 'This comparison audits offline transformations of public synthetic input. It does not run a retrieval engine or model. The source also includes bounded code readings and explicit inferences.'}</p>
            </div>
          )}
          <div className="reading-source"><a className="button button-primary" href={currentCase?.source || repo} target="_blank" rel="noreferrer">{zh ? '阅读完整原文' : 'Read the complete source'}</a><DialogClose className="quiet-link">{zh ? '回到书房' : 'Back to the reading room'}</DialogClose></div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
