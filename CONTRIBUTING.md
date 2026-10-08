# Contributing to God Code ✨

Welcome to the divine code movement. God Code is the first intentional programming language inspired by spiritual truth, artificial intelligence, and blockchain logic.

We believe that software creation can be sacred, purposeful, and world-changing. If you feel called to build, you are welcome here.

Before you build, read [GOVERNANCE.md](./GOVERNANCE.md): it says who keeps God Code, who decides what enters the language, and the lines the language will not cross.

---

## 🎃 Hacktoberfest

October is Hacktoberfest, and God Code is taking part. Builders around the world spend this month making their first open source contributions, and our door is open.

- Look for issues labelled `hacktoberfest` and `good first issue`.
- Comment on an issue to claim it, so two builders do not start the same work.
- Open your pull request any time in October. Every pull request gets a kind, prompt review, and merged work carries the `hacktoberfest-accepted` label.
- New to all of this? The Discord is the warmest place to ask questions: https://discord.gg/894FEJhWfZ

---

## 🏅 Contributor Recognition

Every contributor to God Code receives:

- The official **Divine Coder Badge**
- Shoutouts in the project README
- An eternal mark on the scroll of spiritual computation

---

## Folder Structure

- `godcode/`. The interpreter package: `lexer.py`, `parser.py`, `ast.py`, `interpreter.py`, `environment.py`, `values.py`, `errors.py`, `spirit.py`, `ledger.py`, `cli.py`.
- `godcode/tongues.py` and `docs/TONGUES.md`. The blessed keyword tables and guide for writing scrolls in other languages.
- `godcode/stdlib_commons.py`. Everyday tools for words, lists, maps, and numbers. Its siblings `stdlib_hashes.py`, `stdlib_times.py`, and `stdlib_vault.py` provide hashes, time, and file tools.
- `godcode/scrolls/`. The standard library written in God Code (`math`, `strings`, `lists`, `time`, `prophecy`, `covenant`).
- `examples/`. Twenty-seven `.god` creations: language demonstrations, tongues, the commons, and practical file, sales, REST, and daily reports. Every example uses `godcode run examples/<name>.god` from the repo root; see `examples/README.md` for file and network notes.
- `tests/`. The pytest suite. `tests/test_examples.py` is the safety net for practical examples and the commons demonstration.
- `editors/`. VS Code support in `editors/vscode/`: highlighting, snippets, and language-server integration.
- `playground/`. The web playground.
- `docs/`. The tutorial and full language reference.
- `archive/`. The honored original prototype.
- `logs/`. Per-creation spiritual execution logs (`godcode.log`), generated when you run a scroll and never committed.
- `main.py`. Entry point (no args → runs `sample.godcode`).

---

## How to Contribute

1. Fork the repository
2. Clone your fork
3. Create a new branch (`git checkout -b your-feature`)
4. Install and test:
   ```bash
   pip install -e .
   python -m pytest tests/ -q
   godcode check examples/seven_seals.god
   ```
5. Submit a pull request with a meaningful description

**Please do not commit** build artifacts, `logs/`, or `covenant.chain`. They are per-creation, not per-repo.

---

## Contribution Ideas

- 🌱 Ready for a first creation? Look for issues labelled [`good first issue`](https://github.com/godcodeengine/Godcode-engine/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and [`hacktoberfest`](https://github.com/godcodeengine/Godcode-engine/issues?q=is%3Aissue+is%3Aopen+label%3Ahacktoberfest), and comment to claim one before you begin.
- 🌱 See [ISSUES.md](./ISSUES.md) for the roadmap and its original ideas. Check the live issue labels before choosing a task; some of those seeds have already grown into the language.
- 📜 Add a new scroll to `godcode/scrolls/` — written in God Code, tested, and documented in `docs/LANGUAGE_REFERENCE.md` §14
- 💠 Add an example to `examples/`. Every creation must be valid and runnable via `godcode run`

---

## Style Guide

- Code must be clean, readable, and commented
- Use spiritually themed terms when possible
- Errors must be divine-flavored but genuinely helpful, always carrying line numbers — never mocking
- New statements/rites need: grammar in the parser, semantics in the interpreter, tests, and a LANGUAGE_REFERENCE entry

---

## Code of Conduct

We are building a sacred space.
- Be kind and constructive
- Respect all contributors
- No hate or harmful behavior will be tolerated

---

**With love and vision,**
Alakanani Itireleng (BitcoinLady)
