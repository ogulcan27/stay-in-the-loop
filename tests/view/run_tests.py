"""Unified Knowledge View suite (09_KNOWLEDGE_VIEW, 07 §V).

Usage: run_tests.py [<skill_dir>]
Temporary git projects get real Human Sync state from the sync model (08); graph, ULA artifacts and queue §B are fixtures
written in their template formats. The view is built, patched, read and checked by the view model (09).
"""
import atexit
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import REPO as DEV_REPO, report, skill_dir, use  # noqa: E402

use("sync", "view")
import sync_model as sm  # noqa: E402
import music_fixture as MF  # noqa: E402
import readability as RB  # noqa: E402
import view_model as vm  # noqa: E402
from sync_model import Repo, wu  # noqa: E402
from view_model import GRAPH_F, QUEUE_F, VIEW_F, Reader, View, ViewBlocked  # noqa: E402

SKILL = skill_dir()
SP = sm.Protocol(SKILL)
P = vm.Protocol(SKILL)
TMP = Path(tempfile.mkdtemp(prefix="view_"))
atexit.register(shutil.rmtree, TMP, True)
RESULTS = []
PRJ = "PRJ-7c1d2e3f"
INTERNAL = {"state", "sync", "passes", "maps", "concepts", "experiences", "audits"}


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def project(name, prj=PRJ, steps=3):
    repo = Repo(TMP / name)
    repo.write(sm.CONFIG_F, f"# Learning Config\n\n```text\nproject_id: {prj}\nproject_name: {name}\npersonal_library_path: UNCONFIGURED\n"
                            "work_unit_source: phase-doc\n```\n")
    for n in range(1, steps + 1):
        repo.step(n, [f"src/s{n}.py"])
    return repo


def state_rows(root):
    text = (root / sm.STATE_F).read_text(encoding="utf-8") if (root / sm.STATE_F).exists() else None
    return sm.parse_state(SP, text)[1] if text else []


def sync(repo, view, arg="", judge=None, sync_only=True):
    """08 §11 sync-only run, then the 09 §8 view trigger with the pre-run state rows."""
    pre = state_rows(repo.root)
    out = sm.Sync(SP, repo.root).run(arg, judge=judge)
    rd = Reader()
    out["view"] = view.on_sync(pre, rd, sync_only=sync_only)
    out["view_reads"] = rd.log
    return out


def blocks(text):
    """{key: block text} for every marker section."""
    return {k: View.lines_of(text, s) for k, s in View.spans(text).items()}


def vtext(repo):
    return (repo.root / VIEW_F).read_text(encoding="utf-8")


def hs(n):
    return f"HS:{sm.record_id(wu(n))}"


def node(nid, name, ntype="CONCEPT", parent="-", depth="-", status="ACTIVE", arts="-", events="-", meaning="Kısa anlam cümlesi burada."):
    d = {c: "-" for c in P.node_cols}
    d.update(node_id=nid, canonical_name=name, node_type=ntype, parent_id=parent, short_meaning=meaning, system_role="Rol.",
             home_ref="UNASSIGNED", available_depth=depth, source_event_ids=events, source_artifacts=arts, node_status=status)
    return d


def edge(eid, s, rel, t):
    d = {c: "-" for c in P.edge_cols}
    d.update(edge_id=eid, source_node_id=s, relation_type=rel, target_node_id=t, meaning="m", evidence_status="VERIFIED")
    return d


def write_graph(repo, version, nodes, edges):
    repo.write(GRAPH_F, vm.render_graph(P, version, nodes, edges))


TPL_LIGHT = (SKILL / "templates" / "LIGHT_ULA_TEMPLATE.md").read_text(encoding="utf-8")
TPL_FULL = (SKILL / "ula" / "templates" / "CONTENT_BUILD_TEMPLATE.md").read_text(encoding="utf-8")


def light(repo, rel, topic, filled, status="COMPLETE"):
    """LIGHT_ULA.md from the template: given sections filled, others keep the template body."""
    out, cur = [], None
    for line in TPL_LIGHT.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            cur = m.group(1)
            out += [line, "", filled[cur], ""] if cur in filled else [line]
            continue
        if cur in filled:
            continue
        out.append(line.replace("status: IN_PROGRESS", f"status: {status}").replace("<canonical technical term>", topic))
    repo.write(rel, "\n".join(out) + "\n")


def full(repo, rel, filled, status="COMPLETE"):
    """CONTENT.md from the template with a 04 §9 header: given level-1 sections filled, others 'internal …'."""
    out, cur = [f"```yaml\nevent_id: LE-x\nartifact: CONTENT\nartifact_status: {status}\nupdated_at: 2026-10-28\n```\n"], None
    for line in TPL_FULL.splitlines():
        m = re.match(r"^# (.+)$", line)
        if m:
            cur = m.group(1)
            out += [line, "", filled.get(cur, f"internal {cur} text"), ""]
            continue
        if cur is None:
            out.append(line)
    repo.write(rel, "\n".join(out) + "\n")


L_LIGHT = {"L0 — Local Map": "Data → Split → Model", "L1 — Simple Explanation": "Gelecek bilgisi geçmişe sızar. Skor yanlış iyi görünür.",
           "L2 — Mechanism": "1. Feature gelecek satırı kullanır.\n2. Model bunu ezberler.\n\n```text\nt+1 → feature(t)\n```",
           "Retrieval": "Hangi feature gelecek bilgisini taşır?"}
L_FULL = {"Local Map": "```text\nData → Split → Walk-Forward → Score\n```", "L1 — Simple Explanation": "Zaman sırasını koruyarak test et.",
          "L2 — Mechanism": "## Mechanism Map\n\nPencere ileri kayar. Her adımda yalnız geçmiş eğitilir.",
          "L3 — Theory": "## Core Idea\n\nStationarity varsayımı zayıftır.", "L4 — Math / Formalism": "## Formula / Formal Representation\n\n$$E = \\frac{1}{K}\\sum_k e_k$$",
          "Example": "Aylık veri, 12 pencere.", "Retrieval Check": "Pencere neden ileri kayar?", "R — Reference Links": "GENERAL THEORY: time-series CV."}


def learning_graph(repo, version=1, extra=()):
    """ROOT → Validation (DOMAIN) → Temporal Leakage (Light), Walk-Forward (Full or not yet)."""
    nodes = [node("KN-00000001", "Project Root", "ROOT"),
             node("KN-0000000a", "Validation", "DOMAIN", "KN-00000001"),
             node("KN-0000000b", "Temporal Leakage", "CONCEPT", "KN-0000000a", "L1; L2", events="LE-LP-20261028-01-01",
                  arts=LIGHT_A)]
    return nodes + list(extra)


LIGHT_A = "docs/learning/passes/LP-20261028-01/ula/LE-LP-20261028-01-01/LIGHT_ULA.md"
FULL_A = "docs/learning/passes/LP-20261028-02/ula/LE-LP-20261028-02-01/CONTENT.md"


def human_files(root):
    learn = root / "docs/learning"
    return sorted(f.relative_to(learn).as_posix() for f in learn.rglob("*") if f.is_file() and f.relative_to(learn).parts[0] not in INTERNAL)


# Test A - creation only when content exists (09 §2)
pa = project("pa")
va = View(P, pa.root)
check("A initialized project without content -> no view", (va.update(["INDEX"]), (pa.root / VIEW_F).exists()), ("NO_CONTENT", False))
check("A no content -> no V finding", va.integrity(None), [])
pu = project("pu", prj="UNCONFIGURED")
check("A project_id UNCONFIGURED -> no view", (View(P, pu.root).update(["INDEX"]), (pu.root / VIEW_F).exists()), ("NO_CONTENT", False))
check("A skill install / dev repository has no view", (DEV_REPO / VIEW_F).exists(), False)

# Test B - incremental Human Sync presentation: Stages 1-3, then 4-5 (spec 36)
pb = project("pb")
vb = View(P, pb.root)
r1 = sync(pb, vb)
t1 = vtext(pb)
b1 = blocks(t1)
check("B first sync creates the view", (r1["view"], sorted(k for k in b1 if k.startswith("HS:"))), ("CREATED", sorted(hs(n) for n in (1, 2, 3))))
check("B view == deterministic rebuild", t1, vb.rebuild())
check("B no V finding", vb.integrity(t1), [])
pb.step(4, ["src/s4.py"])
pb.step(5, ["src/s5.py"])
r2 = sync(pb, vb)
t2 = vtext(pb)
b2 = blocks(t2)
check("B Stages 1-3 sections byte-identical", [b2[hs(n)] == b1[hs(n)] for n in (1, 2, 3)], [True, True, True])
check("B Stages 4-5 added", (r2["view"], hs(4) in b2, hs(5) in b2), ("UPDATED", True, True))
idx = re.findall(r"^- \[(Step \d)\]\(#(hs-[0-9a-f]{8})\)", b2["INDEX"], re.M)
check("B index lists 5 units in seq order with stable anchors", idx, [(f"Step {n}", sm.record_id(wu(n)).lower()) for n in range(1, 6)])
check("B HS order in file follows seq", [k for k in View.spans(t2) if k.startswith("HS:")], [hs(n) for n in range(1, 6)])
check("B second update reads only new records, no whole view", (sorted(k for k, _, _ in r2["view_reads"] if k == "RECORD"),
      sorted(u for k, u, _ in r2["view_reads"] if k == "RECORD"), "WHOLE_REBUILD" in [k for k, _, _ in r2["view_reads"]]),
      (["RECORD", "RECORD"], sorted([sm.record_id(wu(4)), sm.record_id(wu(5))]), False))
check("B unrelated sections only touched by index", [k for k in b2 if k in b1 and b1[k] != b2[k]], ["INDEX", "MODEL", "JOURNEY"])
check("B incremental == rebuild after Stage 5", t2, vb.rebuild())
check("B machine metadata only inside Technical Trace", ([x for x in ("checkpoint", "record_version", "git:", "Evidence") if x in b2[hs(4)].split("<details>")[0]],
      "git:" in b2[hs(4)].split("<details>")[1]), ([], True))
check("B empty record parts omitted, one sentence and Record kept", (re.findall(r"^#### (.+)$", b2[hs(1)], re.M), re.findall(r"^\*\*(.+?:)\*\* ", b2[hs(1)], re.M)),
      ([], ["Status:", "Tek cümlede:", "Record:"]))
check("B status line Current", "**Status:** Current\n" in b2[hs(1)], True)
again = sync(pb, vb)
check("B up-to-date sync -> view unchanged", (again["result"], vtext(pb) == t2), ("UP_TO_DATE", True))

