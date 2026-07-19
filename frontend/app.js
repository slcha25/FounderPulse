const API = '';
const el = (id) => document.getElementById(id);

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* ============================== View routing ============================== */

const VIEWS = ['home', 'intake', 'run', 'results'];

function showView(name) {
  VIEWS.forEach((v) => el(`view-${v}`).classList.toggle('hidden', v !== name));
  window.scrollTo({ top: 0 });
}

function openIntake() {
  el('intake-form').reset();
  selectedFiles = [];
  renderFileList();
  showView('intake');
}

/* ============================== Shared diagram renderers ============================== */

const AGENT_LABELS = {
  founder: 'Founder & Team', market: 'Market', product: 'Product & Technology',
  competition: 'Competition', financial: 'Business & Financials', risk: 'Risk Resilience',
};
const SECTION_ORDER = ['founder', 'market', 'product', 'competition', 'financial', 'risk'];
const STAGE_ICONS = { sources: '🌐', knowledge_processing: '🧩', scanning: '🔬', delegate: '🧭', decision: '⚖️', memo: '📝', complete: '🎉' };

function renderChain(container, nodes, gateIndex) {
  if (!container) return;
  let html = '<div class="diagram-chain">';
  nodes.forEach((n, i) => {
    const gateCls = gateIndex === i ? ' dn-gate' : '';
    html += `<div class="diagram-node${gateCls}" data-stage="${n.key || ''}"><div class="dn-icon">${n.icon}</div><div class="dn-label">${n.label}</div></div>`;
    if (i < nodes.length - 1) html += '<div class="diagram-connector"></div>';
  });
  html += '</div>';
  container.innerHTML = html;
}

function renderRadial(container, center, nodes) {
  if (!container) return;
  const rect = container.getBoundingClientRect();
  const cx = rect.width / 2;
  const cy = rect.height / 2;
  const radius = Math.max(60, Math.min(cx, cy) - 44);
  let html = `<div class="diagram-hub"><div class="dn-icon">${center.icon}</div><div class="dn-label">${center.label}</div></div>`;
  nodes.forEach((n, i) => {
    const angle = (2 * Math.PI * i / nodes.length) - Math.PI / 2;
    const x = cx + radius * Math.cos(angle);
    const y = cy + radius * Math.sin(angle);
    const lineLen = Math.max(0, radius - 8);
    const angleDeg = angle * 180 / Math.PI;
    html += `<div class="diagram-spoke-line" style="width:${lineLen}px; top:${cy}px; left:${cx}px; transform:rotate(${angleDeg}deg);"></div>`;
    html += `<div class="diagram-spoke" data-mini="${n.key || ''}" style="top:${y}px; left:${x}px;"><span>${n.icon}</span><span>${n.label}</span></div>`;
  });
  container.innerHTML = html;
}

/* ============================== Showcase carousel (How it works / Solutions) ============================== */

