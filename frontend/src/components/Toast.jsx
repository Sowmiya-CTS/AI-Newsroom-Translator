import React from 'react';

const ICONS = { success: '✓', info: 'ℹ', warning: '⚠', error: '✗' };

export default function Toast({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`}>
          <span className="toast-icon">{ICONS[t.type] || '•'}</span>
          <div className="toast-text">
            {t.title && <strong>{t.title}</strong>}
            <span>{t.message}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
