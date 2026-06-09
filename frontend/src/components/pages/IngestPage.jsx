import React, { useState } from 'react';
import { ingestArticle, transcribeContent } from '../../services/api';

const LANGUAGES = [
  { code: 'hi', name: 'Hindi',     flag: '🇮🇳' },
  { code: 'ta', name: 'Tamil',     flag: '🇮🇳' },
  { code: 'te', name: 'Telugu',    flag: '🇮🇳' },
  { code: 'bn', name: 'Bengali',   flag: '🇧🇩' },
  { code: 'mr', name: 'Marathi',   flag: '🇮🇳' },
  { code: 'gu', name: 'Gujarati',  flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada',   flag: '🇮🇳' },
  { code: 'ml', name: 'Malayalam', flag: '🇮🇳' },
  { code: 'pa', name: 'Punjabi',   flag: '🇮🇳' },
  { code: 'or', name: 'Odia',      flag: '🇮🇳' },
  { code: 'fr', name: 'French',    flag: '🇫🇷' },
  { code: 'es', name: 'Spanish',   flag: '🇪🇸' },
  { code: 'ar', name: 'Arabic',    flag: '🇸🇦' },
];

const CATEGORIES = ['General','Politics','Business','Sports','Entertainment','Health','Technology','International','Environment','Science'];

const SAMPLE_PROMPTS = [
  {
    type: 'Breaking News',
    icon: '⚡',
    title: 'Major Earthquake off Japan Coast',
    content: 'Breaking: A 7.2 magnitude earthquake struck off the coast of Japan early this morning at 5:48 AM JST. The Japan Meteorological Agency has issued tsunami warnings for coastal prefectures including Iwate, Miyagi, and Fukushima. Authorities have ordered evacuation of residents within 1 kilometer of the coast. The epicenter was located 80 kilometers east of Sendai at a depth of 35 kilometers. No casualties have been confirmed yet but rescue teams have been deployed.',
    category: 'International',
    source: 'AP Wire'
  },
  {
    type: 'Politics',
    icon: '🏛',
    title: 'Economic Policy Package Announced',
    content: 'The Prime Minister today announced a comprehensive economic policy package worth 50 billion dollars, aimed at revitalizing domestic manufacturing and creating 2 million jobs over the next five years. The package includes tax incentives for small businesses, infrastructure investment of 20 billion dollars, and a new skills training program. Opposition parties have criticized the plan as inadequate to address the current economic challenges.',
    category: 'Politics',
    source: 'Reuters'
  },
  {
    type: 'Sports',
    icon: '🏆',
    title: 'National Team Wins Championship',
    content: 'In a thrilling final at Wembley Stadium on Sunday, the national football team secured a historic 3-2 victory against the reigning champions to clinch the international title for the first time in 30 years. Captain Rahul Sharma scored the decisive goal in the 89th minute, sending thousands of fans into jubilation across the country. The victory has been dedicated to the nation by the team.',
    category: 'Sports',
    source: 'ESPN'
  },
  {
    type: 'Health Alert',
    icon: '🏥',
    title: 'Health Ministry Issues Advisory',
    content: 'The Ministry of Health today issued a public health advisory regarding a rise in respiratory infections across five northern states. Officials confirmed 2,400 new cases reported over the past 48 hours, with the highest concentration in urban districts. The ministry has advised citizens to wear masks in crowded spaces, maintain hand hygiene, and seek medical attention for symptoms persisting beyond 72 hours. Hospitals have been placed on heightened alert.',
    category: 'Health',
    source: 'Health Ministry'
  },
];

export default function IngestPage({ onArticleCreated, addToast }) {
  const [mode, setMode] = useState('article');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [source, setSource] = useState('');
  const [category, setCategory] = useState('General');
  const [priority, setPriority] = useState('normal');
  const [selectedLangs, setSelectedLangs] = useState(['hi', 'ta', 'te', 'bn']);
  const [rawTranscript, setRawTranscript] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastId, setLastId] = useState(null);

  const toggleLang = (code) => {
    setSelectedLangs(prev =>
      prev.includes(code) ? prev.filter(l => l !== code) : [...prev, code]
    );
  };

  const selectAll = () => setSelectedLangs(LANGUAGES.map(l => l.code));
  const clearAll = () => setSelectedLangs([]);

  const handleSubmit = async () => {
    if (mode === 'article' && (!title.trim() || !content.trim())) {
      addToast('error', 'Validation Error', 'Title and content are required.');
      return;
    }
    if (mode === 'transcribe' && !rawTranscript.trim()) {
      addToast('error', 'Validation Error', 'Please paste a broadcast transcript.');
      return;
    }
    if (selectedLangs.length === 0) {
      addToast('error', 'Validation Error', 'Select at least one target language.');
      return;
    }

    setLoading(true);
    try {
      let res;
      if (mode === 'transcribe') {
        res = await transcribeContent({ audio_text: rawTranscript, source_language: 'en' });
        setLastId(res.data.article_id);
        addToast('success', 'Transcript Ingested', `Article #${res.data.article_id} created. AI pipeline running...`);
        setRawTranscript('');
      } else {
        res = await ingestArticle({ title, content, source, category, priority, target_languages: selectedLangs });
        setLastId(res.data.article_id);
        addToast('success', 'Article Ingested', `Article #${res.data.article_id} created. Translating to ${selectedLangs.length} languages...`);
        setTitle(''); setContent(''); setSource('');
      }
      onArticleCreated();
    } catch (e) {
      addToast('error', 'Ingestion Failed', e.response?.data?.detail || e.message);
    }
    setLoading(false);
  };

  const applyPrompt = (p) => {
    setMode('article');
    setTitle(p.title);
    setContent(p.content);
    setCategory(p.category);
    setSource(p.source);
    setPriority('high');
  };

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Ingest Content</h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Submit a news article or raw broadcast transcript to start the AI localization pipeline.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16, alignItems: 'start' }}>
        {/* Left: Form */}
        <div>
          {/* Mode Toggle */}
          <div className="card" style={{ marginBottom: 14 }}>
            <div className="tabs" style={{ marginBottom: 0 }}>
              <button className={`tab-btn ${mode === 'article' ? 'active' : ''}`} onClick={() => setMode('article')}>
                📝 News Article
              </button>
              <button className={`tab-btn ${mode === 'transcribe' ? 'active' : ''}`} onClick={() => setMode('transcribe')}>
                🎙 Broadcast Transcript
              </button>
            </div>
          </div>

          {/* Form */}
          <div className="card">
            {mode === 'article' ? (
              <>
                <div className="form-group">
                  <label className="form-label">Headline / Title *</label>
                  <input className="form-input" placeholder="e.g. Earthquake Strikes Off Japan Coast" value={title} onChange={e => setTitle(e.target.value)} />
                </div>
                <div className="form-row col3" style={{ marginBottom: 14 }}>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Source</label>
                    <input className="form-input" placeholder="Reuters, AP, BBC..." value={source} onChange={e => setSource(e.target.value)} />
                  </div>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Category</label>
                    <select className="form-select" value={category} onChange={e => setCategory(e.target.value)}>
                      {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                    </select>
                  </div>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Priority</label>
                    <select className="form-select" value={priority} onChange={e => setPriority(e.target.value)}>
                      <option value="normal">Normal</option>
                      <option value="high">High</option>
                      <option value="breaking">⚡ Breaking News</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Full Article Content *</label>
                  <textarea className="form-textarea" rows={8}
                    placeholder="Paste or type the full news article content here..."
                    value={content} onChange={e => setContent(e.target.value)} />
                </div>
              </>
            ) : (
              <div className="form-group">
                <label className="form-label">Raw Broadcast Transcript *</label>
                <textarea className="form-textarea" rows={10}
                  placeholder="Paste raw spoken broadcast transcript here. Claude will clean, structure, categorize, and generate a headline automatically..."
                  value={rawTranscript} onChange={e => setRawTranscript(e.target.value)} />
                <div className="alert alert-info" style={{ marginTop: 10 }}>
                  Claude will automatically generate a headline, clean the transcript, identify the category, and extract key facts.
                </div>
              </div>
            )}

            {/* Language Selection */}
            <div className="divider" />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <div className="form-label" style={{ marginBottom: 0 }}>
                Target Languages ({selectedLangs.length} selected)
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-ghost btn-sm" onClick={selectAll}>All</button>
                <button className="btn btn-ghost btn-sm" onClick={clearAll}>Clear</button>
              </div>
            </div>
            <div className="lang-selector-grid" style={{ marginBottom: 16 }}>
              {LANGUAGES.map(l => (
                <div
                  key={l.code}
                  className={`lang-sel-item ${selectedLangs.includes(l.code) ? 'selected' : ''}`}
                  onClick={() => toggleLang(l.code)}
                >
                  <span>{l.flag}</span>
                  {l.name}
                  {selectedLangs.includes(l.code) && <span style={{ color: 'var(--blue)', fontSize: 10 }}>✓</span>}
                </div>
              ))}
            </div>

            <button
              className="btn btn-primary btn-lg"
              style={{ width: '100%' }}
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <><div className="spinner" style={{ width: 16, height: 16 }} /> Processing...</>
              ) : mode === 'transcribe' ? (
                '🎙 Transcribe & Localize'
              ) : (
                '🚀 Ingest & Start Localization'
              )}
            </button>

            {lastId && (
              <div className="alert alert-success" style={{ marginTop: 12 }}>
                ✓ Article #{lastId} created and AI pipeline running. Check the <strong>Review Queue</strong> in ~30 seconds.
              </div>
            )}
          </div>
        </div>

        {/* Right: Sample Prompts */}
        <div>
          <div className="card">
            <div className="card-title" style={{ marginBottom: 14 }}>Quick-Fill Templates</div>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 14, lineHeight: 1.5 }}>
              Click a template to auto-fill the form for a live demo.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {SAMPLE_PROMPTS.map((p, i) => (
                <div
                  key={i}
                  onClick={() => applyPrompt(p)}
                  style={{
                    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)', padding: '12px 14px', cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-light)'}
                  onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
                    <span>{p.icon}</span>
                    <span style={{ fontSize: 11, color: 'var(--cyan)', fontWeight: 600 }}>{p.type}</span>
                    <span style={{ fontSize: 10, color: 'var(--text-muted)', marginLeft: 'auto' }}>{p.source}</span>
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>{p.title}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {p.content.slice(0, 90)}...
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card" style={{ marginTop: 14 }}>
            <div className="card-title" style={{ marginBottom: 10 }}>Pipeline Steps</div>
            {[
              ['1', 'Ingest', 'Article stored in queue'],
              ['2', 'Sensitivity', 'Claude analyzes content risk'],
              ['3', 'Translate', 'Each language in parallel'],
              ['4', 'Adapt', 'Cultural references localized'],
              ['5', 'Review', 'Editor approves before publish'],
            ].map(([n, step, desc]) => (
              <div key={n} style={{ display: 'flex', gap: 10, padding: '8px 0', borderBottom: '1px solid var(--border)', alignItems: 'flex-start' }}>
                <div style={{ width: 20, height: 20, background: 'var(--blue)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, flexShrink: 0, marginTop: 1 }}>{n}</div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600 }}>{step}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