function buildShowcase(containerId, eyebrowLabel, items, opts = {}) {
  const root = el(containerId);
  if (!root) return;
  let index = 0;
  let autoplayTimer = null;

  function renderDiagram(item) {
    const canvas = el(`${containerId}-canvas`);
    if (item.diagram.layout === 'radial') renderRadial(canvas, item.diagram.center, item.diagram.nodes);
    else renderChain(canvas, item.diagram.nodes, item.diagram.gateIndex);
  }

  function render() {
    const item = items[index];
    root.innerHTML = `
      <div class="showcase">
        <div class="showcase-tabs">
          ${items.map((it, i) => `<button type="button" class="showcase-tab${i === index ? ' active' : ''}" data-idx="${i}">${escapeHtml(it.tab)}</button>`).join('')}
        </div>
        <div class="showcase-body">
          <div class="showcase-left">
            <span class="eyebrow eyebrow-dark">${escapeHtml(eyebrowLabel)}</span>
            ${item.problem ? `<div class="showcase-problem">Problem: ${escapeHtml(item.problem)}</div>` : ''}
            <h3><span class="showcase-icon">${item.icon}</span>${escapeHtml(item.title)}</h3>
            <p class="desc">${escapeHtml(item.desc)}</p>
            <ul class="showcase-checklist">${item.checklist.map((c) => `<li>${escapeHtml(c)}</li>`).join('')}</ul>
          </div>
          <div class="showcase-canvas" id="${containerId}-canvas"></div>
        </div>
        <div class="showcase-nav">
          <div class="showcase-dots">${items.map((_, i) => `<div class="showcase-dot${i === index ? ' active' : ''}"></div>`).join('')}</div>
          <span class="showcase-count">${index + 1} / ${items.length}</span>
          <div class="showcase-arrows">
            <button type="button" class="showcase-arrow" data-dir="-1">←</button>
            <button type="button" class="showcase-arrow" data-dir="1">→</button>
          </div>
        </div>
      </div>`;

    renderDiagram(item);

    root.querySelectorAll('.showcase-tab').forEach((btn) => {
      btn.onclick = () => { index = Number(btn.dataset.idx); render(); resetAutoplay(); };
    });
    root.querySelectorAll('.showcase-arrow').forEach((btn) => {
      btn.onclick = () => { index = (index + Number(btn.dataset.dir) + items.length) % items.length; render(); resetAutoplay(); };
    });
  }

  function resetAutoplay() {
    if (autoplayTimer) clearInterval(autoplayTimer);
    if (opts.autoplay) autoplayTimer = setInterval(() => { index = (index + 1) % items.length; render(); }, opts.autoplay);
  }

  render();
  resetAutoplay();
  window.addEventListener('resize', () => renderDiagram(items[index]));
}

const WORKFLOW_ITEMS = [
  { tab: 'Intake', icon: '📥', title: 'Intake', desc: 'The analyst enters the company name plus anything already on hand — a URL, a pitch deck, financials — and confirms scope and processing permission.', checklist: ['Company + URL', 'Stage & sector', 'Fund thesis notes', 'Drag-and-drop documents'], diagram: { layout: 'chain', nodes: [{ icon: '🏢', label: 'Company Info' }, { icon: '📎', label: 'Documents' }, { icon: '✅', label: 'Validated Case' }] } },
  { tab: 'Sources', icon: '🌐', title: 'Source Agents', desc: 'Specialist collectors pull only permitted evidence — public web, the company’s own site, and anything you uploaded — and record exactly where every fact came from.', checklist: ['Public web search', 'Company website', 'Funding databases', 'Your uploaded files'], diagram: { layout: 'chain', nodes: [{ icon: '🔎', label: 'Web Search' }, { icon: '🏠', label: 'Company Site' }, { icon: '📎', label: 'Uploads' }, { icon: '🗂️', label: 'Evidence Store' }] } },
  { tab: 'Profile', icon: '🧩', title: 'Knowledge Processing', desc: 'One agent normalizes every evidence record into a single Startup Profile, resolves entity confusion, and separates verified fact from inference.', checklist: ['Entity resolution', 'Fact vs. inference', 'Claim-level citations', 'Versioned profile'], diagram: { layout: 'chain', nodes: [{ icon: '🗂️', label: 'Raw Evidence' }, { icon: '🧩', label: 'Normalize' }, { icon: '📋', label: 'Startup Profile' }] } },
  { tab: 'Scanning', icon: '🔬', title: 'Six Scanning Agents', desc: 'Founder, Market, Product, Competition, Financial and Risk agents analyze the same profile snapshot independently and in parallel — every case, every time.', checklist: ['0–10 score + confidence', 'Cited evidence', 'Assumptions flagged', 'No cross-agent overwrites'], diagram: { layout: 'radial', center: { icon: '📋', label: 'Profile' }, nodes: [{ icon: '🧑‍💼', label: 'Founder' }, { icon: '📈', label: 'Market' }, { icon: '🛠️', label: 'Product' }, { icon: '⚔️', label: 'Competition' }, { icon: '💰', label: 'Financial' }, { icon: '⚠️', label: 'Risk' }] } },
  { tab: 'Delegate', icon: '🧭', title: 'Delegate Agent', desc: 'Checks evidence coverage, contradictions and confidence across all six reports, and flags exactly what’s still missing for the human reviewer.', checklist: ['Coverage check', 'Conflict detection', 'Confidence rollup', 'Gap list for review'], diagram: { layout: 'chain', nodes: [{ icon: '🔬', label: '6 Reports' }, { icon: '🧭', label: 'Check Gaps' }, { icon: '📝', label: 'Diligence Plan' }] } },
  { tab: 'Decision', icon: '⚖️', title: 'Decision Agent', desc: 'Applies your fund’s configured weights deterministically, classifies the case, then explains the recommendation — grounded only in the evidence already produced.', checklist: ['Weighted scoring', 'Recommend / Research / Decline', 'No unsupported facts', 'Sensitivity analysis'], diagram: { layout: 'chain', nodes: [{ icon: '⚖️', label: 'Weighted Score' }, { icon: '🏷️', label: 'Classify' }, { icon: '💬', label: 'Rationale' }] } },
  { tab: 'Memo & Gate', icon: '📝', title: 'Memo + Human Gate', desc: 'An IC-ready memo is generated with every citation intact. A named human reviewer — not the system — records the final Accept or Reject within 24 hours.', checklist: ['Editable IC memo', 'Full audit trail', '24-hour SLA countdown', 'Human Accept / Reject'], diagram: { layout: 'chain', gateIndex: 1, nodes: [{ icon: '📝', label: 'Memo' }, { icon: '🧑‍⚖️', label: 'Human Review' }, { icon: '✅', label: 'Accept / Reject' }] } },
];

