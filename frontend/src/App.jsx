import React, { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Toast from './components/Toast';
import DashboardPage from './components/pages/DashboardPage';
import IngestPage from './components/pages/IngestPage';
import ReviewPage from './components/pages/ReviewPage';
import PublishedPage from './components/pages/PublishedPage';
import AnalyticsPage from './components/pages/AnalyticsPage';
import { getStats, getArticles, ingestArticle, createWebSocket } from './services/api';
import './App.css';

const DEMO_ARTICLE = {
  title: 'Major Earthquake Strikes Off Japan Coast — Tsunami Warning Issued',
  content: 'A powerful earthquake measuring 7.2 on the Richter scale struck off the northeastern coast of Japan at 5:48 AM local time on Thursday. The Japan Meteorological Agency immediately issued a tsunami warning for coastal prefectures including Iwate, Miyagi, and Fukushima. Residents within one kilometer of the coast have been ordered to evacuate to higher ground. The epicenter was located approximately 80 kilometers east of Sendai at a depth of 35 kilometers. Emergency response teams from the Japan Self-Defense Forces have been deployed to affected areas. At least 12 injuries have been reported in Sendai city, though no fatalities have been confirmed. The government has convened an emergency response committee and Prime Minister's office is coordinating relief efforts. International agencies including the Pacific Tsunami Warning Center have extended warnings to neighboring countries. Nuclear facilities in the region have been placed on precautionary alert status.',
  source: 'AP Wire / NHK',
  category: 'International',
  priority: 'breaking',
  target_languages: ['hi', 'ta', 'te', 'bn', 'mr', 'gu']
};

let toastIdCounter = 0;

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [articles, setArticles] = useState([]);
  const [liveEvents, setLiveEvents] = useState([]);
  const [toasts, setToasts] = useState([]);
  const [demoRunning, setDemoRunning] = useState(false);
  const wsRef = useRef(null);

  const addToast = useCallback((type, title, message) => {
    const id = ++toastIdCounter;
    setToasts(prev => [{ id, type, title, message }, ...prev.slice(0, 4)]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 5000);
  }, []);

  const loadData = useCallback(async () => {
    try {
      const [statsRes, articlesRes] = await Promise.all([getStats(), getArticles()]);
      setStats(statsRes.data);
      setArticles(articlesRes.data.articles);
    } catch (e) {}
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, [loadData]);

  useEffect(() => {
    const connect = () => {
      try {
        const ws = createWebSocket((event) => {
          setLiveEvents(prev => [event, ...prev.slice(0, 29)]);

          if (event.event === 'translation_done') {
            addToast('success', 'Translation Complete', `${event.language} ready for #${event.article_id}`);
          } else if (event.event === 'ready_for_review') {
            addToast('info', 'Ready for Review', `Article #${event.article_id} is in the editor queue`);
          } else if (event.event === 'sensitivity_done') {
            const level = event.sensitivity?.overall_level;
            if (level === 'high' || level === 'critical') {
              addToast('warning', 'Sensitivity Alert', `#${event.article_id} flagged as ${level}`);
            }
          } else if (event.event === 'editor_action') {
            addToast('info', 'Editor Action', `Article #${event.article_id}: ${event.action}`);
          }
          loadData();
        });
        wsRef.current = ws;
        ws.onclose = () => setTimeout(connect, 3000);
      } catch(e) {}
    };
    connect();
    return () => wsRef.current?.close();
  }, [addToast, loadData]);

  const runLiveDemo = async () => {
    setDemoRunning(true);
    addToast('info', '⚡ Live Demo', 'Ingesting breaking news article...');
    try {
      const res = await ingestArticle(DEMO_ARTICLE);
      addToast('success', 'Demo Started', `Article #${res.data.article_id} created. Watch the pipeline run!`);
      setPage('dashboard');
      loadData();
    } catch(e) {
      addToast('error', 'Demo Failed', 'Make sure the backend is running on port 8000.');
    }
    setTimeout(() => setDemoRunning(false), 30000);
  };

  const reviewCount = articles.filter(a => a.status === 'review').length;
  const processingCount = articles.filter(a => a.status === 'processing').length;

  const PAGE_TITLES = {
    dashboard: { title: 'Newsroom Dashboard', sub: 'Real-time AI Content Localization' },
    ingest:    { title: 'Ingest Content',      sub: 'Submit articles or broadcast transcripts' },
    review:    { title: 'Review Queue',         sub: 'Editor review before broadcasting' },
    published: { title: 'Published Articles',   sub: 'Live multilingual content' },
    analytics: { title: 'Analytics',            sub: 'Pipeline performance insights' },
  };
  const pt = PAGE_TITLES[page] || PAGE_TITLES.dashboard;

  return (
    <div className="app-shell">
      <Sidebar
        page={page}
        onNavigate={setPage}
        reviewCount={reviewCount}
        processingCount={processingCount}
      />

      <div className="app-main">
        {/* Header */}
        <header className="app-header">
          <div style={{ flex: 1 }}>
            <div className="header-title">{pt.title}</div>
            <div className="header-sub">{pt.sub}</div>
          </div>
          <div className="header-actions">
            {stats && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', gap: 12 }}>
                <span style={{ color: 'var(--green)' }}>● {stats.published} Published</span>
                <span style={{ color: 'var(--purple)' }}>● {stats.review} In Review</span>
                <span style={{ color: 'var(--blue)' }}>● {stats.processing} Processing</span>
              </div>
            )}
            <button
              className={`demo-btn ${demoRunning ? 'running' : ''}`}
              onClick={runLiveDemo}
              disabled={demoRunning}
            >
              {demoRunning ? '⚡ Demo Running...' : '⚡ Live Demo'}
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">
          {page === 'dashboard' && (
            <DashboardPage
              stats={stats}
              articles={articles}
              liveEvents={liveEvents}
              onNavigate={setPage}
            />
          )}
          {page === 'ingest' && (
            <IngestPage
              onArticleCreated={loadData}
              addToast={addToast}
            />
          )}
          {page === 'review' && (
            <ReviewPage
              articles={articles}
              liveEvents={liveEvents}
              addToast={addToast}
              onRefresh={loadData}
            />
          )}
          {page === 'published' && (
            <PublishedPage articles={articles} />
          )}
          {page === 'analytics' && (
            <AnalyticsPage stats={stats} articles={articles} />
          )}
        </main>
      </div>

      <Toast toasts={toasts} />
    </div>
  );
}
