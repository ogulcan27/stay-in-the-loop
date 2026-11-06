# Stay in the Loop — Project Knowledge

<!-- SITL:VIEW project_id=<PRJ-xxxxxxxx> -->

> Template: `.claude/skills/stay-in-the-loop/templates/KNOWLEDGE_VIEW_TEMPLATE.md`
> Target: `docs/learning/STAY_IN_THE_LOOP.md`
> Role: DERIVED human-facing view. Authority `docs/learning/` state dosyalarıdır. Elle düzenleme.
> Rules: `references/09_KNOWLEDGE_VIEW.md`. Yalnız içerik oluşunca oluşturulur (§2).

<!-- SITL:INDEX:START -->
## Project Home

**Start here:** [Project in 60 Seconds](#project-in-60-seconds) · [Current Position](#where-are-we-now) · [Project Journey](#project-journey)

**Human Sync** — project comprehension

- [<label>](#hs-xxxxxxxx)
- [<label>](#hs-xxxxxxxx) · needs refresh

**Learning** — technical learning. Human Sync ≠ learned.

- [<KN-xxxxxxxx> — <canonical_name>](#kn-xxxxxxxx) · L1 L2

**Knowledge Architecture:** [Knowledge Map](#knowledge-map)

**Open Questions / Learning Debt:** [Open Questions](#what-is-still-unresolved) · [Open Learning Debt](#open-learning-debt)
<!-- SITL:INDEX:END -->

<!-- SITL:MODEL:START -->
## Project in 60 Seconds

#### What are we building?

#### Where are we now?

#### How does it work at the highest level?

#### Five things to remember

#### What is still unresolved?

<details>
<summary><strong>Technical Project Snapshot</strong></summary>

#### Architecture

#### Components

#### Active Decisions

#### Invariants

#### Dependencies

</details>
<!-- SITL:MODEL:END -->

<!-- SITL:JOURNEY:START -->
## Project Journey

- [<label>](#hs-xxxxxxxx) — <Problem> → <Action> → **<Result>**
  - Revision: [<label>](#hs-xxxxxxxx) — <Problem> → <Action> → **<Result>**
- [<label>](#hs-xxxxxxxx) — <Problem> → <Action> → **<Result>** · **Current position**

Not yet synced: <label>, <label>

[↑ Project Home](#project-home)
<!-- SITL:JOURNEY:END -->

## Human Sync

<!-- SITL:HS:<HS-xxxxxxxx>:START v=<record_version> -->
<a id="hs-xxxxxxxx"></a>
### <label>

**Status:** <Current | Needs refresh>

**Tek cümlede:** <konu + işlem veya karar + sonuç>

**Anahtar kavramlar:** <basit anlam (Term)> · <basit anlam (Term)>

#### Zihinsel Model

#### Neden Önemli?

<details>
<summary><strong>Technical Trace</strong></summary>

#### Why

#### What Changed

#### Key Decisions

#### Dependencies

#### Open Points

#### Evidence

#### More Terms

**Record:** `<HS-xxxxxxxx>` v<record_version> · `<work_unit_id>` · `<checkpoint>`

</details>

[↑ Project Home](#project-home)
<!-- SITL:HS:<HS-xxxxxxxx>:END -->

## Learning

<!-- SITL:KN:<KN-xxxxxxxx>:START depth=<L1;L2> -->
<a id="kn-xxxxxxxx"></a>
### <KN-xxxxxxxx> — <canonical_name>

#### Where am I?

[Project Home](#project-home) → [Knowledge Map](#knowledge-map) → <ROOT> → <parent> → **<canonical_name>**

Parent: <[parent](#kn-xxxxxxxx); parent_id yoksa Yok.>

Reading order — Previous: <NEXT kaynağı> · Next: <NEXT hedefi; NEXT yoksa satır yok>

Also part of: <secondary PART_OF; yoksa satır yok>

Learning depth: <L1 · L2> · Source: `<event-id>` (`<artifact path>`)

<Local Map: yalnız primary child ≥ 3 ise Mermaid flowchart LR>

#### L0 — Map

#### L1 — Simple Mental Model

#### L2 — Mechanism

<details>
<summary><strong>L3 — Theory</strong></summary>

</details>

<details>
<summary><strong>L4 — Formalism</strong></summary>

</details>

#### Boundary

#### Example

#### Retrieval

<details>
<summary><strong>Reference</strong></summary>

</details>

#### Related Concepts

- <RELATION> → [<name>](#kn-xxxxxxxx)
<!-- SITL:KN:<KN-xxxxxxxx>:END -->

<!-- SITL:MAP:START -->
## Knowledge Map

```mermaid
flowchart LR
    KN_xxxxxxxx["<canonical_name> (KN-xxxxxxxx)"] --> KN_yyyyyyyy["<canonical_name> (KN-yyyyyyyy)"]
```

[↑ Project Home](#project-home)
<!-- SITL:MAP:END -->

<!-- SITL:DEBT:START -->
## Open Learning Debt

- `<KD-...>` — <concept> · <priority> · <work_unit_ids>

[↑ Project Home](#project-home)
<!-- SITL:DEBT:END -->
