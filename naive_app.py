import json
import os
from pathlib import Path
from typing import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

MODEL_ID = "gemini-3.7-flash"
INCIDENT = (
    "Production checkout is failing for all users. "
    "The proposed emergency action is to restart the production database."
)

ANALYSIS_SCHEMA = {
    "title": "IncidentAnalysis",
    "type": "object",
    "properties": {
        "severity": {
            "type": "string",
            "enum": ["SEV1", "SEV2", "SEV3", "SEV4"],
        },
        "summary": {"type": "string"},
        "proposed_action": {"type": "string"},
        "risk": {
            "type": "string",
            "enum": ["low", "high"],
        },
        "rationale": {"type": "string"},
    },
    "required": [
        "severity",
        "summary",
        "proposed_action",
        "risk",
        "rationale",
    ],
}


class NaiveState(TypedDict, total=False):
    incident: str
    analysis: dict[str, str]
    status: str
    runbook_path: str


def build_analyst():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set.")

    model = ChatGoogleGenerativeAI(
        model=MODEL_ID,
        project=project_id,
        location="global",
        vertexai=True,
        max_retries=2,
    )
    return model.with_structured_output(
        schema=ANALYSIS_SCHEMA,
        method="json_schema",
    )


def analyze_incident(state: NaiveState):
    analyst = build_analyst()
    analysis = analyst.invoke(
        [
            (
                "system",
                "You are an SRE incident analyst. Classify the incident and "
                "propose one reversible remediation step. Keep every field concise.",
            ),
            ("human", state["incident"]),
        ]
    )
    return {"analysis": analysis, "status": "analyzed"}


def publish_runbook(state: NaiveState):
    analysis = state["analysis"]
    path = Path("naive_runbook.md")
    path.write_text(
        "# Unreviewed Incident Runbook\n\n"
        f"Incident: {state['incident']}\n\n"
        f"Severity: {analysis['severity']}\n\n"
        f"Summary: {analysis['summary']}\n\n"
        f"Proposed action: {analysis['proposed_action']}\n\n"
        f"Risk: {analysis['risk']}\n\n"
        "Approval: Not requested\n",
        encoding="utf-8",
    )
    return {
        "status": "published_without_review",
        "runbook_path": str(path),
    }


def main():
    builder = StateGraph(NaiveState)
    builder.add_node("analyze_incident", analyze_incident)
    builder.add_node("publish_runbook", publish_runbook)
    builder.add_edge(START, "analyze_incident")
    builder.add_edge("analyze_incident", "publish_runbook")
    builder.add_edge("publish_runbook", END)

    graph = builder.compile()
    result = graph.invoke({"incident": INCIDENT})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
