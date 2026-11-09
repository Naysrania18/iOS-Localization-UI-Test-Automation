"""
generate_test_cases.py

Reads the app's Localizable.strings files and asks an LLM (Claude, via the
Anthropic API) to suggest localization UI test case IDEAS for each string.

The output is printed and saved to generated_test_cases.md.
The LLM output is a starting point only: a human must review it.

Usage (from the repo root or from this folder):
    python generate_test_cases.py
    python generate_test_cases.py --model claude-sonnet-5-5
"""

import argparse
import os
import re
import sys
from pathlib import Path

import anthropic

# ---------------------------------------------------------------------------
# Paths: this script lives in <repo>/ai-localization-tools/, the app lives in
# <repo>/iOSLocalizationUITestAutomation/.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
STRINGS_DIR = REPO_ROOT / "iOSLocalizationUITestAutomation"
OUTPUT_FILE = Path(__file__).resolve().parent / "generated_test_cases.md"

# The model can be changed with --model or the ANTHROPIC_MODEL env variable.
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# Matches lines like:  "title" = "My To-Do List";
STRING_LINE = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', re.MULTILINE)


def read_strings_file(path: Path) -> dict:
    """Return {key: value} from a Localizable.strings file."""
    try:
        # utf-8-sig also handles a BOM; Xcode sometimes saves as UTF-16.
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            text = path.read_text(encoding="utf-16")
    except OSError as err:
        print(f"Could not read {path}: {err}")
        return {}
    return {key: value for key, value in STRING_LINE.findall(text)}


def load_languages() -> dict:
    """Load en (required) and es (optional). Returns {'en': {...}, 'es': {...}}."""
    languages = {}
    for code in ("en", "es"):
        path = STRINGS_DIR / f"{code}.lproj" / "Localizable.strings"
        if path.exists():
            languages[code] = read_strings_file(path)
        elif code == "en":
            sys.exit(f"Required file not found: {path}")
        else:
            print(f"Note: {path} not found, continuing with English only.")
    return languages


def build_prompt(languages: dict) -> str:
    """Describe the strings to the model and say what we want back."""
    lines = []
    for key, english in languages["en"].items():
        line = f'- key "{key}": EN = "{english}"'
        if "es" in languages:
            line += f' | ES = "{languages["es"].get(key, "(MISSING)")}"'
        lines.append(line)

    return (
        "You are helping a QA engineer test the localization of a small iOS "
        "to-do app (SwiftUI, tested with XCUITest). The app has an English/Spanish "
        "toggle. Here are its UI strings:\n\n"
        + "\n".join(lines)
        + "\n\nFor EACH key, suggest 2-3 concise localization UI test case ideas "
        "(for example: translated correctly, not truncated, correct after switching "
        "language, special characters such as accents display properly). "
        "Format the answer in Markdown: one '## <key>' heading per key, then a "
        "bullet list of test ideas. Do not add any other sections."
    )


def generate(prompt: str, model: str) -> str:
    """Call the Anthropic API and return the text, or '' on failure."""
    # The client reads ANTHROPIC_API_KEY from the environment automatically.
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as err:
        print(f"Anthropic API error: {err}")
        return ""

    # response.content is a list of blocks; keep only the text ones.
    parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
    return "".join(parts).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate localization test case ideas with an LLM.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. See README.md for how to set it.")

    languages = load_languages()
    if not languages["en"]:
        sys.exit("No strings found in the English file; nothing to generate.")

    output = generate(build_prompt(languages), args.model)
    if not output:
        sys.exit("The model returned no output. Nothing was saved.")

    header = (
        "# AI-generated localization test case ideas\n\n"
        "> These are AI suggestions. Review them before use; they may be wrong or incomplete.\n\n"
    )
    full_text = header + output + "\n"

    print(full_text)
    try:
        OUTPUT_FILE.write_text(full_text, encoding="utf-8")
        print(f"Saved to {OUTPUT_FILE}")
    except OSError as err:
        sys.exit(f"Could not save the file: {err}")


if __name__ == "__main__":
    main()
