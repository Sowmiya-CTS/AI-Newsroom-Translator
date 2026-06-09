import React, { useState, useCallback } from 'react';
import { getArticle, editorAction, getArticleSummary, checkTone } from '../../services/api';

function PipelineStatus({ article }) {
  const steps = ['pending', 'processing', 'review', 'approved', 'published'];
  const rejected = article.status === 'rejected';
  const currentIdx = steps.indexOf(article.status);

  return (
    <div className="pipeline-track" style={{ gap: 4 }}>
      {steps.map((s, i) => {
        const done = rejected ? false : i < currentIdx;
        const active = !rejected && i === currentIdx;
        return (
          <React.Fragment key={s}>
            <div className={`pipeline-step ${done ? 'done' : active ? 'active' : ''}`} style={{ padding: '5px 10px', fontSize: 11 }}>
              {done ? '✓' : active ? '◉' : '○'} {s}
            </div>
            {i < steps.length - 1 && <span className="pipeline-arrow" style={{ fontSize: 10 }}>→</span>}
          </React.Fragment>
        );
      })}
      {rejected && (
        <div className="pipeline-step" style={{ background: 'rgba(239,68,68,0.08)', borderColor: 'rgba(239,68,68,0.25)', color: 'var(--red)', padding: '5px 10px', fontSize: 11, marginLeft: 8 }}>
          ✕ rejected
        </div>
      )}
    </div>
  );
}

function SensitivityPanel({ sensitivity }) {
  if (!sensitivity) return (
    <div className="empty-state" style={{ padding: 20 }}>
      <p>Sensitivity analysis pending...</p>
    </div>
  );

  return (
    <div>
      <div className={`sensitivity-overview ${sensitivity.overall_level}`}>
        <div className="sensitivity-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className={`badge severity-${sensitivity.overall_level}`} style={{ fontSize: 12, padding: '4px 12px' }}>
              {sensitivity.overall_level.toUpperCase()}
            </span>
            <span style={{ fontWeight: 600 }}>Sensitivity Level</span>
          </div>
          <span style={{ fontSize: 13, fontWeight: 600 }} className={sensitivity.safe_to_publish ? '' : ''}>
            {sensitivity.safe_to_publish
              ? <span style={{ color: 'var(--green)' }}>✓ Safe to Publish</span>
              : <span style={{ color: 'var(--red)' }}>✗ Requires Review</span>
            }
          </span>
        </div>
        <p className="sensitivity-rec">{sensitivity.recommendation}</p>
      </div>

      {sensitivity.flags?.length > 0 ? (
        <div className="flag-list">
          {sensitivity.flags.map((f, i) => (
            <div key={i} className="flag-item">
              <div className="flag-item-header">
                <span className={`badge severity-${f.severity}`}>{f.severity}</span>
                <span className="flag-category">{f.category}</span>
              </div>
              <p className="flag-desc">{f.description}</p>
              {f.flagged_text && <div className="flag-text">"{f.flagged_text}"</div>}
            </div>
          ))}
        </div>
      ) : (
        <div className="alert alert-success">No specific content flags raised. Article appears suitable for publication.</div>
      )}
    </div>
  );
}