/* ============================== Live run (real-time SSE) ============================== */

const LIVE_CHAIN_1 = [
  { key: 'intake', icon: '📥', label: 'Intake' },
  { key: 'sources', icon: '🌐', label: 'Sources' },
  { key: 'knowledge_processing', icon: '🧩', label: 'Profile' },
];
const LIVE_SCANNING_AGENTS = [
  { key: 'founder', icon: '🧑‍💼', label: 'Founder' },
  { key: 'market', icon: '📈', label: 'Market' },
  { key: 'product', icon: '🛠️', label: 'Product' },
  { key: 'competition', icon: '⚔️', label: 'Competition' },
  { key: 'financial', icon: '💰', label: 'Financial' },
  { key: 'risk', icon: '⚠️', label: 'Risk' },
];
const LIVE_CHAIN_2 = [
  { key: 'delegate', icon: '🧭', label: 'Delegate' },
  { key: 'decision', icon: '⚖️', label: 'Decision' },
  { key: 'memo', icon: '📝', label: 'Memo' },
  { key: 'human', icon: '🧑‍⚖️', label: 'Human Gate' },
];

function setNodeState(root, stageKey, status) {
  const node = root.querySelector(`[data-stage="${stageKey}"]`);
  if (!node) return;
  node.classList.remove('active', 'done', 'error');
  if (status) node.classList.add(status);
}

function setMiniState(root, agentKey, status) {
  const mini = root.querySelector(`[data-mini="${agentKey}"]`);
  if (!mini) return;
  mini.classList.remove('active', 'done');
  if (status) mini.classList.add(status);
}

function handleProgressEvent(event, root) {
  if (event.stage === 'scanning' && event.agent) {
    setMiniState(root, event.agent, event.status === 'done' ? 'done' : 'active');
  } else if (event.stage !== 'complete') {
    setNodeState(root, event.stage, event.status === 'done' ? 'done' : event.status === 'error' ? 'error' : 'active');
  }
  appendLogLine(event);
}

