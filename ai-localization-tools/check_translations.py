"""
check_translations.py

Asks an LLM (Claude) to review the Spanish translations (es.lproj) against the
English source strings (en.lproj) and flag anything that looks wrong,
machine-literal, or like a missing/placeholder translation.

IMPORTANT: everything the LLM reports is an "AI suggestion to review", NOT a
definitive error. A fluent human speaker should make the final call.

Before calling the LLM, a simple non-AI check runs too (missing keys, empty
values, identical-to-English values), so you get something useful even if the
AI output is poor.

Usage:
    python check_translations.py
    python check_translations.py --model claude-sonnet-5-5
"""

import argparse
import os
import re
import sys
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
STRINGS_DIR = REPO_ROOT / "iOSLocalizationUITestAutomation"
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

STRING_LINE = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', re.MULTILINE)


def read_strings_file(path: Path) -> dict:
    """Return {key: value} from a Localizable.strings file."""
    try:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            text = path.read_text(encoding="utf-16")
    except OSError as err:
        sys.exit(f"Could not read {path}: {err}")
    return {key: value for key, value in STRING_LINE.findall(text)}


def plain_checks(en: dict, es: dict) -> list:
    """Simple rule-based checks (no AI). Returns a list of messages."""
    problems = []
    for key, english in en.items():
        spanish = es.get(key)
        if spanish is None:
            problems.append(f'"{key}": missing in es.lproj')
        elif not spanish.strip():
            problems.append(f'"{key}": Spanish value is empty')
        elif spanish.strip().lower() == english.strip().lower():
            problems.append(f'"{key}": identical to English ("{english}"), maybe untranslated '
                            "(fine for names or loanwords)")
    for key in es:
        if key not in en:
            problems.append(f'"{key}": in es.lproj but not in en.lproj (unused?)')
    return problems


def ask_llm(en: dict, es: dict, model: str) -> str:
    """Ask the model to review the translations. Returns '' on failure."""
    pairs = "\n".join(
        f'- key "{k}": EN = "{v}" | ES = "{es.get(k, "(MISSING)")}"' for k, v in en.items()
    )
    prompt = (
        "Review these English -> Spanish UI translations for a to-do iOS app. "
        "Flag only entries that look wrong, too literal / machine-translated, "
        "inconsistent in tone, or like a missing or placeholder translation. "
        "For each flagged entry give: the key, the issue, and a suggested alternative. "
        "If an entry looks fine, do not mention it. If nothing looks wrong, say "
        "'No issues spotted'. Be honest about uncertainty.\n\n" + pairs
    )
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as err:
        print(f"Anthropic API error: {err}")
        return ""
    parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
    return "".join(parts).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-assisted review of Spanish translations.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    en_path = STRINGS_DIR / "en.lproj" / "Localizable.strings"
    es_path = STRINGS_DIR / "es.lproj" / "Localizable.strings"
    for path in (en_path, es_path):
        if not path.exists():
            sys.exit(f"File not found: {path}")

    en, es = read_strings_file(en_path), read_strings_file(es_path)
    if not en:
        sys.exit("No English strings found; nothing to check.")

    print("=" * 60)
    print("TRANSLATION CHECK")
    print("=" * 60)

    print("\n[1] Plain checks (rule-based, no AI)")
    problems = plain_checks(en, es)
    print("\n".join(f"  - {p}" for p in problems) if problems else "  No issues found by simple rules.")

    print("\n[2] AI suggestions to review (NOT definitive)")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("  Skipped: ANTHROPIC_API_KEY is not set. See README.md.")
        return
    result = ask_llm(en, es, args.model)
    if not result:
        print("  The AI returned no output. Only the plain checks above apply.")
        return
    print(result)

    print("\nReminder: the AI can be wrong or miss problems. "
          "Have a Spanish speaker review the translations before shipping.")


if __name__ == "__main__":
    main()
