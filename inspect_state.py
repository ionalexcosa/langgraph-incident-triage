import argparse
import json

from app import DB_PATH, build_graph
from langgraph.checkpoint.sqlite import SqliteSaver

def parse_args():
    parser = argparse.ArgumentParser(
        description="Inspect a saved incident workflow without resuming it."
    )
    parser.add_argument("--thread", required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    config = {"configurable": {"thread_id": args.thread}}

    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        graph = build_graph(checkpointer)
        snapshot = graph.get_state(config)

    if not snapshot.values:
        raise SystemExit(f"No checkpoint found for thread {args.thread}.")

    report = {
        "values": snapshot.values,
        "next": list(snapshot.next),
        "created_at": snapshot.created_at,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()