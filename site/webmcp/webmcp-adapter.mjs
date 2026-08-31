import {
  createExecutionReceipt,
  evaluateControl,
  recordPendingAuthorityRequest,
} from './control-core.mjs';

const EMPTY_SCHEMA = Object.freeze({
  type: 'object',
  properties: {},
  additionalProperties: false,
});

function controlSummary(state) {
  return {
    manifestPresent: state.evidence.manifest.present,
    manifestRevision: state.evidence.manifest.revision,
    securityEvidencePresent: state.evidence.securityScan.present,
    securityVerdict: state.evidence.securityScan.verdict,
    securityRevision: state.evidence.securityScan.revision,
    securityFreshness: state.evidence.securityScan.freshness,
    policyVersion: state.policy.version,
    pendingAuthorityRequest: state.pendingAuthorityRequest,
    grantId: state.authority.grant?.grantId ?? null,
    grantRevoked: state.authority.revoked,
  };
}

function nextAction(status) {
  switch (status) {
    case 'AUTHORIZED':
      return 'execute_authorized_release is available while this exact authority snapshot remains valid';
    case 'HUMAN_REQUIRED':
      return 'request authority, then wait for an explicit human grant in the visible page UI';
    case 'STALE':
      return 'a human must restore fresh evidence before any new grant can authorize execution';
    case 'INVALIDATED':
      return 'the prior grant cannot be reused; a human must restore/review evidence and issue a new grant';
    case 'BLOCKED':
      return 'required evidence or policy must be repaired by a human before execution can become available';
    default:
      return 'stop; unknown control state';
  }
}

export function createWebMCPController({
  modelContext,
  getState,
  setState,
  onReceipt = () => {},
}) {
  if (!modelContext || typeof modelContext.registerTool !== 'function') {
    throw new TypeError('modelContext.registerTool is required');
  }
  if (typeof getState !== 'function' || typeof setState !== 'function') {
    throw new TypeError('getState and setState callbacks are required');
  }
  if (typeof onReceipt !== 'function') {
    throw new TypeError('onReceipt must be a function');
  }

  const baseControllers = new Map();
  const registeredNames = new Set();
  let executeController = null;
  let baseRegistered = false;
  let disposed = false;

  async function register(tool) {
    const controller = new AbortController();
    controller.signal.addEventListener('abort', () => {
      registeredNames.delete(tool.name);
    }, { once: true });
    await modelContext.registerTool(tool, { signal: controller.signal });
    registeredNames.add(tool.name);
    return controller;
  }

  async function ensureBaseTools() {
    if (baseRegistered) {
      return;
    }

    const inspectController = await register({
      name: 'inspect_release_control',
      title: 'Inspect release control',
      description: 'Inspect current EvidenceBound release evidence, authority status, and the safe next action.',
      inputSchema: EMPTY_SCHEMA,
      annotations: {
        readOnlyHint: true,
        untrustedContentHint: false,
      },
      execute: async () => {
        const state = getState();
        const decision = await evaluateControl(state);
        return {
          ...decision,
          evidence: controlSummary(state),
          modelVisibleTools: [...registeredNames].sort(),
          nextAction: nextAction(decision.status),
          boundary: 'CONTROLLED_DEMO_NO_EXTERNAL_RELEASE',
        };
      },
    });
    baseControllers.set('inspect_release_control', inspectController);

    const requestController = await register({
      name: 'request_release_authority',
      title: 'Request release authority',
      description: 'Record a visible request for human release authority. This tool never grants, approves, or restores authority.',
      inputSchema: {
        type: 'object',
        properties: {
          reason: {
            type: 'string',
            minLength: 1,
            maxLength: 240,
            description: 'Short reason the agent is requesting human authority.',
          },
        },
        required: ['reason'],
        additionalProperties: false,
      },
      annotations: {
        readOnlyHint: false,
        untrustedContentHint: false,
      },
      execute: async ({ reason }) => {
        const current = getState();
        const next = recordPendingAuthorityRequest(current);
        setState(next);
        const decision = await evaluateControl(next);
        return {
          ...decision,
          requestRecorded: true,
          requestReason: reason,
          humanGrantCreated: false,
          nextAction: nextAction(decision.status),
        };
      },
    });
    baseControllers.set('request_release_authority', requestController);

    const receiptsController = await register({
      name: 'list_control_receipts',
      title: 'List control receipts',
      description: 'List recent controlled release receipts created in this browser tab. Receipts do not claim an external deployment.',
      inputSchema: EMPTY_SCHEMA,
      annotations: {
        readOnlyHint: true,
        untrustedContentHint: false,
      },
      execute: async () => {
        const state = getState();
        return {
          receipts: state.receipts.slice(-10),
          count: state.receipts.length,
          durability: 'TAB_LOCAL_CONTROLLED_DEMO',
        };
      },
    });
    baseControllers.set('list_control_receipts', receiptsController);

    baseRegistered = true;
  }

  async function sync() {
    if (disposed) {
      throw new Error('WebMCP controller is disposed');
    }

    await ensureBaseTools();

    if (executeController) {
      executeController.abort();
      executeController = null;
    }

    const decision = await evaluateControl(getState());
    if (decision.status !== 'AUTHORIZED') {
      return decision;
    }

    executeController = await register({
      name: 'execute_authorized_release',
      title: 'Execute authorized controlled release',
      description: 'Execute the controlled release only while current evidence exactly matches a live human grant. Revalidates authority at execution time.',
      inputSchema: {
        type: 'object',
        properties: {
          releaseNote: {
            type: 'string',
            minLength: 1,
            maxLength: 240,
            description: 'Short controlled-demo execution note.',
          },
        },
        required: ['releaseNote'],
        additionalProperties: false,
      },
      annotations: {
        readOnlyHint: false,
        untrustedContentHint: false,
      },
      execute: async ({ releaseNote }) => {
        const liveState = getState();
        const liveDecision = await evaluateControl(liveState);
        if (liveDecision.status !== 'AUTHORIZED') {
          return {
            ...liveDecision,
            effect: 'BLOCKED_BEFORE_EFFECT',
            externalSideEffect: false,
            releaseNote,
          };
        }

        const receipt = await createExecutionReceipt(liveState);
        onReceipt(receipt);
        return {
          ...receipt,
          releaseNote,
          boundary: 'CONTROLLED_DEMO_NO_EXTERNAL_RELEASE',
        };
      },
    });

    return decision;
  }

  function dispose() {
    if (executeController) {
      executeController.abort();
      executeController = null;
    }
    for (const controller of baseControllers.values()) {
      controller.abort();
    }
    baseControllers.clear();
    baseRegistered = false;
    disposed = true;
  }

  function getRegisteredToolNames() {
    return [...registeredNames].sort();
  }

  return {
    sync,
    dispose,
    getRegisteredToolNames,
  };
}
