const encoder = new TextEncoder();

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function canonicalize(value) {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalize(item)).join(',')}]`;
  }
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`).join(',')}}`;
}

async function sha256Hex(value) {
  const bytes = encoder.encode(value);
  const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

export function createInitialState() {
  return {
    evidence: {
      manifest: {
        present: true,
        artifact: 'evidencebound-control-plane@candidate',
        revision: 1,
      },
      securityScan: {
        present: true,
        verdict: 'PASS',
        findings: 0,
        revision: 1,
        freshness: 'CURRENT',
      },
    },
    policy: {
      version: 'release-policy-v1',
      hardBlocked: false,
    },
    authority: {
      grant: null,
      revoked: false,
    },
    pendingAuthorityRequest: false,
    receipts: [],
  };
}

export async function evidenceFingerprint(state) {
  const authorityInput = {
    evidence: state.evidence,
    policy: state.policy,
  };
  return sha256Hex(canonicalize(authorityInput));
}

export async function evaluateControl(state) {
  const fingerprint = await evidenceFingerprint(state);

  if (
    state.policy.hardBlocked ||
    !state.evidence.manifest.present ||
    !state.evidence.securityScan.present ||
    state.evidence.securityScan.verdict !== 'PASS'
  ) {
    return {
      status: 'BLOCKED',
      reason: 'required evidence or policy gate is not satisfied',
      evidenceFingerprint: fingerprint,
    };
  }

  if (state.evidence.securityScan.freshness !== 'CURRENT') {
    return {
      status: 'STALE',
      reason: 'required security evidence is outside its validity horizon',
      evidenceFingerprint: fingerprint,
    };
  }

  if (state.authority.grant) {
    if (state.authority.revoked) {
      return {
        status: 'INVALIDATED',
        reason: 'human authority was explicitly revoked',
        evidenceFingerprint: fingerprint,
      };
    }
    if (state.authority.grant.evidenceFingerprint !== fingerprint) {
      return {
        status: 'INVALIDATED',
        reason: 'current evidence no longer matches the granted snapshot',
        evidenceFingerprint: fingerprint,
      };
    }
    return {
      status: 'AUTHORIZED',
      reason: 'current evidence and human grant match exactly',
      evidenceFingerprint: fingerprint,
      grantId: state.authority.grant.grantId,
    };
  }

  return {
    status: 'HUMAN_REQUIRED',
    reason: state.pendingAuthorityRequest
      ? 'agent requested authority; a human decision is still required'
      : 'current evidence is usable but no human grant exists',
    evidenceFingerprint: fingerprint,
  };
}

export async function grantCurrentAuthority(state) {
  const next = clone(state);
  const decision = await evaluateControl({
    ...next,
    authority: { grant: null, revoked: false },
  });
  if (decision.status !== 'HUMAN_REQUIRED') {
    throw new Error(`cannot grant authority while control state is ${decision.status}`);
  }
  const fingerprint = decision.evidenceFingerprint;
  next.authority = {
    grant: {
      grantId: `grant-${fingerprint.slice(0, 12)}`,
      evidenceFingerprint: fingerprint,
    },
    revoked: false,
  };
  next.pendingAuthorityRequest = false;
  return next;
}

export function expireSecurityEvidence(state) {
  const next = clone(state);
  next.evidence.securityScan.freshness = 'STALE';
  return next;
}

export function correctSecurityEvidence(state) {
  const next = clone(state);
  next.evidence.securityScan.revision += 1;
  next.evidence.securityScan.findings += 1;
  return next;
}

export function removeRequiredEvidence(state) {
  const next = clone(state);
  next.evidence.manifest.present = false;
  return next;
}
