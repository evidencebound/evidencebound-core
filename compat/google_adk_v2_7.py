"""Credential-free compatibility acceptance against real Google ADK v2.7.0."""
from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncGenerator
from importlib.metadata import version
from typing import Any

from google.adk.agents.base_agent import BaseAgent
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from evidencebound import (
    ActionDecision,
    EvidenceBound,
    EvidenceRecord,
    PolicyBinding,
    ProvenanceRecord,
)
from evidencebound.adapters.google_adk import (
    AdkCallbackAdapter,
    adk_consequential_action_allowed,
)

EXPECTED_ADK_VERSION = "2.7.0"
APP_NAME = "evidencebound_adk_compat"
USER_ID = "compat-user"
OUTPUT_KEY = "synthetic.output"


class SyntheticAgent(BaseAgent):
    """Real ADK BaseAgent subclass with no model/provider/network dependency."""

    async def _run_async_impl(self, ctx: Any) -> AsyncGenerator[Event, None]:
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            output={"synthetic": True},
        )


def make_adapter() -> AdkCallbackAdapter:
    eb = EvidenceBound(policy=PolicyBinding("adk-compat-policy", "1"))
    return AdkCallbackAdapter(
        evidencebound=eb,
        evidence_factory=lambda _ctx: [
            EvidenceRecord(
                "adk-compat-evidence",
                {"source": "synthetic"},
                ProvenanceRecord("compat-test", "urn:evidencebound:adk:v2.7.0"),
            )
        ],
        output_factory=lambda ctx: ctx.state[OUTPUT_KEY],
        agent_name="synthetic_agent",
    )


def make_agent(adapter: AdkCallbackAdapter) -> SyntheticAgent:
    parameters = tuple(inspect.signature(adapter.after_agent).parameters)
    assert parameters == ("callback_context",), parameters

    # Construction exercises ADK's real callback signature validator. v2.7.0
    # requires the callback parameter to be named exactly ``callback_context``.
    return SyntheticAgent(
        name="synthetic_agent",
        after_agent_callback=adapter.after_agent,
    )


def assert_upstream_rejects_wrong_callback_name() -> None:
    def wrong_name(context: Any) -> None:
        del context

    try:
        SyntheticAgent(name="invalid_callback_agent", after_agent_callback=wrong_name)
    except ValueError:
        return
    raise AssertionError("Google ADK accepted an after_agent_callback without callback_context")


async def make_runner(
    *,
    session_id: str,
) -> tuple[Runner, InMemorySessionService, AdkCallbackAdapter]:
    adapter = make_adapter()
    agent = make_agent(adapter)
    sessions = InMemorySessionService()
    await sessions.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state={OUTPUT_KEY: {"answer": 42}},
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=sessions,
    )
    return runner, sessions, adapter


async def completed_lifecycle_is_allowed() -> None:
    runner, sessions, adapter = await make_runner(session_id="completed")
    before = await sessions.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="completed",
    )
    assert before is not None
    assert not adk_consequential_action_allowed(before.state)

    events = [
        event
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id="completed",
        )
    ]
    assert events, "real ADK runner produced no events"
    assert adapter.last_verification is not None
    assert adapter.last_verification.action is ActionDecision.ALLOW

    after = await sessions.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="completed",
    )
    assert after is not None
    serialized = after.state.get(adapter.state_key)
    assert isinstance(serialized, dict)
    assert serialized["action"] == ActionDecision.ALLOW.value
    assert adk_consequential_action_allowed(after.state)


def _state_delta_contains_verification(event: Event, state_key: str) -> bool:
    state_delta = event.actions.state_delta if event.actions else None
    return bool(state_delta and state_key in state_delta)


async def completed_lifecycle_emits_verification_state_event() -> None:
    runner, _sessions, adapter = await make_runner(session_id="state-event")
    events = [
        event
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id="state-event",
        )
    ]
    assert any(
        _state_delta_contains_verification(event, adapter.state_key) for event in events
    ), "ADK completed lifecycle did not emit the EvidenceBound callback state delta"


async def early_stopped_lifecycle_is_blocked() -> None:
    runner, sessions, adapter = await make_runner(session_id="early-stop")
    stream = runner.run_async(
        user_id=USER_ID,
        session_id="early-stop",
    )
    first_event = await anext(stream)
    assert first_event.author == "synthetic_agent"

    during = await sessions.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="early-stop",
    )
    assert during is not None
    assert adapter.last_verification is None
    assert not adk_consequential_action_allowed(during.state)

    await stream.aclose()

    after_close = await sessions.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="early-stop",
    )
    assert after_close is not None
    assert adapter.last_verification is None
    assert adapter.state_key not in after_close.state
    assert not adk_consequential_action_allowed(after_close.state)


async def main() -> None:
    installed = version("google-adk")
    assert installed == EXPECTED_ADK_VERSION, (
        f"compatibility lane expected google-adk {EXPECTED_ADK_VERSION}, got {installed}"
    )
    print(f"GOOGLE_ADK_VERSION={installed}")
    assert_upstream_rejects_wrong_callback_name()
    await completed_lifecycle_is_allowed()
    await completed_lifecycle_emits_verification_state_event()
    await early_stopped_lifecycle_is_blocked()
    print("GOOGLE_ADK_COMPAT_PASS")


if __name__ == "__main__":
    asyncio.run(main())
