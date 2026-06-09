import React from 'react';

const NAV = [
  { id: 'dashboard',  icon: '▦',  label: 'Dashboard' },
  { id: 'ingest',     icon: '⊕',  label: 'Ingest Content' },
  { id: 'review',     icon: '◈',  label: 'Review Queue' },
  { id: 'published',  icon: '◉',  label: 'Published' },
  { id: 'analytics',  icon: '▣',  label: 'Analytics' },
];

export default function Sidebar({ page, onNavigate, reviewCount, processingCount }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">📡</div>
        <div className="brand-name">
          AI Newsroom<br /><span>Assistant</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>

        {NAV.map(n => (
          <button
            key={n.id}
            className={`nav-item ${page === n.id ? 'active' : ''}`}
            onClick={() => onNavigate(n.id)}
          >
            <span className="nav-icon">{n.icon}</span>
            {n.label}
            {n.id === 'review' && reviewCount > 0 && (
              <span className="nav-badge">{reviewCount}</span>
            )}
            {n.id === 'ingest' && processingCount > 0 && (
              <span className="nav-badge blue">{processingCount}</span>
            )}
          </button>
        ))}

        <div className="nav-section-label" style={{ marginTop: 12 }}>Languages</div>
        <div style={{ padding: '6px 12px', fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.8 }}>
          Hindi • Tamil • Telugu<br />
          Bengali • Marathi • Gujarati<br />
          Kannada • Malayalam<br />
          Punjabi • Odia<br />
          French • Spanish • Arabic
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="live-indicator">
          <div className="pulse-dot" />
          <span>AI Pipeline Active</span>
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 8, padding: '0 4px' }}>
          Powered by Claude claude-sonnet-4-6<br />
          Cognizant CODEX Hackathon 2026
        </div>
      </div>
    </aside>
  );
}
