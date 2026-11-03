"""Readability baseline for a derived STAY_IN_THE_LOOP.md (09 §13).

Usage: readability.py <view_file> [<graph_file>]
Default graph: <view_dir>/maps/SEMANTIC_GRAPH.md. Read-only. Prints one 'metric: value' line per 09 §13.2 metric.
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import DEFAULT_SKILL  # noqa: E402
import view_model as vm  # noqa: E402

LINK = re.compile(r"\]\(#([^)\s]+)\)")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
SUMMARY = re.compile(r"^<summary><strong>(.+)</strong></summary>$")
HIDDEN = re.compile(r"^\s*(?:<!--.*-->|<a id=\"[^\"]+\"></a>|</?details>)\s*$")


def slug(heading):
    """GitHub heading anchor: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(text):
    """Explicit <a id> anchors plus GitHub heading slugs (fence-aware, duplicates get -n)."""
    out, seen, fence = set(ANCHOR.findall(text)), Counter(), False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
        m = None if fence else vm.HEADING.match(line)
        if m:
            s = slug(m.group(2))
            out.add(s if not seen[s] else f"{s}-{seen[s]}")
            seen[s] += 1
    return out


def visibility(text):
    """(visible, collapsed, details_blocks, max_depth): non-blank rendered lines outside / inside <details>."""
    visible = collapsed = blocks = depth = top = 0
    for line in text.splitlines():
        s = line.strip()
        if s == "<details>":
            blocks, depth = blocks + 1, depth + 1
            top = max(top, depth)
        elif s == "</details>":
            depth -= 1
        elif not s or HIDDEN.match(line):
            continue
        elif depth == 0 or s.startswith("<summary>") and depth == 1:
            visible += 1
        else:
            collapsed += 1
    return visible, collapsed, blocks, top


def map_edges(block):
    """Rendered Mermaid edges by kind: hierarchy (-->), NEXT (-. NEXT .->), relation (-- REL -->)."""
    kinds = Counter()
    for body in vm.mermaid_blocks(block):
        for line in body.splitlines():
            if " -. NEXT .-> " in line:
                kinds["NEXT"] += 1
            elif re.search(r" -- [A-Z_]+ --> ", line):
                kinds["RELATION"] += 1
            elif " --> " in line:
                kinds["HIERARCHY"] += 1
    return kinds


def local_maps(block, P):
    """Local maps in one KN section, counted per map unit, not per rendering (09 §13.2).

    Returns (Counter by source, Mermaid block count). Sources: CONCEPT_L0 (09 §6.1 L0 part),
    BLOCK (`ula/CONTENT_BUILDER.md` §31 heading), GRAPH (Mermaid local map in the Where am I? part, 09 §7.2).
    """
    kinds, part, fence, mermaid = Counter(), None, False, 0
    for line in block.splitlines():
        if line.startswith("```"):
            if not fence and line.strip() == "```mermaid":
                mermaid += 1
                if part == P.where_part:
                    kinds["GRAPH"] += 1
            fence = not fence
            continue
        m = None if fence else vm.HEADING.match(line) or SUMMARY.match(line)
        if not m:
            continue
        title = m.group(m.lastindex).strip()
        if m.re is SUMMARY or len(m.group(1)) == 4:
            part = title
        if title == P.l0_part:
            kinds["CONCEPT_L0"] += 1
        elif title.startswith(f"{P.block_map_prefix} — "):
            kinds["BLOCK"] += 1
    return kinds, mermaid


def fmt(counter):
    return "; ".join(f"{k}={counter[k]}" for k in sorted(counter)) or "-"


def metrics(view_text, graph_text, skill=DEFAULT_SKILL):
    """Ordered {metric: value} for one view (09 §13.2). Deterministic for the same inputs."""
    spans = vm.View.spans(view_text)
    sec = {k: vm.View.lines_of(view_text, s) for k, s in spans.items()}
    kn = [k for k in spans if k.startswith("KN:")]
    P = vm.Protocol(skill)
    _, nodes, edges = vm.parse_graph(P, graph_text)
    links = LINK.findall(view_text)
    known = anchors(view_text)
    visible, collapsed, blocks, depth = visibility(view_text)
    local, local_mermaid = Counter(), 0
    for k in kn:
        kinds, mermaid = local_maps(sec[k], P)
        local, local_mermaid = local + kinds, local_mermaid + mermaid
    fences = sum(line.startswith("```") for line in sec.get("MAP", "").splitlines()) // 2
    return {
        "lines_total": len(view_text.splitlines()),
        "lines_visible": visible,
        "lines_collapsed": collapsed,
        "details_blocks": blocks,
        "details_max_depth": depth,
        "hs_units": sum(k.startswith("HS:") for k in spans),
        "kn_concepts": len(kn),
        "graph_nodes": len(nodes),
        "graph_edges": len(edges),
        "graph_edges_by_relation": fmt(Counter(e["relation_type"] for e in edges)),
        "links_internal": len(links),
        "links_broken": sum(t not in known for t in links),
        "links_from_index": len(LINK.findall(sec.get("INDEX", ""))),
        "links_from_hs": sum(len(LINK.findall(b)) for k, b in sec.items() if k.startswith("HS:")),
        "links_from_kn": sum(len(LINK.findall(sec[k])) for k in kn),
        "kn_without_outgoing_link": sum(not LINK.findall(sec[k]) for k in kn),
        "maps_global": fences,
        "maps_local_structured": sum(local.values()),
        "maps_local_by_source": "; ".join(f"{k}={local[k]}" for k in sorted(P.local_sources)),
        "maps_local_mermaid": local_mermaid,
        "global_map_edges_by_kind": fmt(map_edges(sec.get("MAP", ""))),
    }


def main():
    view = Path(sys.argv[1])
    graph = Path(sys.argv[2]) if len(sys.argv) > 2 else view.parent / "maps" / "SEMANTIC_GRAPH.md"
    text = view.read_text(encoding="utf-8")
    gtext = graph.read_text(encoding="utf-8") if graph.exists() else ""
    for k, v in metrics(text, gtext).items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
