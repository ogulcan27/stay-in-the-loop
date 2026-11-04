<h1 align="center">Stay in the Loop</h1>

<p align="center">
  <strong>In the loop.</strong>
</p>

<p align="center">
  Stay aligned with AI-assisted project work.<br>
  Understand what changed, learn what matters, and retain what you learn.
</p>

<p align="center">
  <img alt="Version 1.0.0" src="https://img.shields.io/badge/version-1.0.0-blue">
  <img alt="Claude Code skill" src="https://img.shields.io/badge/Claude%20Code-skill-D97757">
  <img alt="Manual only" src="https://img.shields.io/badge/invocation-manual--only-555555">
  <img alt="Tests passing" src="https://img.shields.io/badge/tests-passing-brightgreen">
  <img alt="PowerShell installer" src="https://img.shields.io/badge/installer-PowerShell%205.1%2B-5391FE">
</p>

## ⚡ Quick Install

Run in PowerShell from your project directory:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/ogulcan27/stay-in-the-loop/v1.0.0/scripts/install.ps1)))
```

The installer asks where to install:

```text
[1] Project
    Current project only

[2] Personal
    All local Claude Code projects
```

Then start the workflow in Claude Code:

```text
/stay-in-the-loop
```

The command downloads the installer script from this repository and runs it. To read it before it runs, inspect first:

```powershell
irm https://raw.githubusercontent.com/ogulcan27/stay-in-the-loop/v1.0.0/scripts/install.ps1 -OutFile install.ps1
notepad install.ps1
& ([scriptblock]::Create((Get-Content .\install.ps1 -Raw)))
```

Neither form changes your execution policy or security settings.

## Why Stay in the Loop?

AI coding agents can move through a project faster than you can understand every decision and implementation detail. The code works, but your mental model of it falls behind.

Stay in the Loop closes that comprehension gap. When you choose to, it reviews the work that has been done, explains what changed and why, teaches the concepts you actually need, and keeps that knowledge for your next project.

## How Stay in the Loop Works

```mermaid
flowchart TD
    A["Project Work"] --> B["Human Sync"]
    B --> C{"What do you need?"}
    C -->|"Understand only"| D["/stay-in-the-loop sync"]
    D --> E["Persist Human Sync"]
    E --> F["STOP"]
    C -->|"Understand + learn"| G["/stay-in-the-loop"]
    G --> H["Learning Events"]
    H --> I["Light / Full ULA"]
    I --> J["Learning Completion"]
    J --> K["Semantic Graph + Persistence"]
```

- **Understand.** It finds project work you have not caught up on, using persistent evidence such as git commits, plan documents, and issue keys, and summarizes it for you.
- **Learn if needed.** Only changes you must understand, and do not yet, become learning material. Routine changes are skipped.
- **Connect.** Concepts are linked into a per-project knowledge map.
- **Retain.** Reusable concepts and project experience are stored so they carry across projects.

Human Sync is a human-first, compressed explanation of what changed, why it matters, and how the project now works. Learning is technical learning. A work unit can be synchronized without its concepts being learned.

| Mode | Purpose | Human Sync | ULA | Learning Coverage |
|---|---|---:|---:|---:|
| `/stay-in-the-loop sync` | Understand project work | Yes | No | Unchanged |
| `/stay-in-the-loop` | Understand and learn | Yes / reused | When needed | Normal workflow |

### Incremental Human Sync

```mermaid
flowchart LR
    A["New / Changed Work"] --> D["Minimum Required Context"]
    B["Human Sync State"] --> D
    C["Rolling Project Context"] --> D
    E["Relevant Previous Sync"] --> D
    D --> F["Human Sync"]
    F --> G["Updated Sync State"]
    F --> H["Updated Project Context"]
