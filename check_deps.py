#!/usr/bin/env python3
"""
Dependency checker for the QUOT project.

Scans every provider requirements.txt, compares against what is installed,
and tells you exactly what to run to fix any gaps.

Usage:
    python check_deps.py              # check all providers
    python check_deps.py openai       # check one provider
    python check_deps.py --install    # check then install missing/outdated
"""

import sys
import re
import subprocess
import importlib.metadata
from pathlib import Path

# Providers that have their own requirements.txt
PROVIDERS = [
    ("root",        Path("requirements.txt")),
    ("openai",      Path("openai/requirements.txt")),
    ("anthropic",   Path("anthropic/requirements.txt")),
    ("google",      Path("google/requirements.txt")),
    ("hugging_face",Path("hugging_face/requirements.txt")),
    ("watsonX",     Path("watsonX/requirements.txt")),
    ("multi",       Path("multi/requirements.txt")),
    ("fastAPI",     Path("fastAPI/requirements.txt")),
]

# Some pip distribution names differ from what importlib.metadata uses.
# Map pip name (lowercased) → metadata dist name.
DIST_NAME_MAP = {
    "langchain-classic":      "langchain_classic",
    "langchain-core":         "langchain_core",
    "langchain-community":    "langchain_community",
    "langchain-chroma":       "langchain_chroma",
    "langchain-openai":       "langchain_openai",
    "langchain-anthropic":    "langchain_anthropic",
    "langchain-google-genai": "langchain_google_genai",
    "langchain-huggingface":  "langchain_huggingface",
    "langchain-ibm":          "langchain_ibm",
    "langchain-text-splitters":"langchain_text_splitters",
    "python-dotenv":          "dotenv",
    "huggingface-hub":        "huggingface_hub",
    "sentence-transformers":  "sentence_transformers",
    "ibm-watsonx-ai":         "ibm_watsonx_ai",
    "google-generativeai":    "google.generativeai",
    "pypdf":                  "pypdf",
    "pydantic":               "pydantic",
}


def parse_requirements(path: Path) -> list[tuple[str, str, str]]:
    """
    Return list of (raw_name, op, version) tuples from a requirements.txt.
    Lines that are comments or blank are skipped.
    """
    results = []
    if not path.exists():
        return results
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_\-\.]+)\s*([><=!~]+)\s*([\w\.\*]+)", line)
        if m:
            results.append((m.group(1), m.group(2), m.group(3)))
        else:
            results.append((line, None, None))
    return results


def installed_version(pip_name: str) -> str | None:
    """Return the installed version string, or None if not found."""
    candidates = [
        pip_name,
        pip_name.replace("-", "_"),
        pip_name.replace("_", "-"),
        DIST_NAME_MAP.get(pip_name.lower()),
    ]
    for name in candidates:
        if name is None:
            continue
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return None


def version_tuple(v: str) -> tuple[int, ...]:
    """Convert '1.2.3' to (1, 2, 3) for simple comparison."""
    try:
        return tuple(int(x) for x in re.split(r"[.\-]", v) if x.isdigit())
    except (ValueError, TypeError):
        return (0,)


def check_provider(req_path: Path) -> list[dict]:
    """Check one requirements.txt and return a list of issue dicts."""
    issues = []
    for name, op, required_ver in parse_requirements(req_path):
        inst = installed_version(name)
        if inst is None:
            issues.append({"pkg": name, "status": "MISSING",
                           "installed": None, "required": f"{op}{required_ver}" if op else None,
                           "req_file": str(req_path)})
        elif op in (">=", "==") and required_ver:
            if version_tuple(inst) < version_tuple(required_ver):
                issues.append({"pkg": name, "status": "OUTDATED",
                               "installed": inst, "required": f"{op}{required_ver}",
                               "req_file": str(req_path)})
    return issues


def check_pip_up_to_date(install_mode: bool) -> None:
    """Warn (and optionally upgrade) if pip itself is outdated."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", "pip"],
            capture_output=True, text=True, check=False
        )
        # Output format: "pip (X.Y.Z)"
        m = re.search(r"pip \((\S+)\)", result.stdout)
        latest = m.group(1) if m else None
        current = installed_version("pip")
        if latest and current and version_tuple(current) < version_tuple(latest):
            print(f"[pip] OUTDATED  installed={current}  latest={latest}")
            if install_mode:
                print("[pip] Upgrading pip ...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                    check=False
                )
            else:
                print("[pip] Run: python -m pip install --upgrade pip")
        else:
            print(f"[pip] OK  ({current})")
    except (OSError, subprocess.SubprocessError):
        print("[pip] Could not check pip version")


def _print_issue_row(iss: dict) -> None:
    """Print a single issue line in the summary table."""
    inst = iss["installed"] or "not installed"
    req  = iss["required"] or "(any)"
    print(f"               {iss['status']:8}  {iss['pkg']:<40}  "
          f"installed={inst:<12}  required={req}")


def main():
    """Check all provider dependencies and report missing or outdated packages."""
    install_mode = "--install" in sys.argv
    filter_provider = next((a for a in sys.argv[1:] if not a.startswith("-")), None)

    targets = [(lbl, p) for lbl, p in PROVIDERS
               if filter_provider is None or lbl == filter_provider]

    if not targets:
        print(f"Unknown provider '{filter_provider}'. "
              f"Options: {[lbl for lbl, _ in PROVIDERS]}")
        sys.exit(1)

    check_pip_up_to_date(install_mode)
    print()

    all_issues: list[dict] = []
    for label, req_path in targets:
        if not req_path.exists():
            print(f"  [{label}] requirements.txt not found — skipping")
            continue
        issues = check_provider(req_path)
        ok_count = sum(1 for _ in parse_requirements(req_path)) - len(issues)
        status = "OK" if not issues else f"{len(issues)} issue(s)"
        print(f"[{label:>12}]  {ok_count} ok   {status}")
        for iss in issues:
            _print_issue_row(iss)
        all_issues.extend(issues)

    if not all_issues:
        print("\nAll dependencies satisfied.")
        return

    # Group by requirements file for targeted install commands
    by_file: dict[str, list[str]] = {}
    for iss in all_issues:
        by_file.setdefault(iss["req_file"], []).append(iss["pkg"])

    print(f"\n{len(all_issues)} issue(s) found.")
    print("\nTo fix, run:")
    for req_file in by_file:
        print(f"  pip install -r {req_file}")

    if install_mode:
        for req_file in by_file:
            print(f"\n  Installing from {req_file} ...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file],
                check=False
            )
            if result.returncode != 0:
                print(f"  pip install failed for {req_file} (exit {result.returncode})")
    else:
        print("\nRun with --install to install automatically:")
        print("  python check_deps.py --install")


if __name__ == "__main__":
    main()
