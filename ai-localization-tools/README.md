# AI Localization Tools

Two small Python scripts that add LLM assistance to this repo's localization
testing. They only read the `Localizable.strings` files; they do not touch the
Swift app or the XCUITest code. They run on Windows, macOS or Linux (no Mac needed).

| Script | What it does |
|---|---|
| `generate_test_cases.py` | Reads `en.lproj` (and `es.lproj` if present) and asks Claude for localization UI test case ideas per string. Prints them and saves `generated_test_cases.md`. |
| `check_translations.py` | Runs simple rule-based checks, then asks Claude to review the Spanish translations against the English source and flag anything that looks wrong, too literal, or missing/placeholder. |

## How this fits an AI-driven automation service

The XCUITests check that the app behaves correctly. These tools sit in front of
that: the LLM proposes *what* to test and flags *suspect translations*, and a
person turns the good ideas into real tests. It is the same pattern as extending
an AI-driven automation service: the model generates candidates, the pipeline
handles input/output safely, and humans stay in the loop.

## Setup

1. Install Python 3.9+.
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set your API key (get one at console.anthropic.com):
   - PowerShell (current window): `$env:ANTHROPIC_API_KEY = "your-key"`
   - Command Prompt: `set ANTHROPIC_API_KEY=your-key`
   - macOS/Linux: `export ANTHROPIC_API_KEY="your-key"`

   Never commit your key to git.
4. Optional: choose a model with `--model <name>` or the `ANTHROPIC_MODEL`
   environment variable. The default is `claude-sonnet-5-5`.

## Run

```
python generate_test_cases.py
python check_translations.py
```

## Important: human review required

The LLM output is **assistive, not authoritative**. Test ideas may be irrelevant
or miss cases, and translation flags may be wrong (or miss real problems). Treat
everything as "AI suggestions to review", and have a Spanish speaker confirm
translations before relying on them.

These scripts were written without being run against the live API, so check
the first run's output carefully.