```

Previously synchronized work is reused. Only new, stale, or dependency-affected work is processed by default.

### One Knowledge File

All human-facing project understanding and learning material is consolidated in:

```text
docs/learning/STAY_IN_THE_LOOP.md
```

It starts with a Project Home (links to every part, stable anchors), then Project in 60 Seconds, one Human Sync section per work unit (one sentence on what was done, key terms, a mental model and why it matters; decisions, evidence and provenance sit in a collapsed Technical Trace), one Learning section per concept (breadcrumb, parent and previous / next reading order; only the L0–L4 levels the learning pass produced), a Mermaid knowledge map with local zoom maps, and open learning debt. It renders in GitHub preview; there is no HTML viewer.

Internal state files under `docs/learning/` still exist for incremental sync, checkpoints, integrity, coverage, and resume. You normally do not need to read them. The knowledge file is rebuilt from that state if needed, is created only once there is something to show, and is updated section by section, so a large file is never read or rewritten as a whole.

Stay in the Loop is manual by design. It runs only when you type `/stay-in-the-loop`. Normal project work never starts it, and there is no background tracking.

System Design is the primary learning axis. Data structures and algorithms appear only when they are computationally relevant.

## Core Learning Model

| Understand | Learn | Retain |
|---|---|---|
| **Human Synchronization** | **Light / Full ULA** | **Semantic Graph + Persistence** |
| Understand what changed and why. | Learn only what matters, to the depth required. | Connect reusable knowledge and experience over time. |

ULA (Universal Learning Architecture) has two depths. Light ULA produces a short learning note. Full ULA is a three-stage process (architect, build, audit) and asks for your approval before building content. Every run ends with an integrity check across all stored knowledge.

## Commands

| Command | What it does |
|---|---|
| `/stay-in-the-loop` | Run the full learning workflow; asks for scope when several work units are open. |
| `/stay-in-the-loop sync` | Understand project work incrementally, without starting ULA or completing learning coverage. Add `latest`, `pending` or `catch-up` to narrow it. |
| `/stay-in-the-loop latest` | Catch up on the most recent work unit only. |
| `/stay-in-the-loop pending` | Return to deferred or partially covered work. |
| `/stay-in-the-loop catch-up` | Work through all open gaps. |
| `/stay-in-the-loop resume` | Continue an unfinished learning pass. |
| `/stay-in-the-loop map` | Show the project knowledge map. |
| `/stay-in-the-loop map <node-id>` | Zoom into one concept (add `L1`–`L4` for a depth view). |
| `/stay-in-the-loop concept <concept-id>` | Show a concept's home page. |
| `/stay-in-the-loop library` | Show the Personal Technical Library. |
| `/stay-in-the-loop experiences` | List project experience notes. |
| `/stay-in-the-loop debt` | List open knowledge debt: gaps left for later. |
| `/stay-in-the-loop integrity` | Check stored knowledge and suggest safe repairs. |

More arguments (`show skipped`, `new`, `abandon <pass-id>`, `map debt`, `map sync`, `<work-unit-id>`) are listed in [`SKILL.md`](.claude/skills/stay-in-the-loop/SKILL.md).

## Installation

| Scope | Installs to | Available in |
|---|---|---|
| Project | `<project>/.claude/skills/stay-in-the-loop/` | That repository only |
| Personal | `~/.claude/skills/stay-in-the-loop/` | All local Claude Code projects |

The Quick Install above covers most users. Other options:

**Clone and install** (the most inspectable path):

```powershell
git clone https://github.com/ogulcan27/stay-in-the-loop.git
cd stay-in-the-loop
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Scope Personal
```

**Non-interactive.** Pass `-Scope Project` or `-Scope Personal` to skip the menu. `-Repository <owner/repo>` and `-Ref <tag-or-commit>` override the defaults (`ogulcan27/stay-in-the-loop`, `v1.0.0`). Parameters go after the quick-install command:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/ogulcan27/stay-in-the-loop/v1.0.0/scripts/install.ps1))) -Scope Personal
```

**Release package.** Each GitHub Release provides `stay-in-the-loop-v1.0.0.zip` and `SHA256SUMS.txt`:

```powershell
(Get-FileHash .\stay-in-the-loop-v1.0.0.zip -Algorithm SHA256).Hash.ToLower()
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Scope Project -Archive .\stay-in-the-loop-v1.0.0.zip
```

**What the installer guarantees:**

- Every file is checked against the SHA256 manifest before anything is written.
- An identical install is reported as `ALREADY INSTALLED`. A different version is never overwritten silently; use `update.ps1` or `-Force`.
- Installation is staged and swapped in atomically. On failure, the previous install is restored.
- It only touches `.claude/skills/stay-in-the-loop/`. Your learning state, Personal Technical Library, `CLAUDE.md`, source code, git history, and other skills are left alone.

