"""Replay local PrologMCP and Euclid-MCP over stdio. See --help.

knowledge admits one flat Horn clause per line. Arguments are atoms or named
variables, and rule bodies are positive conjunctions. Reject unsupported input.
"""
import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
from contextlib import AsyncExitStack
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PINS = {
    "prolog": "4ae536fd9b1cef8419d1798b5d4cb1569cba3cae",
    "euclid": "aed10179131fc990739f5d69b0584f4a065f0faa",
}
TERM = re.compile(r"[a-z][a-z0-9_]*\(\s*[a-zA-Z][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z][a-zA-Z0-9_]*)*\s*\)")
VARIABLE = re.compile(r"\b[A-Z][a-zA-Z0-9_]*\b")


def euclid_program(source):
    def term(match):
        if not TERM.fullmatch(match):
            raise ValueError(f"Unsupported term {match!r}")
        return VARIABLE.sub(lambda m: "$" + m[0].lower(), match)

    lines = []
    for raw in source.splitlines():
        clause = raw.strip()
        if not clause:
            continue
        if not clause.endswith("."):
            raise ValueError(f"Missing terminal period in {clause!r}")
        parts = clause[:-1].split(":-")
        head = term(parts[0].strip())
        if len(parts) == 2:
            body = re.split(r"(?<=\))\s*,\s*", parts[1].strip())
            head += " IF " + " AND ".join(term(literal) for literal in body)
        elif len(parts) != 1:
            raise ValueError("Bad clause")
        lines.append(head)
    return "\n".join(lines)


def run_output(*args):
    return subprocess.check_output(args, text=True, encoding="utf-8").strip()


def server_spec(kind, args):
    root = getattr(args, kind + "_repo").resolve()
    commit = run_output("git", "-C", str(root), "rev-parse", "HEAD")
    if commit != PINS[kind] or run_output("git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"):
        raise ValueError(f"Use a clean checkout of {kind} commit {PINS[kind]}")
    python = getattr(args, kind + "_python").resolve()
    module = "prolog_mcp.server" if kind == "prolog" else "euclid_mcp"
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "USERPROFILE", "HOME", "TEMP", "TMP") if key in os.environ}
    env["PATH"] = str(args.swipl.resolve().parent) + os.pathsep + env["PATH"]
    env["PYTHONPATH"] = str(root / "src" if kind == "prolog" else root)
    env["PYTHONUTF8"] = "1"
    metadata = {
        "server_commit": commit,
        "server_entry": f"python -m {module}",
        "server_runtime": run_output(str(python), "-c", "import platform,importlib.metadata as m; print(platform.python_version(), 'mcp', m.version('mcp'))"),
        "swipl": run_output(str(args.swipl.resolve()), "--version"),
        "client_sdk": version("mcp"),
    }
    return StdioServerParameters(command=str(python), args=["-m", module], env=env, cwd=str(root)), metadata


async def one_case(session, kind, case):
    record = {"id": case["id"], "calls": [], "predicted": None}
    start = perf_counter()

    async def call(name, params):
        begun = perf_counter()
        entry = {"tool": name, "arguments": params}
        record["calls"].append(entry)
        try:
            reply = await asyncio.wait_for(session.call_tool(name, params), timeout=45)
            entry["response"] = reply.model_dump(mode="json", by_alias=True, exclude_none=True)
            if reply.isError:
                raise ValueError(f"{name} returned MCP tool error")
            if reply.structuredContent is not None:
                return reply.structuredContent
            return json.loads(reply.content[0].text)
        finally:
            entry["elapsed_ms"] = round((perf_counter() - begun) * 1000, 2)

    load = None
    try:
        source = case["knowledge"]
        translated = euclid_program(source)
        if kind == "prolog":
            result = await call("create_session", {"source_text": source})
            load = result.get("load_id")
            if not load or not result["ok"] or any(m.get("severity") == "error" for m in result["messages"]):
                raise ValueError("Session load failed")
        bits = []
        for goal in case["goals"]:
            if not TERM.fullmatch(goal) or VARIABLE.search(goal):
                raise ValueError("Ground query required")
            if kind == "euclid":
                result = await call("reason", {"knowledge": translated, "query": goal, "max_solutions": 1, "max_depth": 30})
                if result.get("error") or result.get("query") != goal or not isinstance(result.get("solutions"), list):
                    raise ValueError("Euclid query error: " + str(result.get("error")))
                proved = bool(result["solutions"])
            else:
                result = await call("run_goal", {"load_id": load, "goal": goal, "time_limit": 30, "max_answers": 1})
                if not result["ok"] or result.get("outcome") not in ("success", "failure"):
                    raise ValueError("Prolog query error: " + str(result))
                proved = result["outcome"] == "success"
            bits.append("1" if proved else "0")
        record["bits"] = "".join(bits)
        record["predicted"] = case["decode"][record["bits"]]
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if load:
            try:
                result = await call("close_session", {"load_id": load})
                if not result.get("closed"):
                    raise ValueError("Session did not close")
            except Exception as exc:
                record["cleanup_error"] = str(exc)
        record["elapsed_ms"] = round((perf_counter() - start) * 1000, 2)
    return record


async def main(args):
    cases_bytes = args.cases.read_bytes()
    cases = json.loads(cases_bytes.decode("utf-8-sig"))
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Duplicate case ID")
    args.output.mkdir(parents=True, exist_ok=True)
    for kind in args.servers:
        server, metadata = server_spec(kind, args)
        output = {"server": kind, **metadata, "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(), "cases": []}
        path = args.output / (kind + ".json")
        async with AsyncExitStack() as stack:
            r, w = await stack.enter_async_context(stdio_client(server))
            session = await stack.enter_async_context(ClientSession(r, w))
            await asyncio.wait_for(session.initialize(), timeout=45)
            for case in cases:
                row = await one_case(session, kind, case)
                output["cases"].append(row)
                tmp = path.with_suffix(".tmp")
                tmp.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                tmp.replace(path)
        print(kind, len(output["cases"]), "cases,", sum("error" in r for r in output["cases"]), "errors", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--servers", nargs="+", choices=PINS, default=list(PINS))
    for kind in PINS:
        p.add_argument("--" + kind + "-repo", type=Path)
        p.add_argument("--" + kind + "-python", type=Path)
    p.add_argument("--swipl", required=True, type=Path)
    options = p.parse_args()
    for selected in options.servers:
        if not getattr(options, selected + "_repo") or not getattr(options, selected + "_python"):
            p.error("Selected servers need their --NAME-repo and --NAME-python.")
    asyncio.run(main(options))
