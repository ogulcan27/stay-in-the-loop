"""Mutation checks: break one protocol rule in a temporary skill copy; the suite must catch it.

A mutation is caught when every expected suite reports at least one failing test.
The skill under test is never modified.
"""
import re
import shutil
import tempfile
from pathlib import Path

import run_all

R01, R08 = "references/01_OPERATIONAL_CORE.md", "references/08_HUMAN_SYNC_STATE.md"
R03, R04, R05 ="references/03_HUMAN_SYNC_PROTOCOL.md", "references/04_ULA_PROTOCOL.md", "references/05_MINDMAP_PROTOCOL.md"
R06, R07 = "references/06_KNOWLEDGE_PERSISTENCE.md", "references/07_INTEGRITY_CHECKS.md"
R09 = "references/09_KNOWLEDGE_VIEW.md"

# (id, description, [(file, regex, replacement)], expected failing suites)
MUTATIONS = [
    ("P4-M1", "03 ULA_CANDIDATE disposition row removed",
     [(R03, r"^\| MUST_UNDERSTAND \| GAP \| yeterli \| ULA_CANDIDATE \|\n", "")], ["phase4", "integration"]),
    ("P5-M1", "04 review gate removed (architecture proposed -> FULL_ULA_BUILD)",
     [(R04, r"^(\| FULL_ULA_ARCHITECT \| architecture proposed \|) FULL_ULA_REVIEW ", r"\1 FULL_ULA_BUILD ")], ["phase5"]),
    ("P5-M2", "04 open ULA event no longer blocks the unit",
     [(R04, r"^(\| ULA_CANDIDATE \| ula_status not COMPLETE \|) yes \|$", r"\1 no |")], ["phase5"]),
    ("P5-M3", "04 Builder without frozen architecture",
     [(R04, r"^(\| FULL_ULA_REVIEW \| user approve \| FULL_ULA_BUILD \|) user_approval ", r"\1 - "),
      (R04, r"^(\| FULL_ULA_BUILD \| content generated \| FULL_ULA_AUDIT \|) frozen_architecture ", r"\1 - ")], ["phase5"]),
    ("P6-M1", "07 M-04 orphan edge check removed", [(R07, r"^\| M-04 \|.*\n", "")], ["phase6"]),
    ("P6-M2", "07 M-08 hierarchy cycle check removed", [(R07, r"^\| M-08 \|.*\n", "")], ["phase6"]),
    ("P6-M3", "05 §7.1 idempotent merge broken (UNION -> APPEND)",
     [(R05, r"^\| source_event_ids \| UNION \|$", "| source_event_ids | APPEND |"),
      (R05, r"^\| project_appearances \| UNION \|$", "| project_appearances | APPEND |")], ["phase6"]),
    ("P7-M1", "06 §7 NAME resolution row removed (duplicate Concept Home prevention)",
     [(R06, r"^\| NAME \|.*\n", "")], ["phase7", "integration"]),
    ("P7-M2", "06 §20 RESOLVED guard removed + 07 P-12 removed",
     [(R06, r"^(\| OPEN \| RESOLVED \|) .+ \|$", r"\1 - |"), (R07, r"^\| P-12 \|.*\n", "")], ["phase7"]),
    ("P7-M3", "06 §22 atomic write removed (SEQUENTIAL, no rollback)",
     [(R06, r"^\| write_mode \| ALL_OR_NOTHING \|$", "| write_mode | SEQUENTIAL |"),
      (R06, r"^\| on_write_error \| RESTORE_PRE_IMAGES \|$", "| on_write_error | NONE |")], ["phase7"]),
    ("P8-M1", "07 L-04 removed (fake RESOLVED debt accepted)", [(R07, r"^\| L-04 \|.*\n", "")], ["integration"]),
    ("P8-M2", "06 §22.1 on_existing BLOCKED -> OVERWRITE (concurrent write)",
     [(R06, r"^\| on_existing \| BLOCKED \|$", "| on_existing | OVERWRITE |")], ["integration"]),
    ("P8-M3", "06 §22.1 stale_lock USER_DECISION -> AUTO_REMOVE",
     [(R06, r"^\| stale_lock \| USER_DECISION \|$", "| stale_lock | AUTO_REMOVE |")], ["integration"]),
    ("P8-M4", "07 L-08 WARNING -> FAIL (coverage independence broken)",
     [(R07, r"^(\| L-08 \|.*\|) WARNING (\|.*\|)$", r"\1 FAIL \2")], ["integration"]),
    ("P8-M5", "07 §L.1 COVERAGE_LEDGER marked DERIVED",
     [(R07, r"^(\| `COVERAGE_LEDGER` \|) AUTHORITATIVE (\|.*\|) NO \|$", r"\1 DERIVED \2 YES |")], ["integration"]),
    ("P8-M8", "07 L-20 removed (repair trusted without CHECK 2)", [(R07, r"^\| L-20 \|.*\n", "")], ["integration"]),
    ("P8-M6", "config template hard-codes a personal library path",
     [("templates/LEARNING_CONFIG_TEMPLATE.md", r"^personal_library_path: UNCONFIGURED$", "personal_library_path: D:/Users/me/library")],
     ["static"]),
    ("P8-M7", "07 §L.6 renumbered; SKILL.md pointer becomes stale",
     [(R07, r"^### L\.6 Command$", "### L.9 Command")], ["static"]),
    ("ISO-M1", "01 §0 additional working directories become a project root source",
     [(R01, r"^\| Additional working directories \| NO \|$", "| Additional working directories | YES |")], ["isolation"]),
    ("ISO-M2", "06 §2.3 personal library inside docs/learning/ accepted",
     [(R06, r"^(\| Path bir `docs/learning/` dizinini veya altını gösteriyor \|) CONFIG ERROR \|$", r"\1 Library olarak kullanılır. |")],
     ["isolation"]),
    ("ISO-M3", "development-project identifier leaks into runtime first-run rule",
     [("references/02_COVERAGE_PROTOCOL.md", r"project adı \(= active project root klasör adı\)", "project adı (= V8_Clean_Validation)")],
     ["static"]),
    ("SYNC-M1", "08 §7 default sync no longer refreshes STALE records",
     [(R08, r"^\| `sync` \| `UNSYNCED_AFTER ∪ STALE` \|", "| `sync` | `UNSYNCED_AFTER` |")], ["sync"]),
    ("SYNC-M2", "08 §8 STALE refresh rereads full raw evidence",
     [(R08, r"^(\| `STALE` \| `CONTEXT`, `DEP_RECORDS`, `OWN_RECORD`, `DELTA`) \| `RAW_EVIDENCE`, ", r"\1, `RAW_EVIDENCE` | ")], ["sync"]),
    ("SYNC-M3", "08 §8 dependency records dropped from the UNSYNCED plan",
     [(R08, r"^\| `UNSYNCED` \| `CONTEXT`, `DEP_RECORDS`, `RAW_EVIDENCE` \|", "| `UNSYNCED` | `CONTEXT`, `RAW_EVIDENCE` |")], ["sync"]),
    ("SYNC-M4", "08 §6 TYPO in an evidence path invalidates the record",
     [(R08, r"^\| `TYPO` \| `SYNCED`;", "| `TYPO` | `STALE`;")], ["sync"]),
    ("SYNC-M5", "08 §11 sync-only may write the coverage ledger",
     [(R08, r"^\| `COVERAGE_LEDGER.md` \| NO \|$", "| `COVERAGE_LEDGER.md` | YES |")], ["sync"]),
    ("SYNC-M6", "07 S-01 removed (SYNCED unit without record accepted)", [(R07, r"^\| S-01 \|.*\n", "")], ["sync"]),
    ("SYNC-M7", "07 S-04 removed (another project's record accepted)", [(R07, r"^\| S-04 \|.*\n", "")], ["sync", "isolation"]),
    ("SYNC-M8", "07 S-16 removed (existing records regenerated from scratch)", [(R07, r"^\| S-16 \|.*\n", "")], ["sync"]),
    ("DEP-M1", "08 §6.1 impact NONE invalidates the dependent (over-invalidation)",
     [(R08, r"^\| `NONE` \| `SYNCED` \|$", "| `NONE` | `STALE` |")], ["sync"]),
    ("DEP-M2", "08 §6.1 CONTRACT impact keeps the dependent SYNCED (stale understanding kept)",
     [(R08, r"^\| `CONTRACT` \| `STALE` \|$", "| `CONTRACT` | `SYNCED` |")], ["sync"]),
    ("DEP-M3", "08 §6.1 every later unit treated as dependent",
     [(R08, r"^\| edges \| EXPLICIT_DEPENDS_ON \|$", "| edges | LATER_SEQ |")], ["sync"]),
    ("DEP-M4", "08 §6.1 blanket transitive cascade",
     [(R08, r"^\| transitive \| ON_MATERIAL_IMPACT \|$", "| transitive | ALWAYS |")], ["sync"]),
    ("DEP-M5", "08 §6.1 dependent raw evidence read to decide impact",
     [(R08, r"^\| evidence \| RECORDS_FIRST \|$", "| evidence | RAW_FIRST |")], ["sync"]),
    ("VIEW-M1", "09 §1 local map for every concept (no branching threshold)",
     [(R09, r"^\| local_map_min_children \| 3 \|$", "| local_map_min_children | 1 |")], ["view"]),
    ("VIEW-M2", "09 §9 concept retrieval reads the whole document",
     [(R09, r"^(\| `KN` \|) `MARKERS`, `INDEX`, `TARGET`, `DEP_SECTIONS` \| `WHOLE_VIEW`, `OTHER_SECTIONS` \|$",
       r"\1 `WHOLE_VIEW` | `OTHER_SECTIONS` |")], ["view"]),
    ("VIEW-M3", "09 §1 section patch replaced by full regeneration",
     [(R09, r"^\| write_mode \| SECTION_PATCH \|$", "| write_mode | FULL_REWRITE |")], ["view"]),
    ("VIEW-M4", "09 §1 global map dumps the whole hierarchy",
     [(R09, r"^\| global_map_depth \| 2 \|$", "| global_map_depth | 9 |")], ["view"]),
    ("VIEW-M5", "09 §5 STALE record presented as Current",
     [(R09, r"^\| `STALE` \| `Needs refresh` \|$", "| `STALE` | `Current` |")], ["view"]),
    ("VIEW-M6", "07 V-05 removed (Human Sync section from another project accepted)", [(R07, r"^\| V-05 \|.*\n", "")], ["view"]),
    ("VIEW-M7", "07 V-03 removed (broken section markers accepted)", [(R07, r"^\| V-03 \|.*\n", "")], ["view"]),
    ("VIEW-M8", "08 §11 sync-only may write every view section",
     [(R08, r"^\| `STAY_IN_THE_LOOP.md` \| .* \|$", "| `STAY_IN_THE_LOOP.md` | YES |")], ["view"]),
    ("VIEW-M9", "09 §1 L1 / L2 hidden behind collapsible blocks",
     [(R09, r"^\| collapsed \| L3; L4; Reference \|$", "| collapsed | L1; L2; L3; L4; Reference |")], ["view"]),
    ("VIEW-M10", "07 §L.1 knowledge view becomes authoritative",
     [(R07, r"^(\| `KNOWLEDGE_VIEW` \|) DERIVED \|", r"\1 AUTHORITATIVE |")], ["integration", "view"]),
    ("HUMAN-M1", "09 §5.1 one sentence hidden in the technical trace",
     [(R09, r"^\| `Tek cümlede:` \| Purpose \| HUMAN \|$", "| `Tek cümlede:` | Purpose | TRACE |")], ["view"]),
    ("HUMAN-M2", "09 §5.1 why it matters hidden in the technical trace",
     [(R09, r"^\| `Neden Önemli\?` \| Downstream Impact \| HUMAN \|$", "| `Neden Önemli?` | Downstream Impact | TRACE |")], ["view"]),
    ("HUMAN-M3", "09 §5.1 evidence / provenance dropped from the view",
     [(R09, r"^\| `Evidence` \| Evidence / Provenance \| TRACE \|\n", "")], ["view"]),
    ("HUMAN-M4", "09 §1 key terms uncapped",
     [(R09, r"^\| key_terms_max \| 5 \|$", "| key_terms_max | 9 |")], ["view"]),
    ("HUMAN-M5", "07 V-15 removed (unexplained internal symbols accepted)", [(R07, r"^\| V-15 \|.*\n", "")], ["view"]),
    ("HUMAN-M6", "09 §1 every invariant and decision pushed into five things to remember",
     [(R09, r"^\| remember_max \| 5 \|$", "| remember_max | 14 |")], ["view"]),
    ("HUMAN-M7", "09 §3 model back to the agent-oriented Project Mental Model",
     [(R09, r"^(\| 3 \| `MODEL` \|) `## Project in 60 Seconds` \|", r"\1 `## Project Mental Model` |")], ["view"]),
    ("VIS-M1", "09 §13.4 NEXT treated as a semantic dependency",
     [(R09, r"^\| `SEMANTIC` \| `REQUIRES`, ", "| `SEMANTIC` | `NEXT`, `REQUIRES`, ")], ["view"]),
    ("VIS-M2", "09 §13.5 Markdown view becomes authoritative",
     [(R09, r"^\| Markdown view \| DERIVED \|", "| Markdown view | AUTHORITATIVE |")], ["view"]),
    ("VIS-M3", "09 §13.2 broken-link metric dropped from the contract",
     [(R09, r"^\| `links_broken` \|.*\n", "")], ["view"]),
    ("VIS-M4", "09 §6.2 artifact local map no longer projected (real local maps removed from the view)",
     [(R09, r"^\| L0 — Map \| `## L0 — Local Map` \| `# Local Map` \|\n", "")], ["view"]),
    ("VIS-M5", "09 §3 INDEX back to Quick Index (no Project Home)",
     [(R09, r"^(\| 2 \| `INDEX` \|) `## Project Home` \|", r"\1 `## Quick Index` |")], ["view"]),
    ("VIS-M6", "09 §3.2 Project Home anchor no longer the heading slug (links break)",
     [(R09, r"^\| `project-home` \| `## Project Home` \| heading \|$", "| `home` | `## Project Home` | heading |")], ["view"]),
    ("VIS-M7", "09 §13.4 reading order taken from a semantic relation",
     [(R09, r"^\| `NAVIGATION` \| `NEXT` \|", "| `NAVIGATION` | `USES` |")], ["view"]),
    ("VIS-M8", "07 V-01 removed (broken internal links accepted)", [(R07, r"^\| V-01 \|.*\n", "")], ["view"]),
    ("VIS-M9", "07 V-16 removed (duplicate navigation anchors accepted)", [(R07, r"^\| V-16 \|.*\n", "")], ["view"]),
    ("VIS-M10", "07 V-17 removed (wrong parent / previous / next accepted)", [(R07, r"^\| V-17 \|.*\n", "")], ["view"]),
    ("VIS-M11", "template Project Home loses Knowledge Architecture",
     [("templates/KNOWLEDGE_VIEW_TEMPLATE.md", r"^\*\*Knowledge Architecture:\*\* .*\n\n", "")], ["view"]),
    ("VIS-M12", "09 §3 DEBT no longer structural (legacy view keeps a broken Open Learning Debt link)",
     [(R09, r"^- `DEBT` structural top-level destination.*\n", "")], ["view"]),
    ("VIS-M13", "09 §6.2 block-structured Full L1 row removed (block L1 bodies dropped)",
     [(R09, r"^\| L1 — Simple Mental Model \| her block'ta `## L1 — …` \|\n", "")], ["view"]),
    ("VIS-M14", "09 §6.2 block Orientation / Transition shown",
     [(R09, r"^- Block'un .* paragrafları gösterilmez.*\n", "")], ["view"]),
    ("VIS-M15", "09 §6.2 block L4 only under the standard heading (NO L4 REQUIRED dropped)",
     [(R09, r"^(\| L4 — Formalism \| her block'ta) `## L4 — …` \|", r"\1 `## L4 — Math / Formalism` |")], ["view"]),
    ("VIS-M16", "09 §6.2 block LOCAL MAP no longer in L0",
     [(R09, r"^(\| L0 — Map \| `# L0 — …`), ardından her `# LOCAL MAP — …` \|", r"\1 |")], ["view"]),
    ("VIS-M17", "09 §5.4 journey ordered by record_id instead of seq (units reordered)",
     [(R09, r"^(\| node \| Record'u olan unit \(`SYNCED`, `STALE`\)), `seq` sırası \|", r"\1, `record_id` sırası |")], ["view"]),
    ("VIS-M18", "09 §5.4 revision parent pattern lost (revisions no longer grouped)",
     [(R09, r"^\| revision \| Native step ID `<parent>-R<n>` \|", "| revision | Native step ID `<parent>-REV<n>` |")], ["view"]),
    ("VIS-M19", "09 §5.4 journey step taken from Downstream Impact (unsupported claim)",
     [(R09, r"^\| adım \| Record `Purpose`:", "| adım | Record `Downstream Impact`:")], ["view"]),
    ("VIS-M20", "09 §5.4 journey link no longer the HS anchor (broken Human Sync link)",
     [(R09, r"^\| link \| HS section anchor'ı `#hs-xxxxxxxx` \|", "| link | HS section anchor'ı `#hs_xxxxxxxx` |")], ["view"]),
    ("VIS-M21", "07 V-18 removed (stale journey accepted)", [(R07, r"^\| V-18 \|.*\n", "")], ["view"]),
    ("VIS-M22", "09 §3 JOURNEY no longer structural (legacy view never gets a journey)",
     [(R09, r"^- `JOURNEY` structural top-level destination.*\n", "")], ["view"]),
    ("VIS-M23", "template JOURNEY loses the revision line",
     [("templates/KNOWLEDGE_VIEW_TEMPLATE.md", r"^  - Revision: .*\n", "")], ["view"]),
    ("VIS-M24", "08 §11 sync-only run may not write JOURNEY",
     [("references/08_HUMAN_SYNC_STATE.md", r"^(\| `STAY_IN_THE_LOOP.md` \| Yalnız HS), JOURNEY,", r"\1,")], ["view"]),
]


def mutate(skill, rel, pattern, repl):
    f = skill / rel
    text, n = re.subn(pattern, repl, f.read_text(encoding="utf-8"), flags=re.M)
    assert n == 1, f"mutation target not unique in {rel}: {pattern} ({n})"
    f.write_text(text, encoding="utf-8")


def main(skill):
    ok = True
    for mid, desc, edits, expected in MUTATIONS:
        tmp = Path(tempfile.mkdtemp(prefix=f"mut_{mid}_"))
        copy = tmp / "stay-in-the-loop"
        shutil.copytree(skill, copy)
        for edit in edits:
            mutate(copy, *edit)
        results = {name: run_all.run_suite(name, copy) for name in run_all.SUITES}
        shutil.rmtree(tmp, ignore_errors=True)
        hit = {n: r for n, r in results.items() if r[2]}
        caught = all(n in hit for n in expected)
        ok &= caught
        print(f"{mid:<6} {'CAUGHT' if caught else 'MISSED'}  {desc}")
        print(f"       " + ", ".join(f"{n} {p}/{t}" for n, (p, t, _) in hit.items()) + f"; e.g. {next(iter(hit.values()))[2][:2] if hit else []}")
    return ok
