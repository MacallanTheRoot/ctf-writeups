#!/usr/bin/env python3
import argparse
import json


def flatten(project):
    payload = {"nodes": [], "edges": []}
    for node in project["nodes"]:
        props = node.get("props", {})
        payload["nodes"].append(
            {
                "id": node["id"],
                "type": node["resource_type"],
                "name": node["name"],
                "namespace": str(props.get("namespace", "")),
                "labels": str(props.get("labels", "")),
                "selector": str(props.get("selector", "")),
                "replicas": int(props.get("replicas") or 1),
                "port": int(props.get("port") or 0),
                "mount": str(props.get("mount", "")),
            }
        )
    for edge in project["edges"]:
        payload["edges"].append(
            {
                "source_id": edge["source_id"],
                "target_id": edge["target_id"],
                "binding": edge["binding"],
                "role": edge["role"],
                "port": int(edge.get("port") or 0),
            }
        )
    return payload


def fix(project):
    nodes = {node["id"]: node for node in project["nodes"]}
    nodes["dep-specter"]["props"]["namespace"] = "specter-net"
    nodes["svc-specter"]["props"]["port"] = 9555
    nodes["pod-veil"]["props"]["mount"] = "specter-key"
    project["edges"].append(
        {
            "source_id": "sec-specter",
            "target_id": "pod-veil",
            "binding": "mount",
            "role": "specter-key",
            "port": 0,
        }
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="extracted demo.wkubeproj")
    parser.add_argument("-o", "--output", default="solved_payload.json")
    args = parser.parse_args()

    with open(args.project, encoding="utf-8") as source:
        project = json.load(source)
    fix(project)
    with open(args.output, "w", encoding="utf-8") as output:
        json.dump(flatten(project), output, separators=(",", ":"))
    print(args.output)


if __name__ == "__main__":
    main()
