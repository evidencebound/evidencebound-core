import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createInitialState,
  evaluateControl,
  grantCurrentAuthority,
  revokeAuthority,
  expireSecurityEvidence,
  correctSecurityEvidence,
  removeRequiredEvidence,
  restoreFreshEvidence,
  recordPendingAuthorityRequest,
  createExecutionReceipt,
} from './control-core.mjs';

test('initial current evidence requires a human grant', async () => {
  const state = createInitialState();
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'HUMAN_REQUIRED');
});

test('grant bound to current evidence authorizes execution', async () => {
  let state = createInitialState();
  state = await grantCurrentAuthority(state);
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'AUTHORIZED');
});

test('expired evidence is stale even with a previous grant', async () => {
  let state = await grantCurrentAuthority(createInitialState());
  state = expireSecurityEvidence(state);
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'STALE');
});

test('corrected evidence invalidates an existing grant', async () => {
  let state = await grantCurrentAuthority(createInitialState());
  state = correctSecurityEvidence(state);
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'INVALIDATED');
});

test('missing required evidence blocks', async () => {
  const state = removeRequiredEvidence(createInitialState());
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'BLOCKED');
});

test('explicit revocation invalidates the exact prior grant', async () => {
  let state = await grantCurrentAuthority(createInitialState());
  state = revokeAuthority(state);
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'INVALIDATED');
  assert.match(decision.reason, /revoked/i);
});

test('restoring fresh evidence clears obsolete authority and requires a new human grant', async () => {
  let state = await grantCurrentAuthority(createInitialState());
  state = correctSecurityEvidence(state);
  state = restoreFreshEvidence(state);
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'HUMAN_REQUIRED');
  assert.equal(state.authority.grant, null);
});

test('an agent authority request never grants authority', async () => {
  let state = createInitialState();
  state = recordPendingAuthorityRequest(state);
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'HUMAN_REQUIRED');
  assert.equal(state.pendingAuthorityRequest, true);
  assert.equal(state.authority.grant, null);
});

test('execution receipt can only be created from current AUTHORIZED state', async () => {
  const unauthorized = createInitialState();
  await assert.rejects(() => createExecutionReceipt(unauthorized), /AUTHORIZED/);

  const authorized = await grantCurrentAuthority(createInitialState());
  const receipt = await createExecutionReceipt(authorized);
  assert.equal(receipt.status, 'AUTHORIZED');
  assert.match(receipt.receiptId, /^receipt-[a-f0-9]{16}$/);
  assert.equal(receipt.effect, 'CONTROLLED_RELEASE_EXECUTED');
  assert.equal(receipt.externalSideEffect, false);
});