function appendLogLine(event) {
  const log = el('activity-log');
  if (!log) return;
  const line = document.createElement('div');
  const cls = event.status === 'done' ? 'done' : event.status === 'error' ? 'error' : '';
  const icon = event.status === 'done' ? '✓' : event.status === 'error' ? '✕' : (STAGE_ICONS[event.stage] || '•');
  const who = event.agent ? (AGENT_LABELS[event.agent] || event.agent) : event.stage_label;
  const time = new Date(event.ts * 1000).toLocaleTimeString();
  line.className = `log-line ${cls}`;
  line.innerHTML = `<span class="log-time">${time}</span>${icon} <strong>${escapeHtml(who)}</strong> — ${escapeHtml(event.detail || '')}`;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function startLiveRun(runId, onComplete) {
  const root = el('live-workflow');
  renderChain(el('live-chain-1'), LIVE_CHAIN_1);
  renderRadial(el('live-scanning-hub'), { icon: '📋', label: 'Profile' }, LIVE_SCANNING_AGENTS);
  renderChain(el('live-chain-2'), LIVE_CHAIN_2, 3);
  setNodeState(root, 'intake', 'done');
  el('activity-log').innerHTML = '';

  const es = new EventSource(`${API}/api/runs/${runId}/stream`);
  es.onmessage = (msg) => {
    const event = JSON.parse(msg.data);
    if (event.stage === 'complete') {
      es.close();
      if (event.status === 'error') {
        appendLogLine({ ...event, detail: `Error: ${event.detail}` });
        alert(`Pipeline failed: ${event.detail}`);
        showView('intake');
      } else {
        appendLogLine({ ...event, detail: 'Case ready' });
        setNodeState(root, 'memo', 'done');
        onComplete(event.case_id);
      }
      return;
    }
    handleProgressEvent(event, root);
  };
}

/* ============================== Solutions ============================== */

const SOLUTION_ITEMS = [
  { tab: 'Fragmented Info', icon: '🧩', title: 'One structured, cited profile', problem: 'Fragmented information across decks, sites and databases', desc: 'Source Agents pull from the company site, public web research and any documents you upload into a single normalized Startup Profile.', checklist: ['Company website', 'Web research', 'Funding databases', 'Your documents'], diagram: { layout: 'radial', center: { icon: '📋', label: 'Profile' }, nodes: [{ icon: '🏠', label: 'Website' }, { icon: '🔎', label: 'Web' }, { icon: '🗃️', label: 'Funding DB' }, { icon: '📎', label: 'Uploads' }] } },
  { tab: 'Repetition', icon: '🔁', title: 'Six specialists, every time', problem: 'Analysts repeat the same research for every company', desc: 'Founder, Market, Product, Competition, Financial and Risk agents run in parallel on every case — nothing gets skipped because an analyst ran out of hours.', checklist: ['Runs in parallel', 'Same depth every case', 'No analyst fatigue', 'Consistent coverage'], diagram: { layout: 'radial', center: { icon: '📋', label: 'Profile' }, nodes: [{ icon: '🧑‍💼', label: 'Founder' }, { icon: '📈', label: 'Market' }, { icon: '🛠️', label: 'Product' }, { icon: '⚔️', label: 'Competition' }, { icon: '💰', label: 'Financial' }, { icon: '⚠️', label: 'Risk' }] } },
  { tab: 'Frameworks', icon: '🧭', title: 'One shared scoring contract', problem: 'Inconsistent frameworks, no recorded evidence', desc: 'Every agent returns the same 0–10 score, confidence band and citations, weighted by your fund’s configured thesis — not by which analyst wrote the memo.', checklist: ['0–10 + confidence', 'Configurable weights', 'Same anchors every case', 'Version-tracked policy'], diagram: { layout: 'chain', nodes: [{ icon: '🔬', label: 'Score' }, { icon: '📊', label: 'Confidence' }, { icon: '⚖️', label: 'Weighted' }, { icon: '🏷️', label: 'Recommend' }] } },
  { tab: 'Hallucination', icon: '🔍', title: 'Cited or labeled, never guessed', problem: 'A single LLM answer can mix fact and inference', desc: 'Every factual statement links to an evidence ID with a real URL. Assumptions and gaps are labeled explicitly instead of presented as fact.', checklist: ['evidence_id on every claim', 'Fact vs. assumption', 'Contradictions preserved', 'Low confidence flagged'], diagram: { layout: 'chain', nodes: [{ icon: '💬', label: 'Claim' }, { icon: '🔗', label: 'Evidence ID' }, { icon: '🌐', label: 'Real URL' }] } },
  { tab: 'Memory', icon: '🧠', title: 'Every case becomes case memory', problem: 'Investment teams lose learning across companies', desc: 'Each run is saved as a structured, versioned case — the foundation for a learning loop that compares outcomes across your whole pipeline over time.', checklist: ['Versioned per case', 'Tenant-isolated', 'Reflection on verified outcomes', 'Human-approved learning'], diagram: { layout: 'chain', nodes: [{ icon: '📁', label: 'Case' }, { icon: '🗄️', label: 'Case Memory' }, { icon: '🧠', label: 'Experience Memory' }] } },
  { tab: 'Accountability', icon: '⚖️', title: 'A human always signs off', problem: 'No accountability for AI-driven investment calls', desc: 'FounderPulse recommends and drafts the memo. A named reviewer records the final Accept or Reject with a rationale, inside a 24-hour window.', checklist: ['Binary Accept/Reject', 'Required rationale', '24h SLA tracked', 'Override audit trail'], diagram: { layout: 'chain', gateIndex: 2, nodes: [{ icon: '⚖️', label: 'Decision Agent' }, { icon: '📝', label: 'Memo' }, { icon: '🧑‍⚖️', label: 'Reviewer' }, { icon: '✅', label: 'Accept/Reject' }] } },
];

/* ============================== Marquee ============================== */

const MARQUEE_ITEMS = [
  { text: 'EVIDENCE-CITED SCORING', color: '#34d399' },
  { text: 'SIX SPECIALIST AGENTS', color: '#38bdf8' },
  { text: 'HUMAN-IN-THE-LOOP', color: '#fbbf24' },
  { text: '24-HOUR DECISION SLA', color: '#f472b6' },
  { text: 'CONFIDENCE-BANDED', color: '#a78bfa' },
  { text: 'NO HALLUCINATED CLAIMS', color: '#6ee7b7' },
  { text: 'WEIGHTED FUND THESIS', color: '#facc15' },
];

function renderMarquee() {
  const track = el('marquee-track');
  if (!track) return;
  const itemsHtml = MARQUEE_ITEMS.map((m) => `<span class="marquee-item" style="color:${m.color}">${escapeHtml(m.text)}</span><span class="marquee-dot">•</span>`).join('');
  track.innerHTML = itemsHtml + itemsHtml;
}

/* ============================== Case grid ============================== */

function recClass(decisionClass) {
  if (!decisionClass) return '';
  if (decisionClass.startsWith('Recommend')) return 'recommend';
  if (decisionClass.startsWith('More')) return 'research';
  return 'decline';
}

async function loadCaseGrid() {
  const res = await fetch(`${API}/api/cases`);
  const cases = await res.json();
  const grid = el('case-grid');
  const empty = el('case-empty');
  if (!cases.length) { grid.innerHTML = ''; empty.classList.remove('hidden'); return; }
  empty.classList.add('hidden');
  grid.innerHTML = cases.map((c) => {
    const decisionPill = c.decision_class ? `<span class="pill ${recClass(c.decision_class)}">${escapeHtml(c.decision_class)}</span>` : '';
    const humanPill = c.human_decision ? `<span class="pill ${c.human_decision.outcome === 'accept' ? 'accepted' : 'rejected'}">${c.human_decision.outcome.toUpperCase()}</span>` : '';
    return `<div class="case-card" data-case-id="${c.case_id}">
      <div class="case-name">${escapeHtml(c.company_name)}</div>
      <div class="muted" style="font-size:12px">${c.weighted_score ?? '-'}/10 · ${new Date(c.created_at).toLocaleDateString()}</div>
      <div class="case-badges">${decisionPill}${humanPill}</div>
    </div>`;
  }).join('');
  grid.querySelectorAll('.case-card').forEach((card) => {
    card.onclick = () => loadCaseById(card.dataset.caseId);
  });
}

async function loadCaseById(caseId) {
  const res = await fetch(`${API}/api/cases/${caseId}`);
  if (!res.ok) return;
  showResults(await res.json());
}

/* ============================== Markdown renderer (memo) ============================== */

function inline(text) {
  text = escapeHtml(text);
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  return text;
}

function mdToHtml(md) {
  const lines = md.split('\n');
  let html = '';
  let inTable = false;
  let tableRows = [];
  let inList = false;

  function flushTable() {
    if (!inTable) return;
    const rows = tableRows.filter((r, i) => i !== 1);
    const [headerRow, ...bodyRows] = rows;
    const headers = headerRow.split('|').map((s) => s.trim()).filter(Boolean);
    html += '<table><thead><tr>' + headers.map((h) => `<th>${escapeHtml(h)}</th>`).join('') + '</tr></thead><tbody>';
    for (const row of bodyRows) {
      const cells = row.split('|').map((s) => s.trim()).filter((c, i, arr) => !(i === 0 && c === '') && !(i === arr.length - 1 && c === ''));
      html += '<tr>' + cells.map((c) => `<td>${escapeHtml(c)}</td>`).join('') + '</tr>';
    }
    html += '</tbody></table>';
    inTable = false;
    tableRows = [];
  }

  function closeList() {
    if (inList) { html += '</ul>'; inList = false; }
  }

  for (const line of lines) {
    if (/^\s*\|.*\|\s*$/.test(line)) {
      inTable = true;
      tableRows.push(line.trim());
      continue;
    } else if (inTable) {
      flushTable();
    }

    if (/^#{1,3}\s+/.test(line)) {
      closeList();
      const level = line.match(/^#+/)[0].length;
      const text = line.replace(/^#{1,3}\s+/, '');
      html += `<h${level}>${inline(text)}</h${level}>`;
    } else if (/^>\s?/.test(line)) {
      closeList();
      html += `<blockquote>${inline(line.replace(/^>\s?/, ''))}</blockquote>`;
    } else if (/^-{3,}\s*$/.test(line)) {
      closeList();
      html += '<hr/>';
    } else if (/^-\s+/.test(line)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${inline(line.replace(/^-\s+/, ''))}</li>`;
    } else if (line.trim() === '') {
      closeList();
    } else {
      closeList();
      html += `<p>${inline(line)}</p>`;
    }
  }
  closeList();
  flushTable();
  return html;
}

/* ============================== Results view ============================== */

let countdownTimer = null;

function confidenceBand(conf) {
  if (conf >= 0.8) return { label: 'High', cls: 'high' };
  if (conf >= 0.6) return { label: 'Medium', cls: 'medium' };
  return { label: 'Low', cls: 'low' };
}

function startCountdown(decisionDueAt) {
  if (countdownTimer) clearInterval(countdownTimer);
  const target = new Date(decisionDueAt).getTime();
  const render = () => {
    const diff = target - Date.now();
    const box = el('sla-countdown-box');
    if (!box) return;
    if (diff <= 0) {
      box.textContent = 'SLA deadline passed — default outcome is Reject - Insufficient Information unless a human records a decision.';
      box.className = 'sla-countdown overdue';
      return;
    }
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    box.textContent = `24h SLA: ${h}h ${m}m remaining until decision_due_at`;
    box.className = 'sla-countdown';
  };
  render();
  countdownTimer = setInterval(render, 30000);
}

function scoreCard(key, report) {
  const band = confidenceBand(report.confidence);
  const strengths = (report.strengths || []).map((s) => `<li>${escapeHtml(s)}</li>`).join('') || '<li>none</li>';
  const risks = (report.risks || []).map((r) => `<li>[${r.severity}] ${escapeHtml(r.description)}</li>`).join('') || '<li>none</li>';
  const missing = (report.missing_information || []).map((m) => `<li>${escapeHtml(m)}</li>`).join('') || '<li>none</li>';
  return `<div class="score-card">
    <h3>${AGENT_LABELS[key] || key}</h3>
    <div class="score-bar-track"><div class="score-bar-fill" style="width:${report.score * 10}%"></div></div>
    <div class="score-meta">
      <span>${report.score}/10</span>
      <span class="badge ${band.cls}">${band.label} confidence</span>
    </div>
    <details>
      <summary>Strengths / risks / gaps</summary>
      <strong>Strengths</strong><ul>${strengths}</ul>
      <strong>Risks</strong><ul>${risks}</ul>
      <strong>Missing info</strong><ul>${missing}</ul>
    </details>
  </div>`;
}

function humanDecisionPanel(caseData) {
  const panel = el('human-decision-panel');
  if (caseData.human_decision) {
    const hd = caseData.human_decision;
    panel.innerHTML = `<div class="recorded-decision ${hd.outcome}">
      <strong>${hd.outcome.toUpperCase()}</strong> by ${escapeHtml(hd.reviewer)} at ${new Date(hd.decided_at).toLocaleString()}<br/>
      Deadline met: ${hd.deadline_met ? 'Yes' : 'No'}<br/>
      Rationale: ${escapeHtml(hd.rationale)}
    </div>`;
    return;
  }
  panel.innerHTML = `
    <input type="text" id="reviewer-name" placeholder="Your name (reviewer)" />
    <textarea id="decision-rationale" rows="3" placeholder="Rationale for Accept/Reject (required)"></textarea>
    <div class="decision-buttons">
      <button class="accept-btn" id="accept-btn">Accept</button>
      <button class="reject-btn" id="reject-btn">Reject</button>
    </div>`;
  el('accept-btn').onclick = () => submitHumanDecision(caseData.case_id, 'accept');
  el('reject-btn').onclick = () => submitHumanDecision(caseData.case_id, 'reject');
}

async function submitHumanDecision(caseId, outcome) {
  const reviewer = el('reviewer-name').value.trim();
  const rationale = el('decision-rationale').value.trim();
  if (!reviewer || !rationale) {
    alert('Reviewer name and rationale are required — FR-11 requires a recorded rationale for every human decision.');
    return;
  }
  const res = await fetch(`${API}/api/cases/${caseId}/human-decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome, rationale, reviewer }),
  });
  const data = await res.json();
  if (!res.ok) { alert(data.detail || 'Failed to record decision'); return; }
  showResults(data);
  loadCaseGrid();
}

function showResults(caseData) {
  showView('results');

  const decision = caseData.decision;
  const banner = el('rec-banner');
  banner.className = `rec-banner ${recClass(decision.decision_class)}`;
  banner.innerHTML = `<span class="rec-class">${escapeHtml(decision.decision_class)}</span>` +
    `<div id="sla-countdown-box" class="sla-countdown"></div>` +
    `Weighted score: <strong>${decision.weighted_score}/10</strong> · ` +
    `Overall confidence: <strong>${decision.overall_confidence.toFixed(2)}</strong> · ` +
    `Hard red flag: <strong>${decision.hard_red_flag ? 'Yes' : 'No'}</strong>`;
  startCountdown(caseData.decision_due_at);

  const cost = caseData.cost_summary || {};
  el('cost-note').textContent = cost.estimated_cost_usd !== undefined
    ? `Pipeline cost: ~$${cost.estimated_cost_usd} (${cost.total_prompt_tokens + cost.total_completion_tokens} tokens, ${cost.model})`
    : '';

  const grid = el('score-grid');
  grid.innerHTML = SECTION_ORDER.filter((k) => caseData.reports[k]).map((k) => scoreCard(k, caseData.reports[k])).join('');

  el('memo-output').innerHTML = mdToHtml(caseData.memo_markdown);

  humanDecisionPanel(caseData);
}

/* ============================== Intake: file upload ============================== */

let selectedFiles = [];

function renderFileList() {
  const ul = el('file-list');
  ul.innerHTML = selectedFiles.map((f, i) => `<li>${escapeHtml(f.name)} <button type="button" data-idx="${i}">remove</button></li>`).join('');
  ul.querySelectorAll('button').forEach((btn) => {
    btn.onclick = () => { selectedFiles.splice(Number(btn.dataset.idx), 1); renderFileList(); };
  });
}

function addFiles(fileList) {
  for (const f of fileList) selectedFiles.push(f);
  renderFileList();
}

const dropzone = el('dropzone');
const fileInput = el('file-input');
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  addFiles(e.dataTransfer.files);
});
fileInput.addEventListener('change', () => addFiles(fileInput.files));

