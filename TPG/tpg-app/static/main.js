/* ══════════════════════════════════════════════════════════
   TPG — main.js
   Three modes: cursor | node | edge | path
   ══════════════════════════════════════════════════════════ */

/* ── DOM ─────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);
const toolBtns    = document.querySelectorAll('.tool-btn');
const toolHint    = $('tool-hint');
const clearBtn    = $('clear-btn');
const modal       = $('modal');
const modalCancel = $('modal-cancel');
const modalConfirm= $('modal-confirm');
const nodeCountEl = $('node-count');
const edgeCountEl = $('edge-count');
const canvasEmpty = $('canvas-empty');
const modePill    = $('mode-pill');

const qSlider     = $('q-slider');
const qVal        = $('q-val');
const bNodesEl    = $('b-nodes');
const initBtn     = $('init-btn');
const resetBtn    = $('reset-btn');
const stepBtn     = $('step-btn');
const playBtn     = $('play-btn');
const speedSlider = $('speed-slider');
const turnVal     = $('turn-val');
const aCount      = $('a-count');
const bCount      = $('b-count');
const eqBadge     = $('eq-badge');

/* ── Vis.js datasets ─────────────────────────────────────── */
let visNodes = new vis.DataSet();
let visEdges = new vis.DataSet();
let network  = null;

/* ── App state ───────────────────────────────────────────── */
let currentTool    = 'cursor';
let nextNodeId     = 0;
let nextEdgeId     = 0;
let edgeFirstNode  = null;   // for edge tool
let pathLastNode   = null;   // for path tool
let simRunning     = false;
let playing        = false;
let playInterval   = null;

/* ── Colour tokens ───────────────────────────────────────── */
const COLOR = {
  A: { background: '#4ade80', border: '#22c55e', highlight: { background: '#6ee7a0', border: '#22c55e' } },
  B: { background: '#f87171', border: '#ef4444', highlight: { background: '#fca5a5', border: '#ef4444' } },
  DEFAULT: { background: '#6c8fff', border: '#3b6bff', highlight: { background: '#8aa5ff', border: '#3b6bff' } },
  SELECTED: { background: '#e8c347', border: '#ca9a00', highlight: { background: '#f0d070', border: '#ca9a00' } },
};

const HINTS = {
  cursor: 'Click and drag to move nodes.',
  node:   'Click anywhere on the canvas to add a node.',
  edge:   'Click a node to start an edge, then click another to connect them.',
  path:   'Click nodes in sequence — each click extends the path. Press Esc to finish.',
};

/* ── Init Vis network ────────────────────────────────────── */
function buildNetwork() {
  const container = document.getElementById('network');
  network = new vis.Network(container, { nodes: visNodes, edges: visEdges }, {
    physics: {
      solver: 'forceAtlas2Based',
      forceAtlas2Based: { gravitationalConstant: -55, springLength: 100 },
      stabilization: { iterations: 150 },
    },
    edges: {
      color: { color: '#2a3347', highlight: '#6c8fff', hover: '#4a5a7a' },
      width: 2,
      smooth: { type: 'continuous' },
      selectionWidth: 3,
    },
    nodes: {
      shape: 'dot',
      size: 20,
      font: { color: '#d4daf0', size: 13, face: 'JetBrains Mono, monospace', bold: true },
      borderWidth: 2.5,
      shadow: { enabled: true, color: 'rgba(0,0,0,0.4)', size: 8, x: 0, y: 3 },
    },
    interaction: {
      hover: true,
      dragView: true,
      zoomView: true,
      dragNodes: true,
      selectConnectedEdges: false,
    },
  });

  // Canvas click — for node/edge/path tools
  network.on('click', onCanvasClick);
  network.on('deselectNode', () => {
    if (currentTool === 'edge' && edgeFirstNode !== null) {
      visNodes.update({ id: edgeFirstNode, color: COLOR.DEFAULT });
      edgeFirstNode = null;
      toolHint.textContent = HINTS.edge;
    }
  });
}

