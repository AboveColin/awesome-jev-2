"""Act automatically above a threshold, escalate below it.

This is the pattern calibration exists for: because confidence tracks accuracy,
a threshold becomes a policy dial between throughput and error rate rather than
a guess.

The model call and the plumbing are done. The POLICY — where the thresholds sit
and what happens in between — is deliberately left to you in `decide_action`,
because it depends on what being wrong actually costs in your system, and that
is not something this file can know.

Run:
    pip install typesafe-sdk
    export TYPESAFE_API_KEY=...
    python main.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from typesafe_sdk import Choice, TypeSafeClient

Action = Literal["auto", "review", "reject"]

QUEUES = {
    "refund": "Customer wants money back for a charge they dispute",
    "bug": "Something in the product is broken or erroring",
    "howto": "Customer is asking how to do something that already works",
    "other": "Does not fit the queues above",
}

TICKETS = [
    "You charged me twice for September. Please refund the duplicate.",
    "The export button spins forever and then shows a 500 page.",
    "Where do I change my notification settings?",
    # Deliberately ambiguous: a refund request AND a bug report at once.
    "Your billing page crashed and now I've been charged two times. Fix it and refund me.",
]


@dataclass(frozen=True)
class Decision:
    """One routing decision plus everything needed to audit it later."""

    ticket: str
    queue: str
    confidence: float
    probabilities: dict[str, float]


def classify(client: TypeSafeClient, ticket: str) -> Decision:
    response = client.system_one(
        state=ticket,
        questions={
            "queue": Choice(
                instructions="Which support queue should handle this ticket",
                criteria=QUEUES,
            )
        },
    )
    answer = response.answers["queue"]
    return Decision(
        ticket=ticket,
        queue=answer.choice,
        confidence=answer.confidence,
        probabilities=dict(answer.probabilities),
    )


# ---------------------------------------------------------------------------
# YOUR TURN
# ---------------------------------------------------------------------------
def decide_action(decision: Decision) -> tuple[Action, str]:
    """Turn a decision plus its confidence into what the system actually does.

    Return one of:
        ("auto",   reason)  -- route it, no human involved
        ("review", reason)  -- put it in a human queue
        ("reject", reason)  -- refuse to route; send it somewhere safe

    Things worth weighing:

    * **One threshold or two?** A single cutoff gives you auto-or-review. Two
      cutoffs let you separate "confidently right" from "confidently unroutable"
      — useful when a low-confidence answer means the taxonomy is wrong, not
      that the ticket is hard.

    * **Should the threshold depend on the queue?** Misrouting a `howto` costs
      a few minutes. Misrouting a `refund` touches money. The Inbox Zero entry
      in this catalog chooses a separate threshold for each decision for
      exactly this reason. examples/README.md gives the range of the constants
      catalogued projects compare Jev's answers with: what they chose, not
      what you should.

    * **Is `confidence` enough, or do you want the runner-up?** Two options at
      0.45/0.44 and one at 0.89 can report similar confidence in some shapes.
      `decision.probabilities` is available if the margin matters to you.

    * **What about `other`?** A confident `other` is a different signal from an
      unconfident `refund`. One means "this genuinely doesn't fit"; the other
      means "I couldn't tell". They probably deserve different handling.

    Whatever you choose, the reason string should be good enough to appear in an
    audit log — the point of a calibrated gate is being able to explain later
    why a given ticket was or was not touched by a person.
    """
    raise NotImplementedError("Implement your escalation policy here")


def main() -> None:
    client = TypeSafeClient()

    for ticket in TICKETS:
        decision = classify(client, ticket)
        print(f"\n{decision.ticket}")
        print(f"  -> {decision.queue}  confidence {decision.confidence:.2f}")
        print(f"     {decision.probabilities}")
        try:
            action, reason = decide_action(decision)
            print(f"     action: {action}  ({reason})")
        except NotImplementedError as exc:
            print(f"     action: {exc}")


if __name__ == "__main__":
    main()