# Test C - stale presentation and refresh (spec 37)
pc = project("pc", steps=4)
pc.step(5, ["src/s5.py"], depends=2)
pc.step(6, ["src/s6.py"])
vc = View(P, pc.root)
sync(pc, vc)
c0 = vtext(pc)
pc.write("src/s2.py", "# step 2 changed\nv2 behaviour\n")
pc.commit("change step 2")
judge = {("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(5)): "CONTRACT"}
rc = sync(pc, vc, "latest", judge)
c1 = vtext(pc)
k0, k1 = blocks(c0), blocks(c1)
st = {r["work_unit_id"]: r["sync_status"] for r in state_rows(pc.root)}
check("C material change -> Step 2 + dependent Step 5 STALE (state)", (st[wu(2)], st[wu(5)], st[wu(1)]), ("STALE", "STALE", "SYNCED"))
check("C stale shown as Needs refresh", ["**Status:** Needs refresh\n" in k1[hs(n)] for n in (2, 5)], [True, True])
check("C only status line changed in stale sections", [[a for a, b in zip(k0[hs(n)].splitlines(), k1[hs(n)].splitlines()) if a != b] for n in (2, 5)],
      [[k0[hs(2)].splitlines()[4]], [k0[hs(5)].splitlines()[4]]])
check("C unrelated HS sections byte-identical", [k0[hs(n)] == k1[hs(n)] for n in (1, 3, 4, 6)], [True] * 4)
check("C index marks needs refresh", re.findall(r"\(#(hs-[0-9a-f]{8})\) · needs refresh", k1["INDEX"]),
      [sm.record_id(wu(2)).lower(), sm.record_id(wu(5)).lower()])
check("C no duplicate stale + current versions", (c1.count(f"SITL:{hs(2)}:START"), c1.count("**Tek cümlede:**")), (1, 6))
check("C stale view passes V checks", vc.integrity(c1), [])
check("C sync latest: target empty, staleness persisted only", (rc["synced"], rc["refreshed"]), ([], []))
rc2 = sync(pc, vc, "", judge)
c2 = vtext(pc)
k2 = blocks(c2)
check("C refresh -> v2, Current again", [(View.spans(c2)[hs(n)][2]["v"], "**Status:** Current\n" in k2[hs(n)]) for n in (2, 5)], [("2", True), ("2", True)])
check("C refresh leaves unrelated HS byte-identical", [k1[hs(n)] == k2[hs(n)] for n in (1, 3, 4, 6)], [True] * 4)
check("C refresh content from new record version", "(v2)" in k2[hs(2)], True)
check("C incremental == rebuild", c2, vc.rebuild())

# Test D - Light then Full ULA persist into one concept section (spec 38)
pd = project("pd")
vd = View(P, pd.root)
sync(pd, vd)
d0 = blocks(vtext(pd))
light(pd, LIGHT_A, "Temporal Leakage", L_LIGHT)
before_files = sorted(f.relative_to(pd.root).as_posix() for f in pd.root.rglob("*") if f.is_file() and ".git" not in f.parts)
pre_graph = None
write_graph(pd, 1, learning_graph(pd), [])
rd = Reader()
check("D map sync -> view updated", vd.on_map_sync(pre_graph, rd), "UPDATED")
d1 = vtext(pd)
kb = blocks(d1)["KN:KN-0000000b"]
check("D Light concept in STAY_IN_THE_LOOP.md", ("### KN-0000000b — Temporal Leakage" in kb, "Skor yanlış iyi görünür." in kb), (True, True))
check("D Light levels only L0-L2 (+Retrieval)", re.findall(r"^#### (.+)$", kb, re.M),
      ["Where am I?", "L0 — Map", "L1 — Simple Mental Model", "L2 — Mechanism", "Retrieval"])
check("D Light: no L3 / L4 fabricated", ("L3 —" in kb, "L4 —" in kb, "<details>" in kb), (False, False, False))
check("D Light: Self-Check / Metadata not shown", ("Self-Check" in kb, "mode: LIGHT" in kb), (False, False))
check("D marker depth = available_depth", View.spans(d1)["KN:KN-0000000b"][2]["depth"], "L1;L2")
after_files = sorted(f.relative_to(pd.root).as_posix() for f in pd.root.rglob("*") if f.is_file() and ".git" not in f.parts)
check("D no new user-facing file (only graph fixture added)", sorted(set(after_files) - set(before_files)), [GRAPH_F])
check("D HS sections untouched by learning", [blocks(d1)[hs(n)] == d0[hs(n)] for n in (1, 2, 3)], [True, True, True])
check("D artifact reads limited to the concept's artifact", sorted({u for k, u, _ in rd.log if k == "ARTIFACT"}), [LIGHT_A])
check("D no record read for a learning update", [u for k, u, _ in rd.log if k == "RECORD"], [])
g1 = (pd.root / GRAPH_F).read_text(encoding="utf-8")
full(pd, FULL_A, L_FULL)
nodes = learning_graph(pd)
nodes[2] = dict(nodes[2], available_depth="L1; L2; L3; L4", source_artifacts=f"{LIGHT_A}; {FULL_A}",
                source_event_ids="LE-LP-20261028-01-01; LE-LP-20261028-02-01")
write_graph(pd, 2, nodes, [])
vd.on_map_sync(g1)
d2 = vtext(pd)
kf = blocks(d2)["KN:KN-0000000b"]
check("D Full: deeper levels in the same section", (d2.count("SITL:KN:KN-0000000b:START"), "<summary><strong>L3 — Theory</strong></summary>" in kf,
      "<summary><strong>L4 — Formalism</strong></summary>" in kf), (1, True, True))
check("D Full: L1 from latest artifact, L0 kept", ("Zaman sırasını koruyarak test et." in kf, "#### L0 — Map" in kf), (True, True))
check("D Full: L0-L2 open, L3 / L4 / Reference collapsed", (kf.count("<details>"), "#### L2 — Mechanism" in kf), (3, True))
check("D Full: internal artifact parts not shown", [x for x in ("internal Oral Version", "internal Content Integrity Check", "internal Transition")
                                                  if x in kf], [])
check("D Full: inner artifact headings demoted", (re.findall(r"^#{1,3} ", kf, re.M), "###### Core Idea" in kf), (["### "], True))
check("D Full: only the concept + index changed", [k for k in blocks(d2) if blocks(d1).get(k) != blocks(d2)[k]], ["INDEX", "KN:KN-0000000b"])
check("D no per-level user-facing file", human_files(pd.root), ["STAY_IN_THE_LOOP.md"])
check("D view == rebuild", d2, vd.rebuild())
check("D view passes V checks", vd.integrity(d2), [])

# Test E - normal workflow reuses Human Sync; learning not duplicated (spec 39)
pe = project("pe")
ve = View(P, pe.root)
hsj = {("hs", wu(2)): {"Purpose": "Validation katmanı eklendi → sızıntı kontrolü → güvenilir skor",
                       "Why It Changed": "Skorlar fazla iyiydi. Kontrol gerekliydi.", "Dependencies": "Yok."}}
sync(pe, ve, judge=hsj)
e0 = vtext(pe)
rd = Reader()
src = sm.Sync(SP, pe.root).full_sources([wu(1), wu(2), wu(3)], reader=rd)
check("E full mode reuses SYNCED records", set(map(tuple, src.values())), {("OWN_RECORD",)})
check("E view HS unchanged by full-mode Human Sync reuse", ve.on_sync(state_rows(pe.root)), "UNCHANGED")
light(pe, LIGHT_A, "Temporal Leakage", L_LIGHT)
write_graph(pe, 1, learning_graph(pe), [])
ve.on_map_sync(None)
e1 = vtext(pe)
eb = blocks(e1)
check("E HS sections byte-identical after learning", [blocks(e0)[hs(n)] == eb[hs(n)] for n in (1, 2, 3)], [True, True, True])
check("E HS parts follow 09 §5.1 order, empty ones omitted", re.findall(r"^(?:#### (.+)|\*\*(.+?:)\*\* )", eb[hs(2)], re.M),
      [("", "Status:"), ("", "Tek cümlede:"), ("Why", ""), ("", "Record:")])
check("E learning added to Learning section", e1.index("## Learning") < e1.index("SITL:KN:KN-0000000b:START") < e1.index("SITL:MAP:START"), True)
hs_lines = {l for k, b in eb.items() if k.startswith("HS:") for l in b.splitlines() if len(l) > 25}
kn_lines = {l for k, b in eb.items() if k.startswith("KN:") for l in b.splitlines() if len(l) > 25}
check("E no prose shared between Human Sync and Learning", sorted(hs_lines & kn_lines), [])
check("E Learning index states Human Sync ≠ learned", "Human Sync ≠ learned" in eb["INDEX"], True)

# Test F - sync-only never writes KN / MAP / DEBT (08 §11, 09 §8, V-13)
check("F 08 §11 sync-only view scope", P.sync_only_kinds, ["HS", "JOURNEY", "MODEL", "INDEX"])
pe.write(QUEUE_F, vm.render_queue(P, [dict(zip(P.debt_cols, ["KD-LP-20261028-01-01", "Regime Persistence", "LE-LP-20261028-01-02",
                                                           wu(3), "Rejim kalıcılığı.", "Model seçimi.", "LATER", "OPEN", "2026-10-28", "UNASSIGNED", "-"]))]))
ve.on_debt()
f0 = blocks(vtext(pe))
check("F debt listed in Open Learning Debt", "`KD-LP-20261028-01-01` — Regime Persistence · LATER" in f0["DEBT"], True)
pe.step(4, ["src/s4.py"])
sync(pe, ve)
f1 = blocks(vtext(pe))
check("F sync-only: KN / MAP / DEBT byte-identical", [f0[k] == f1[k] for k in ("KN:KN-0000000b", "MAP", "DEBT")], [True, True, True])
check("F sync-only: new HS added", hs(4) in f1, True)
rd = Reader()
ve.update(["KN:KN-0000000b", "MAP", "DEBT"], rd, sync_only=True)
check("F sync-only filters KN / MAP / DEBT keys", [u for k, u, _ in rd.log if k == "SECTION"], [])

# Test G - section-level retrieval on a large view (spec 40)
pg = project("pg", steps=40)
vg = View(P, pg.root)
sm.Sync(SP, pg.root).run("")
big = [node("KN-00000001", "Project Root", "ROOT")] + [node(f"KN-a{d:07x}", f"Domain {d}", "DOMAIN", "KN-00000001", "L1", arts=LIGHT_A)
                                                         for d in range(6)]
for i in range(150):
    big.append(node(f"KN-{i + 0x100:08x}", f"Concept {i}", "CONCEPT", f"KN-a{i % 6:07x}", "L1; L2", arts=LIGHT_A, events=f"LE-{i}"))
bedges = [edge(f"KE-{i:04d}", f"KN-{i + 0x100:08x}", "REQUIRES", f"KN-{i + 0x101:08x}") for i in range(0, 149, 7)]
light(pg, LIGHT_A, "Concept", L_LIGHT)
write_graph(pg, 1, big, bedges)
vg.update([])
gt = vtext(pg)
total = len(gt.splitlines())
rd = Reader()
got = vg.retrieve("KN", "KN:KN-00000107", rd=rd)
read_lines = sum(n for k, _, n in rd.log if k in ("SECTION", "WHOLE_VIEW"))
check("G KN plan = markers + index + target", [(k, u) for k, u, _ in rd.log], [("MARKERS", "-"), ("SECTION", "INDEX"), ("SECTION", "KN:KN-00000107")])
check("G whole document not read by default", "WHOLE_VIEW" in rd.kinds(), False)
check("G lines read << document", (read_lines < total / 4, total > 2000), (True, True))
check("G target section returned intact", (got["KN:KN-00000107"].startswith("<!-- SITL:KN:KN-00000107:START"),
                                           got["KN:KN-00000107"].endswith("<!-- SITL:KN:KN-00000107:END -->")), (True, True))
rd = Reader()
vg.retrieve("KN", "KN:KN-00000107", deps=True, rd=rd)
check("G dependencies only on request: REQUIRES target", [u for k, u, _ in rd.log if k == "SECTION"], ["INDEX", "KN:KN-00000107", "KN:KN-00000108"])
rd = Reader()
vg.retrieve("HS", hs(7), rd=rd)
check("G HS plan = markers + index + target", [u for k, u, _ in rd.log if k == "SECTION"], ["INDEX", hs(7)])
check("G 09 §9 never-list keeps WHOLE_VIEW out of HS / KN", all("WHOLE_VIEW" in P.plan[r][1] and "WHOLE_VIEW" not in P.plan[r][0] for r in ("HS", "KN")), True)

# Test H - section write stability (spec 41)
g_pre = (pg.root / GRAPH_F).read_text(encoding="utf-8")
big2 = [dict(n) for n in big]
target = next(n for n in big2 if n["node_id"] == "KN-00000120")
target["available_depth"] = "L1; L2; L3"
light(pg, "docs/learning/passes/LP-x/ula/LE-x/LIGHT_ULA.md", "Concept", dict(L_LIGHT, **{"L3 — Theory": "Neden: varsayım bozulur."}))
target["source_artifacts"] = f"{LIGHT_A}; docs/learning/passes/LP-x/ula/LE-x/LIGHT_ULA.md"
write_graph(pg, 2, big2, bedges)
rd = Reader()
vg.on_map_sync(g_pre, rd)
ht = vtext(pg)
hb0, hb1 = blocks(gt), blocks(ht)
check("H only the modified concept + index changed", sorted(k for k in hb1 if hb0.get(k) != hb1[k]), ["INDEX", "KN:KN-00000120"])
check("H every other section byte-identical", sum(hb0[k] == hb1[k] for k in hb0), len(hb0) - 2)
check("H unchanged prefix / suffix bytes", (ht.split("<!-- SITL:KN:KN-00000120:START")[0].split("<!-- SITL:INDEX:END -->")[1]
                                            == gt.split("<!-- SITL:KN:KN-00000120:START")[0].split("<!-- SITL:INDEX:END -->")[1],
                                            ht.split("<!-- SITL:KN:KN-00000120:END -->")[1] == gt.split("<!-- SITL:KN:KN-00000120:END -->")[1]), (True, True))
check("H write read only the changed concept", (sorted({u for k, u, _ in rd.log if k == "SECTION"}), "WHOLE_REBUILD" in rd.kinds()),
      (["INDEX", "KN:KN-00000120", "MAP"], False))
check("H incremental == rebuild", ht, vg.rebuild())

# Test I - global map derived from the Semantic Graph (spec 42)
gmap = blocks(ht)["MAP"]
mer = vm.mermaid_blocks(gmap + "\n")
check("I one Mermaid flowchart LR", (len(mer), mer[0].splitlines()[0]), (1, "flowchart LR"))
check("I Mermaid static check", vm.mermaid_errors(mer[0]), [])
ids = set(re.findall(r"KN_([0-9a-f]{8})\[", mer[0]))
gnodes = {n["node_id"]: n for n in big2}
check("I map nodes are graph nodes", all(f"KN-{i}" in gnodes for i in ids), True)
pedges = re.findall(r"KN_([0-9a-f]{8}) --> KN_([0-9a-f]{8})$", mer[0], re.M)
check("I map edges = graph parent_id", all(gnodes[f"KN-{c}"]["parent_id"] == f"KN-{p}" for p, c in pedges) and len(pedges) == len(ids) - 1, True)
check("I map has no lesson / meaning text", ("Kısa anlam" in gmap, "Skor yanlış" in gmap, "Rol." in gmap), (False, False, False))
labels = re.findall(r'\["([^"]*)"\]', mer[0])
check("I short labels: name + ID only", all(len(l.split(" (KN-")[0]) <= P.int_rule("map_label_max_chars") and re.search(r"\(KN-[0-9a-f]{8}\)$", l)
                                            for l in labels), True)
pi = project("pi", steps=1)
long_name = "A Very Long Canonical Concept Name That Goes Beyond The Map Limit Easily"
write_graph(pi, 1, [node("KN-00000001", "Root", "ROOT"), node("KN-00000002", long_name, parent="KN-00000001", depth="L1", arts=LIGHT_A),
                    node("KN-00000003", "Next Step", parent="KN-00000001", status="DEBT")],
            [edge("KE-0001", "KN-00000002", "NEXT", "KN-00000003"), edge("KE-0002", "KN-00000002", "USES", "KN-00000003")])
light(pi, LIGHT_A, "x", L_LIGHT)
vi = View(P, pi.root)
vi.update([])
imap = blocks(vtext(pi))["MAP"]
check("I long label shortened, DEBT tagged, NEXT edge drawn", ("…" in imap, long_name not in imap, "Next Step (DEBT) (KN-00000003)" in imap,
                                                            "KN_00000002 -. NEXT .-> KN_00000003" in imap), (True, True, True, True))
check("I global map shows only hierarchy + NEXT (no USES)", "USES" in imap, False)
check("I DEBT node: no Learning section, appears in map", ("SITL:KN:KN-00000003" in vtext(pi), "KN_00000003" in imap), (False, True))

# Test J - recursive zoom: global map + local maps (spec 43)
pj = project("pj", steps=1)
zn = [node("KN-00000001", "Machine Learning", "ROOT"),
      node("KN-00000010", "Sequence Models", "DOMAIN", "KN-00000001", "L1", arts=LIGHT_A),
      node("KN-00000020", "Hidden-State Models", "CONCEPT", "KN-00000010", "L1; L2", arts=LIGHT_A),
      node("KN-00000021", "Attention", "CONCEPT", "KN-00000010", "L1", arts=LIGHT_A),
      node("KN-00000022", "Recurrent Nets", "CONCEPT", "KN-00000010", "L1", arts=LIGHT_A),
      node("KN-00000030", "State Process", "CONCEPT", "KN-00000020", "L1", arts=LIGHT_A),
      node("KN-00000031", "Observation Process", "CONCEPT", "KN-00000020", "L1", arts=LIGHT_A),
      node("KN-00000032", "Duration", "CONCEPT", "KN-00000020", "L1; L2", arts=LIGHT_A),
      node("KN-00000040", "Duration Model", "CONCEPT", "KN-00000032", "L1", arts=LIGHT_A),
      node("KN-00000050", "Probabilistic Models", "DOMAIN", "KN-00000001")]
ze = [edge("KE-0001", "KN-00000020", "PART_OF", "KN-00000050"), edge("KE-0002", "KN-00000020", "USES", "KN-00000040")]
light(pj, LIGHT_A, "x", L_LIGHT)
write_graph(pj, 1, zn, ze)
vj = View(P, pj.root)
vj.update([])
jt = vtext(pj)
jb = blocks(jt)
jmap = vm.mermaid_blocks(jb["MAP"] + "\n")[0]
check("J global map: depth <= 2 only", (("KN_00000020" in jmap), ("KN_00000030" in jmap), ("KN_00000040" in jmap)), (True, False, False))
lm = {k: vm.mermaid_blocks(b + "\n") for k, b in jb.items() if k.startswith("KN:")}
check("J local maps only for 3+ children", sorted(k for k, v in lm.items() if v), ["KN:KN-00000010", "KN:KN-00000020"])
hsm = lm["KN:KN-00000020"][0]
check("J local map: State / Observation / Duration branches", [c in hsm for c in ("KN_00000030", "KN_00000031", "KN_00000032")], [True, True, True])
check("J local map shows node relations", "KN_00000020 -- USES --> KN_00000040" in hsm, True)
check("J local maps valid Mermaid", [vm.mermaid_errors(v[0]) for v in lm.values() if v], [[], []])
check("J breadcrumb from parent_id chain", re.search(r"^.* → \*\*Duration Model\*\*$", jb["KN:KN-00000040"], re.M).group(0),
      "[Project Home](#project-home) → [Knowledge Map](#knowledge-map) → Machine Learning → [Sequence Models](#kn-00000010) → "
      "[Hidden-State Models](#kn-00000020) → [Duration](#kn-00000032) → **Duration Model**")
check("J secondary membership shown separately", "Also part of: Probabilistic Models" in jb["KN:KN-00000020"], True)
check("J maps carry no lesson text", any("Skor yanlış" in b for k, b in jb.items() if k == "MAP") or any("Skor yanlış" in m[0] for m in lm.values() if m), False)
check("J lesson text once per concept section", all(b.count("Skor yanlış iyi görünür.") == 1 for k, b in jb.items() if k.startswith("KN:")), True)
check("J related concepts link to sections", "- USES → [Duration Model](#kn-00000040)" in jb["KN:KN-00000020"], True)

# Test K - 07 §V integrity, candidate safety, write failure (spec 33, 34)
check("K 18 V checks", sorted(P.checks), [f"V-{i:02d}" for i in range(1, 19)])
check("K structural / misleading checks FAIL", sorted(c for c, s in P.checks.items() if s == "FAIL"),
      ["V-02", "V-03", "V-04", "V-05", "V-09", "V-10", "V-12", "V-13"])
base = vtext(pd)
vf = (pd.root / VIEW_F)


def crafted(fn):
    vf.write_text(fn(base), encoding="utf-8")
    try:
        return [c for c, _ in vd.integrity(vtext(pd))]
    finally:
        vf.write_text(base, encoding="utf-8")


kn_block = blocks(base)["KN:KN-0000000b"]
check("K V-01 index -> missing section", "V-01" in crafted(lambda t: t.replace(kn_block + "\n\n", "")), True)
check("K V-02 duplicate concept section", "V-02" in crafted(lambda t: t.replace(kn_block, kn_block + "\n\n" + kn_block)), True)
check("K V-03 broken marker pairing", "V-03" in crafted(lambda t: t.replace("<!-- SITL:KN:KN-0000000b:END -->\n", "")), True)
check("K V-03 unknown SITL marker", "V-03" in crafted(lambda t: t.replace("## Learning\n", "## Learning\n<!-- SITL:XX:START -->\n")), True)
check("K V-04 concept ID mismatch", "V-04" in crafted(lambda t: t.replace("### KN-0000000b — ", "### KN-0000000c — ")), True)
check("K V-05 header project mismatch", "V-05" in crafted(lambda t: t.replace(f"project_id={PRJ}", "project_id=PRJ-00000000")), True)
other = "HS-deadbeef"
check("K V-05 HS section from another project", "V-05" in crafted(lambda t: t.replace(hs(1)[3:], other)), True)
check("K V-07 stale record version", "V-07" in crafted(lambda t: t.replace(f"SITL:{hs(1)}:START v=1", f"SITL:{hs(1)}:START v=7")), True)
check("K V-06 STALE shown as Current", "V-06" in crafted(lambda t: t.replace(f"{blocks(t)[hs(1)].splitlines()[4]}",
                                                                              blocks(t)[hs(1)].splitlines()[4].replace("Current", "Needs refresh"))), True)
check("K V-09 unclosed fence", "V-09" in crafted(lambda t: t.replace("#### L1 — Simple Mental Model\n", "#### L1 — Simple Mental Model\n```text\n")), True)
check("K V-10 level-2 heading inside a section", "V-10" in crafted(lambda t: t.replace("#### L1 — Simple Mental Model", "## L1 — Simple Mental Model")), True)
check("K V-11 L4 heading on a Light (L1;L2) concept", [c for c, _ in ve.integrity(vtext(pe).replace("#### L2 — Mechanism", "#### L4 — Formalism"))],
      ["V-11"])
check("K V-14 map node not in graph", "V-14" in crafted(lambda t: t.replace("KN_0000000b[", "KN_0000beef[")), True)
check("K clean view -> no finding", vd.integrity(base), [])
# misleading presentation is repaired section by section
st_text = (pd.root / sm.STATE_F).read_text(encoding="utf-8")
(pd.root / sm.STATE_F).write_text(st_text.replace("| SYNCED |", "| STALE |", 1), encoding="utf-8")
found = vd.integrity(vtext(pd))
check("K state STALE, view Current -> V-06 + V-18 WARNING", found, [("V-06", "WARNING"), ("V-18", "WARNING")])
pre = blocks(vtext(pd))
res = vd.repair()
post = blocks(vtext(pd))
check("K repair rewrites only that HS section (+ index, journey)", (res[1], sorted(k for k in post if pre[k] != post[k])), ("REPAIRED", [hs(1), "INDEX", "JOURNEY"]))
check("K after repair: clean", vd.integrity(vtext(pd)), [])
(pd.root / sm.STATE_F).write_text(st_text, encoding="utf-8")
vd.repair()
# structural FAIL blocks writes; file unchanged
good = vtext(pd)
vf.write_text(good.replace("<!-- SITL:MAP:END -->\n", ""), encoding="utf-8")
bad = vtext(pd)
try:
    vd.update(["INDEX", "MAP"])
    blocked = None
except ViewBlocked as e:
    blocked = str(e)
check("K corrupt view -> update BLOCKED, no write", (blocked, vtext(pd) == bad), ("V-03", True))
check("K corrupt view -> repair refuses (FAIL)", vd.repair()[1], "FAIL")
vf.write_text(good, encoding="utf-8")
# candidate FAIL: a record with an unclosed fence never reaches the view; authoritative sync stays
pk = project("pk", steps=2)
vk = View(P, pk.root)
sync(pk, vk)
k_before = vtext(pk)
pk.step(3, ["src/s3.py"])
try:
    sync(pk, vk, judge={("hs", wu(3)): {"How It Works": "```text\nGirdi → Çıktı"}})
    cand = None
except ViewBlocked as e:
    cand = str(e)
check("K candidate V-09 -> view write refused", (cand, vtext(pk) == k_before), ("V-09", True))
check("K authoritative sync not undone by view failure", {r["work_unit_id"]: r["sync_status"] for r in state_rows(pk.root)}[wu(3)], "SYNCED")
# write failure mid-way restores the pre-image (no half section, no lone marker)
pk.write(f"{sm.SYNC}/records/{sm.record_id(wu(3))}.md", (pk.root / f"{sm.SYNC}/records/{sm.record_id(wu(3))}.md").read_text(encoding="utf-8").replace("```text\nGirdi → Çıktı", "Girdi → Çıktı"))
try:
    vk.update([hs(3), "JOURNEY", "MODEL", "INDEX"], fail_on="INDEX")
    wf = None
except ViewBlocked as e:
    wf = str(e)
check("K injected write error -> pre-image restored", (wf, vtext(pk) == k_before, vk.integrity(vtext(pk), structural_only=True)), ("write error", True, []))
vk.update([hs(3), "JOURNEY", "MODEL", "INDEX"])
check("K retry after failure -> consistent", (vk.integrity(vtext(pk)), vtext(pk) == vk.rebuild()), ([], True))
# foreign file is never overwritten
pf = project("pf")
(pf.root / VIEW_F).parent.mkdir(parents=True, exist_ok=True)
(pf.root / VIEW_F).write_text("# My own notes\n", encoding="utf-8")
vfo = View(P, pf.root)
try:
    sync(pf, vfo)
    fo = None
except ViewBlocked as e:
    fo = str(e)
check("K foreign STAY_IN_THE_LOOP.md -> V-12, not overwritten", (fo, (pf.root / VIEW_F).read_text(encoding="utf-8")), ("V-12", "# My own notes\n"))

# Test L - migration of an existing project (spec 31)
pl = project("pl")
sm.Sync(SP, pl.root).run("")
light(pl, LIGHT_A, "Temporal Leakage", L_LIGHT)
full(pl, FULL_A, L_FULL)
mig_nodes = learning_graph(pl, extra=[node("KN-0000000c", "Walk-Forward Validation", "CONCEPT", "KN-0000000a", "L1; L2; L3; L4", arts=FULL_A)])
write_graph(pl, 3, mig_nodes, [edge("KE-0001", "KN-0000000b", "NEXT", "KN-0000000c")])
learn = pl.root / "docs/learning"
snap = {f.relative_to(learn).as_posix(): sha(f.read_bytes()) for f in learn.rglob("*") if f.is_file()}
check("L existing content, no view -> V-08 WARNING", vl_f := View(P, pl.root).integrity(None), [("V-08", "WARNING")])
vl = View(P, pl.root)
check("L derived repair builds the view", vl.repair()[1], "REBUILT")
after = {f.relative_to(learn).as_posix(): sha(f.read_bytes()) for f in learn.rglob("*") if f.is_file()}
check("L authoritative files untouched (no move / delete)", {k: v for k, v in after.items() if k != "STAY_IN_THE_LOOP.md"}, snap)
check("L migrated view: HS + both concepts + provenance path", (len([k for k in blocks(vtext(pl)) if k.startswith("HS:")]),
                                                                  sorted(k for k in blocks(vtext(pl)) if k.startswith("KN:")),
                                                                  f"(`{FULL_A}`)" in blocks(vtext(pl))["KN:KN-0000000c"]),
      (3, ["KN:KN-0000000b", "KN:KN-0000000c"], True))
check("L migrated view clean", vl.integrity(vtext(pl)), [])

# Test M - one human-facing file for a multi-unit, multi-concept, multi-map project (spec 35)
check("M pilot-like projects: only STAY_IN_THE_LOOP.md is human-facing", [human_files(p.root) for p in (pb, pc, pd, pe, pg, pj, pl)],
      [["STAY_IN_THE_LOOP.md"]] * 7)
check("M no HTML anywhere under docs/learning", [f.name for p in (pb, pd, pg, pj, pl) for f in (p.root / "docs/learning").rglob("*.htm*")], [])
check("M no per-level files", [f.name for p in (pd, pg, pj, pl) for f in (p.root / "docs/learning").rglob("*") if re.search(r"L[0-4]\.md$", f.name)], [])

# Test N - README architecture visualization (spec 44)
readme = (DEV_REPO / "README.md").read_text(encoding="utf-8")
check("N README: How Stay in the Loop Works near the top", 0 < readme.find("## How Stay in the Loop Works") < readme.find("## Install") if "## Install" in readme
      else "## How Stay in the Loop Works" in readme, True)
rm = vm.mermaid_blocks(readme)
check("N README: >= 2 Mermaid diagrams, all closed", (len(rm) >= 2, readme.count("```mermaid") == len(rm)), (True, True))
check("N README: Mermaid static check", [vm.mermaid_errors(b) for b in rm], [[] for _ in rm])
arch = next((b for b in rm if "/stay-in-the-loop sync" in b), "")
check("N README: Human Sync vs Learning branches", [x in arch for x in ("Human Sync", "/stay-in-the-loop sync", "STOP", "Light / Full ULA",
                                                                     "Semantic Graph")], [True] * 5)
inc = next((b for b in rm if "Minimum Required Context" in b), "")
check("N README: incremental Human Sync diagram", [x in inc for x in ("Human Sync State", "Rolling Project Context", "Relevant Previous Sync",
                                                                    "Updated Sync State")], [True] * 4)
check("N README: incremental reuse explained", ("Previously synchronized work is reused." in readme,
                                               "Only new, stale, or dependency-affected work is processed by default." in readme), (True, True))
check("N README: mode table", [bool(re.search(p, readme, re.M)) for p in (r"^\| Mode \| Purpose \| Human Sync \| ULA \| Learning Coverage \|$",
                                                                       r"^\| `/stay-in-the-loop sync` \| .* \| Unchanged \|$",
                                                                       r"^\| `/stay-in-the-loop` \| .* \| Normal workflow \|$")], [True] * 3)
check("N README: single knowledge file + internal state explained", ("docs/learning/STAY_IN_THE_LOOP.md" in readme,
      all(w in readme for w in ("incremental sync", "checkpoints", "integrity", "coverage", "resume"))), (True, True))

# Test P - human-first Human Sync rendering on a realistic research project (09 §5, 07 V-15)
pp = project("pp", steps=8)
vp = View(P, pp.root)
sync(pp, vp, judge={("hs", wu(n)): c for n, c in MF.UNITS.items()})
p0 = vtext(pp)
pb_ = blocks(p0)


def human(block):
    return block.split("<details>", 1)[0].split("\n", 5)[-1]


def record(n):
    return vm.parts_of((pp.root / f"{sm.SYNC}/records/{sm.record_id(wu(n))}.md").read_text(encoding="utf-8"), 2)


def parts_seq(block):
    return [h or b for h, b in re.findall(r"^(?:#### (.+)|\*\*(.+?:)\*\* )", block, re.M)]


check("P full layer order (rich unit)", parts_seq(pb_[hs(1)]), ["Status:", "Tek cümlede:", "Anahtar kavramlar:", "Zihinsel Model", "Neden Önemli?",
      "Why", "What Changed", "Key Decisions", "Open Points", "Evidence", "Record:"])
check("P trace is one collapsed block after the human layer", [(b.count("<details>"), b.count("<summary><strong>Technical Trace</strong></summary>"),
      b.index("#### Neden Önemli?") < b.index("<details>") if "#### Neden Önemli?" in b else True) for k, b in pb_.items() if k.startswith("HS:")], [(1, 1, True)] * 8)
check("P one sentence = record Purpose, shown once", [(pb_[hs(n)].count(record(n)["Purpose"]), f"**Tek cümlede:** {record(n)['Purpose']}" in pb_[hs(n)])
      for n in range(1, 9)], [(1, True)] * 8)
check("P key terms: plain meaning first, internal term second", "**Anahtar kavramlar:** haftalık benzersiz dinleyici sayısı (N) · "
      "haftalık toplam dinleme sayısı (C) · veri yok, sıfır değil (empty ≠ zero)" in pb_[hs(1)], True)
kt3 = re.search(r"^\*\*Anahtar kavramlar:\*\* (.+)$", pb_[hs(3)], re.M).group(1).split(" · ")
check("P term that already carries a symbol: no nested parentheses", kt3[:1], ["tahmin anında bilinebilen bilgi sınırı — prediction-time information boundary (S-B)"])
check("P key terms capped at key_terms_max; rest in More Terms (trace)", (len(kt3), "- geçmişe dönük düzeltilmiş veri (revised data)" in pb_[hs(3)].split("<details>")[1]),
      (5, True))
check("P Mental Model only where the record has one", ["#### Zihinsel Model" in human(pb_[hs(n)]) for n in (1, 2, 3, 7)], [True, True, True, False])
check("P Why It Matters = human downstream meaning, before trace",
      human(pb_[hs(3)]).split("#### Neden Önemli?\n\n")[1].strip(), MF.UNITS[3]["Downstream Impact"])
lost, dup = [], []
for n in range(1, 9):
    rec, blk = record(n), pb_[hs(n)]
    for name, body in rec.items():
        if name in ("Header", "Technical Translation"):
            continue
        for line in vm.shift(body, 2).splitlines():
            if line.strip() and line.strip() not in ("Yok.", "```", "```text") and not set(line) <= set("|-"):
                (lost if blk.count(line) == 0 else dup if blk.count(line) > 1 and len(line) > 12 else []).append(f"{n}:{line[:40]}")
    for a, t in vm.TERM.findall(rec.get("Technical Translation", "").replace("```text", "")):
        if blk.count(f"{a} — {t.strip()}" if "(" in t else f"{a} ({t.strip()})") != 1:
            lost.append(f"{n}:term {a}")
check("P every record line appears exactly once (no loss, no duplicate summary)", (lost, dup), ([], []))
head4 = dict(sm.KV.findall(record(4)["Header"]))
check("P provenance kept: Record line has id, version, work unit, checkpoint",
      f"**Record:** `{head4['record_id']}` v{head4['record_version']} · `{head4['work_unit_id']}` · `{head4['checkpoint']}`" in pb_[hs(4)].split("<details>")[1], True)
check("P evidence table in trace, not in human layer", [("VERIFIED (" in pb_[hs(n)].split("<details>")[1], "VERIFIED" in human(pb_[hs(n)])) for n in (1, 2, 3)],
      [(True, False)] * 3)
quality = {}
for n in MF.TYPES:
    h = human(pb_[hs(n)])
    quality[MF.TYPES[n]] = ("**Tek cümlede:**" in h, len(re.search(r"^\*\*Anahtar kavramlar:\*\* (.+)$", h, re.M).group(1).split(" · ")) >= 2,
                            "#### Neden Önemli?" in h, vm.undefined_symbols(h), len([l for l in h.splitlines() if l.strip()]) <= 15,
                            re.search(r"VERIFIED|INFERRED|UNRESOLVED|checkpoint|git:|HS-", h) is None)
check("P quality: research definition / data audit / freeze answer what, remember, next in the human layer only",
      quality, {t: (True, True, True, [], True, True) for t in MF.TYPES.values()})
check("P human-first symbols defined on first use (N, C, S-B, M(W), W, K(t), TF-03)",
      [vm.undefined_symbols(human(pb_[hs(n)])) for n in (1, 2, 3, 5, 6, 8)], [[]] * 6)
check("P old-style record flagged: undefined IDs in the human layer", vm.undefined_symbols(human(pb_[hs(4)])), ["TF-04", "TF-05", "TF-06"])
check("P symbol rule: bare N flagged; meaning (N) / meaning — M(W) / N = meaning / fenced letters / OPTION words not",
      [vm.undefined_symbols(x) for x in ("N arttı.", "benzersiz dinleyici sayısı (N) arttı. N düştü.", "dinleyici değişimi — M(W)",
                                          "N = benzersiz dinleyici sayısı", "```text\nN → C\n```", "PROBLEM ├── OPTION A", "K(t) = N(t+12)",
                                          "```text\nK(t)\n```", " — S-B")],
      [["N"], [], [], [], [], [], ["K(t)"], ["K(t)"], ["S-B"]])
check("P V-15 WARNING on the old-style section only", vp.integrity(p0), [("V-15", "WARNING")])
learn = pp.root / "docs/learning"
auth = lambda: {f.relative_to(learn).as_posix(): sha(f.read_bytes()) for f in sorted(learn.rglob("*")) if f.is_file() and f.name != "STAY_IN_THE_LOOP.md"}  # noqa: E731
a0 = auth()
check("P V-15 is not repaired by view writes (record is the source)", (vp.repair(), vtext(pp) == p0), (([("V-15", "WARNING")], "NOTHING"), True))
(pp.root / VIEW_F).unlink()
rd = Reader()
vp.repair(rd)
check("P migration: rebuild from existing records reproduces the view", vtext(pp), p0)
check("P authoritative records, state and context unchanged by view writes", auth(), a0)
check("P view rebuild reads no ULA artifact; Human Sync never invokes ULA", ("ARTIFACT" in rd.kinds(), (learn / "passes").exists()), (False, False))
pp.write("src/s5.py", "# step 5 changed\nv2 behaviour\n")
pp.commit("change step 5")
sync(pp, vp, "latest", {("material", wu(5)): "BEHAVIOUR", **{("hs", wu(n)): c for n, c in MF.UNITS.items()}})
p1 = blocks(vtext(pp))
check("P stale: only the status line of that section changes", [a for a, b in zip(pb_[hs(5)].splitlines(), p1[hs(5)].splitlines()) if a != b],
      ["**Status:** Current"])
check("P stale: other sections byte-identical", [k for k in pb_ if k != hs(5) and pb_[k] != p1[k]], ["INDEX", "MODEL", "JOURNEY"])
sync(pp, vp, "", {("hs", wu(n)): c for n, c in MF.UNITS.items()})
p2 = blocks(vtext(pp))
check("P refresh: section rebuilt from record v2, others untouched", (View.spans(vtext(pp))[hs(5)][2]["v"], "**Status:** Current\n" in p2[hs(5)],
      [k for k in p1 if k.startswith("HS:") and k != hs(5) and p1[k] != p2[k]]), ("2", True, []))
pp.write(sm.CONTEXT_F, f"# Project Sync Context\n\n## Header\n\n```text\nproject_id: {PRJ}\n```\n\n{MF.CONTEXT}")
before_model = blocks(vtext(pp))
vp.update(["MODEL"])
m = blocks(vtext(pp))
model = m["MODEL"]
check("P Project in 60 Seconds: heading and human-first order", (model.splitlines()[1], parts_seq(model.split("<details>")[0])),
      ("## Project in 60 Seconds", ["What are we building?", "Where are we now?", "How does it work at the highest level?", "Five things to remember",
                                    "What is still unresolved?"]))
five = model.split("#### Five things to remember\n\n")[1].split("\n\n")[0].splitlines()
check("P five things = invariants first, then active decisions", five, ["- Eksik hafta sıfır değil, boştur.",
      "- Model yalnız tahmin haftasından önce yayımlanmış veriyi görür.", "- Her özellik aynı activity tanımını kullanır.",
      "- Ana ölçü benzersiz dinleyici sayısı, toplam dinleme yardımcı.", "- Hedef 12 haftalık dinleyici artışı."])
check("P technical snapshot collapsed, keeps the rest", (model.count("<summary><strong>Technical Project Snapshot</strong></summary>"),
      parts_seq(model.split("<details>")[1])), (1, ["Architecture", "Components", "Active Decisions", "Dependencies"]))
ctx_lines = [l for l in MF.CONTEXT.splitlines() if l.strip() and not l.startswith(("## ", "```"))]
check("P every context line appears exactly once in the model", [l for l in ctx_lines if model.count(l) != 1], [])
check("P model update touches only MODEL + Project Home (09 §3.1)", [k for k in m if m[k] != before_model[k]], ["INDEX", "MODEL"])
check("P view == rebuild; only V-15 (old-style record) remains", (vtext(pp) == vp.rebuild(), vp.integrity(vtext(pp))), (True, [("V-15", "WARNING")]))

# Test O - protocol vocabulary
check("O authority rules", {k: P.rules[k] for k in ("authority", "read_mode", "write_mode", "on_write_error", "failure_effect")},
      {"authority": "DERIVED", "read_mode": "MARKERS_THEN_SECTION", "write_mode": "SECTION_PATCH", "on_write_error": "RESTORE_PRE_IMAGE",
       "failure_effect": "WARNING"})
check("O structure order", P.order, ["VIEW", "INDEX", "MODEL", "JOURNEY", "HS", "KN", "MAP", "DEBT"])
check("O status lines", P.status_line, {"SYNCED": "Current", "STALE": "Needs refresh"})
check("O HS template parts = 09 §5.1 mapping", P.hs_sections, [v for v, _, _ in P.hs_map])
check("O MODEL template = 09 §3 heading + §5.3 parts", (P.model_template_heading, P.model_sections), (P.model_heading, [v for v, _, _ in P.model_map]))
check("O Light has no L4 source", P.artifact_map["L4 — Formalism"]["LIGHT"], None)
check("O collapsed parts", P.collapsed, ["L3", "L4", "Reference"])
s07 = (SKILL / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8")
check("O 07 §L.1 KNOWLEDGE_VIEW is DERIVED", bool(re.search(r"^\| `KNOWLEDGE_VIEW` \| DERIVED \|", s07, re.M)), True)
check("O 07 §L.3 runs §V", "+ §V + §L checks" in s07, True)
check("O view template has no per-level or HTML file target", re.findall(r"(?:L[0-4]\.md|\.html\b)", (SKILL / "templates" / "KNOWLEDGE_VIEW_TEMPLATE.md").read_text(encoding="utf-8")), [])

# Test Q - readability baseline and rendering contract (09 §13)
pq = project("pq")
vq = View(P, pq.root)
sync(pq, vq)
light(pq, LIGHT_A, "Temporal Leakage", L_LIGHT)
B2_MAP = "## LOCAL MAP — B2 Üretim Döngüsü\n\n```text\nB2.1 Başlangıç\n   ↓\nB2.2 Süre ve emission\n   ↓\nB2.3 Geçiş\n```\n\nDöngüde üç seçim vardır."
B4_MAP = "## LOCAL MAP — B4 Süre Aileleri\n\n```text\nSüre PMF'i\n├── B4.1 Geometric\n└── B4.2 L2 PMF\n```\n\nİki aile aynı yüzeyi doldurur."
full(pq, FULL_A, dict(L_FULL, **{"Local Map": f"{L_FULL['Local Map']}\n\nPencere ileri kayar.\n\n{B2_MAP}\n\n{B4_MAP}"}))
write_graph(pq, 1, learning_graph(pq, extra=[node("KN-0000000c", "Walk-Forward", "CONCEPT", "KN-0000000a", "L1; L2; L3; L4",
                                                  events="LE-LP-20261028-02-01", arts=FULL_A)]),
            [edge("KE-0001", "KN-0000000b", "NEXT", "KN-0000000c"), edge("KE-0002", "KN-0000000c", "USES", "KN-0000000b")])
vq.on_map_sync(None)
q_files = lambda: {f.relative_to(pq.root).as_posix(): sha(f.read_bytes()) for f in sorted(pq.root.rglob("*")) if f.is_file() and ".git" not in f.parts}  # noqa: E731
q0, qt, qg = q_files(), vtext(pq), (pq.root / GRAPH_F).read_text(encoding="utf-8")
qm = RB.metrics(qt, qg, SKILL)
check("Q baseline tool reports exactly the 09 §13.2 metrics", list(qm), P.metrics)
check("Q baseline fixture structure", qm, {
    "lines_total": 273, "lines_visible": 118, "lines_collapsed": 12, "details_blocks": 7, "details_max_depth": 1, "hs_units": 3, "kn_concepts": 2,
    "graph_nodes": 4, "graph_edges": 2, "graph_edges_by_relation": "NEXT=1; USES=1", "links_internal": 29, "links_broken": 0,
    "links_from_index": 10, "links_from_hs": 3, "links_from_kn": 10, "kn_without_outgoing_link": 0, "maps_global": 1,
    "maps_local_structured": 4, "maps_local_by_source": "BLOCK=2; CONCEPT_L0=2; GRAPH=0", "maps_local_mermaid": 0,
    "global_map_edges_by_kind": "HIERARCHY=3; NEXT=1"})
check("Q local map sources = 09 §13.2 source table", [x.split("=")[0] for x in qm["maps_local_by_source"].split("; ")], sorted(P.local_sources))
check("Q existing ASCII LOCAL MAP blocks (HSMM shape) are local maps", re.findall(r"^##### (LOCAL MAP — .+)$", qt, re.M),
      ["LOCAL MAP — B2 Üretim Döngüsü", "LOCAL MAP — B4 Süre Aileleri"])
as_mermaid = qt.replace("##### LOCAL MAP — B2 Üretim Döngüsü\n\n```text", "##### LOCAL MAP — B2 Üretim Döngüsü\n\n```mermaid", 1)
qc = RB.metrics(as_mermaid, qg, SKILL)
check("Q text -> Mermaid conversion is no local map gain", (qc["maps_local_structured"], qc["maps_local_by_source"], qc["maps_local_mermaid"]),
      (4, "BLOCK=2; CONCEPT_L0=2; GRAPH=0", 1))
without_b4 = re.sub(r"^##### LOCAL MAP — B4.*?İki aile aynı yüzeyi doldurur\.\n", "", qt, count=1, flags=re.M | re.S)
check("Q removing a real local map lowers the count", (RB.metrics(without_b4, qg, SKILL)["maps_local_structured"],
      RB.metrics(without_b4, qg, SKILL)["maps_local_by_source"]), (3, "BLOCK=1; CONCEPT_L0=2; GRAPH=0"))
jm = RB.metrics(jt, (pj.root / GRAPH_F).read_text(encoding="utf-8"), SKILL)
check("Q graph Mermaid local maps counted as GRAPH (Test J view)", (jm["maps_local_by_source"], jm["maps_local_mermaid"], jm["maps_local_structured"]),
      (f"BLOCK=0; CONCEPT_L0={jm['kn_concepts']}; GRAPH=2", 2, jm["kn_concepts"] + 2))
check("Q baseline deterministic", RB.metrics(qt, qg, SKILL), qm)
check("Q baseline is read-only", q_files(), q0)
check("Q visible + collapsed + blank + markup lines = total", qm["lines_visible"] + qm["lines_collapsed"] + sum(
      not l.strip() or bool(RB.HIDDEN.match(l)) for l in qt.splitlines()), qm["lines_total"])
broken = qt.replace("](#kn-0000000c)", "](#kn-0000000d)", 1)
check("Q broken link counted", RB.metrics(broken, qg, SKILL)["links_broken"], 1)
check("Q contract: seven reader questions", P.reader_questions, ["Where am I?", "What is this?", "Why does it matter?", "What came before?",
      "What does this depend on?", "Where is this used?", "Where do I go next?"])
content_kinds = [k for k in P.order if k not in ("VIEW", "INDEX")]
check("Q contract: Human Sync and Learning are separate navigation domains",
      (P.domains["HUMAN_SYNC"], P.domains["LEARNING"], sorted(P.domains["HUMAN_SYNC"] + P.domains["LEARNING"]) == sorted(content_kinds)),
      (["MODEL", "JOURNEY", "HS"], ["KN", "MAP", "DEBT"], True))
classes = [r for rs in P.edge_classes.values() for r in rs]
check("Q contract: every graph relation has exactly one class", (sorted(classes), len(classes) == len(set(classes))), (sorted(P.relation_types), True))
check("Q contract: NEXT is navigation only, never dependency", (P.edge_classes["NAVIGATION"], "NEXT" in P.edge_classes["SEMANTIC"]), (["NEXT"], False))
check("Q contract: Markdown view is the only DERIVED layer", {k: v[0] for k, v in P.layers.items() if v[0] != "AUTHORITATIVE"},
      {"Markdown view": "DERIVED"})
check("Q contract: DERIVED layer is the 09 §1 view", P.layers["Markdown view"][1], [Path(P.path).name])
check("Q view == rebuild (rendering unchanged by the contract)", qt, vq.rebuild())

# Test R - Project Home and navigation architecture (09 §3.1, §3.2, §6.3; 07 V-01, V-16, V-17)
pr = project("pr", steps=2)
vr = View(P, pr.root)
sync(pr, vr)
light(pr, LIGHT_A, "x", L_LIGHT)
rn = [node("KN-00000001", "Project Root", "ROOT"),
      node("KN-000000a1", "Estimation", "DOMAIN", "KN-00000001", "L1", arts=LIGHT_A),
      node("KN-000000b1", "Forward Pass", "CONCEPT", "KN-000000a1", "L1; L2", arts=LIGHT_A),
      node("KN-000000b2", "Backward Pass", "CONCEPT", "KN-000000a1", "L1", arts=LIGHT_A),
      node("KN-000000b3", "Smoothing", "CONCEPT", "KN-000000a1", "L1", arts=LIGHT_A)]
r_edges = [edge("KE-0001", "KN-000000b1", "NEXT", "KN-000000b2"), edge("KE-0002", "KN-000000b2", "NEXT", "KN-000000b3"),
           edge("KE-0003", "KN-000000b3", "USES", "KN-000000b1")]
write_graph(pr, 1, rn, r_edges)
vr.on_map_sync(None)
rt = vtext(pr)
rb = blocks(rt)
where = lambda b: b.split("#### Where am I?\n\n", 1)[1].split("\nLearning depth:", 1)[0]  # noqa: E731
r_kn = [k for k in rb if k.startswith("KN:")]
tpl = (SKILL / "templates" / "KNOWLEDGE_VIEW_TEMPLATE.md").read_text(encoding="utf-8")
bold = lambda b: re.findall(r"^\*\*(.+?)\*\*", b, re.M)  # noqa: E731
check("R Project Home is the INDEX entry point", (P.heading["INDEX"], rb["INDEX"].splitlines()[1], vm.slug("Project Home")),
      ("## Project Home", "## Project Home", "project-home"))
check("R Project Home order = template = 09 §3.1", (bold(rb["INDEX"]), bold(tpl.split("<!-- SITL:INDEX:START -->")[1].split("<!-- SITL:INDEX:END -->")[0])),
      (["Start here:", "Human Sync", "Learning", "Knowledge Architecture:", "Open Questions / Learning Debt:"],) * 2)
check("R Project Home links every top-level destination", sorted(set(vm.link_targets(rb["INDEX"])) & set(P.anchor.values())),
      sorted({"project-in-60-seconds", "project-journey", "knowledge-map", "open-learning-debt"} | {vm.slug(v) for v in vr.model_layers(Reader())["HUMAN_VIEWS"]
                                                                                if vm.slug(v) in P.anchor.values()}))
check("R 09 §3.2 heading anchors are the GitHub slugs of their headings", [(a, t) for a, t, s in P.anchor_rows if s == "heading" and vm.slug(t.lstrip("# ")) != a], [])
check("R every Learning Concept exposes Project Home, Knowledge Map and parent", [k for k in r_kn if not (
      where(rb[k]).startswith("[Project Home](#project-home) → [Knowledge Map](#knowledge-map) → ") and "\nParent: " in where(rb[k]))], [])
check("R conceptual parent = primary parent_id", [re.search(r"^Parent: (.+)$", rb[k], re.M).group(1) for k in r_kn],
      ["Project Root", "[Estimation](#kn-000000a1)", "[Estimation](#kn-000000a1)", "[Estimation](#kn-000000a1)"])
check("R previous / next from NEXT only, where applicable", [re.findall(r"^Reading order — (.+)$", rb[k], re.M) for k in r_kn],
      [[], ["Next: [Backward Pass](#kn-000000b2)"], ["Previous: [Forward Pass](#kn-000000b1) · Next: [Smoothing](#kn-000000b3)"],
       ["Previous: [Backward Pass](#kn-000000b2)"]])
check("R navigation order is not dependency: USES not in reading order, NEXT not a dependency target",
      ("Smoothing" in where(rb["KN:KN-000000b1"]), vr.dep_keys(vr.sources(), "KN:KN-000000b2"),
       [w for k in r_kn for w in ("REQUIRES", "DEPENDS_ON", "USES", "requires", "depends") if w in where(rb[k])]), (False, [], []))
check("R HS, MAP and DEBT end with the Project Home back link", [k for k in rb if k.split(":")[0] in ("HS", "MAP", "DEBT")
      and rb[k].splitlines()[-2] != "[↑ Project Home](#project-home)"], [])
nav_anchors = {a for a in set(P.anchor.values()) | {k[3:].lower() for k in rb if ":" in k} if a in vm.anchors_of(rt)}
check("R conditional anchor absent -> not linked", ("what-is-still-unresolved" in vm.anchors_of(rt), "#what-is-still-unresolved" in rt), (False, False))
check("R every navigation anchor at most once; linked ones exactly once",
      ([a for a in sorted(set(P.anchor.values()) | nav_anchors) if vm.anchors_of(rt).count(a) > 1],
       [a for a in sorted(set(vm.link_targets(rt))) if vm.anchors_of(rt).count(a) != 1]), ([], []))
check("R no broken internal link; clean view", (RB.metrics(rt, (pr.root / GRAPH_F).read_text(encoding="utf-8"), SKILL)["links_broken"], vr.integrity(rt)), (0, []))
check("R anchors deterministic: view == rebuild == rebuild", (rt == vr.rebuild(), vr.rebuild() == vr.rebuild()), (True, True))
# rename: identity unchanged -> anchors unchanged; neighbours re-rendered incrementally
pre_graph = (pr.root / GRAPH_F).read_text(encoding="utf-8")
write_graph(pr, 2, [dict(n, canonical_name="Backward Recursion") if n["node_id"] == "KN-000000b2" else n for n in rn], r_edges)
vr.on_map_sync(pre_graph)
r1 = blocks(vtext(pr))
check("R rename keeps every anchor", sorted(set(vm.anchors_of(vtext(pr))) & nav_anchors), sorted(nav_anchors))
check("R rename updates neighbours' reading order", ("Next: [Backward Recursion](#kn-000000b2)" in r1["KN:KN-000000b1"],
      "Previous: [Backward Recursion](#kn-000000b2)" in r1["KN:KN-000000b3"]), (True, True))
check("R rename incremental == rebuild", vtext(pr), vr.rebuild())
# concept added: only the new section, its NEXT neighbour, its parent (local map), MAP and INDEX change
rn2 = [dict(n, canonical_name="Backward Recursion") if n["node_id"] == "KN-000000b2" else n for n in rn] + \
      [node("KN-000000b4", "Posterior Decoding", "CONCEPT", "KN-000000a1", "L1", arts=LIGHT_A)]
pre_graph = (pr.root / GRAPH_F).read_text(encoding="utf-8")
write_graph(pr, 3, rn2, r_edges + [edge("KE-0004", "KN-000000b3", "NEXT", "KN-000000b4")])
vr.on_map_sync(pre_graph)
r2 = blocks(vtext(pr))
check("R concept added: changed sections", sorted(k for k in r2 if r1.get(k) != r2[k]), ["INDEX", "KN:KN-000000a1", "KN:KN-000000b3", "KN:KN-000000b4", "MAP"])
check("R concept added: previous / next linked both ways", (re.findall(r"^Reading order — (.+)$", r2["KN:KN-000000b4"], re.M),
      "Next: [Posterior Decoding](#kn-000000b4)" in r2["KN:KN-000000b3"]), (["Previous: [Smoothing](#kn-000000b3)"], True))
check("R concept added incremental == rebuild; clean", (vtext(pr) == vr.rebuild(), vr.integrity(vtext(pr))), (True, []))
# concept removed (SUPERSEDED): neighbours drop it, no navigation link breaks
pre_graph = (pr.root / GRAPH_F).read_text(encoding="utf-8")
write_graph(pr, 4, [dict(n, node_status="SUPERSEDED", superseded_by="KN-000000b3") if n["node_id"] == "KN-000000b2" else n for n in rn2],
            r_edges + [edge("KE-0004", "KN-000000b3", "NEXT", "KN-000000b4")])
vr.on_map_sync(pre_graph)
r3 = blocks(vtext(pr))
check("R concept removed: neighbours drop it from reading order", (re.findall(r"^Reading order — (.+)$", r3["KN:KN-000000b1"], re.M),
      re.findall(r"^Reading order — (.+)$", r3["KN:KN-000000b3"], re.M)), ([], ["Next: [Posterior Decoding](#kn-000000b4)"]))
check("R concept removed: Project Home drops it, no broken link", ("#kn-000000b2" in r3["INDEX"], vr.broken_link_keys(vtext(pr), View.spans(vtext(pr)))),
      (False, []))
# integrity: broken, duplicate, wrong parent, invalid previous / next, missing back link
pre_graph = (pr.root / GRAPH_F).read_text(encoding="utf-8")
write_graph(pr, 5, rn2, r_edges + [edge("KE-0004", "KN-000000b3", "NEXT", "KN-000000b4")])
vr.on_map_sync(pre_graph)
base_r = vtext(pr)
check("R fixture restored before integrity checks", (base_r == vr.rebuild(), vr.integrity(base_r)), (True, []))
rf = pr.root / VIEW_F


def r_crafted(fn):
    rf.write_text(fn(base_r), encoding="utf-8")
    try:
        return [c for c, _ in vr.integrity(vtext(pr))]
    finally:
        rf.write_text(base_r, encoding="utf-8")


check("R broken anchor in a concept -> V-01", "V-01" in r_crafted(lambda t: t.replace("Next: [Backward Recursion](#kn-000000b2)", "Next: [Backward Recursion](#kn-0000beef)")),
      True)
check("R Project Home anchor gone -> V-01", "V-01" in r_crafted(lambda t: t.replace("## Project Home", "## Home")), True)
check("R duplicate navigation anchor -> V-16 only", r_crafted(lambda t: t.replace("#### L1 — Simple Mental Model", "#### Knowledge Map", 1)), ["V-16"])
check("R wrong parent link -> V-17", r_crafted(lambda t: t.replace("Parent: [Estimation](#kn-000000a1)", "Parent: [Smoothing](#kn-000000b3)", 1)), ["V-17"])
check("R invalid previous / next -> V-17", r_crafted(lambda t: t.replace("Next: [Backward Recursion](#kn-000000b2)", "Next: [Smoothing](#kn-000000b3)")), ["V-17"])
check("R missing Project Home back link -> V-17", r_crafted(lambda t: t.replace("\n\n[↑ Project Home](#project-home)\n<!-- SITL:DEBT:END", "\n<!-- SITL:DEBT:END")),
      ["V-17"])
rf.write_text(base_r.replace("Parent: [Estimation](#kn-000000a1)", "Parent: [Smoothing](#kn-000000b3)", 1), encoding="utf-8")
wrong = blocks(vtext(pr))
found, res = vr.repair()
check("R V-17 repair rewrites only the wrong section", (found, res, vtext(pr) == base_r, [k for k in wrong if wrong[k] != blocks(base_r)[k]]),
      ([("V-17", "WARNING")], "REPAIRED", True, ["KN:KN-000000b1"]))
rf.write_text(base_r.replace("#### L1 — Simple Mental Model", "#### Knowledge Map", 1), encoding="utf-8")
check("R V-16 not repaired by the view", vr.repair()[1], "NOTHING")
old = base_r.replace("[Project Home](#project-home) → [Knowledge Map](#knowledge-map) → ", "").replace("\n\n[↑ Project Home](#project-home)", "")
old = re.sub(r"\n\n(?:Parent|Reading order) .*(?=\n)|\n\nParent: .*(?=\n)", "", old)
old = re.sub(r"\n\n<!-- SITL:JOURNEY:START -->.*<!-- SITL:JOURNEY:END -->", "", old, flags=re.S)
rf.write_text(old, encoding="utf-8")
old_found = vr.integrity(vtext(pr))
check("R pre-VIS-02 view (no JOURNEY) -> V-01, V-08, V-17; repair == rebuild", (old_found, vr.repair()[1], vtext(pr) == base_r),
      ([("V-01", "WARNING"), ("V-08", "WARNING"), ("V-17", "WARNING")], "REPAIRED", True))
# legacy view without DEBT (HSMM shape): zero OPEN debt, repair inserts the structural DEBT destination
legacy = re.sub(r"\n\n<!-- SITL:DEBT:START -->.*<!-- SITL:DEBT:END -->", "", old, flags=re.S)
rf.write_text(legacy, encoding="utf-8")
lg_found, lg_broken = vr.integrity(vtext(pr)), RB.metrics(vtext(pr), (pr.root / GRAPH_F).read_text(encoding="utf-8"), SKILL)["links_broken"]
lg_res = vr.repair()[1]
lg = vtext(pr)
check("R legacy view without DEBT / JOURNEY, zero OPEN debt -> V-01, V-08, V-17; 2 broken links",
      ("SITL:DEBT" in legacy, [d for d in vr.sources()["debts"] if d["debt_status"] == "OPEN"], lg_found, lg_broken),
      (False, [], [("V-01", "WARNING"), ("V-08", "WARNING"), ("V-17", "WARNING")], 2))
check("R legacy repair inserts DEBT (Yok. + back link); links_broken 0; clean; == rebuild",
      (lg_res, blocks(lg)["DEBT"].splitlines()[1:-1], RB.metrics(lg, (pr.root / GRAPH_F).read_text(encoding="utf-8"), SKILL)["links_broken"],
       vr.integrity(lg), lg == base_r),
      ("REPAIRED", ["## Open Learning Debt", "", "Yok.", "", "[↑ Project Home](#project-home)"], 0, [], True))
rf.write_text(base_r, encoding="utf-8")
# empty Learning state
pr0 = project("pr0", steps=1)
vr0 = View(P, pr0.root)
sync(pr0, vr0)
r0 = blocks(vtext(pr0))
check("R empty Learning: Project Home lists Yok., no KN section", ("**Learning** — technical learning. Human Sync ≠ learned.\n\n- Yok." in r0["INDEX"],
      [k for k in r0 if k.startswith("KN:")]), (True, []))
check("R empty Learning: map and debt still navigable; clean", (r0["MAP"].splitlines()[-2], vr0.broken_link_keys(vtext(pr0), View.spans(vtext(pr0))),
      vr0.integrity(vtext(pr0))), ("[↑ Project Home](#project-home)", [], []))

# Test S - block-structured Full ULA CONTENT.md (09 §6.2, HSMM shape) survives VIS-02 migration
BLOCK_A = "docs/learning/passes/LP-20261031-01/ula/LE-LP-20261031-01-01/CONTENT.md"
BLOCK_CONTENT = """```yaml
event_id: LE-LP-20261031-01-01
artifact: CONTENT
artifact_status: COMPLETE
updated_at: 2026-10-31
```

# ULA Learning Content — Explicit-Duration HSMM

<!-- builder note -->

# L0 — Harita

```text
B1 Neden → B2 Döngü
```

# B1 — Neden Gerekli

**Orientation.** Parent: L0. Next: B2.

## L1 — Simple Explanation

HMM süreyi geometrik kabul eder.

## L2 — Mechanism

### Mechanism Map

Kalma kararı ayrı bir dağılımdan gelir.

## L3 — Theory

Geometrik süre hafızasızdır.

## L4 — Math / Formalism

$$P(d) = p(1-p)^{d-1}$$

**Transition.** Şimdi döngüye bakalım.

---

# LOCAL MAP — B2 Üretim Döngüsü

```text
B2.1 Başlangıç
   ↓
B2.2 Süre
```

# B2 — Üretim Döngüsü

**Orientation.** Parent: L0. Previous: B1.

## L1 — Simple Explanation

Model önce rejim, sonra süre seçer.

## L2 — Mechanism

1. Rejim seç.
2. Süre çek.

## L3 — Theory

`A`'nın köşegeni sıfırdır.

## L4 — NO L4 REQUIRED

Bu blok bir döngü tarifidir.

**Transition.** Event 02 çıkarımı sorar.

---

# Retrieval Check

1. Kalma kararı nerede?

# R — Reference

- GENERAL THEORY: explicit-duration HSMM.

# Learning Integrity Check

internal audit text
"""
ps = project("ps", steps=1)
vs = View(P, ps.root)
sync(ps, vs)
light(ps, LIGHT_A, "x", L_LIGHT)
ps.write(BLOCK_A, BLOCK_CONTENT)
write_graph(ps, 1, [node("KN-00000001", "HSMM Study", "ROOT"),
                    node("KN-000000c1", "Explicit-Duration HSMM", "CONCEPT", "KN-00000001", "L1; L2; L3; L4", arts=BLOCK_A, events="LE-LP-20261031-01-01"),
                    node("KN-000000c2", "Duration Lattice", "CONCEPT", "KN-00000001", "L1", arts=LIGHT_A)],
            [edge("KE-0001", "KN-000000c1", "NEXT", "KN-000000c2")])
vs.on_map_sync(None)
st = vtext(ps)
sb = blocks(st)["KN:KN-000000c1"]
part = lambda b, name: b.split(name, 1)[1].split("\n\n#### ", 1)[0].split("\n</details>", 1)[0]  # noqa: E731
check("S block-structured Full: parts in 09 §6.1 order", re.findall(r"^(?:#### |<summary><strong>)(.+?)(?:</strong></summary>)?$", sb, re.M),
      ["Where am I?", "L0 — Map", "L1 — Simple Mental Model", "L2 — Mechanism", "L3 — Theory", "L4 — Formalism", "Retrieval", "Reference", "Related Concepts"])
check("S L0 = L0 body + LOCAL MAP blocks", part(sb, "#### L0 — Map\n\n"),
      "```text\nB1 Neden → B2 Döngü\n```\n\n##### LOCAL MAP — B2 Üretim Döngüsü\n\n```text\nB2.1 Başlangıç\n   ↓\nB2.2 Süre\n```")
check("S level part gathers every block under ##### <block>", part(sb, "#### L1 — Simple Mental Model\n\n"),
      "##### B1 — Neden Gerekli\n\nHMM süreyi geometrik kabul eder.\n\n##### B2 — Üretim Döngüsü\n\nModel önce rejim, sonra süre seçer.")
check("S nested level sub-heading shifted under the block", "##### B1 — Neden Gerekli\n\n###### Mechanism Map\n\nKalma kararı" in sb, True)
check("S NO L4 REQUIRED kept as first body line", part(sb, "<summary><strong>L4 — Formalism</strong></summary>\n\n"),
      "###### B1 — Neden Gerekli\n\n$$P(d) = p(1-p)^{d-1}$$\n\n###### B2 — Üretim Döngüsü\n\nNO L4 REQUIRED.\n\nBu blok bir döngü tarifidir.\n")
check("S Retrieval Check and R — Reference projected", ("1. Kalma kararı nerede?" in sb, "- GENERAL THEORY: explicit-duration HSMM." in sb), (True, True))
check("S title, comments, Orientation, Transition, Integrity Check not shown",
      [w for w in ("ULA Learning Content", "builder note", "**Orientation.**", "**Transition.**", "internal audit text") if w in st], [])
src_lines = [l for blk in re.split(r"^# ", BLOCK_CONTENT, flags=re.M) if re.match(r"(B\d|L0|LOCAL MAP|Retrieval|R —)", blk)
             for l in blk.splitlines()[1:] if l.strip() and l != "---" and not l.startswith(("#", "**Orientation.**", "**Transition.**"))]
check("S every learning line of the artifact is in the KN section", [l for l in src_lines if l not in sb.splitlines()], [])
check("S block view clean; == rebuild", (vs.integrity(st), st == vs.rebuild()), ([], True))
# pre-VIS-02 view of the same project, also without DEBT: repair adds navigation, keeps the learning body
learn_body = lambda t: blocks(t)["KN:KN-000000c1"].split("\nLearning depth:", 1)[1]  # noqa: E731
s_old = st.replace("[Project Home](#project-home) → [Knowledge Map](#knowledge-map) → ", "").replace("\n\n[↑ Project Home](#project-home)", "")
s_old = re.sub(r"\n\n(?:Parent|Reading order) .*(?=\n)", "", s_old)
s_old = re.sub(r"\n\n<!-- SITL:JOURNEY:START -->.*<!-- SITL:JOURNEY:END -->", "", s_old, flags=re.S)
s_old = re.sub(r"\n\n<!-- SITL:DEBT:START -->.*<!-- SITL:DEBT:END -->", "", s_old, flags=re.S)
(ps.root / VIEW_F).write_text(s_old, encoding="utf-8")
s_found = [c for c, _ in vs.integrity(vtext(ps))]
s_res = vs.repair()[1]
s_new = vtext(ps)
check("S pre-VIS-02 Full ULA view -> V-01, V-08, V-17", s_found, ["V-01", "V-08", "V-17"])
check("S migration keeps the learning body, adds navigation; clean; == rebuild",
      (s_res, learn_body(s_new) == learn_body(s_old), "\nReading order — Next: [Duration Lattice](#kn-000000c2)\n" in s_new,
       RB.metrics(s_new, (ps.root / GRAPH_F).read_text(encoding="utf-8"), SKILL)["links_broken"], vs.integrity(s_new), s_new == st),
      ("REPAIRED", True, True, 0, [], True))

# Test T - Project Journey (09 §5.4; 07 V-08, V-18): Human Sync authority fixtures written with the sync model's own writers
CP = "git:000000000000"


def hs_authority(repo, units):
    """Human Sync state + records. units: (step id, label, sync_status, Purpose). Downstream Impact carries a claim the journey must not use."""
    rows = []
    for seq, (step, label, status, purpose) in enumerate(units, 1):
        wid = f"phase-doc:docs/{step.lower()}_report.md#{step}"
        rid = "-" if status == "UNSYNCED" else sm.record_id(wid)
        rows.append({c: "-" for c in SP.state_cols} | {"work_unit_id": wid, "seq": seq, "label": label, "sync_status": status, "record_id": rid,
                                                        "record_version": "-" if rid == "-" else 1, "checkpoint": CP, "synced_at": "2026-11-05"})
        if rid != "-":
            head = {"record_id": rid, "project_id": PRJ, "work_unit_id": wid, "record_version": 1, "checkpoint": CP, "updated_at": "2026-11-05"}
            repo.write(f"{sm.SYNC}/records/{rid}.md", sm.render_record(SP, head, {"Purpose": purpose, "Downstream Impact": f"{label} bu yüzden sonrakini başlattı."}))
    repo.write(sm.STATE_F, sm.render_state(SP, PRJ, rows))
    return rows


def journey(units, name):
    repo = project(name, steps=0)
    rows = hs_authority(repo, units)
    v = View(P, repo.root)
    text = v.rebuild()
    return repo, v, rows, blocks(text)["JOURNEY"], text


def purpose(label):
    return f"{label} problemi vardı → {label} işlemi yapıldı → {label} sonucu oluştu"


def nodes_of(block):
    return re.findall(r"^(  - Revision: |- )\[([^\]]+)\]\((#[^)]+)\) — (.+)$", block, re.M)


MARKS = re.compile(r" · (?:Needs refresh|\*\*Current position\*\*|revision of \S+)")
unbold = lambda s: s.replace("**", "")  # noqa: E731

seq_units = [(f"S{i}", f"Adım {i}", "SYNCED", purpose(f"S{i}")) for i in range(1, 4)]
pt, vt, rows_t, jt, tt = journey(seq_units, "pt")
check("T sequential: one top-level node per unit, seq order, no revision", [(p, l) for p, l, _, _ in nodes_of(jt)],
      [("- ", "Adım 1"), ("- ", "Adım 2"), ("- ", "Adım 3")])
check("T node = Problem → Action → **Result** from the record Purpose", nodes_of(jt)[0][3], "S1 problemi vardı → S1 işlemi yapıldı → **S1 sonucu oluştu**")
check("T every node links its own HS section; anchors exist", ([h for _, _, h, _ in nodes_of(jt)], [h[1:] in vm.anchors_of(tt) for _, _, h, _ in nodes_of(jt)]),
      ([f"#{r['record_id'].lower()}" for r in rows_t], [True] * 3))
check("T current position = 08 §3.2 position (exactly one, last seq)", [l for _, l, _, t in nodes_of(jt) if t.endswith("· **Current position**")], ["Adım 3"])
check("T Project Home links the journey; journey returns home; clean", ("[Project Journey](#project-journey)" in blocks(tt)["INDEX"],
      jt.splitlines()[-2], vt.integrity(tt), RB.metrics(tt, "", SKILL)["links_broken"]), (True, "[↑ Project Home](#project-home)", [], 0))
spec_fmt = (SKILL / "references" / "09_KNOWLEDGE_VIEW.md").read_text(encoding="utf-8").split("### 5.4 Project Journey", 1)[1].split("```text\n", 1)[1].split("```", 1)[0]
tpl_j = tpl.split("<!-- SITL:JOURNEY:START -->\n", 1)[1].split("<!-- SITL:JOURNEY:END -->", 1)[0]
check("T template JOURNEY block = 09 §5.4 format", tpl_j, spec_fmt)
check("T journey sits between MODEL and Human Sync (09 §3 order)", tt.index("SITL:MODEL:END") < tt.index("SITL:JOURNEY:START") < tt.index("## Human Sync"), True)

rev_units = [("Q1", "Kurulum (Q1)", "SYNCED", purpose("Q1")), ("Q2", "Test (Q2)", "SYNCED", purpose("Q2")),
             ("Q2-R1", "Test düzeltmesi (Q2-R1)", "SYNCED", purpose("Q2-R1")), ("Q3", "Ayırma (Q3)", "SYNCED", purpose("Q3"))]
_, _, _, jr_, _ = journey(rev_units, "ptr")
check("T revisions: R unit nested under its parent, visually distinct", [(p, l) for p, l, _, _ in nodes_of(jr_)],
      [("- ", "Kurulum (Q1)"), ("- ", "Test (Q2)"), ("  - Revision: ", "Test düzeltmesi (Q2-R1)"), ("- ", "Ayırma (Q3)")])

stale_units = [rev_units[0], ("Q2", "Test (Q2)", "STALE", purpose("Q2")), rev_units[2]]
_, _, _, js, _ = journey(stale_units, "pts")
check("T stale unit: Needs refresh marker, still once; current on last seq", [(l, t.split("** · ", 1)[1]) for _, l, _, t in nodes_of(js)
      if "** · " in t], [("Test (Q2)", "Needs refresh"), ("Test düzeltmesi (Q2-R1)", "**Current position**")])

gap_units = [("Q1", "Kurulum (Q1)", "SYNCED", purpose("Q1")), ("Q2-R1", "Test düzeltmesi (Q2-R1)", "SYNCED", purpose("Q2-R1")),
             ("Q3", "Ayırma (Q3)", "SYNCED", purpose("Q3"))]
_, _, _, jg, _ = journey(gap_units, "ptg")
check("T missing intermediate phase: no Q2 invented; orphan revision top-level, marked", ([(p, l) for p, l, _, _ in nodes_of(jg)],
      "Q2)" in jg.replace("Q2-R1)", ""), "· revision of Q2" in jg), ([("- ", "Kurulum (Q1)"), ("- ", "Test düzeltmesi (Q2-R1)"), ("- ", "Ayırma (Q3)")], False, True))
uns_units = [gap_units[0], ("Q2", "Test (Q2)", "UNSYNCED", "-"), gap_units[1], gap_units[2]]
_, _, _, ju, _ = journey(uns_units, "ptu")
check("T UNSYNCED parent: not a node, listed once as not yet synced; revision stays top-level",
      ([l for _, l, _, _ in nodes_of(ju)], re.findall(r"^Not yet synced: .*$", ju, re.M), "· revision of Q2" in ju),
      (["Kurulum (Q1)", "Test düzeltmesi (Q2-R1)", "Ayırma (Q3)"], ["Not yet synced: Test (Q2)"], True))

multi_units = [("Q4", "Pipeline (Q4)", "SYNCED", purpose("Q4")), ("Q5", "Rapor (Q5)", "SYNCED", purpose("Q5")),
               ("Q4-R1", "Komutlar (Q4-R1)", "SYNCED", purpose("Q4-R1")), ("Q4-R2", "Çıktılar (Q4-R2)", "SYNCED", purpose("Q4-R2")),
               ("Q4-R3", "Metrikler (Q4-R3)", "SYNCED", purpose("Q4-R3"))]
pm, vm_, rows_m, jm, tm = journey(multi_units, "ptm")
check("T multiple revisions share one parent (even after a later phase); seq order inside the group",
      [(p, l) for p, l, _, _ in nodes_of(jm)],
      [("- ", "Pipeline (Q4)"), ("  - Revision: ", "Komutlar (Q4-R1)"), ("  - Revision: ", "Çıktılar (Q4-R2)"), ("  - Revision: ", "Metrikler (Q4-R3)"),
       ("- ", "Rapor (Q5)")])
_, _, _, jrr, _ = journey([("Q4", "Pipeline (Q4)", "SYNCED", purpose("Q4")), ("Q4-R1-R1", "Ek düzeltme (Q4-R1-R1)", "SYNCED", purpose("Q4-R1-R1")),
                           ("Q4-R2", "Çıktılar (Q4-R2)", "SYNCED", purpose("Q4-R2")), ("Q4-R2-R1", "Çıktı düzeltmesi (Q4-R2-R1)", "SYNCED", purpose("Q4-R2-R1"))], "ptrr")
check("T revision of a revision groups under the root node, also when the middle unit is absent", [(p, l, "revision of" in t) for p, l, _, t in nodes_of(jrr)],
      [("- ", "Pipeline (Q4)", False), ("  - Revision: ", "Ek düzeltme (Q4-R1-R1)", False), ("  - Revision: ", "Çıktılar (Q4-R2)", False),
       ("  - Revision: ", "Çıktı düzeltmesi (Q4-R2-R1)", False)])
check("T current position may be a revision (highest seq)", [l for _, l, _, t in nodes_of(jm) if "**Current position**" in t], ["Metrikler (Q4-R3)"])
check("T every synced unit exactly once", sorted(l for _, l, _, _ in nodes_of(jm)), sorted(r["label"] for r in rows_m))
records = {f"#{r['record_id'].lower()}": (r["label"], purpose(r["work_unit_id"].split("#")[1])) for r in rows_m}
check("T no unsupported claim: each node = label + record Purpose + fixed markers only",
      [l for _, l, h, t in nodes_of(jm) if (l, unbold(MARKS.sub("", t))) != records[h]], [])
check("T Downstream Impact claim never enters the journey", "bu yüzden" in jm, False)
odd = [("X1", "Serbest (X1)", "SYNCED", "Tek cümlelik amaç, ok yok"), ("X2", "İki ok (X2)", "SYNCED", "a → b → c → d")]
_, _, _, jo, _ = journey(odd, "pto")
check("T Purpose not Problem → Action → Result: written as is, nothing bolded or split", [t.split(" · ")[0] for _, _, _, t in nodes_of(jo)],
      ["Tek cümlelik amaç, ok yok", "a → b → c → d"])
_, _, _, j0, t0 = journey([("Q1", "Kurulum (Q1)", "UNSYNCED", "-")], "pt0")
check("T no synced unit: Yok., Not yet synced, back link; clean", (j0.splitlines()[3:8], vm_.integrity(tm)),
      (["Yok.", "", "Not yet synced: Kurulum (Q1)", "", "[↑ Project Home](#project-home)"], []))
check("T 02 §4 step ID per source", [vm.step_id(w) for w in ("phase-doc:docs/a.md#18Q-4-R1", "jira:ABC-44", "user:cache-redesign")],
      ["18Q-4-R1", "ABC-44", "cache-redesign"])
# derived only from Human Sync: graph, queue and context changes leave the journey unchanged
vm_.f.write_text(tm, encoding="utf-8")
write_graph(pm, 1, [node("KN-00000001", "Root", "ROOT")], [])
pm.write(sm.CONTEXT_F, "# Project Sync Context\n\n## Current Position\n\n- Başka bir konum\n\n## Active Decisions\n\n- Uydurma karar\n")
t_ind = vm_.rebuild()
check("T journey independent of graph and context (MODEL changes, JOURNEY does not)",
      (blocks(t_ind)["JOURNEY"] == jm, blocks(t_ind)["MODEL"] != blocks(tm)["MODEL"], "Uydurma karar" in blocks(t_ind)["JOURNEY"]), (True, True, False))
# integrity: V-18 for wrong order / missing link / missing current; repair rewrites only JOURNEY
tm = vm_.rebuild()
vm_.f.write_text(tm, encoding="utf-8")


def t_crafted(fn):
    vm_.f.write_text(fn(tm), encoding="utf-8")
    try:
        return [c for c, _ in vm_.integrity(vm_.f.read_text(encoding="utf-8"))]
    finally:
        vm_.f.write_text(tm, encoding="utf-8")


lines_m = jm.splitlines()
swap = "\n".join(lines_m[:3] + [lines_m[7], lines_m[4], lines_m[5], lines_m[6], lines_m[3]] + lines_m[8:])
check("T wrong order -> V-18", t_crafted(lambda t: t.replace(jm, swap)), ["V-18"])
check("T revision ungrouped -> V-18", t_crafted(lambda t: t.replace("  - Revision: [Komutlar", "- [Komutlar")), ["V-18"])
check("T current position lost -> V-18", t_crafted(lambda t: t.replace(" · **Current position**", "")), ["V-18"])
check("T broken HS link in the journey -> V-01 + V-18", t_crafted(lambda t: t.replace(jm, jm.replace(f"]({nodes_of(jm)[0][2]})", "](#hs-0000beef)", 1))),
      ["V-01", "V-18"])
check("T invented journey line -> V-18", t_crafted(lambda t: t.replace("\n\n[↑ Project Home](#project-home)\n<!-- SITL:JOURNEY:END",
      "\n- [Pipeline (Q4)](#" + rows_m[0]["record_id"].lower() + ") — karar alındı\n\n[↑ Project Home](#project-home)\n<!-- SITL:JOURNEY:END")), ["V-18"])
vm_.f.write_text(tm.replace(jm, swap), encoding="utf-8")
pre_b = blocks(vm_.f.read_text(encoding="utf-8"))
t_res = vm_.repair()
post_b = blocks(vm_.f.read_text(encoding="utf-8"))
check("T V-18 repair rewrites only JOURNEY; == rebuild", (t_res, sorted(k for k in post_b if pre_b[k] != post_b[k]), vm_.f.read_text(encoding="utf-8") == tm),
      (([("V-18", "WARNING")], "REPAIRED"), ["JOURNEY"], True))
# legacy view (no JOURNEY): V-08, repair inserts it after MODEL
vm_.f.write_text(re.sub(r"\n\n<!-- SITL:JOURNEY:START -->.*<!-- SITL:JOURNEY:END -->", "", tm, flags=re.S), encoding="utf-8")
t_leg = [c for c, _ in vm_.integrity(vm_.f.read_text(encoding="utf-8"))]
check("T legacy view without JOURNEY -> V-01, V-08; repair inserts it; == rebuild", (t_leg, vm_.repair()[1], vm_.f.read_text(encoding="utf-8") == tm),
      (["V-01", "V-08"], "REPAIRED", True))
# journey failure never touches Human Sync authority; view pre-image restored
auth_t = {f.relative_to(pm.root).as_posix(): sha(f.read_bytes()) for f in sorted((pm.root / sm.SYNC).rglob("*")) if f.is_file()}
vm_.f.write_text(tm.replace(jm, swap), encoding="utf-8")
before_fail = vm_.f.read_bytes()
try:
    vm_.update(["JOURNEY", "INDEX"], fail_on="JOURNEY")
    t_err = None
except ViewBlocked as e:
    t_err = str(e)
check("T journey write failure: view pre-image restored, Human Sync state + records unchanged",
      (t_err, vm_.f.read_bytes() == before_fail, {f.relative_to(pm.root).as_posix(): sha(f.read_bytes()) for f in sorted((pm.root / sm.SYNC).rglob("*")) if f.is_file()} == auth_t),
      ("write error", True, True))
# real sync run: the 09 §8 trigger keeps the journey current incrementally
pj_ = project("ptj", steps=3)
vj_ = View(P, pj_.root)
sync(pj_, vj_)
jj = blocks(vtext(pj_))["JOURNEY"]
check("T real sync: journey written by the sync trigger; incremental == rebuild", ([l for _, l, _, _ in nodes_of(jj)], "**Current position**" in jj.splitlines()[5],
      vtext(pj_) == vj_.rebuild()), (["Step 1", "Step 2", "Step 3"], True, True))

report(RESULTS)
