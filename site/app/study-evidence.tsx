import { useState, type CSSProperties } from 'react';
import { BookOpen, RotateCcw } from 'lucide-react';

export function StudyScene({ zh }: { zh: boolean }) {
  const [scenario, setScenario] = useState<'late' | 'early'>('late');
  const [revealed, setRevealed] = useState(false);
  const late = scenario === 'late';
  const stages = [zh ? '存储记录' : 'Stored record', zh ? '返回材料' : 'Retrieved material', zh ? '最终输入' : 'Final input'];

  return <div className={'skill-demo study-demo study-trace' + (revealed ? ' trace-revealed' : '')}>
    <div className="demo-heading"><h4>{zh ? '这句话，是谁说的？' : 'Who said this?'}</h4><p>{zh ? '对照已有记录，找到名字消失的位置。' : 'Compare the records to find where the name disappeared.'}</p></div>
    <div className="trace-final-input" hidden={revealed}>
      <div><span className="trace-label">{zh ? '最后收到的内容' : 'WHAT THE READER RECEIVES'}</span><p>“{zh ? '我选了眺望。' : 'I chose the view.'}”</p></div>
      <div className="trace-unknown"><span>{zh ? '说话者' : 'SPEAKER'}</span><strong>{zh ? '未知' : 'Unknown'}</strong></div>
    </div>
    <div className="trace-action-row">
      <button className="trace-reveal-button" onClick={() => setRevealed(!revealed)} aria-expanded={revealed} aria-controls="study-records"><BookOpen size={18} />{revealed ? (zh ? '收起记录' : 'Close the records') : (zh ? '对照三份记录' : 'Compare three records')}<span aria-hidden="true">{revealed ? '−' : '+'}</span></button>
      <span>{revealed ? (zh ? '沿着同一个名字，看它在哪一处消失。' : 'Follow the same name across the records.') : (zh ? '仅凭这一句，无法确认。' : 'This sentence alone cannot tell us.')}</span>
    </div>
    <div id="study-records" hidden={!revealed}>{revealed && <div className={'trace-records-wrap ' + (late ? 'loss-late' : 'loss-early')}>
      <ol className="trace-records" key={scenario} aria-label={zh ? '按处理顺序对照三份记录' : 'Three records in processing order'}>{stages.map((stage, i) => {
        const kept = late && i < 2;
        const boundary = late ? i === 2 : i === 0;
        return <li key={stage} className={'trace-record ' + (kept ? 'name-kept' : 'name-missing') + (boundary ? ' loss-boundary' : '')} style={{'--record': i} as CSSProperties}>
          <span className="trace-boundary-note">{boundary ? (late ? (zh ? '名字在这里消失' : 'NAME DROPPED HERE') : (zh ? '最早记录已缺失' : 'ALREADY MISSING HERE')) : kept ? (zh ? '名字还在' : 'NAME PRESERVED') : (zh ? '仍然没有名字' : 'STILL MISSING')}</span>
          <div className="trace-paper"><div className="trace-paper-top"><span>{stage}</span><i aria-hidden="true" /></div><span className="trace-field-label">{zh ? '说话者' : 'SPEAKER'}</span><strong className="trace-name">{kept ? (zh ? '林' : 'Lin') : <><span aria-hidden="true">?</span><small>{zh ? '姓名缺失' : 'Name missing'}</small></>}</strong><p className="trace-quote">{zh ? '我选了眺望。' : 'I chose the view.'}</p><span className="trace-paper-note">{i === 0 ? (zh ? '保存下来的内容' : 'What was saved') : i === 1 ? (zh ? '检索返回的内容' : 'What was retrieved') : (zh ? '交给读者的内容' : 'What the reader received')}</span></div>
        </li>;
      })}</ol>
      <div className="trace-discovery" role="status" aria-live="polite"><span className="discovery-mark" aria-hidden="true">{zh ? '见' : '!'}</span><div><h5>{late ? (zh ? '说话者是林。名字在整理最终输入时丢了。' : 'Lin said it. The name was lost while preparing the final input.') : (zh ? '最早的存储记录，就已经没有名字。' : 'The name is already missing from the stored record.')}</h5><p>{late ? (zh ? '前两份都保留了“林”，应检查返回材料到最终输入之间的整理。' : 'The first two records preserve Lin. Inspect the transformation from retrieved material to final input.') : (zh ? '这三份记录还不能告诉我们是谁说的。下一步要回查保存前的材料。' : 'These records cannot tell us who spoke. Look further back, before the material was saved.')}</p></div></div>
      <div className="trace-another"><button onClick={() => setScenario(late ? 'early' : 'late')}><RotateCcw size={14} />{zh ? '再看另一种情况' : 'Try another case'}</button><span>{zh ? '最后那句话不变，丢失的位置会改变。' : 'The final sentence stays the same. The point of loss changes.'}</span></div>
    </div>}</div>
    <a className="demo-source" href="https://github.com/IndelibleVivi/soundings/blob/main/docs/examples/diagnosing-evidence-loss.md" target="_blank" rel="noreferrer"><BookOpen size={14} />{zh ? '原案例 · 离线构造对照' : 'Source case · Constructed offline comparison'}</a>
  </div>;
}
