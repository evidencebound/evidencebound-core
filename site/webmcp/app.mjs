import {
  correctSecurityEvidence,
  createInitialState,
  evaluateControl,
  expireSecurityEvidence,
  grantCurrentAuthority,
  removeRequiredEvidence,
  restoreFreshEvidence,
  revokeAuthority,
} from './control-core.mjs';
import { createWebMCPController } from './webmcp-adapter.mjs';

let state = createInitialState();
let controller = null;
let browserToolNames = [];
let runtimeState = 'WEBMCP_UNAVAILABLE';
let runtimeDetail = 'This browser does not expose document.modelContext. Use the supported ChatGPT browser or Chrome with WebMCP enabled.';
let events = [];

const elements = {
  runtime: document.querySelector('#runtime-badge'),
  controlState: document.querySelector('#control-state'),
  controlReason: document.querySelector('#control-reason'),
  fingerprint: document.querySelector('#fingerprint'),
  grantId: document.querySelector('#grant-id'),
  pendingRequest: document.querySelector('#pending-request'),
  compilerTools: document.querySelector('#compiler-tools'),
  browserTools: document.querySelector('#browser-tools'),
  toolNote: document.querySelector('#tool-note'),
  manifestStatus: document.querySelector('#manifest-status'),
  manifestRevision: document.querySelector('#manifest-revision'),
  scanStatus: document.querySelector('#scan-status'),
  scanRevision: document.querySelector('#scan-revision'),
  scanFindings: document.querySelector('#scan-findings'),
  policyStatus: document.querySelector('#policy-status'),
  hardBlock: document.querySelector('#hard-block'),
  eventLedger: document.querySelector('#event-ledger'),
  receiptLedger: document.querySelector('#receipt-ledger'),
  grant: document.querySelector('#grant-authority'),
  revoke: document.querySelector('#revoke-authority'),
  expire: document.querySelector('#expire-evidence'),
  correct: document.querySelector('#correct-evidence'),
  remove: document.querySelector('#remove-evidence'),
  restore: document.querySelector('#restore-evidence'),
  reset: document.querySelector('#reset-demo'),
  probe: document.querySelector('#probe-tools'),
};

function timeLabel() {
  return new Date().toISOString().slice(11, 19) + 'Z';
}

function recordEvent(message) {
  events = [{ at: timeLabel(), message }, ...events].slice(0, 16);
}

function replaceList(element, items, emptyMessage) {
  element.replaceChildren();
  const values = items.length ? items : [emptyMessage];
  for (const value of values) {
    const item = document.createElement('li');
    item.textContent = value;
    element.append(item);
  }
}

function renderLedger() {
  elements.eventLedger.replaceChildren();
  if (!events.length) {
    const empty = document.createElement('li');
    empty.textContent = 'No state transition recorded.';
    elements.eventLedger.append(empty);
  } else {
    for (const event of events) {
      const item = document.createElement('li');
      const stamp = document.createElement('code');
      stamp.textContent = event.at;
      item.append(stamp, document.createTextNode(` — ${event.message}`));
      elements.eventLedger.append(item);
    }
  }

  elements.receiptLedger.replaceChildren();
  if (!state.receipts.length) {
    const empty = document.createElement('li');
    empty.textContent = 'No execution receipt yet.';
    elements.receiptLedger.append(empty);
  } else {
    for (const receipt of [...state.receipts].reverse()) {
      const item = document.createElement('li');
      item.textContent = `${receipt.receiptId} · ${receipt.effect} · ${receipt.evidenceFingerprint.slice(0, 16)}…`;
      elements.receiptLedger.append(item);
    }
  }
}

async function render() {
  const decision = await evaluateControl(state);
  elements.controlState.textContent = decision.status;
  elements.controlState.dataset.state = decision.status;
  elements.controlReason.textContent = decision.reason;
  elements.fingerprint.textContent = `${decision.evidenceFingerprint.slice(0, 20)}…`;
  elements.grantId.textContent = state.authority.grant?.grantId ?? 'none';
  elements.pendingRequest.textContent = String(state.pendingAuthorityRequest);

  elements.manifestStatus.textContent = state.evidence.manifest.present ? 'PRESENT' : 'MISSING';
  elements.manifestRevision.textContent = String(state.evidence.manifest.revision);
  elements.scanStatus.textContent = state.evidence.securityScan.present
    ? `${state.evidence.securityScan.verdict} · ${state.evidence.securityScan.freshness}`
    : 'MISSING';
  elements.scanRevision.textContent = String(state.evidence.securityScan.revision);
  elements.scanFindings.textContent = String(state.evidence.securityScan.findings);
  elements.policyStatus.textContent = state.policy.version;
  elements.hardBlock.textContent = String(state.policy.hardBlocked);

  const compilerToolNames = controller?.getRegisteredToolNames() ?? [];
  replaceList(elements.compilerTools, compilerToolNames, runtimeState === 'AVAILABLE' ? 'No tools registered' : 'WebMCP runtime unavailable');
  replaceList(elements.browserTools, browserToolNames, runtimeState === 'AVAILABLE' ? 'Not probed yet' : 'WebMCP runtime unavailable');

  elements.runtime.textContent = runtimeState;
  elements.runtime.title = runtimeDetail;
  elements.runtime.classList.toggle('available', runtimeState === 'AVAILABLE');
  elements.runtime.classList.toggle('error', runtimeState !== 'AVAILABLE');

  elements.toolNote.textContent = decision.status === 'AUTHORIZED'
    ? 'AUTHORIZED: the execution tool is registered, but it will re-check the live authority snapshot inside execute().'
    : `${decision.status}: execute_authorized_release must not be model-visible.`;

  elements.grant.disabled = decision.status !== 'HUMAN_REQUIRED';
  elements.revoke.disabled = !state.authority.grant || state.authority.revoked;
  elements.expire.disabled = !state.evidence.securityScan.present || state.evidence.securityScan.freshness === 'STALE';
  elements.correct.disabled = !state.evidence.securityScan.present;
  elements.remove.disabled = !state.evidence.manifest.present;
  elements.restore.disabled = (
    decision.status === 'HUMAN_REQUIRED' &&
    !state.authority.grant &&
    state.evidence.manifest.present &&
    state.evidence.securityScan.present &&
    state.evidence.securityScan.verdict === 'PASS' &&
    state.evidence.securityScan.freshness === 'CURRENT'
  );

  renderLedger();
}

