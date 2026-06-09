import React from 'react';

const STAT_CONFIG = [
  { key: 'total',             label: 'Total Articles',    color: 'blue',   icon: '◈' },
  { key: 'processing',        label: 'Processing',        color: 'cyan',   icon: '⟳' },
  { key: 'review',            label: 'Awaiting Review',   color: 'yellow', icon: '◉' },
  { key: 'approved',          label: 'Approved',          color: 'green',  icon: '✓' },
  { key: 'published',         label: 'Published',         color: 'purple', icon: '▲' },
  { key: 'total_translations',label: 'Translations Done', color: 'teal',   icon: '⬡' },
  { key: 'critical_flags',    label: 'Critical Flags',    color: 'red',    icon: '⚑' },
  { key: 'rejected',          label: 'Rejected',          color: 'gray',   icon: '✕' },
];

function ActivityDot({ event }) {
  if (event.event === 'translation_done') return <div className="activity-dot green" />;
  if (event.event === 'sensitivity_done') return <div className="activity-dot yellow" />;
  if (event.event === 'ready_for_review') return <div className="activity-dot purple" />;
  if (event.event === 'editor_action')    return <div className="activity-dot" />;
  if (event.event === 'translation_error') return <div className="activity-dot red" />;
  return <div className="activity-dot" />;
}

function ActivityText({ event }) {
  const id = <strong>#{event.article_id}</strong>;
  switch (event.event) {
    case 'translation_done':  return <>{id} — {event.language} translation complete</>;
    case 'sensitivity_done':  return <>{id} — Sensitivity analysis complete</>;
    case 'ready_for_review':  return <>{id} — Ready for editor review</>;
    case 'editor_action':     return <>{id} — Editor: {event.action}</>;
    case 'translation_error': return <>{id} — Translation failed: {event.language}</>;
    case 'status_update':     return <>{id} — Status → {event.status}</>;
    default: return <>{id} — {event.event}</>;
  }
}

export default function DashboardPage({ stats, articles, liveEvents, onNavigate }) {
  const recent = (articles || []).slice(0, 5);

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Newsroom Dashboard</h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Real-time overview of your AI content localization pipeline
        </p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {STAT_CONFIG.map(s => (
          <div key={s.key} className={`stat-card ${s.color}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="stat-value">{stats ? (stats[s.key] ?? 0) : '—'}</div>
                <div className="stat-label">{s.label}</div>
              </div>
              <span style={{ fontSize: 22, opacity: 0.25 }}>{s.icon}</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16 }}>
        {/* Recent Articles */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Recent Articles</div>
              <div className="card-sub">Latest ingested content</div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => onNavigate('review')}>
              View All →
            </button>
          </div>

          {recent.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📰</div>
              <p>No articles yet.<br />Go to <strong>Ingest Content</strong> to get started.</p>
            </div>
          ) : (
            <div className="article-list">
              {recent.map(a => (
                <div key={a.id} className="article-item" onClick={() => onNavigate('review')}>
                  <div className="article-item-header">
                    <span className="article-item-id">#{a.id}</span>
                    <span className={`badge badge-${a.status}`}>{a.status}</span>
                    {a.sensitivity && (
                      <span className={`badge severity-${a.sensitivity.overall_level}`}>
                        {a.sensitivity.overall_level}
                      </span>
                    )}
                    {a.priority === 'breaking' && <span className="priority-breaking">⚡ BREAKING</span>}
                    {a.priority === 'high' && a.priority !== 'breaking' && <span className="priority-high">↑ HIGH</span>}
                  </div>
                  <div className="article-item-title">{a.title}</div>
                  <div className="article-item-meta">
                    <span>{a.source}</span>
                    <span>{a.category}</span>
                    <span>{a.translations?.length || 0} translations</span>
                    <span>{new Date(a.created_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Activity Feed */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Live Activity</div>
              <div className="card-sub">Real-time pipeline events</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--green)' }}>
              <div className="pulse-dot" />
              LIVE
            </div>
          </div>

          {liveEvents.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px' }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>📡</div>
              <p>Waiting for pipeline events.<br />Ingest an article to begin.</p>
            </div>
          ) : (
            <div className="activity-feed" style={{ maxHeight: 380, overflowY: 'auto' }}>
              {liveEvents.map((e, i) => (
                <div key={i} className="activity-row">
                  <ActivityDot event={e} />
                  <div className="activity-body"><ActivityText event={e} /></div>
                  <div className="activity-time">now</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Pipeline Overview */}
      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-title" style={{ marginBottom: 14 }}>How It Works — AI Processing Pipeline</div>
        <div className="pipeline-track" style={{ flexWrap: 'wrap', gap: 8 }}>
          {[
            { label: '1. Ingest', desc: 'Article or transcript', icon: '⊕' },
            { label: '2. Transcribe', desc: 'Clean & structure', icon: '◐' },
            { label: '3. Sensitivity', desc: 'Flag content risk', icon: '⚑' },
            { label: '4. Translate', desc: '14 regional languages', icon: '⬡' },
            { label: '5. Adapt', desc: 'Cultural localization', icon: '◈' },
            { label: '6. Review', desc: 'Editor approval', icon: '◉' },
            { label: '7. Publish', desc: 'Broadcast ready', icon: '▲' },
          ].map((s, i, arr) => (
            <React.Fragment key={s.label}>
              <div className="pipeline-step done">
                <span>{s.icon}</span>
                <div>
                  <div style={{ fontWeight: 600 }}>{s.label}</div>
                  <div style={{ fontSize: 10, opacity: 0.7 }}>{s.desc}</div>
                </div>
              </div>
              {i < arr.length - 1 && <span className="pipeline-arrow">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
