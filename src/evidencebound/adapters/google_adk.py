"""Dependency-free integration seam for Google ADK agent callbacks.

Google ADK's tested callback contract invokes ``after_agent_callback`` with a
single keyword argument named ``callback_context``. EvidenceBound does not import
ADK; callers provide functions that extract evidence and the protected output from
that context (commonly from ADK state populated through ``output_key``).
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from ..api import EvidenceBound
from ..models import ActionDecision, EvidenceRecord, VerificationResult

EvidenceFactory = Callable[[Any], list[EvidenceRecord]]
OutputFactory = Callable[[Any], object]
DEFAULT_ADK_STATE_KEY = "evidencebound.verification"


def adk_consequential_action_allowed(
    state: object,
    *,
    state_key: str = DEFAULT_ADK_STATE_KEY,
) -> bool:
    """Return True only for an explicit serialized EvidenceBound ``ALLOW`` result.

    The helper deliberately treats missing, malformed or incomplete callback state
    as blocked. It does not infer approval from an ADK response event or from agent
    completion alone.
    """
    if not isinstance(state, Mapping):
        return False
    result = state.get(state_key)
    if not isinstance(result, Mapping):
        return False
    return result.get("action") == ActionDecision.ALLOW.value


@dataclass(slots=True)
class AdkCallbackAdapter:
    """Callable-compatible ADK after-agent adapter without an ADK dependency.

    Register ``adapter.after_agent`` as ``after_agent_callback``. The method
    returns ``None`` so it does not replace the agent response. It stores the
    structured EvidenceBound verification in ``callback_context.state`` when
    that object exposes a mutable mapping-like ``state`` attribute.
    """

    evidencebound: EvidenceBound
    evidence_factory: EvidenceFactory
    output_factory: OutputFactory
    agent_name: str
    state_key: str = DEFAULT_ADK_STATE_KEY
    last_verification: VerificationResult | None = None

    def after_agent(self, callback_context: Any) -> None:
        evidence = self.evidence_factory(callback_context)
        output = self.output_factory(callback_context)
        checkpoint = self.evidencebound.checkpoint(
            agent=self.agent_name,
            evidence=evidence,
            output=output,
        )
        result = self.evidencebound.verify(checkpoint)
        self.last_verification = result
        state = getattr(callback_context, "state", None)
        if state is not None:
            state[self.state_key] = result.to_dict()
        return None