async function probeBrowserTools({ record = true } = {}) {
  if (!document.modelContext || typeof document.modelContext.getTools !== 'function') {
    browserToolNames = [];
    if (record) recordEvent('Browser tool probe unavailable: document.modelContext.getTools is absent.');
    await render();
    return;
  }

  try {
    const tools = await document.modelContext.getTools();
    browserToolNames = tools.map((tool) => tool.name).sort();
    if (record) recordEvent(`Browser reported ${browserToolNames.length} WebMCP tool(s).`);
  } catch (error) {
    browserToolNames = [];
    runtimeState = 'WEBMCP_ERROR';
    runtimeDetail = error instanceof Error ? error.message : String(error);
    if (record) recordEvent(`Browser tool probe failed: ${runtimeDetail}`);
  }
  await render();
}

async function syncController() {
  if (!controller) {
    await render();
    return;
  }
  try {
    await controller.sync();
    runtimeState = 'AVAILABLE';
    runtimeDetail = 'document.modelContext accepted the EvidenceBound WebMCP registrations.';
    await probeBrowserTools({ record: false });
  } catch (error) {
    runtimeState = 'WEBMCP_ERROR';
    runtimeDetail = error instanceof Error ? error.message : String(error);
    recordEvent(`WebMCP registration failed: ${runtimeDetail}`);
    await render();
  }
}

async function applyHumanMutation(label, mutation) {
  try {
    state = await mutation(state);
    recordEvent(label);
    await syncController();
  } catch (error) {
    recordEvent(`Rejected human transition: ${error instanceof Error ? error.message : String(error)}`);
    await render();
  }
}

function bindControls() {
  elements.grant.addEventListener('click', () => {
    void applyHumanMutation('Human granted authority to the exact current evidence fingerprint.', grantCurrentAuthority);
  });
  elements.revoke.addEventListener('click', () => {
    void applyHumanMutation('Human revoked the current grant.', revokeAuthority);
  });
  elements.expire.addEventListener('click', () => {
    void applyHumanMutation('Human advanced the controlled security evidence beyond its validity horizon.', expireSecurityEvidence);
  });
  elements.correct.addEventListener('click', () => {
    void applyHumanMutation('Human recorded a corrected security evidence revision; the prior grant no longer matches.', correctSecurityEvidence);
  });
  elements.remove.addEventListener('click', () => {
    void applyHumanMutation('Human removed required release-manifest evidence.', removeRequiredEvidence);
  });
  elements.restore.addEventListener('click', () => {
    void applyHumanMutation('Human restored a fresh evidence set; obsolete authority was cleared.', restoreFreshEvidence);
  });
  elements.reset.addEventListener('click', () => {
    state = createInitialState();
    events = [];
    browserToolNames = [];
    recordEvent('Controlled demo reset to current evidence with no human grant.');
    void syncController();
  });
  elements.probe.addEventListener('click', () => {
    void probeBrowserTools();
  });
}

function initializeWebMCP() {
  const modelContext = document.modelContext;
  if (!modelContext || typeof modelContext.registerTool !== 'function') {
    runtimeState = 'WEBMCP_UNAVAILABLE';
    recordEvent('Controlled demo initialized; WebMCP API not detected in this browser.');
    return;
  }

  controller = createWebMCPController({
    modelContext,
    getState: () => state,
    setState: (nextState) => {
      state = nextState;
      recordEvent('Agent recorded an authority request; no human grant was created.');
      void render();
    },
    onReceipt: (receipt) => {
      state = { ...state, receipts: [...state.receipts, receipt] };
      recordEvent(`Agent executed the controlled effect under ${receipt.grantId}.`);
      void render();
    },
  });

  if (typeof modelContext.addEventListener === 'function') {
    modelContext.addEventListener('toolchange', () => {
      void probeBrowserTools({ record: false });
    });
  }
  recordEvent('Controlled demo initialized; WebMCP API detected.');
}

bindControls();
initializeWebMCP();
await syncController();
