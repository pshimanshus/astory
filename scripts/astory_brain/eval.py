from __future__ import annotations

import json
from pathlib import Path

from .retrieval import recall


def run_retrieval_eval(
    index_dir: str | Path,
    qrels_path: str | Path,
    top_k: int = 5,
) -> dict:
    qrels = json.loads(Path(qrels_path).read_text(encoding="utf-8"))
    failures: list[dict] = []
    hits = 0
    forbidden_hit_count = 0

    for item in qrels:
        results = recall(
            index_dir,
            item["query"],
            role=item.get("role"),
            run_id=item.get("run_id"),
            limit=top_k,
        )
        result_paths = [result.chunk.path for result in results]
        expected_paths = item.get("expected_paths", [])
        forbidden_paths = item.get("forbidden_paths", [])
        missing_expected = [path for path in expected_paths if path not in result_paths]
        if not missing_expected:
            hits += 1
        else:
            failures.append(
                {
                    "query": item["query"],
                    "code": "expected_path_missing",
                    "expected_paths": missing_expected,
                    "actual_paths": result_paths,
                }
            )
        forbidden = [path for path in forbidden_paths if path in result_paths]
        if forbidden:
            forbidden_hit_count += len(forbidden)
            failures.append(
                {
                    "query": item["query"],
                    "code": "forbidden_path_hit",
                    "forbidden_paths": forbidden,
                    "actual_paths": result_paths,
                }
            )

    recall_at_k = hits / len(qrels) if qrels else 1.0
    return {
        "status": "pass" if recall_at_k >= 1.0 and forbidden_hit_count == 0 else "fail",
        "recall_at_k": recall_at_k,
        "forbidden_hit_count": forbidden_hit_count,
        "failures": failures,
    }
