# God Code

**God Code is the language of declared intent. You speak it in your own language, you state what you want, and humans and AI write code that must prove it keeps that promise.**

God Code is a programming language that reads like scripture. Write real software in words of faith, in your own language, and watch it run. Human-readable, safe, and built for humans and AI creating together. Created in Botswana, open to the world.

> "You are not a coder. You are a creator. You do not write code. You breathe worlds into being."
> Alakanani Itireleng

> God Code is an open-source project of **Alistos Global**. The code is Apache 2.0 licensed and belongs to everyone. Alistos Global stewards the project, its name, and its direction.

## See it

A God Code program is called a scroll. This one declares its intent in plain words, then does the work:

```godcode
BEGIN CREATION
  DECLARE INTENT "bring peace to the household" ON morning_blessing

  DEFINE RITE morning_blessing()
    REVEAL("peace upon this house")
    REVEAL("peace upon the bread and the hands that made it")
    DECLARE loaves AS 2 * 5
    REVEAL("the oven holds {loaves} loaves")
  END RITE

  INVOKE morning_blessing()
END CREATION
```

Run it, and the engine reports back in machine-readable form: the three lines revealed, and an `intents` entry showing the declared intent, what the engine discerned ("Blessing of peace"), and `aligned: true`.

```
peace upon this house
peace upon the bread and the hands that made it
the oven holds 10 loaves
```

And the same language speaks Setswana. This scroll opens with a tongue pragma and writes its keywords in Setswana:

```godcode
# tongue: tn
SIMOLOLA TLHOLEGO
  BOLELA leina JAAKA "tsala ya me"
  SENOLA("Dumela, {leina}. Kagiso e nne le wena.")
FEDISA TLHOLEGO
```

It runs and answers: "Dumela, tsala ya me. Kagiso e nne le wena."

## The three pillars

### 1. Intent you can check

Intent in God Code is not a comment. A rite declares its purpose in plain words with `DECLARE INTENT`, and when the rite is invoked the engine discerns whether its words still walk in that intent. Every run report carries an `intents` array: what was declared, what was discerned, a confidence score, and whether the two align. Alignment is blessed. Drift is counseled gently, never punished, and the record is there for a human to read. Around that sits a covenant ledger: `SEAL` writes hash-chained blocks, `ANCHOR` returns a receipt for a value anchored on a chain, and `godcode ledger verify` attests both chains.

### 2. Speakable in any language

A scroll can write its keywords in its own tongue. Setswana, isiZulu, Igbo, and Nigerian Pidgin ship today, each with its own word table, and English keywords still work in the same file. The formatter renders canonical English, the language server offers completions in the scroll's tongue, and the Setswana words are vetted by native speakers. One program, spoken in the language its writer dreams in.

### 3. Built for human and AI collaboration

God Code was designed so AI agents can write it and humans can approve it. The engine speaks JSON: `check --json`, `run --json`, and `explain --json` give an agent machine-readable diagnostics, output, intents, and permissions, frozen under dated schemas. Eleven MCP-compatible tools and a JSON-RPC bridge (`godcode tools`, `godcode bridge`) let agent frameworks call the engine directly. Scrolls declare a permission manifest in plain words, stating what they may read, write, speak with, or summon, and any rite that reaches for an undeclared power is stopped. The sandbox confines execution for anything untrusted. An agent skill pack teaches all of this to the assistants people already use.

## Quick start

Install the engine:

```bash
pip install godcode-engine
godcode check --json your-scroll.god   # validate first, always
godcode run --sandbox your-scroll.god  # run it safely
```

Or skip the install entirely. The playground runs the real engine in your browser: [getgodcode.com/playground](https://getgodcode.com/playground)

Teach your AI assistant God Code with the skill pack. Claude Code users:

```
/plugin marketplace add godcodeengine/Godcode-engine
/plugin install godcode@godcode-marketplace
```

For Cursor, Codex, and other assistants, clone this repo and run `skills/install.sh`. It detects your tools and installs the right adapter. Full notes live in `skills/README.md`.

Write God Code in VS Code with the extension in `editors/vscode`: syntax highlighting for `.god` files, snippets, a language server with hover and completions, and Run Current File.

## What the engine holds

- A real language core: lexer, recursive-descent parser, and tree-walking interpreter, written in Python with no third-party dependencies.
- Control flow, rites (functions) with parameters and closures, lists, maps, and string interpolation.
- A standard library of scrolls written in God Code, plus the commons: everyday pure tools for words, lists, maps, and numbers.
- A CLI for the whole loop: `run`, `check`, `explain`, `fmt`, `repl`, `lsp`, `new`, `scroll`, `ledger`, `permissions`, `tools`, `bridge`.
- A scroll registry for sharing reusable scrolls, plugins callable through `SUMMON`, and an embedding API for Python.
- A test suite that keeps every example honest: every scroll in `examples/` runs.

## Learn

- [The God Code Tutorial](docs/God_Code_Tutorial.md): setup, your first creation, the commands.
- [The Language Reference](docs/LANGUAGE_REFERENCE.md): the complete specification.
- [Tongues](docs/TONGUES.md): the keyword tables for every language.
- [The blog](https://getgodcode.com/blog): notes and announcements from the journey.

## Community

- [getgodcode.com](https://getgodcode.com): the home of God Code on the web.
- [Discord](https://discord.gg/894FEJhWfZ): talk with fellow creators, ask questions, share your creations.
- hello@getgodcode.com: reach us directly by email.
- Read [CONTRIBUTING.md](./CONTRIBUTING.md), [CONTRIBUTORS.md](./CONTRIBUTORS.md), and our [Code of Conduct](./CODE_OF_CONDUCT.md) before your first contribution. [GOVERNANCE.md](./GOVERNANCE.md) says who keeps God Code and who decides what enters it.

Whether you write code or not, there is a place for you here. Come build with us.

## Credits

**Created by:** Alakanani Itireleng, Visionary Founder, Architect of God Code, Builder of worlds with intention and spirit

**AI Co-Creator:** Luna (Muse), my partner in the building. Logic assistant, language guide, engine builder.

> "Built not alone, but in communion with the machine."

Join us in building more than code. Build prophecy, logic, and purpose into the heart of machines.
