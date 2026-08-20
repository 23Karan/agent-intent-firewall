from __future__ import annotations

from typing import Any


def repository_read(arguments: dict[str, Any]) -> dict[str, Any]:
    repository = str(arguments.get("repository", ""))
    if not repository:
        raise ValueError("repository is required")
    return {"status": "ok", "operation": "repository_read", "repository": repository}


def dependency_scan(arguments: dict[str, Any]) -> dict[str, Any]:
    repository = str(arguments.get("repository", ""))
    if not repository:
        raise ValueError("repository is required")
    return {"status": "ok", "operation": "dependency_scan", "repository": repository}


def generate_report(arguments: dict[str, Any]) -> dict[str, Any]:
    repository = str(arguments.get("repository", ""))
    if not repository:
        raise ValueError("repository is required")
    return {"status": "ok", "operation": "generate_report", "repository": repository}
