import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createInitialState,
  grantCurrentAuthority,
  expireSecurityEvidence,
  correctSecurityEvidence,
  removeRequiredEvidence,
} from './control-core.mjs';
import { createWebMCPController } from './webmcp-adapter.mjs';

class FakeModelContext {
  constructor() {
    this.tools = new Map();
    this.history = [];
  }

  async registerTool(tool, options = {}) {
    if (this.tools.has(tool.name)) {
      throw new Error(`duplicate tool registration: ${tool.name}`);
    }
    this.tools.set(tool.name, tool);
    this.history.push({ event: 'registered', name: tool.name, tool });
    options.signal?.addEventListener('abort', () => {
      if (this.tools.get(tool.name) === tool) {
        this.tools.delete(tool.name);
      }
      this.history.push({ event: 'removed', name: tool.name, tool });
    }, { once: true });
  }

  names() {
    return [...this.tools.keys()].sort();
  }

  descriptor(name) {
    return this.tools.get(name);
  }
}

function harness(initialState = createInitialState()) {
  let state = initialState;
  const receipts = [];
  const modelContext = new FakeModelContext();
  const controller = createWebMCPController({
    modelContext,
    getState: () => state,
    setState: (next) => {
      state = next;
    },
    onReceipt: (receipt) => {
      receipts.push(receipt);
      state = { ...state, receipts: [...state.receipts, receipt] };
    },
  });
  return {
    modelContext,
    controller,
    receipts,
    getState: () => state,
    setState: (next) => {
      state = next;
    },
  };
}

const BASE_TOOLS = [
  'inspect_release_control',
  'list_control_receipts',
  'request_release_authority',
];

test('HUMAN_REQUIRED exposes only safe inspection/request/receipt tools', async () => {
  const h = harness();
  const decision = await h.controller.sync();
  assert.equal(decision.status, 'HUMAN_REQUIRED');
  assert.deepEqual(h.modelContext.names(), BASE_TOOLS);
});

test('AUTHORIZED adds the controlled mutation capability', async () => {
  const h = harness(await grantCurrentAuthority(createInitialState()));
  const decision = await h.controller.sync();
  assert.equal(decision.status, 'AUTHORIZED');
  assert.deepEqual(h.modelContext.names(), [...BASE_TOOLS, 'execute_authorized_release'].sort());
});

test('STALE removes a previously registered mutation capability', async () => {
  const h = harness(await grantCurrentAuthority(createInitialState()));
  await h.controller.sync();
  h.setState(expireSecurityEvidence(h.getState()));
  const decision = await h.controller.sync();
  assert.equal(decision.status, 'STALE');
  assert.deepEqual(h.modelContext.names(), BASE_TOOLS);
});

test('INVALIDATED removes a previously registered mutation capability', async () => {
  const h = harness(await grantCurrentAuthority(createInitialState()));
  await h.controller.sync();
  h.setState(correctSecurityEvidence(h.getState()));
  const decision = await h.controller.sync();
  assert.equal(decision.status, 'INVALIDATED');
  assert.deepEqual(h.modelContext.names(), BASE_TOOLS);
});

test('BLOCKED never exposes the mutation capability', async () => {
  const h = harness(removeRequiredEvidence(createInitialState()));
  const decision = await h.controller.sync();
  assert.equal(decision.status, 'BLOCKED');
  assert.deepEqual(h.modelContext.names(), BASE_TOOLS);
});

test('no model-callable tool can grant revoke correct restore or approve human authority', async () => {
  const h = harness(await grantCurrentAuthority(createInitialState()));
  await h.controller.sync();
  for (const name of h.modelContext.names()) {
    assert.doesNotMatch(name, /grant|approve|revoke|correct|restore/i);
  }
});

test('agent request creates a pending human request but does not grant authority', async () => {
  const h = harness();
  await h.controller.sync();
  const requestTool = h.modelContext.descriptor('request_release_authority');
  const result = await requestTool.execute({ reason: 'Release the reviewed candidate' });
  assert.equal(result.status, 'HUMAN_REQUIRED');
  assert.equal(h.getState().pendingAuthorityRequest, true);
  assert.equal(h.getState().authority.grant, null);
});

test('authorized execution produces a bounded controlled receipt', async () => {
  const h = harness(await grantCurrentAuthority(createInitialState()));
  await h.controller.sync();
  const tool = h.modelContext.descriptor('execute_authorized_release');
  const result = await tool.execute({ releaseNote: 'Controlled judge execution' });
  assert.equal(result.status, 'AUTHORIZED');
  assert.equal(result.effect, 'CONTROLLED_RELEASE_EXECUTED');
  assert.equal(result.externalSideEffect, false);
  assert.equal(h.receipts.length, 1);
});

test('retained stale descriptor fails closed after correction and creates no receipt', async () => {
  const h = harness(await grantCurrentAuthority(createInitialState()));
  await h.controller.sync();
  const retainedDescriptor = h.modelContext.descriptor('execute_authorized_release');

  h.setState(correctSecurityEvidence(h.getState()));
  await h.controller.sync();
  assert.deepEqual(h.modelContext.names(), BASE_TOOLS);

  const result = await retainedDescriptor.execute({ releaseNote: 'Attempt using stale descriptor' });
  assert.equal(result.status, 'INVALIDATED');
  assert.equal(result.effect, 'BLOCKED_BEFORE_EFFECT');
  assert.equal(h.receipts.length, 0);
});
