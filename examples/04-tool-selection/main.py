"""Tool selection with an explicit way to choose nothing.

Two design points, both borrowed from patterns visible in real integrations in
the catalog:

1. **Always include a `none` option.** Without one, a closed choice must return
   *something*, so an agent with no suitable tool returns the least wrong tool
   instead of declining. The option set is the only place "do nothing" can live.

2. **Ask a separate Noul about whether a tool is needed at all.** A choice over
   tools answers "which is most suitable", which is a relative question. Whether
   this turn needs a tool is an absolute one. The vendor's own limitations doc
   makes this distinction explicitly: a Choice over options and one Noul per
   option are not the same question.

Run:
    pip install typesafe-sdk
    export TYPESAFE_API_KEY=...
    python main.py
"""

from __future__ import annotations

from typesafe_sdk import Choice, Noul, TypeSafeClient

TOOLS = {
    "search_docs": "Look something up in the product documentation",
    "read_file": "Read a named file from the user's project",
    "run_tests": "Execute the project's test suite",
    "open_pr": "Create a pull request from the current branch",
    # The escape hatch. Without this row the model cannot decline.
    "none": "No tool is needed; answer from the conversation alone",
}

TURNS = [
    "What does the retry policy default to?",
    "Open a PR for this branch.",
    "Thanks, that worked!",
    # Ambiguous on purpose: could be read as a request to run tests.
    "I think something's broken but I'm not sure what.",
]


def select_tool(client: TypeSafeClient, turn: str) -> None:
    response = client.system_one(
        state={"turn": turn, "available_tools": list(TOOLS)},
        questions={
            "tool": Choice(
                instructions="Which tool, if any, should handle this turn",
                criteria=TOOLS,
            ),
            "needs_tool": Noul(
                instructions="This turn requires calling a tool at all",
            ),
        },
    )

    tool = response.answers["tool"]
    needs = response.answers["needs_tool"]

    print(f"\n{turn}")
    print(f"  tool        {tool.choice}  (confidence {tool.confidence:.2f})")
    print(f"  needs_tool  {needs.noul:.2f}")

    # The two answers can disagree, and that disagreement is information: a
    # confident tool pick with a low needs_tool probability usually means the
    # turn is conversational and the "best" tool is just the least irrelevant.
    #
    # 0.5 and 0.6 below are unverified starting points: not measured here,
    # and not taken from any catalogued project or vendor page. Tune both on
    # your own turns and pin the model version you tuned against.
    # examples/README.md gives the range of constants catalogued projects
    # use, as observations, not advice.
    if tool.choice == "none" or needs.noul < 0.5:
        print("  -> answer directly, no tool call")
    elif tool.confidence < 0.6:
        print("  -> ambiguous; hand the turn to the planning model")
    else:
        print(f"  -> call {tool.choice}")
        # This picks WHICH tool. Filling in the arguments is a separate job:
        # closed-set arguments can be more questions in the same request, but
        # free-form ones need code or a generative model.


def main() -> None:
    client = TypeSafeClient()
    for turn in TURNS:
        select_tool(client, turn)


if __name__ == "__main__":
    main()
