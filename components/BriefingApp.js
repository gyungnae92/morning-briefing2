'use client';
import { useState, useEffect } from 'react';

const RADIO = [
  { id:'cbs', name:'박성태의 뉴스쇼', color:'#E4002B' },
  { id:'mbc', name:'김종배의 시선집중', color:'#00A651' },
  { id:'sbs', name:'김태현의 정치쇼', color:'#0068B7' },
  { id:'kbs', name:'전격시사', color:'#1D1D1B' },
  { id:'factory', name:'김어준 뉴스공장', color:'#FF6B00' },
];
const KW = ['정치','경제','노동','여성','사회','국제','지역현안(평택)'];
const ic = { high:'#E4002B', medium:'#F5A623', low:'#8E8E93' };
const il = { high:'🔴 주요', medium:'🟡 일반', low:'⚪ 참고' };

function Badge({ source }) {
  const m = RADIO.find(r => source.includes(r.name));
  return <span style={{ fontSize:11, padding:'2px 8px', borderRadius:10, background:m?m.color+'15':'#f0f0f0', color:m?m.color:'#888', fontWeight:500 }}>📻 {source}</span>;
}

export default function BriefingApp() {
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kws, setKws] = useState(new Set(KW));
  const [selSrc, setSelSrc] = useState(null);
  const [openPanels, setOpenPanels] = useState(new Set());

  async function loadBriefing() {
    setLoading(true); setError(null);
    try {
      const res = await fetch('/api/briefing');
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setBriefing(data);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { loadBriefing(); }, []);

  function togglePanel(key) {
    setOpenPanels(p => { const n = new Set(p); n.has(key)?n.delete(key):n.add(key); return n; });
  }

  function filtered() {
    if (!briefing?.sections) return [];
    return briefing.sections
      .map(s => ({ ...s, items: selSrc ? s.items.filter(it => it.sources?.some(x => x.includes(selSrc))) : s.items }))
      .filter(s => s.items.length > 0 && (kws.size === KW.length || kws.has(s.category)));
  }

  const meta = briefing?._meta;

  return (
    <div style={{ maxWidth:680, margin:'0 auto', padding:'32px 20px', minHeight:'100vh' }}>
      <div style={{ marginBottom:28 }}>
        <div style={{ fontSize:11, letterSpacing:'0.15em', color:'#999', marginBottom:6, fontWeight:500 }}>MORNING BRIEFING</div>
        <h1 style={{ fontSize:28, fontWeight:800, margin:0, lineHeight:1.3 }}>오늘의 아침 브리핑</h1>
        {meta && (
          <div style={{ fontSize:13, color:'#777', marginTop:4 }}>
            {meta.date} · {meta.time_slot === 'morning' ? '오전' : '오후'} 업데이트
          </div>
        )}
      </div>

      {/* 소스 필터 */}
      <div style={{ marginBottom:20 }}>
        <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
          {RADIO.map(r => <button key={r.id} onClick={() => setSelSrc(selSrc===r.name?null:r.name)} style={{ padding:'6px 14px', borderRadius:20, cursor:'pointer', border:`1.5px solid ${selSrc===r.name?r.color:'#ddd'}`, background:selSrc===r.name?r.color+'12':'#fff', color:selSrc===r.name?r.color:'#555', fontSize:12, fontWeight:600 }}><span style={{ display:'inline-block', width:7, height:7, borderRadius:'50%', background:r.color, marginRight:6, verticalAlign:'middle' }} />{r.name}</button>)}
        </div>
      </div>

      {/* 로딩 */}
      {loading && (
        <div style={{ textAlign:'center', padding:'60px 20px' }}>
          <div style={{ width:40, height:40, border:'3px solid #eee', borderTopColor:'#1a1a1a', borderRadius:'50%', margin:'0 auto 16px', animation:'spin .8s linear infinite' }} />
          <div style={{ fontSize:15, fontWeight:600, color:'#333' }}>브리핑 불러오는 중...</div>
        </div>
      )}

      {/* 에러 */}
      {error && !loading && (
        <div style={{ padding:'20px', background:'#FFF5F5', border:'1px solid #FDD', borderRadius:12, textAlign:'center' }}>
          <div style={{ fontSize:14, color:'#C00', marginBottom:12 }}>{error}</div>
          <button onClick={loadBriefing} style={{ padding:'8px 16px', border:'1px solid #C00', borderRadius:8, background:'#fff', color:'#C00', fontSize:13, cursor:'pointer' }}>다시 시도</button>
        </div>
      )}

      {/* 브리핑 */}
      {briefing && !loading && (
        <div style={{ animation:'fadeIn .4s ease' }}>
          {briefing.one_liner && <div style={{ padding:'16px 20px', background:'#1a1a1a', borderRadius:12, marginBottom:16, color:'#fff', fontSize:15, fontWeight:600, lineHeight:1.6 }}>📌 {briefing.one_liner}</div>}
          {briefing.data_quality && <div style={{ padding:'10px 14px', background:'#F0F7FF', border:'1px solid #D0E3F7', borderRadius:8, marginBottom:16, fontSize:12, color:'#2C5F8A' }}>📊 {briefing.data_quality}</div>}

          {/* 키워드 필터 */}
          <div style={{ display:'flex', gap:6, flexWrap:'wrap', marginBottom:20 }}>
            <span style={{ fontSize:12, color:'#999', alignSelf:'center', marginRight:4 }}>필터:</span>
            {KW.map(k => <button key={k} onClick={() => setKws(p => { const n=new Set(p); n.has(k)?n.delete(k):n.add(k); return n; })} style={{ padding:'4px 12px', borderRadius:14, border:'1px solid #ddd', cursor:'pointer', background:kws.has(k)?(k.includes('평택')?'#FF6B00':'#1a1a1a'):'#fff', color:kws.has(k)?'#fff':k.includes('평택')?'#FF6B00':'#888', fontSize:12, fontWeight:k.includes('평택')?700:500 }}>{k}</button>)}
          </div>

          {/* 섹션 */}
          {filtered().map((sec, si) => <div key={si} style={{ marginBottom:28 }}>
            <div style={{ fontSize:13, fontWeight:700, color:sec.category?.includes('평택')?'#FF6B00':'#555', letterSpacing:'0.05em', marginBottom:12, display:'flex', alignItems:'center', gap:6 }}><span style={{ fontSize:16 }}>{sec.icon}</span>{sec.category}<span style={{ fontSize:11, color:'#bbb', fontWeight:400 }}>· {sec.items.length}건</span></div>
            {sec.items.map((item, ii) => {
              const key = item.id || `${si}-${ii}`;
              const open = openPanels.has(key);
              return <div key={ii} style={{ background:'#fff', borderRadius:10, marginBottom:10, borderLeft:`3px solid ${ic[item.importance]||'#999'}`, boxShadow:open?'0 2px 12px rgba(0,0,0,0.08)':'0 1px 3px rgba(0,0,0,0.04)', overflow:'hidden' }}>
                <div onClick={() => togglePanel(key)} style={{ padding:'16px 18px', cursor:'pointer' }}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
                    <div style={{ fontSize:15, fontWeight:700, color:'#111', marginBottom:4, lineHeight:1.4, flex:1 }}>{item.headline}</div>
                    <span style={{ fontSize:16, color:'#bbb', marginLeft:8, transform:open?'rotate(180deg)':'none', transition:'transform .2s' }}>▾</span>
                  </div>
                  {item.source_detail && <div style={{ fontSize:11, color:'#999', marginBottom:6, fontStyle:'italic' }}>{item.source_detail}</div>}
                  <div style={{ fontSize:13, color:'#444', lineHeight:1.7, marginBottom:8, wordBreak:'keep-all' }}>{item.summary}</div>
                  <div style={{ display:'flex', gap:6, flexWrap:'wrap', alignItems:'center' }}>
                    {item.sources?.map((s,j) => <Badge key={j} source={s} />)}
                    <span style={{ fontSize:10, color:'#bbb', marginLeft:'auto' }}>{il[item.importance]}</span>
                  </div>
                </div>
                {/* 녹취록 패널 — raw_sources에서 매칭 */}
                {open && briefing.raw_sources && (
                  <div style={{ padding:'0 18px 16px' }}>
                    <div style={{ background:'#F7F6F3', borderRadius:10, padding:16, borderTop:'2px solid #E8E6E1' }}>
                      <div style={{ fontSize:13, fontWeight:700, marginBottom:10 }}>🔍 관련 원문</div>
                      {briefing.raw_sources
                        .filter(rs => item.sources?.some(s => rs.source.includes(s) || s.includes(rs.source)))
                        .slice(0, 3)
                        .map((rs, ri) => (
                          <div key={ri} style={{ background:'#fff', borderRadius:8, padding:14, marginBottom:8, border:'1px solid #E8E6E1' }}>
                            <div style={{ fontSize:12, fontWeight:600, color:'#555', marginBottom:6 }}>📄 {rs.source} — {rs.title?.slice(0,50)}</div>
                            {rs.url && <a href={rs.url} target="_blank" rel="noopener noreferrer" style={{ fontSize:11, color:'#0068B7', display:'block', marginBottom:6 }}>{rs.url} ↗</a>}
                            {rs.video_id && <a href={`https://youtube.com/watch?v=${rs.video_id}`} target="_blank" rel="noopener noreferrer" style={{ fontSize:11, color:'#0068B7', display:'block', marginBottom:6 }}>▶️ 유튜브 원본 ↗</a>}
                            <div style={{ fontSize:13, color:'#222', lineHeight:1.85, padding:'10px 14px', background:'#FAFAF8', borderLeft:'3px solid #D4D0C8', borderRadius:'0 6px 6px 0', fontFamily:"'Noto Serif KR', serif", wordBreak:'keep-all', whiteSpace:'pre-wrap', maxHeight:300, overflow:'auto' }}>{rs.text}</div>
                          </div>
                        ))}
                      {briefing.raw_sources.filter(rs => item.sources?.some(s => rs.source.includes(s) || s.includes(rs.source))).length === 0 && (
                        <div style={{ fontSize:13, color:'#999', textAlign:'center', padding:12 }}>매칭되는 원문이 없습니다.</div>
                      )}
                    </div>
                  </div>
                )}
              </div>;
            })}
          </div>)}

          <button onClick={loadBriefing} style={{ width:'100%', padding:14, border:'1px solid #ddd', borderRadius:10, background:'#fff', color:'#555', fontSize:14, fontWeight:600, cursor:'pointer', marginTop:8 }}>🔄 새로고침</button>
        </div>
      )}

      <div style={{ marginTop:40, paddingTop:20, borderTop:'1px solid #e0e0e0', fontSize:11, color:'#bbb', textAlign:'center', lineHeight:1.8 }}>
        CBS 뉴스쇼 · MBC 시선집중 · SBS 정치쇼 · KBS 전격시사 · 뉴스공장<br/>매일 오전 8시 · 오후 1시 자동 업데이트
      </div>
    </div>
  );
}