/* ── Tool switching ──────────────────────────────────────── */
function setTool(tool) {
  if (simRunning) return;
  currentTool = tool;
  toolBtns.forEach(b => b.classList.toggle('active', b.dataset.tool === tool));
  toolHint.textContent = HINTS[tool];

  // Cancel any in-progress edge/path selection
  if (edgeFirstNode !== null) {
    visNodes.update({ id: edgeFirstNode, color: COLOR.DEFAULT });
    edgeFirstNode = null;
  }
  pathLastNode = null;

  // Vis interaction options
  const draggable = tool === 'cursor';
  network.setOptions({ interaction: { dragNodes: draggable } });
  network.unselectAll();
}

toolBtns.forEach(btn => btn.addEventListener('click', () => setTool(btn.dataset.tool)));

/* ── Canvas click handler ────────────────────────────────── */
function onCanvasClick(params) {
  if (simRunning) return;

  const clickedNodeId = params.nodes.length > 0 ? params.nodes[0] : null;

  if (currentTool === 'node') {
    // Always add a node at the click position, even if clicking on empty space
    if (clickedNodeId === null) {
      addNodeAt(params.pointer.canvas);
    }

  } else if (currentTool === 'edge') {
    if (clickedNodeId === null) return;
    if (edgeFirstNode === null) {
      edgeFirstNode = clickedNodeId;
      visNodes.update({ id: clickedNodeId, color: COLOR.SELECTED });
      toolHint.textContent = `Node ${clickedNodeId} selected — now click the target node.`;
    } else {
      if (clickedNodeId !== edgeFirstNode) {
        addEdge(edgeFirstNode, clickedNodeId);
      }
      visNodes.update({ id: edgeFirstNode, color: COLOR.DEFAULT });
      edgeFirstNode = null;
      toolHint.textContent = HINTS.edge;
    }

  } else if (currentTool === 'path') {
    if (clickedNodeId === null) {
      // Add new node and connect to previous
      const newId = addNodeAt(params.pointer.canvas);
      if (pathLastNode !== null) addEdge(pathLastNode, newId);
      pathLastNode = newId;
      toolHint.textContent = `Path: … → ${newId}. Click to extend, Esc to finish.`;
    } else {
      // Connect existing node
      if (pathLastNode !== null && clickedNodeId !== pathLastNode) {
        addEdge(pathLastNode, clickedNodeId);
      }
      pathLastNode = clickedNodeId;
      toolHint.textContent = `Path: … → ${clickedNodeId}. Click to extend, Esc to finish.`;
    }
  }
}

/* ── Add node ─────────────────────────────────────────────── */
function addNodeAt(pos) {
  const id = nextNodeId++;
  visNodes.add({ id, label: String(id), x: pos.x, y: pos.y, color: COLOR.DEFAULT });
  updateInfo();
  return id;
}

/* ── Add edge ─────────────────────────────────────────────── */
function addEdge(from, to) {
  // Prevent duplicate edges
  const existing = visEdges.get().find(e =>
    (e.from === from && e.to === to) || (e.from === to && e.to === from)
  );
  if (existing) return;
  visEdges.add({ id: nextEdgeId++, from, to });
  updateInfo();
}

/* ── Update sidebar info ─────────────────────────────────── */
function updateInfo() {
  const n = visNodes.length;
  const e = visEdges.length;
  nodeCountEl.textContent = n;
  edgeCountEl.textContent = e;
  canvasEmpty.classList.toggle('hidden', n > 0);
}

/* ── Clear graph ─────────────────────────────────────────── */
clearBtn.addEventListener('click', () => { modal.classList.remove('hidden'); });
modalCancel.addEventListener('click', () => { modal.classList.add('hidden'); });
modalConfirm.addEventListener('click', () => {
  modal.classList.add('hidden');
  visNodes.clear();
  visEdges.clear();
  nextNodeId = 0; nextEdgeId = 0;
  edgeFirstNode = null; pathLastNode = null;
  updateInfo();
});

/* ── Esc key: finish path ────────────────────────────────── */
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (modal && !modal.classList.contains('hidden')) {
      modal.classList.add('hidden'); return;
    }
    pathLastNode = null;
    if (currentTool === 'path') toolHint.textContent = HINTS.path;
    if (edgeFirstNode !== null) {
      visNodes.update({ id: edgeFirstNode, color: COLOR.DEFAULT });
      edgeFirstNode = null;
      toolHint.textContent = HINTS.edge;
    }
  }
});

