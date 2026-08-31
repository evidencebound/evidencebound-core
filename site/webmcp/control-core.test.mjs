import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createInitialState,
  evaluateControl,
  grantCurrentAuthority,
  expireSecurityEvidence,
  correctSecurityEvidence,
  removeRequiredEvidence,
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
