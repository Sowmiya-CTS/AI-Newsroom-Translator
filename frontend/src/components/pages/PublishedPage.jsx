import React, { useState } from 'react';

export default function PublishedPage({ articles }) {
  const [selected, setSelected] = useState(null);
  const published = articles.filter(a => a.status === 'published');

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Published Articles</h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {published.length} article{published.length !== 1 ? 's' : ''} live across all regions
          </p>
        </div>
      </div>

      {published.length === 0 ? (
        <div className="card" style={{ padding: 48 }}>
          <div className="empty-state">
            <div className="empty-icon">📡</div>
            <p>No published articles yet.<br />
            Approve and publish articles from the <strong>Review Queue</strong>.</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 420px' : '1fr', gap: 16 }}>
          <div className="published-grid">
            {published.map(a => (
              <div
                key={a.id}
                className="published-card"
                onClick={() => setSelected(selected?.id === a.id ? null : a)}
                style={selected?.id === a.id ? { borderColor: 'var(--cyan)', background: 'rgba(6,182,212,0.04)' } : {}}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <span className="published-card-badge">● LIVE</span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>#{a.id}</span>
                </div>

                <h3>{a.title}</h3>

                <div style={{ display: 'flex', gap: 10, fontSize: 11, color: 'var(--text-muted)', margin: '8px 0' }}>
                  <span>📰 {a.source}</span>
                  <span>🏷 {a.category}</span>
                </div>

                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 10 }}>
                  {a.content?.slice(0, 120)}...
                </div>

                <div className="lang-chips-row">
                  {(a.translations || []).map(t => (
                    <span key={t.language_code} className="lang-mini">{t.language_name}</span>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, fontSize: 11, color: 'var(--text-muted)' }}>
                  <span>🌐 {a.translations?.length || 0} languages</span>
                  <span>{new Date(a.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          {selected && (
            <div className="card" style={{ position: 'sticky', top: 0, maxHeight: 'calc(100vh - 100px)', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                <div>
                  <span className="published-card-badge">● LIVE — #{selected.id}</span>
                  <h3 style={{ fontSize: 15, fontWeight: 700, lineHeight: 1.4, marginTop: 4 }}>{selected.title}</h3>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                    {selected.source} • {selected.category} • {new Date(selected.updated_at).toLocaleString()}
                  </div>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>✕</button>
              </div>

              <div className="divider" />

              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 16 }}>
                {selected.content}
              </div>

              <div className="section-label">Published in {selected.translations?.length} Languages</div>
              {(selected.translations || []).map(t => (
                <div key={t.language_code} style={{
                  background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-sm)', padding: '12px 14px', marginBottom: 8
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{t.language_name}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Tone {Math.round(t.tone_score * 100)}%</span>
                      <span className={`badge severity-safe`} style={{ fontSize: 10 }}>
                        {t.status === 'editor_revised' ? 'Editor Revised' : 'AI Translated'}
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>{t.translated_title}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {t.translated_content?.slice(0, 200)}...
                  </div>
                  {t.cultural_adaptations?.length > 0 && (
                    <div style={{ marginTop: 8, fontSize: 11, color: 'var(--cyan)' }}>
                      {t.cultural_adaptations.length} cultural adaptation{t.cultural_adaptations.length !== 1 ? 's' : ''} applied
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