/* ============================== Intake: submit ============================== */

el('intake-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const companyName = el('company_name').value.trim();
  const formData = new FormData();
  formData.append('company_name', companyName);
  formData.append('company_url', el('company_url').value.trim());
  formData.append('stage', el('stage').value);
  formData.append('sector', el('sector').value.trim());
  formData.append('thesis_notes', el('thesis_notes').value.trim());
  for (const file of selectedFiles) formData.append('files', file);

  try {
    const res = await fetch(`${API}/api/cases/start`, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to start run');

    el('run-company-name').textContent = companyName;
    showView('run');
    startLiveRun(data.run_id, async (caseId) => {
      const caseRes = await fetch(`${API}/api/cases/${caseId}`);
      showResults(await caseRes.json());
      loadCaseGrid();
    });
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
});

/* ============================== Nav wiring ============================== */

el('nav-home').addEventListener('click', (e) => { e.preventDefault(); showView('home'); });
el('nav-new-case').addEventListener('click', openIntake);
el('hero-new-case').addEventListener('click', openIntake);
el('cases-new-case').addEventListener('click', openIntake);
el('intake-back').addEventListener('click', () => showView('home'));
el('results-back').addEventListener('click', () => { showView('home'); loadCaseGrid(); });

document.querySelectorAll('.nav-scroll').forEach((a) => {
  a.addEventListener('click', (e) => {
    e.preventDefault();
    showView('home');
    requestAnimationFrame(() => {
      document.getElementById(a.dataset.target).scrollIntoView({ behavior: 'smooth' });
    });
  });
});

/* ============================== Contact form ============================== */

el('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const status = el('contact-status');
  const payload = {
    name: el('contact_name').value.trim(),
    email: el('contact_email').value.trim(),
    message: el('contact_message').value.trim(),
  };
  status.textContent = 'Sending…';
  status.className = 'form-status';
  try {
    const res = await fetch(`${API}/api/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to send');
    status.textContent = 'Thanks — your message has been received.';
    status.className = 'form-status success';
    el('contact-form').reset();
  } catch (err) {
    status.textContent = `Error: ${err.message}`;
    status.className = 'form-status error';
  }
});

/* ============================== Init ============================== */

renderMarquee();
buildShowcase('workflow-showcase', 'How it works', WORKFLOW_ITEMS, { autoplay: 5000 });
buildShowcase('solutions-showcase', 'Solutions', SOLUTION_ITEMS, { autoplay: 6200 });
loadCaseGrid();