function TranslationPanel({ article, addToast, onRefresh }) {
  const [activeLang, setActiveLang] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [loading, setLoading] = useState('');
  const [toneResult, setToneResult] = useState(null);
  const [summary, setSummary] = useState('');

  const translations = article.translations || [];
  const active = activeLang
    ? translations.find(t => t.language_code === activeLang)
    : translations[0];

  const doRetranslate = async () => {
    if (!active) return;
    setLoading('retranslate');
    try {
      await editorAction(article.id, {
        article_id: article.id,
        action: 'request_retranslation',
        language_code: active.language_code,
      });
      addToast('info', 'Retranslating', `Fresh translation requested for ${active.language_name}`);
      setTimeout(onRefresh, 3000);
    } catch(e) { addToast('error', 'Failed', e.message); }
    setLoading('');
  };

  const doSaveEdit = async () => {
    setLoading('edit');
    try {
      await editorAction(article.id, {
        article_id: article.id,
        action: 'edit',
        language_code: active.language_code,
        modified_content: editContent,
      });
      addToast('success', 'Saved', `${active.language_name} translation updated.`);
      setEditMode(false);
      onRefresh();
    } catch(e) { addToast('error', 'Save Failed', e.message); }
    setLoading('');
  };

  const doToneCheck = async () => {
    setLoading('tone');
    try {
      const res = await checkTone(article.id, active?.language_code || 'en');
      setToneResult(res.data.analysis);
    } catch(e) { addToast('error', 'Tone check failed', e.message); }
    setLoading('');
  };

  const doSummary = async () => {
    setLoading('summary');
    try {
      const res = await getArticleSummary(article.id);
      setSummary(res.data.summary);
    } catch(e) { addToast('error', 'Summary failed', e.message); }
    setLoading('');
  };

  if (translations.length === 0) return (
    <div className="empty-state">
      <div className="empty-icon">⏳</div>
      <p>Translations are being generated.<br />Check back in a few moments.</p>
    </div>
  );

  return (
    <div>
      <div className="lang-tab-row">
        {translations.map(t => (
          <button
            key={t.language_code}
            className={`lang-chip-btn ${(activeLang || translations[0]?.language_code) === t.language_code ? 'active' : ''}`}
            onClick={() => { setActiveLang(t.language_code); setEditMode(false); setToneResult(null); }}
          >
            <div className={`lang-status-dot ${t.status}`} />
            {t.language_name}
            <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{Math.round(t.tone_score * 100)}%</span>
          </button>
        ))}
      </div>

      {active && (
        <div className="translation-body">
          <div className="translation-title">{active.translated_title}</div>

          {editMode ? (
            <textarea
              className="form-textarea"
              rows={8}
              value={editContent}
              onChange={e => setEditContent(e.target.value)}
              style={{ marginBottom: 10 }}
            />
          ) : (
            <p className="translation-content">{active.translated_content}</p>
          )}

          {active.cultural_adaptations?.length > 0 && (
            <div className="adaptations-box">
              <div className="adaptations-label">Cultural Adaptations ({active.cultural_adaptations.length})</div>
              {active.cultural_adaptations.map((a, i) => (
                <div key={i} className="adaptation-item">{a}</div>
              ))}
            </div>
          )}

          <div className="tone-bar">
            <span style={{ fontSize: 11, color: 'var(--text-muted)', minWidth: 80 }}>Tone Score</span>
            <div className="tone-bar-track">
              <div className="tone-bar-fill" style={{ width: `${active.tone_score * 100}%` }} />
            </div>
            <span className="tone-score-label">{Math.round(active.tone_score * 100)}%</span>
          </div>

          {active.notes && (
            <div className="alert alert-info" style={{ marginTop: 10, fontSize: 12 }}>
              <strong>Translator Note:</strong> {active.notes}
            </div>
          )}

          <div className="translation-actions">
            {editMode ? (
              <>
                <button className="btn btn-success btn-sm" onClick={doSaveEdit} disabled={loading === 'edit'}>
                  {loading === 'edit' ? '...' : '✓ Save Edit'}
                </button>
                <button className="btn btn-ghost btn-sm" onClick={() => setEditMode(false)}>Cancel</button>
              </>
            ) : (
              <button className="btn btn-ghost btn-sm" onClick={() => { setEditMode(true); setEditContent(active.translated_content); }}>
                ✎ Edit Translation
              </button>
            )}
            <button className="btn btn-ghost btn-sm" onClick={doRetranslate} disabled={loading === 'retranslate'}>
              {loading === 'retranslate' ? '...' : '↻ Retranslate'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={doToneCheck} disabled={loading === 'tone'}>
              {loading === 'tone' ? '...' : '◎ Tone Check'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={doSummary} disabled={loading === 'summary'}>
              {loading === 'summary' ? '...' : '≡ Summary'}
            </button>
          </div>

          {toneResult && (
            <div style={{ marginTop: 12, background: 'var(--bg-card)', borderRadius: 'var(--radius-sm)', padding: 12, border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600 }}>Tone Analysis</span>
                <span style={{ fontSize: 12, color: toneResult.is_broadcast_ready ? 'var(--green)' : 'var(--red)' }}>
                  {toneResult.is_broadcast_ready ? '✓ Broadcast Ready' : '✗ Needs Revision'}
                </span>
              </div>
              {toneResult.suggestions?.map((s, i) => (
                <div key={i} style={{ fontSize: 12, color: 'var(--text-muted)', padding: '3px 0' }}>• {s}</div>
              ))}
            </div>
          )}

          {summary && (
            <div className="alert alert-info" style={{ marginTop: 10 }}>
              <strong>Broadcast Summary:</strong> {summary}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ReviewPage({ articles, liveEvents, addToast, onRefresh }) {
  const [selected, setSelected] = useState(null);
  const [activeTab, setActiveTab] = useState('sensitivity');
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [editorNote, setEditorNote] = useState('');
  const [actionLoading, setActionLoading] = useState('');
  const [fullArticle, setFullArticle] = useState(null);

  const handleSelect = useCallback(async (a) => {
    setSelected(a);
    setActiveTab('sensitivity');
    setToneResult(null);
    try {
      const res = await getArticle(a.id);
      setFullArticle(res.data);
    } catch(e) {}
  }, []);

  const [toneResult, setToneResult] = useState(null);

  const refreshFull = async () => {
    onRefresh();
    if (selected) {
      try {
        const res = await getArticle(selected.id);
        setFullArticle(res.data);
      } catch(e) {}
    }
  };

  const doAction = async (action) => {
    if (!selected) return;
    setActionLoading(action);
    try {
      await editorAction(selected.id, {
        article_id: selected.id,
        action,
        editor_note: editorNote || undefined,
      });
      const messages = { approve: 'Article approved.', reject: 'Article rejected.', publish: 'Article published!' };
      addToast(action === 'publish' ? 'success' : action === 'reject' ? 'warning' : 'success', 'Action Applied', messages[action]);
      setEditorNote('');
      refreshFull();
    } catch(e) {
      addToast('error', 'Action Failed', e.message);
    }
    setActionLoading('');
  };

  const article = fullArticle || selected;

  const getEventForId = (id) => liveEvents.find(e => e.article_id === id);

  const filtered = articles.filter(a => {
    const matchSearch = !search || a.title.toLowerCase().includes(search.toLowerCase()) || a.id.toLowerCase().includes(search.toLowerCase());
    const matchStatus = !filterStatus || a.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const statusFilters = ['', 'review', 'processing', 'approved', 'published', 'rejected'];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 16, height: 'calc(100vh - 100px)' }}>
      {/* Left: Article List */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '14px' }}>
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 10 }}>Review Queue ({filtered.length})</div>
          <div className="search-bar">
            <span>🔍</span>
            <input placeholder="Search articles..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
            {statusFilters.map(s => (
              <button key={s} onClick={() => setFilterStatus(s)}
                style={{
                  padding: '3px 10px', borderRadius: 20, fontSize: 11, cursor: 'pointer',
                  background: filterStatus === s ? 'var(--blue)' : 'var(--bg-elevated)',
                  color: filterStatus === s ? 'white' : 'var(--text-muted)',
                  border: `1px solid ${filterStatus === s ? 'var(--blue)' : 'var(--border)'}`,
                }}
              >{s || 'All'}</button>
            ))}
          </div>
        </div>

        <div className="article-list" style={{ flex: 1, overflowY: 'auto' }}>
          {filtered.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <p>No articles match the filter.</p>
            </div>
          )}
          {filtered.map(a => {
            const ev = getEventForId(a.id);
            return (
              <div key={a.id} className={`article-item ${selected?.id === a.id ? 'selected' : ''}`} onClick={() => handleSelect(a)}>
                <div className="article-item-header">
                  <span className="article-item-id">#{a.id}</span>
                  <span className={`badge badge-${a.status}`}>{a.status}</span>
                  {a.sensitivity && (
                    <span className={`badge severity-${a.sensitivity.overall_level}`}>{a.sensitivity.overall_level}</span>
                  )}
                  {a.priority === 'breaking' && <span className="priority-breaking">⚡</span>}
                </div>
                <div className="article-item-title">{a.title}</div>
                <div className="article-item-meta">
                  <span>{a.source}</span>
                  <span>{a.translations?.length || 0} langs</span>
                  <span>{new Date(a.created_at).toLocaleTimeString()}</span>
                </div>
                {ev && (
                  <div className="live-pulse">
                    <div className="pulse-dot" />
                    {ev.event === 'translation_done' ? `${ev.language} translated` :
                     ev.event === 'ready_for_review' ? 'Ready for review!' :
                     ev.event === 'sensitivity_done' ? 'Analyzed' : ev.event}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right: Article Detail */}
      <div style={{ overflowY: 'auto' }}>
        {!article ? (
          <div className="card" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="empty-state">
              <div className="empty-icon">◈</div>
              <p>Select an article from the queue<br />to begin editorial review.</p>
            </div>
          </div>
        ) : (
          <div className="detail-wrapper">
            {/* Header */}
            <div className="detail-article-header">
              <div className="detail-meta-row">
                <span className="article-item-id">#{article.id}</span>
                <span className={`badge badge-${article.status}`}>{article.status.toUpperCase()}</span>
                {article.sensitivity && (
                  <span className={`badge severity-${article.sensitivity.overall_level}`}>
                    {article.sensitivity.overall_level.toUpperCase()} SENSITIVITY
                  </span>
                )}
                {article.priority === 'breaking' && <span className="priority-breaking">⚡ BREAKING NEWS</span>}
              </div>

              <h2 className="detail-title">{article.title}</h2>

              <div className="detail-meta">
                <span>📰 {article.source}</span>
                <span>🏷 {article.category}</span>
                <span>🌐 {article.translations?.length || 0} translations</span>
                <span>🕐 {new Date(article.created_at).toLocaleString()}</span>
              </div>

              <PipelineStatus article={article} />

              <div className="original-box">{article.content}</div>

              {/* Editor Note */}
              <div style={{ marginTop: 12 }}>
                <input
                  className="form-input"
                  placeholder="Add an editor note (optional — logged with action)..."
                  value={editorNote}
                  onChange={e => setEditorNote(e.target.value)}
                />
              </div>

              {/* Action Buttons */}
              <div className="detail-actions">
                {article.status === 'review' && (
                  <>
                    <button className="btn btn-success" onClick={() => doAction('approve')} disabled={!!actionLoading}>
                      {actionLoading === 'approve' ? '...' : '✓ Approve'}
                    </button>
                    <button className="btn btn-danger" onClick={() => doAction('reject')} disabled={!!actionLoading}>
                      {actionLoading === 'reject' ? '...' : '✕ Reject'}
                    </button>
                  </>
                )}
                {article.status === 'approved' && (
                  <button className="btn btn-primary" onClick={() => doAction('publish')} disabled={!!actionLoading}>
                    {actionLoading === 'publish' ? '...' : '▲ Publish to All Regions'}
                  </button>
                )}
                {article.status === 'rejected' && (
                  <button className="btn btn-ghost" onClick={() => doAction('approve')} disabled={!!actionLoading}>
                    ↩ Reinstate & Approve
                  </button>
                )}
                {['review', 'approved', 'published'].includes(article.status) && (
                  <button className="btn btn-cyan btn-sm" onClick={refreshFull}>↻ Refresh</button>
                )}
              </div>
            </div>

            {/* Tabs */}
            <div className="card" style={{ padding: '14px 16px' }}>
              <div className="tabs">
                <button className={`tab-btn ${activeTab === 'sensitivity' ? 'active' : ''}`} onClick={() => setActiveTab('sensitivity')}>
                  ⚑ Sensitivity
                  {article.sensitivity?.flags?.length > 0 && (
                    <span className="tab-count">{article.sensitivity.flags.length}</span>
                  )}
                </button>
                <button className={`tab-btn ${activeTab === 'translations' ? 'active' : ''}`} onClick={() => setActiveTab('translations')}>
                  🌐 Translations
                  <span className="tab-count">{article.translations?.length || 0}</span>
                </button>
                <button className={`tab-btn ${activeTab === 'notes' ? 'active' : ''}`} onClick={() => setActiveTab('notes')}>
                  📝 Editor Notes
                  {article.editor_notes?.length > 0 && (
                    <span className="tab-count">{article.editor_notes.length}</span>
                  )}
                </button>
              </div>

              {activeTab === 'sensitivity' && <SensitivityPanel sensitivity={article.sensitivity} />}

              {activeTab === 'translations' && (
                <TranslationPanel article={article} addToast={addToast} onRefresh={refreshFull} />
              )}

              {activeTab === 'notes' && (
                <div>
                  {(!article.editor_notes || article.editor_notes.length === 0) ? (
                    <div className="empty-state">No editor notes yet.</div>
                  ) : (
                    article.editor_notes.map((n, i) => (
                      <div key={i} style={{ padding: '10px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
                        <span style={{ color: 'var(--blue)', fontWeight: 600 }}>{n.action}</span>
                        <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>{n.note}</span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