/* ── q slider sync ───────────────────────────────────────── */
qSlider.addEventListener('input', () => { qVal.value = qSlider.value; });
qVal.addEventListener('input', () => {
  let v = Math.min(1, Math.max(0, parseFloat(qVal.value) || 0));
  qSlider.value = v; qVal.value = v;
});

/* ── Enter simulation mode ───────────────────────────────── */
initBtn.addEventListener('click', async () => {
  const nodes = visNodes.get().map(n => n.id);
  const edges = visEdges.get().map(e => [e.from, e.to]);
  if (nodes.length === 0) { alert('Add at least one node first.'); return; }

  const q = parseFloat(qVal.value);
  const raw = bNodesEl.value.trim();
  const initial_b = raw ? raw.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n)) : [];

  const res = await fetch('/init', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes, edges, q, initial_b }),
  });
  if (!res.ok) { alert((await res.json()).error); return; }
  const data = await res.json();

  // Lock builder tools
  simRunning = true;
  toolBtns.forEach(b => b.disabled = true);
  clearBtn.disabled = true;
  network.setOptions({ interaction: { dragNodes: false } });
  modePill.textContent = 'SIMULATION';
  modePill.classList.add('sim');
  initBtn.style.display = 'none';
  resetBtn.style.display = 'block';
  stepBtn.disabled = false;
  playBtn.disabled = false;
  eqBadge.className = 'eq-badge hidden';

  renderStates(data);
  updateStats(data);
});

/* ── Back to builder ─────────────────────────────────────── */
resetBtn.addEventListener('click', () => {
  stopPlay();
  simRunning = false;
  toolBtns.forEach(b => b.disabled = false);
  clearBtn.disabled = false;
  network.setOptions({ interaction: { dragNodes: currentTool === 'cursor' } });
  modePill.textContent = 'BUILD';
  modePill.classList.remove('sim');
  initBtn.style.display = 'block';
  resetBtn.style.display = 'none';
  stepBtn.disabled = true;
  playBtn.disabled = true;
  eqBadge.className = 'eq-badge hidden';
  turnVal.textContent = '—';
  aCount.textContent  = '—';
  bCount.textContent  = '—';
  // Restore default node colours
  visNodes.get().forEach(n => visNodes.update({ id: n.id, color: COLOR.DEFAULT }));
});

/* ── Render node states from API ─────────────────────────── */
function renderStates(data) {
  data.nodes.forEach(n => {
    visNodes.update({ id: n.id, color: COLOR[n.state] });
  });
}

function updateStats(data) {
  turnVal.textContent = data.turn;
  aCount.textContent  = data.a_count;
  bCount.textContent  = data.b_count;

  if (data.equilibrium === 'fixed') {
    eqBadge.textContent = '✓ Fixed point';
    eqBadge.className = 'eq-badge fixed';
    stopPlay();
  } else if (data.equilibrium === 'cycle') {
    eqBadge.textContent = '⟳ 2-period cycle';
    eqBadge.className = 'eq-badge cycle';
    stopPlay();
  } else {
    eqBadge.className = 'eq-badge hidden';
  }
}

/* ── Step ────────────────────────────────────────────────── */
async function doStep() {
  const res = await fetch('/step', { method: 'POST' });
  if (!res.ok) return null;
  const data = await res.json();
  renderStates(data);
  updateStats(data);
  return data;
}

stepBtn.addEventListener('click', doStep);

/* ── Auto-play ───────────────────────────────────────────── */
function startPlay() {
  playing = true;
  playBtn.textContent = '⏹ Stop';
  playInterval = setInterval(async () => {
    const data = await doStep();
    if (!data || data.equilibrium) stopPlay();
  }, parseInt(speedSlider.value, 10));
}
function stopPlay() {
  playing = false;
  clearInterval(playInterval);
  playBtn.textContent = '▶ Play';
}

playBtn.addEventListener('click', () => playing ? stopPlay() : startPlay());
speedSlider.addEventListener('input', () => { if (playing) { stopPlay(); startPlay(); } });

/* ── Boot ────────────────────────────────────────────────── */
buildNetwork();
updateInfo();
