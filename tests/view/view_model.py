"""Reference model of 09_KNOWLEDGE_VIEW: one derived human-facing knowledge file per project.

Rules (authority rules table, structure order, marker grammar, HS mapping, status lines, KN parts and artifact mapping,
collapsed parts, retrieval plan, sync-only write scope, 07 §V checks) are parsed from the skill files.
Sources are the authoritative machine files of a temporary project (sync state + records, graph, ULA artifacts, queue §B).
Every source or view read goes through Reader.log so tests can assert what was (not) read.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sync"))
import sync_model as sm  # noqa: E402

VIEW_F = "docs/learning/STAY_IN_THE_LOOP.md"
GRAPH_F = "docs/learning/maps/SEMANTIC_GRAPH.md"
QUEUE_F = "docs/learning/state/LEARNING_QUEUE.md"
TICK = re.compile(r"`([^`]+)`")
MARK = re.compile(r"^<!-- SITL:(INDEX|MODEL|MAP|DEBT|HS:HS-[0-9a-f]{8}|KN:KN-[0-9a-f]{8}):(START|END)((?: [a-z]+=\S+)*) -->$")
HEAD_MARK = re.compile(r"^<!-- SITL:VIEW project_id=(\S+) -->$")
HEADING = re.compile(r"^(#{1,6}) (.*)$")
TITLE = "# Stay in the Loop — Project Knowledge"
NOTE = "> Derived human-facing view. Authority: `docs/learning/` state. Elle düzenleme. Rules: `09_KNOWLEDGE_VIEW`."
FIXED = {"knowledge-map", "open-learning-debt"}
TERM = re.compile(r'^"(.+?)"\s*↔\s*(.+)$')
SYMBOL = re.compile(r"(?<![\w-])(?:[A-Z]{1,5}-[A-Z0-9]{1,6}|[A-Z]\([A-Za-z]\)|[B-HJ-Z])(?![\w(-])")


def undefined_symbols(human):
    """09 §5.2: project symbols whose first occurrence in the HUMAN layer has no plain meaning attached."""
    known, bad, fence = set(), [], False
    for line in human.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        for m in SYMBOL.finditer(line):
            sym = m.group(0)
            if sym in known or (fence and len(sym) == 1):
                continue
            before, after = line[: m.start()], line[m.end():]
            inline = before.endswith("(") and after.startswith(")") and re.search(r"\w", before[:-1])
            dashed = before.endswith(" — ") and re.search(r"\w", before[:-3])
            if inline or dashed or re.match(r"\s*=\s*[a-zçğıöşü]", after):
                known.add(sym)
            elif sym not in bad:
                bad.append(sym)
    return bad


def cells(block):
    return [r for t in sm.tables(block) for r in t]


class Protocol:
    def __init__(self, skill: Path):
        p = (skill / "references" / "09_KNOWLEDGE_VIEW.md").read_text(encoding="utf-8")
        auth = sm.tables(sm.section(p, "## 1. Authority boundary"))
        self.rules = {r[0]: r[1] for r in auth[0]}
        self.path = self.rules["view_path"].strip("`")
        self.collapsed = [x.strip() for x in self.rules["collapsed"].split(";")]
        structure = sm.tables(sm.section(p, "## 3. Structure"))[0]
        self.order = [TICK.findall(r[1])[0] for r in structure]
        self.model_heading = next(TICK.findall(r[2])[0] for r in structure if "MODEL" in r[1])
        hs = sm.tables(sm.section(p, "### 5.1 Parts"))
        self.hs_map = [(r[0].strip("`"), r[1], r[2]) for r in hs[0]]
        self.status_line = {TICK.findall(r[0])[0]: TICK.findall(r[1])[0] for r in hs[1]}
        self.model_map = [tuple(r) for r in sm.tables(sm.section(p, "### 5.3 Project in 60 Seconds"))[0]]
        self.parts = [r[0] for r in sm.tables(sm.section(p, "### 6.1 Parts"))[0]]
        heading = lambda c: TICK.findall(c)[0].lstrip("# ") if "`" in c else None  # noqa: E731
        self.artifact_map = {r[0]: {"LIGHT": heading(r[1]), "FULL": heading(r[2])}
                             for r in sm.tables(sm.section(p, "### 6.2 Artifact mapping"))[0]}
        self.plan = {TICK.findall(r[0])[0]: (TICK.findall(r[1]), TICK.findall(r[2]))
                     for r in sm.tables(sm.section(p, "## 9. Section-level retrieval"))[0]}
        self.reader_questions = [r[1] for r in sm.tables(sm.section(p, "### 13.1 Reader questions"))[0]]
        metrics = sm.tables(sm.section(p, "### 13.2 Metrics"))
        self.metrics = [r[0].strip("`") for r in metrics[0]]
        self.local_sources = [r[0].strip("`") for r in metrics[1]]
        self.domains = {r[0].strip("`"): TICK.findall(r[1]) for r in sm.tables(sm.section(p, "### 13.3 Navigation domains"))[0]}
        self.edge_classes = {r[0].strip("`"): TICK.findall(r[1]) for r in sm.tables(sm.section(p, "### 13.4 Navigation order and semantic dependency"))[0]}
        self.layers = {r[0]: (r[1], TICK.findall(r[2])) for r in sm.tables(sm.section(p, "### 13.5 Authority"))[0]}
        self.l0_part = next(x for x in self.parts if x.startswith("L0 —"))
        self.where_part = self.parts[0]
        cb = (skill / "ula" / "CONTENT_BUILDER.md").read_text(encoding="utf-8").split("# 31. LOCAL MAP OUTPUT", 1)[1]
        self.block_map_prefix = re.search(r"^# (.+) — \[PARENT BLOCK\]$", cb, re.M).group(1)
        p08 = (skill / "references" / "08_HUMAN_SYNC_STATE.md").read_text(encoding="utf-8")
        row = {r[0].strip("`"): r[1] for r in sm.tables(sm.section(p08, "## 11. Sync-only run loop"))[0]}[Path(self.path).name]
        self.sync_only_kinds = ["HS", "KN", "MAP", "DEBT", "MODEL", "INDEX"] if row == "YES" else re.findall(r"\b(HS|KN|MAP|DEBT|MODEL|INDEX)\b", row)
        s07 = sm.section((skill / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8"), "## V. Knowledge View Integrity")
        self.checks = {r[0]: r[2] for r in sm.tables(s07)[0]}
        t = skill / "templates"
        tpl = (t / "KNOWLEDGE_VIEW_TEMPLATE.md").read_text(encoding="utf-8")
        hs_tpl = tpl.split(":START v=", 1)[1].split(":END", 1)[0]
        self.hs_sections = [h or b for h, b in re.findall(r"^(?:#### (.+)|\*\*(.+?:)\*\* )", hs_tpl, re.M) if b != "Status:"]
        model_tpl = tpl.split("<!-- SITL:MODEL:START -->", 1)[1].split("<!-- SITL:MODEL:END -->", 1)[0]
        self.model_sections = re.findall(r"^#### (.+)$", model_tpl, re.M)
        self.model_template_heading = re.search(r"^## (.+)$", model_tpl, re.M).group(0)
        g = (t / "SEMANTIC_GRAPH_TEMPLATE.md").read_text(encoding="utf-8")
        self.node_cols = sm.header(sm.section(g, "## Nodes"))
        self.edge_cols = sm.header(sm.section(g, "## Edges"))
        self.relation_types = next(TICK.findall(r[1]) for r in cells(sm.section(g, "## Field Reference")) if r[0] == "`relation_type`")
        self.debt_cols = sm.header(sm.section((t / "LEARNING_QUEUE_TEMPLATE.md").read_text(encoding="utf-8"), "## B. Knowledge Debt"))

    def int_rule(self, name):
        return int(self.rules[name])


# --- authoritative sources ------------------------------------------------------------

def render_graph(P, version, nodes, edges):
    def table(cols, rows):
        return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows])
    return (f"# Semantic Graph\n\n## Metadata\n\n```yaml\nschema_version: 1\ngraph_version: {version}\nlast_updated: 2026-10-28\n```\n\n"
            f"## Nodes\n\n{table(P.node_cols, nodes)}\n\n## Edges\n\n{table(P.edge_cols, edges)}\n")


def parse_graph(P, text):
    if not text:
        return 0, [], []
    version = int(re.search(r"^graph_version: (\d+)$", text, re.M).group(1))
    nodes = [dict(zip(P.node_cols, r)) for r in sm.tables(sm.section(text, "## Nodes"))[0]]
    edges = [dict(zip(P.edge_cols, r)) for r in sm.tables(sm.section(text, "## Edges"))[0]]
    return version, nodes, edges


def render_queue(P, debts):
    rows = "\n".join("| " + " | ".join(d[c] for c in P.debt_cols) + " |" for d in debts)
    return ("# Learning Queue\n\n## A. Deferred Work Units\n\n## B. Knowledge Debt\n\n| " + " | ".join(P.debt_cols) + " |\n|"
            + "---|" * len(P.debt_cols) + "\n" + rows + "\n")


def parse_queue(P, text):
    return [dict(zip(P.debt_cols, r)) for r in sm.tables(sm.section(text, "## B. Knowledge Debt"))[0]] if text else []


def depth_list(v):
    return [] if v in ("-", "") else [x.strip() for x in v.split(";")]


# --- markdown helpers --------------------------------------------------------------------

def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def shift(text, delta):
    """Move every heading outside code fences down by delta levels (max 6)."""
    out, fence = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
        m = None if fence else HEADING.match(line)
        out.append(f"{'#' * min(6, len(m.group(1)) + delta)} {m.group(2)}" if m else line)
    return "\n".join(out)


def parts_of(text, level):
    """Split a document into {heading: body} at the given heading level (fence-aware)."""
    out, cur, fence = {}, None, False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
        m = None if fence else HEADING.match(line)
        if m and len(m.group(1)) <= level:
            cur = m.group(2).strip() if len(m.group(1)) == level else None
            if cur is not None:
                out[cur] = []
            continue
        if cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def mermaid_id(node_id):
    return node_id.replace("-", "_")


def label(P, node):
    name = node["canonical_name"].replace('"', "'")
    n = P.int_rule("map_label_max_chars")
    name = name if len(name) <= n else name[: n - 1] + "…"
    return f'{name}{" (DEBT)" if node["node_status"] == "DEBT" else ""} ({node["node_id"]})'


# --- reader ------------------------------------------------------------------------------

class Reader:
    def __init__(self):
        self.log = []

    def read(self, kind, key="-", lines=0):
        self.log.append((kind, key, lines))

    def kinds(self):
        return [k for k, _, _ in self.log]


class ViewBlocked(Exception):
    pass


# --- view engine ----------------------------------------------------------------------------

class View:
    """One active project root. Builds, patches, reads and checks docs/learning/STAY_IN_THE_LOOP.md."""

    def __init__(self, P, root: Path):
        self.P, self.root = P, root
        self.f = root / P.path

    def read_file(self, rel):
        f = self.root / rel
        return f.read_text(encoding="utf-8") if f.exists() else None

    # sources (state first; no lesson content)
    def sources(self):
        cfg = dict(sm.KV.findall(self.read_file(sm.CONFIG_F) or ""))
        st = self.read_file(sm.STATE_F)
        rows = []
        if st:
            cols = sm.header(sm.section(st, "## Work Units"))
            rows = [dict(zip(cols, r)) for r in sm.tables(sm.section(st, "## Work Units"))[0]]
            for r in rows:
                r["seq"] = int(r["seq"])
        gv, nodes, edges = parse_graph(self.P, self.read_file(GRAPH_F))
        return {"project_id": cfg.get("project_id", "UNCONFIGURED"), "rows": sorted(rows, key=lambda r: r["seq"]),
                "graph_version": gv, "nodes": nodes, "edges": edges, "debts": parse_queue(self.P, self.read_file(QUEUE_F))}

    # eligibility
    def hs_rows(self, S):
        return [r for r in S["rows"] if r["sync_status"] in self.P.status_line and r["record_id"] != "-"]

    def kn_nodes(self, S):
        return [n for n in S["nodes"] if n["node_status"] == "ACTIVE" and depth_list(n["available_depth"])]

    def has_content(self, S):
        return bool(self.hs_rows(S) or self.kn_nodes(S) or [d for d in S["debts"] if d["debt_status"] == "OPEN"])

    # --- renderers ---
    def terms(self, body):
        """09 §5.1: '"plain" ↔ Term' -> 'plain (Term)' or 'plain — Term(...)'; first key_terms_max shown, the rest in More Terms."""
        pairs, other = [], []
        for line in body.splitlines():
            m = TERM.match(line.strip())
            if m:
                term = m.group(2).strip()
                pairs.append(f"{m.group(1)} — {term}" if "(" in term else f"{m.group(1)} ({term})")
            elif line.strip() and not line.startswith("```") and line.strip() != "Yok.":
                other.append(line.strip())
        n = self.P.int_rule("key_terms_max")
        return " · ".join(pairs[:n]), "\n".join(f"- {x}" for x in pairs[n:] + other)

    def render_hs(self, S, row, rd):
        """09 §5: HUMAN parts open, TRACE parts in one collapsed block. Every record line appears once."""
        rd.read("RECORD", row["record_id"])
        sec = parts_of(self.read_file(f"{sm.SYNC}/records/{row['record_id']}.md"), 2)
        head = dict(sm.KV.findall(sec.get("Header", "")))
        rid = row["record_id"]
        key_terms, more = self.terms(sec.get("Technical Translation", ""))
        special = {"Anahtar kavramlar:": key_terms, "More Terms": more,
                   "Record:": f"`{rid}` v{head['record_version']} · `{head['work_unit_id']}` · `{head['checkpoint']}`"}
        keep = {self.P.hs_map[0][0], "Record:"}
        layers = {"HUMAN": [], "TRACE": []}
        for view, src, layer in self.P.hs_map:
            body = special[view] if view in special else shift(sec.get(src, "Yok."), 2).strip()
            if body in ("", "Yok.") and view not in keep:
                continue
            layers[layer].append(f"**{view}** {body}" if view.endswith(":") else f"#### {view}\n\n{body}")
        out = [f"<!-- SITL:HS:{rid}:START v={row['record_version']} -->", f'<a id="{rid.lower()}"></a>', f"### {row['label']}", "",
               f"**Status:** {self.P.status_line[row['sync_status']]}"]
        out += [x for p in layers["HUMAN"] for x in ("", p)]
        out += ["", "<details>", "<summary><strong>Technical Trace</strong></summary>"] + [x for p in layers["TRACE"] for x in ("", p)] + ["", "</details>"]
        return "\n".join(out + [f"<!-- SITL:HS:{rid}:END -->"])

    def artifact_parts(self, node, rd):
        """Per part: body from the last COMPLETE source artifact that carries it (09 §6.2)."""
        found = {}
        for path in [p.strip() for p in node["source_artifacts"].split(";") if p.strip() not in ("", "-")]:
            rd.read("ARTIFACT", path)
            text = self.read_file(path) or ""
            mode = "FULL" if Path(path).name == "CONTENT.md" else "LIGHT"
            done = re.search(r"^(?:status|artifact_status): COMPLETE\b", text, re.M)
            if not done:
                continue
            level = 1 if mode == "FULL" else 2
            src = parts_of(text, level)
            for part, m in self.P.artifact_map.items():
                body = re.sub(r"\n*-{3,}\s*$", "", strip_comments(src.get(m[mode] or "\0", "")).strip())
                if body:
                    found[part] = (shift(body, 4 - level), path)
        return found

    def chain(self, S, node):
        by = {n["node_id"]: n for n in S["nodes"]}
        out, cur, seen = [], node, set()
        while cur and cur["node_id"] not in seen:
            seen.add(cur["node_id"])
            out.insert(0, cur)
            cur = by.get(cur["parent_id"])
        return out

    def link(self, S, n):
        eligible = {x["node_id"] for x in self.kn_nodes(S)}
        tag = " (DEBT)" if n["node_status"] == "DEBT" else ""
        return f"[{n['canonical_name']}](#{n['node_id'].lower()}){tag}" if n["node_id"] in eligible else n["canonical_name"] + tag

    def children(self, S, node):
        return [n for n in S["nodes"] if n["parent_id"] == node["node_id"] and n["node_status"] != "SUPERSEDED"]

    def local_map(self, S, node):
        kids = self.children(S, node)
        if len(kids) < self.P.int_rule("local_map_min_children"):
            return None
        by = {n["node_id"]: n for n in S["nodes"]}
        lines = ["```mermaid", "flowchart LR", f'    {mermaid_id(node["node_id"])}["{label(self.P, node)}"]']
        lines += [f'    {mermaid_id(node["node_id"])} --> {mermaid_id(k["node_id"])}["{label(self.P, k)}"]' for k in kids]
        for e in S["edges"]:
            if e["source_node_id"] == node["node_id"] and e["relation_type"] not in ("PART_OF", "NEXT") and e["target_node_id"] in by:
                t = by[e["target_node_id"]]
                lines.append(f'    {mermaid_id(node["node_id"])} -- {e["relation_type"]} --> {mermaid_id(t["node_id"])}["{label(self.P, t)}"]')
        return "\n".join(lines + ["```"])

    def render_kn(self, S, node, rd):
        by = {n["node_id"]: n for n in S["nodes"]}
        nid, depth = node["node_id"], depth_list(node["available_depth"])
        parts = self.artifact_parts(node, rd)
        crumbs = [self.link(S, n) if n is not node else f"**{n['canonical_name']}**" for n in self.chain(S, node)]
        out = [f"<!-- SITL:KN:{nid}:START depth={';'.join(depth)} -->", f'<a id="{nid.lower()}"></a>', f"### {nid} — {node['canonical_name']}",
               "", "#### Where am I?", "", " → ".join(crumbs)]
        also = [by[e["target_node_id"]] for e in S["edges"] if e["source_node_id"] == nid and e["relation_type"] == "PART_OF" and e["target_node_id"] in by]
        if also:
            out += ["", "Also part of: " + ", ".join(self.link(S, n) for n in also)]
        events = node["source_event_ids"].replace(" ", "")
        paths = sorted({p for _, p in parts.values()})
        out += ["", f"Learning depth: {' · '.join(depth)} · Source: `{events}`" + "".join(f" (`{p}`)" for p in paths)]
        lm = self.local_map(S, node)
        if lm:
            out += ["", lm]
        for part in self.P.parts:
            level = re.match(r"(L\d) —", part)
            if part not in parts or (level and level.group(1) != "L0" and level.group(1) not in depth):
                continue
            body = parts[part][0]
            short = level.group(1) if level else part
            if short in self.P.collapsed:
                out += ["", "<details>", f"<summary><strong>{part}</strong></summary>", "", shift(body, 1), "", "</details>"]
            else:
                out += ["", f"#### {part}", "", body]
        rel = []
        for e in S["edges"]:
            if e["relation_type"] == "PART_OF":
                continue
            if e["source_node_id"] == nid and e["target_node_id"] in by:
                rel.append(f"- {e['relation_type']} → {self.link(S, by[e['target_node_id']])}")
            elif e["target_node_id"] == nid and e["source_node_id"] in by:
                rel.append(f"- {self.link(S, by[e['source_node_id']])} → {e['relation_type']} → **{node['canonical_name']}**")
        if rel:
            out += ["", "#### Related Concepts", ""] + rel
        return "\n".join(out + [f"<!-- SITL:KN:{nid}:END -->"])

    def render_map(self, S):
        roots = [n for n in S["nodes"] if n["node_status"] != "SUPERSEDED" and (n["node_type"] == "ROOT" or n["parent_id"] == "-")]
        shown, frontier = {}, [(r, 0) for r in roots]
        while frontier:
            n, d = frontier.pop(0)
            if n["node_id"] in shown:
                continue
            shown[n["node_id"]] = n
            if d < self.P.int_rule("global_map_depth"):
                frontier += [(k, d + 1) for k in self.children(S, n)]
        lines = ["<!-- SITL:MAP:START -->", "## Knowledge Map", ""]
        if not shown:
            return "\n".join(lines + ["Yok.", "<!-- SITL:MAP:END -->"])
        lines += ["```mermaid", "flowchart LR"]
        for n in shown.values():
            lines.append(f'    {mermaid_id(n["node_id"])}["{label(self.P, n)}"]')
        for n in shown.values():
            if n["parent_id"] in shown:
                lines.append(f'    {mermaid_id(n["parent_id"])} --> {mermaid_id(n["node_id"])}')
        for e in S["edges"]:
            if e["relation_type"] == "NEXT" and e["source_node_id"] in shown and e["target_node_id"] in shown:
                lines.append(f'    {mermaid_id(e["source_node_id"])} -. NEXT .-> {mermaid_id(e["target_node_id"])}')
        return "\n".join(lines + ["```", "<!-- SITL:MAP:END -->"])

    def render_index(self, S):
        hs = [f"- [{r['label']}](#{r['record_id'].lower()})" + (" · needs refresh" if r["sync_status"] == "STALE" else "") for r in self.hs_rows(S)]
        kn = [f"- [{n['node_id']} — {n['canonical_name']}](#{n['node_id'].lower()}) · {' '.join(depth_list(n['available_depth']))}"
              for n in self.kn_nodes(S)]
        return "\n".join(["<!-- SITL:INDEX:START -->", "## Quick Index", "", "**Human Sync** — project comprehension", ""] + (hs or ["- Yok."])
                         + ["", "**Learning** — technical learning. Human Sync ≠ learned.", ""] + (kn or ["- Yok."])
                         + ["", "[Knowledge Map](#knowledge-map) · [Open Learning Debt](#open-learning-debt)", "<!-- SITL:INDEX:END -->"])

    def render_model(self, rd):
        """09 §5.3: Project in 60 Seconds; snapshot collapsed; remembered items are not repeated in the snapshot."""
        rd.read("CONTEXT")
        ctx = parts_of(self.read_file(sm.CONTEXT_F) or "", 2)
        text = {k: shift(v, 2).strip() for k, v in ctx.items()}
        remember = next(src for _, src, _ in self.P.model_map if ";" in src)
        pooled = [k.strip() for k in remember.split(";")]
        pool = [(k, l) for k in pooled for l in text.get(k, "").splitlines() if l.startswith("- ")]
        used = pool[: self.P.int_rule("remember_max")]
        layers = {"HUMAN": [], "SNAPSHOT": []}
        for view, src, layer in self.P.model_map:
            if src == remember:
                body = "\n".join(l for _, l in used)
            elif src in pooled:
                body = "\n".join(l for l in text.get(src, "").splitlines() if (src, l) not in used).strip()
            else:
                body = text.get(src, "")
            if body:
                layers[layer].append(f"#### {view}\n\n{body}")
        out = [x for p in layers["HUMAN"] for x in ("", p)]
        if layers["SNAPSHOT"]:
            out += ["", "<details>", "<summary><strong>Technical Project Snapshot</strong></summary>"] + \
                   [x for p in layers["SNAPSHOT"] for x in ("", p)] + ["", "</details>"]
        return "\n".join(["<!-- SITL:MODEL:START -->", self.P.model_heading] + (out or ["", "Yok."]) + ["<!-- SITL:MODEL:END -->"])

    def render_debt(self, S):
        rows = [f"- `{d['debt_id']}` — {d['concept']} · {d['priority']} · {d['work_unit_ids']}" for d in S["debts"] if d["debt_status"] == "OPEN"]
        return "\n".join(["<!-- SITL:DEBT:START -->", "## Open Learning Debt", ""] + (rows or ["Yok."]) + ["<!-- SITL:DEBT:END -->"])

    def block(self, S, key, rd):
        if key.startswith("HS:"):
            return self.render_hs(S, next(r for r in S["rows"] if r["record_id"] == key[3:]), rd)
        if key.startswith("KN:"):
            return self.render_kn(S, next(n for n in S["nodes"] if n["node_id"] == key[3:]), rd)
        return {"MAP": lambda: self.render_map(S), "INDEX": lambda: self.render_index(S), "DEBT": lambda: self.render_debt(S),
                "MODEL": lambda: self.render_model(rd)}[key]()

    def rebuild(self, rd=None):
        """09 §12: deterministic full build from authoritative state."""
        rd, S = rd or Reader(), self.sources()
        rd.read("WHOLE_REBUILD")
        hs = [self.render_hs(S, r, rd) for r in self.hs_rows(S)]
        kn = [self.render_kn(S, n, rd) for n in self.kn_nodes(S)]
        parts = [TITLE, "", f"<!-- SITL:VIEW project_id={S['project_id']} -->", "", NOTE, "", self.render_index(S), "", self.render_model(rd), "",
                 "## Human Sync", ""] + [x for b in hs for x in (b, "")] + ["## Learning", ""] + [x for b in kn for x in (b, "")] + \
                [self.render_map(S), "", self.render_debt(S)]
        return "\n".join(parts) + "\n"

    # --- markers / sections ---
    @staticmethod
    def markers(text):
        """Return ([(kind_key, START|END, attrs, line_no)], unknown_lines)."""
        out, unknown = [], []
        for i, line in enumerate(text.splitlines()):
            if "SITL:" not in line:
                continue
            m = MARK.match(line)
            if m:
                out.append((m.group(1), m.group(2), dict(a.split("=", 1) for a in m.group(3).split()), i))
            elif not HEAD_MARK.match(line):
                unknown.append(i)
        return out, unknown

    @classmethod
    def spans(cls, text):
        """{key: (start_line, end_line, attrs)}; raises ViewBlocked('V-03'/'V-02') on structural errors."""
        ms, unknown = cls.markers(text)
        if unknown:
            raise ViewBlocked("V-03")
        out, open_ = {}, None
        for key, kind, attrs, i in ms:
            if kind == "START":
                if open_:
                    raise ViewBlocked("V-03")
                if key in out:
                    raise ViewBlocked("V-02")
                open_ = (key, i, attrs)
            else:
                if not open_ or open_[0] != key:
                    raise ViewBlocked("V-03")
                out[key] = (open_[1], i, open_[2])
                open_ = None
        if open_:
            raise ViewBlocked("V-03")
        return out

    @staticmethod
    def lines_of(text, span):
        return "\n".join(text.splitlines()[span[0]: span[1] + 1])

    def insertion_line(self, text, key, spans, S):
        """09 §3 insertion point (line index) for a new HS / KN block."""
        lines = text.splitlines()
        if key.startswith("HS:"):
            order = [f"HS:{r['record_id']}" for r in self.hs_rows(S)]
            stop = lines.index("## Learning")
        else:
            order = [f"KN:{n['node_id']}" for n in self.kn_nodes(S)]
            stop = spans["MAP"][0]
        later = [spans[k][0] for k in order[order.index(key) + 1:] if k in spans]
        return min(later) if later else stop

    def patch(self, text, key, block, S):
        spans = self.spans(text)
        lines = text.splitlines()
        if key in spans:
            s, e, _ = spans[key]
            lines[s: e + 1] = block.splitlines()
        else:
            at = self.insertion_line(text, key, spans, S)
            lines[at:at] = block.splitlines() + [""]
        return "\n".join(lines) + "\n"

    # --- write (09 §10) ---
    def order_keys(self, keys):
        rank = {"HS": 0, "KN": 0, "MAP": 1, "DEBT": 2, "MODEL": 3, "INDEX": 4}
        return sorted(set(keys), key=lambda k: (rank[k.split(":")[0]], k))

    def update(self, keys, rd=None, sync_only=False, fail_on=None):
        """Section-level update. Returns 'NO_CONTENT' | 'CREATED' | 'UPDATED' | 'UNCHANGED'; raises ViewBlocked."""
        rd, S = rd or Reader(), self.sources()
        if S["project_id"] == "UNCONFIGURED" or not self.read_file(sm.CONFIG_F):
            return "NO_CONTENT"
        if not self.f.exists():
            if not self.has_content(S):
                return "NO_CONTENT"
            new = self.rebuild(rd)
            self.fail_check(self.integrity(new, S, structural_only=True))
            self.write_seq([new], 0 if fail_on else None)
            return "CREATED"
        if self.P.rules["write_mode"] != "SECTION_PATCH":
            new = self.rebuild(rd)
            self.fail_check(self.integrity(new, S, structural_only=True))
            self.write_seq([new])
            return "UPDATED"
        rd.read("MARKERS")
        cur = self.f.read_text(encoding="utf-8")
        self.fail_check(self.integrity(cur, S, structural_only=True))
        spans, steps, text = self.spans(cur), [], cur
        if sync_only:
            keys = [k for k in keys if k.split(":")[0] in self.P.sync_only_kinds]
        for key in self.order_keys(keys):
            exists = key in spans
            if exists:
                rd.read("SECTION", key, spans[key][1] - spans[key][0] + 1)
            if key.startswith("HS:") and not any(r["record_id"] == key[3:] for r in self.hs_rows(S)):
                continue
            if key.startswith("KN:") and not any(n["node_id"] == key[3:] for n in self.kn_nodes(S)):
                continue
            block = self.block(S, key, rd)
            if exists and self.lines_of(text, self.spans(text)[key]) == block:
                continue
            text = self.patch(text, key, block, S)
            steps.append((key, text))
        if not steps:
            return "UNCHANGED"
        found = self.integrity(text, S, structural_only=True)
        if sync_only:
            before, after = self.spans(cur), self.spans(text)
            if any(self.lines_of(cur, before[k]) != self.lines_of(text, after[k]) for k in before
                   if k.split(":")[0] in ("KN", "MAP", "DEBT") and k in after):
                found.append(("V-13", self.P.checks.get("V-13")))
        self.fail_check(found)
        order = [k for k, _ in steps]
        self.write_seq([t for _, t in steps], order.index(fail_on) if fail_on in order else None)
        return "UPDATED"

    def write_seq(self, texts, fail_at=None):
        """One write per block in 09 §10 order; any error restores the pre-image."""
        pre = self.f.read_bytes() if self.f.exists() else None
        try:
            for i, t in enumerate(texts):
                if i == fail_at:
                    self.f.parent.mkdir(parents=True, exist_ok=True)
                    self.f.write_bytes(t.encode("utf-8")[: len(t) // 2])
                    raise OSError("injected write failure")
                self.f.parent.mkdir(parents=True, exist_ok=True)
                self.f.write_bytes(t.encode("utf-8"))
        except OSError:
            if pre is None:
                self.f.unlink(missing_ok=True)
            else:
                self.f.write_bytes(pre)
            raise ViewBlocked("write error")

    def fail_check(self, found):
        fails = [c for c, sev in found if sev == "FAIL"]
        if fails:
            raise ViewBlocked(",".join(sorted(set(fails))))

    # --- triggers (09 §8) ---
    def on_sync(self, pre_rows, rd=None, sync_only=True, fail_on=None):
        post = {r["record_id"]: r for r in self.sources()["rows"] if r["record_id"] != "-"}
        pre = {r["record_id"]: (r["sync_status"], r["record_version"]) for r in pre_rows if r["record_id"] != "-"}
        keys = [f"HS:{k}" for k, r in post.items() if pre.get(k) != (r["sync_status"], r["record_version"])]
        return self.update(keys + ["MODEL", "INDEX"], rd, sync_only=sync_only, fail_on=fail_on)

    def node_sig(self, S, n):
        by = {x["node_id"]: x for x in S["nodes"]}
        rel = [(e["source_node_id"], e["relation_type"], e["target_node_id"], by.get(e["source_node_id"], {}).get("canonical_name"),
                by.get(e["target_node_id"], {}).get("canonical_name")) for e in S["edges"] if n["node_id"] in (e["source_node_id"], e["target_node_id"])]
        kids = [(k["node_id"], k["canonical_name"], k["node_status"]) for k in self.children(S, n)]
        crumbs = [(c["node_id"], c["canonical_name"], c["node_status"], c["available_depth"]) for c in self.chain(S, n)]
        return (n["canonical_name"], n["available_depth"], n["node_status"], n["source_artifacts"], n["source_event_ids"], rel, kids, crumbs)

    def on_map_sync(self, pre_graph_text, rd=None, fail_on=None):
        """Changed KN sections only: compares graph rows before and after the map sync write (graph only)."""
        S = self.sources()
        pv, pn, pe = parse_graph(self.P, pre_graph_text)
        P_ = dict(S, nodes=pn, edges=pe)
        old = {n["node_id"]: self.node_sig(P_, n) for n in pn}
        keys = [f"KN:{n['node_id']}" for n in self.kn_nodes(S) if old.get(n["node_id"]) != self.node_sig(S, n)]
        return self.update(keys + ["MAP", "INDEX"], rd, fail_on=fail_on)

    def on_debt(self, rd=None):
        return self.update(["DEBT"], rd)

    # --- retrieval (09 §9) ---
    def retrieve(self, request, target=None, deps=False, rd=None):
        """Execute the 09 §9 plan for one request. Returns {key: text}."""
        rd = rd or Reader()
        reads, _ = self.P.plan[request]
        text = self.f.read_text(encoding="utf-8")
        S, out = self.sources(), {}
        spans = None
        for code in reads:
            if code == "WHOLE_VIEW":
                rd.read("WHOLE_VIEW", "-", len(text.splitlines()))
                out["*"] = text
            elif code == "MARKERS":
                spans = self.spans(text)
                rd.read("MARKERS", "-", len(self.markers(text)[0]))
            elif code in ("INDEX", "TARGET") or (code == "DEP_SECTIONS" and deps):
                spans = spans or self.spans(text)
                keys = ["INDEX"] if code == "INDEX" else [target] if code == "TARGET" else self.dep_keys(S, target)
                for k in keys:
                    if k in spans:
                        rd.read("SECTION", k, spans[k][1] - spans[k][0] + 1)
                        out[k] = self.lines_of(text, spans[k])
        return out

    def dep_keys(self, S, target):
        if target.startswith("HS:"):
            row = next(r for r in S["rows"] if r["record_id"] == target[3:])
            ids = {r["work_unit_id"]: r["record_id"] for r in S["rows"]}
            return [f"HS:{ids[w]}" for w in sm.split(row["depends_on"]) if ids.get(w, "-") != "-"]
        return [f"KN:{e['target_node_id']}" for e in S["edges"] if e["source_node_id"] == target[3:] and e["relation_type"] in ("REQUIRES", "DEPENDS_ON")]

    # --- 07 §V ---
    def integrity(self, text, S=None, structural_only=False):
        """Return sorted [(check_id, severity)] for the given view text (None = file missing)."""
        S = S or self.sources()
        sev = self.P.checks
        found = []

        def add(cid):
            if cid in sev:
                found.append((cid, sev[cid]))

        if text is None:
            if self.has_content(S):
                add("V-08")
            return sorted(set(found))
        head = next((HEAD_MARK.match(l) for l in text.splitlines() if HEAD_MARK.match(l)), None)
        if not head:
            add("V-12")
            return sorted(set(found))
        if head.group(1) != S["project_id"]:
            add("V-05")
        try:
            spans = self.spans(text)
        except ViewBlocked as e:
            add(str(e))
            return sorted(set(found))
        rows = {r["record_id"]: r for r in S["rows"] if r["record_id"] != "-"}
        nodes = {n["node_id"]: n for n in S["nodes"]}
        anchors = set(FIXED)
        for key, span in spans.items():
            body = self.lines_of(text, span)
            kind, kid = (key.split(":") + [None])[:2]
            if body.count("```") % 2 or body.count("<details>") != body.count("</details>"):
                add("V-09")
            heads, fence = [], False
            for line in body.splitlines():
                if line.startswith("```"):
                    fence = not fence
                m = None if fence else HEADING.match(line)
                if m:
                    heads.append((len(m.group(1)), m.group(2)))
            own = 3 if kind in ("HS", "KN") else 2
            top = [h for h in heads if h[0] <= 3]
            if len(top) != 1 or top[0][0] != own:
                add("V-10")
            if kind in ("HS", "KN"):
                a = re.search(r'<a id="([^"]+)"></a>', body)
                anchors.add(a.group(1) if a else "")
                if kind == "KN":
                    title = top[0][1] if top else ""
                    if not a or a.group(1) != kid.lower() or not title.startswith(f"{kid} — ") or kid not in nodes:
                        add("V-04")
                        continue
                    n = nodes[kid]
                    if title != f"{kid} — {n['canonical_name']}" or span[2].get("depth", "") != ";".join(depth_list(n["available_depth"])):
                        add("V-07")
                    levels = set(re.findall(r"^(?:#### |<summary><strong>)(L[1-4]) —", body, re.M))
                    if n["node_status"] != "ACTIVE" or not depth_list(n["available_depth"]) or levels - set(depth_list(n["available_depth"])):
                        add("V-11")
                else:
                    r = rows.get(kid)
                    if r is None:
                        add("V-05")
                        continue
                    if r["sync_status"] not in self.P.status_line:
                        add("V-11")
                        continue
                    shown = re.search(r"^\*\*Status:\*\* (.+)$", body, re.M)
                    if not shown or shown.group(1) != self.P.status_line[r["sync_status"]]:
                        add("V-06")
                    if span[2].get("v") != r["record_version"]:
                        add("V-07")
                    human = body.split(shown.group(0), 1)[1].split("<details>", 1)[0] if shown else ""
                    if undefined_symbols(human):
                        add("V-15")
            if kind == "MAP":
                for nid, lab in re.findall(r'(KN_[0-9a-f]{8})\["([^"]*)"\]', body):
                    n = nodes.get(nid.replace("_", "-"))
                    if not n or len(lab.split(" (KN-")[0].replace(" (DEBT)", "")) > self.P.int_rule("map_label_max_chars"):
                        add("V-14")
        if not structural_only:
            if "INDEX" in spans:
                for link in re.findall(r"\]\(#([^)]+)\)", self.lines_of(text, spans["INDEX"])):
                    if link not in anchors:
                        add("V-01")
            want = {f"HS:{r['record_id']}" for r in self.hs_rows(S)} | {f"KN:{n['node_id']}" for n in self.kn_nodes(S)}
            if want - set(spans):
                add("V-08")
        else:
            found = [(c, s) for c, s in found if s == "FAIL"]
        return sorted(set(found))

    def repair(self, rd=None):
        """07 §L.3 derived repair for §V WARNINGs: only the sections the checks point to."""
        text = self.f.read_text(encoding="utf-8") if self.f.exists() else None
        S = self.sources()
        found = self.integrity(text, S)
        if any(s == "FAIL" for _, s in found):
            return found, "FAIL"
        if not [c for c, _ in found if c != "V-15"]:
            return found, "NOTHING"
        if text is None:
            self.update([], rd)
            return found, "REBUILT"
        spans = self.spans(text)
        want = [f"HS:{r['record_id']}" for r in self.hs_rows(S)] + [f"KN:{n['node_id']}" for n in self.kn_nodes(S)]
        keys = [k for k in want if k not in spans]
        for k in want:
            if k in spans:
                cur = self.lines_of(text, spans[k])
                if k.startswith("HS:"):
                    r = next(x for x in S["rows"] if x["record_id"] == k[3:])
                    if spans[k][2].get("v") != r["record_version"] or f"**Status:** {self.P.status_line[r['sync_status']]}\n" not in cur:
                        keys.append(k)
                else:
                    n = next(x for x in S["nodes"] if x["node_id"] == k[3:])
                    if spans[k][2].get("depth") != ";".join(depth_list(n["available_depth"])) or f"### {n['node_id']} — {n['canonical_name']}\n" not in cur + "\n":
                        keys.append(k)
        self.update(keys + ["MAP", "INDEX"], rd)
        return found, "REPAIRED"


# --- static Mermaid check (GitHub-safe subset used by the view and README) ---------------

NODE = r'[A-Za-z][A-Za-z0-9_]*(?:\["[^"]*"\]|\{"[^"]*"\})?'
EDGE = r'(?:-->(?:\|"[^"|]*"\|)?|-- [A-Z_]+ -->|-\. [A-Z_]+ \.->)'
MERMAID_LINE = re.compile(rf"^    {NODE}(?: {EDGE} {NODE})?$")


def mermaid_blocks(text):
    return re.findall(r"^```mermaid\n(.*?)^```$", text, re.M | re.S)


def mermaid_errors(block):
    """Static check: header, line grammar, every referenced node id defined with a label once."""
    lines = block.rstrip("\n").splitlines()
    errs = [] if lines and re.match(r"^flowchart (LR|TD)$", lines[0]) else ["header"]
    labelled, used = {}, set()
    for line in lines[1:]:
        if not line.strip():
            continue
        if not MERMAID_LINE.match(line):
            errs.append(f"syntax: {line.strip()}")
            continue
        for nid, lab in re.findall(r'([A-Za-z][A-Za-z0-9_]*)(\["[^"]*"\]|\{"[^"]*"\})?', re.sub(r'\|"[^"]*"\||-- [A-Z_]+ -->|-\. [A-Z_]+ \.->|-->', " ", line)):
            used.add(nid)
            if lab:
                if nid in labelled and labelled[nid] != lab:
                    errs.append(f"relabel: {nid}")
                labelled[nid] = lab
    errs += [f"undefined: {u}" for u in sorted(used - set(labelled))]
    return errs