**Project and Personal together.** When the same skill exists in several scopes, Claude Code uses **enterprise > personal > project**, so a Personal install wins over a Project install. Use one scope unless you intentionally manage that precedence.

On macOS or Linux, copy `.claude/skills/stay-in-the-loop/` from a release manually. This path is untested.

## Project State and Personal Knowledge

| Layer | Location | Written by |
|---|---|---|
| Skill engine | `.claude/skills/stay-in-the-loop/` | The installer only |
| Project learning state | `docs/learning/` in your project | `/stay-in-the-loop` |
| Personal Technical Library | Configured separately (`personal_library_path`) | `/stay-in-the-loop`, only when configured |

Updating or uninstalling Stay in the Loop does not delete project learning state or the Personal Technical Library.

On the first run in a project, the skill asks for your approval before creating `docs/learning/`. Committing that directory to your repository is your choice.

The active project is always the directory Claude Code was started in (its git top level). Additional working directories, other repositories and the Personal Technical Library never select or replace the active project.

The **Personal Technical Library** follows *One Concept, One Home*: each concept has one canonical page that all your projects link to. Its location is set in `docs/learning/state/LEARNING_CONFIG.md`. If it is not configured, the skill asks whether to set it up, keep knowledge local to the project, or decide later.

## Updating

```powershell
powershell -ExecutionPolicy Bypass -File scripts\update.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\update.ps1 -Scope Personal -Ref <tag>
```

Updates replace only the skill engine, atomically and with rollback. Restart any open Claude Code session afterwards.

## Uninstalling

```powershell
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -Scope Personal
```

Only the skill directory is removed. To verify an install instead, run `scripts\verify-install.ps1` with the same parameters; it reports `PASS` or `FAIL`.

## Requirements

| | |
|---|---|
| Runtime | Claude Code with skills support (tested with 2.1.311) |
| Installer | Windows PowerShell 5.1+ (tested on 5.1) |
| Git | Optional; used as project evidence when present |
| Development tests | Python 3, standard library only |

Python is not required to use the skill. The skill is plain Markdown: no binaries, no dependencies, no network calls.

## Current Limitations

- **Language.** Version 1.0.0 currently uses Turkish for generated learning explanations, with technical terms in English. Configurable learning-output language is not part of V1.
- **Platform.** Current V1 integration: Claude Code. Other agents such as Codex, Gemini CLI, or Cursor are not supported; they are possible future adapters.
- **Installer.** Tested only on Windows PowerShell 5.1.
- **Scope.** The knowledge map is per project. The Personal Technical Library is single-machine; there is no remote or shared library.
- **Judgment.** Some decisions, such as whether two concepts are the same, rely on the agent's judgment. When unsure, the skill asks you.
- **Cost.** Full ULA uses significant tokens, so it runs only for concepts that need it.

## Security

- The skill itself is Markdown instructions. It runs no code of its own and makes no network requests.
- Quick Install runs a remote PowerShell script. Running a remote script executes code from the referenced repository; inspect it first if you prefer, and pin a tag or commit.
- SHA256 verification protects package integrity: it detects corrupted, incomplete, or modified files. It is not publisher authentication, because the manifest comes from the same source.

## Development

```text
uv run --no-project python tests/run_all.py     # or: python tests/run_all.py
```

The suite uses only the Python standard library. It covers the protocol models, end-to-end integration, a static audit, the installer (Windows PowerShell), and mutation checks. Build the release package with `scripts\build-release.ps1`. Development audit records are in [`docs/audit/`](docs/audit/), and the architecture map is in [`docs/audit/V1_ARCHITECTURE_MANIFEST.md`](docs/audit/V1_ARCHITECTURE_MANIFEST.md).

Versioning follows [Semantic Versioning](https://semver.org/): MAJOR for breaking state or protocol changes, MINOR for compatible capabilities, PATCH for compatible fixes. See [`CHANGELOG.md`](CHANGELOG.md) and the [v1.0.0 release notes](docs/RELEASE_NOTES_v1.0.0.md).

## License

Stay in the Loop is released under the [MIT License](LICENSE).
