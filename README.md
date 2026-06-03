<div align="center">

# 📚 wiki-vis

**Turn a codebase into a single, self-contained, good-looking `wiki.html`.**

A standard project-wiki solution for [Claude Code](https://claude.com/claude-code): analyze a repo → author a multi-doc, diagram-rich wiki under `docs/` → pack it into one HTML file you can double-click, share, or drop on any static host. *(It also just converts existing Markdown.)*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
&nbsp;![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?logo=python&logoColor=white)
&nbsp;![Dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-22c55e)
&nbsp;![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-8B5CF6)

**English** · [中文](README_cn.md)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshot-dark.png">
  <img alt="wiki-vis screenshot" src="assets/screenshot.png" width="860">
</picture>

<sub>Built-in light & dark themes — this image follows your GitHub theme. Toggle ☾/☀ in any generated wiki.</sub>

</div>

---

## ✨ Highlights

| | |
|---|---|
| 🧭 **Two modes** | Analyze a project and *author* the docs, or convert Markdown you already have |
| 🎨 **Polished theme** | Indigo-gradient + Tailwind-slate, sidebar nav, heading-level **collapsible** color-coded section frames |
| 📊 **Stat bar** | Live counts of sections / subsections / diagrams / tables |
| 🖼️ **Mermaid** | Page-matched theme + **🔍 zoom** overlay (wheel zoom · drag-pan · Esc) |
| 🌗 **Light / dark** | ☾/☀ toggle persisted in `localStorage`; default via `--theme light\|dark\|auto` |
| ✅ **Quality gate** | `lint_mermaid.py` catches `Syntax error` pitfalls; `check_render.py` renders every diagram to be sure |
| 📦 **Single file** | Pure front-end, zero backend; the build script is **Python 3 stdlib only** |

---

## 🧭 Two ways to use it

**1 · Author a project wiki** *(the main use)* — point Claude Code at a repo. It follows [`references/authoring-guide.md`](references/authoring-guide.md):

```
recon → information architecture → diagram-first writing → lint → build → review
```

…and produces a newcomer-friendly, heavily-diagrammed `docs/` set (flowcharts, E-R, sequence) plus the HTML — including *how a multi-agent system is actually executed by Claude Code*.

**2 · Convert existing Markdown** — already have `docs/*.md`? Jump straight to the commands below.

---

## 🛠 How it works

In short: `build_wiki.py` fills a single self-contained template (`template.html`) with your `docs/*.md` and emits one `wiki.html` that renders itself in the browser. When Claude Code authors a wiki from a project, it follows a short pipeline — read the code, lay out the docs, write diagram-first, lint, build, review — detailed in [`references/authoring-guide.md`](references/authoring-guide.md).

---

## 🚀 Quick start

```bash
python3 lint_mermaid.py docs/                              # 1. (recommended) catch diagram errors early
python3 build_wiki.py --docs docs --out wiki.html --lint   # 2. auto mode: README/index first, rest by name
python3 build_wiki.py --config wiki.config.json --lint     #    …or drive it with a config file
open wiki.html            # macOS  (Linux: xdg-open wiki.html)
```

Try the bundled example in seconds:

```bash
python3 build_wiki.py --docs examples/docs --out examples/wiki.html --theme auto
```

---

## ⚙️ Configuration

Everything is optional. **CLI flags override the config file**, which overrides the defaults.

<details open>
<summary><b>CLI flags</b></summary>

| Flag | Meaning |
|---|---|
| `--docs DIR` | Markdown directory (default `docs/`, falls back to `.`) |
| `--out FILE` | Output file (default `wiki.html`) |
| `--config FILE` | JSON config (see below) |
| `--theme light\|dark\|auto` | Default theme (`auto` follows the OS); readers can still toggle |
| `--lint` | Run the Mermaid lint before building; abort on error |
| `--title / --brand / --subtitle / --footer` | Branding text |
| `--template FILE` | Use a custom template shell |

</details>

<details>
<summary><b>wiki.config.json</b> (full sample in <a href="references/wiki.config.example.json"><code>references/</code></a>)</summary>

```json
{
  "title":    "Project Wiki",
  "brand":    "📚 Project Wiki",
  "subtitle": "Engineering docs · Knowledge base",
  "footer":   "Built with wiki-vis · edit .md and re-run to update",
  "docs":     "docs",
  "out":      "wiki.html",
  "theme":    "auto",
  "pages": [
    { "file": "README.md",      "id": "home",     "nav": "🏠 Home" },
    { "file": "01-overview.md", "id": "overview", "nav": "01 · Overview ⭐" }
  ]
}
```

Without `pages`, `*.md` files are auto-discovered. `pages[].nav` may contain emoji; `pages[].id` drives anchors and internal-link routing (auto-derived if omitted).

</details>

---

## 🧩 Install as a Claude Code skill

The repository root **is** a complete skill — clone it into a skills directory:

```bash
git clone https://github.com/yanqiyang62/wiki-vis.git ~/.claude/skills/wiki-vis      # user-level
git clone https://github.com/yanqiyang62/wiki-vis.git .claude/skills/wiki-vis         # or project-level
```

Then just tell Claude *“turn my project into a wiki”*.

---

## 🖼️ Mermaid tips (avoid `Syntax error`)

Both are enforced by `lint_mermaid.py`, so you usually don't have to remember them:

- Put `"` in node text as `#34;` and `#` as `#35;` — `\` escaping does **not** work.
- For a labelled edge whose label contains `. / : ( )`, use the pipe form `A -.->|label| B` instead of `A -.label.-> B`.

---

## 🎨 Theming

Design tokens live in `:root` of `template.html`:

```css
--c-primary:#667eea;  --grad:linear-gradient(135deg,#667eea,#764ba2);   /* accent / gradient */
--c-bg:#f8f9fb;  --c-text:#1e293b;  --c-border:#e2e8f0;  --radius:8px;
```

Per-level section-bar colors are in `.sec-l2 / .sec-l3 / .sec-l4 / .sec-l5 > .sec-head`. Dark-mode overrides sit under `html[data-theme="dark"]`.

---

## 📦 Offline use

The template pulls `marked` / `mermaid` / `highlight.js` from a CDN, so **viewing needs internet**. To go fully offline, download those three libraries and repoint the 4 CDN `src`/`href` in `template.html`'s `<head>` to local paths shipped next to `wiki.html`.

---

## 📁 Project layout

```
wiki-vis/
├── build_wiki.py                 # build: docs/*.md → wiki.html  (Python 3 stdlib)
├── lint_mermaid.py               # static Mermaid lint (file:line + fixes)
├── check_render.py               # optional: render every diagram via headless Chrome
├── template.html                 # the shell: CSS + JS engine + {{placeholders}}
├── SKILL.md                      # Claude Code skill manifest
├── references/
│   ├── authoring-guide.md        # project → multi-doc wiki workflow (the "brain")
│   └── wiki.config.example.json
├── examples/docs/                # sample docs you can build right away
└── assets/                       # screenshots
```

---

<div align="center">
<sub>MIT © <a href="LICENSE">yanqiyang62</a> · made with <a href="https://claude.com/claude-code">Claude Code</a></sub>
</div>
