# VIS-01 — Readability Baseline and Rendering Contract

**Tarih:** 2026-11-02
**Jira:** CLS-2 (Epic CLS-1)
**Branch:** `vis-01-readability-baseline`

## 1. Status

**PASS.** Commit yok; human review bekliyor.

- Rendering contract: `references/09_KNOWLEDGE_VIEW.md` §13.
- Baseline tool: `tests/view/readability.py`. Read-only, deterministik.
- View render davranışı değişmedi. Rebuild byte'ları aynıdır.
- HSMM pilot dosyaları değişmedi (§7).

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §13 Readability contract: §13.1 reader questions, §13.2 metrics + local map source tablosu, §13.3 navigation domains, §13.4 navigation order vs semantic dependency, §13.5 authority |
| `tests/view/readability.py` | Yeni. §13.2 metriklerini hesaplar |
| `tests/view/view_model.py` | Protocol §13 tablolarını, graph template `relation_type` listesini, L0 part adını ve `ula/CONTENT_BUILDER.md` §31 `LOCAL MAP` başlığını parse eder |
| `tests/view/run_tests.py` | Test Q: 18 check |
| `tests/mutation.py` | VIS-M1 – VIS-M4 |
| `distribution/manifest.json` | `09` sha256 güncellendi (`scripts/build-release.ps1`) |
| `docs/audit/VIS_01_READABILITY_BASELINE.md` | Bu rapor |

## 3. Reproduce

```text
uv run --no-project python tests/view/readability.py <project>/docs/learning/STAY_IN_THE_LOOP.md
```

Graph varsayılanı: `<view_dir>/maps/SEMANTIC_GRAPH.md`.

## 4. HSMM Pilot Baseline

Kaynak: `hsmm-claude-skill-test/docs/learning/STAY_IN_THE_LOOP.md` (`PRJ-b96dbc86`). İki çalıştırma byte-identical.

```text
lines_total: 2972
lines_visible: 1019
lines_collapsed: 843
details_blocks: 38
details_max_depth: 1
hs_units: 16
kn_concepts: 9
graph_nodes: 10
graph_edges: 12
graph_edges_by_relation: DEPENDS_ON=1; EVIDENCE_FOR=1; NEXT=6; USES=4
links_internal: 50
links_broken: 0
links_from_index: 26
links_from_hs: 0
links_from_kn: 24
kn_without_outgoing_link: 0
maps_global: 1
maps_local_structured: 14
maps_local_by_source: BLOCK=5; CONCEPT_L0=9; GRAPH=0
maps_local_mermaid: 0
global_map_edges_by_kind: HIERARCHY=9; NEXT=6
```

Satır dağılımı: 952 boş + 158 markup (comment, anchor, `<details>` tag) + 1019 görünür + 843 katlanmış = 2972.
Human Sync satır 116–1135, Learning satır 1136–2950.

`grep` ile bağımsız kontrol: `<details>` 38, link 50, global map `NEXT` 6 ve `-->` 9, `#### L0 — Map` 9, `##### LOCAL MAP —` 5. Hepsi eşleşir.

### 4.1 Local maps

| concept | `CONCEPT_L0` | `BLOCK` |
|---|---|---|
| KN-2b84f1d0 Explicit-Duration HSMM | 1 | 2: B2 Üretim Döngüsü, B4 Süre Aileleri |
| KN-e06a93c5 Duration Lattice Inference | 1 | 2: B3 Forward, B5 Backward ve Smoothing |
| KN-91d7c2ae Penalized EM with L2 Duration | 1 | 1: B3 L2 Süre Güncellemesi |
| Diğer 6 concept | 1 | 0 |

Hepsi ASCII / text map'tir. Mermaid local map yoktur (`maps_local_mermaid: 0`).

### 4.2 Düzeltme: local map ölçümü

İlk raporda `maps_local: 0` yazıyordu. Bu yanlıştı.

- Kök neden: metrik yalnız KN section içindeki Mermaid bloklarını sayıyordu. Bir render teknolojisini ölçüyordu, okuyucunun gördüğü map'i değil.
- Pilot'ta 14 local map vardır: 9 concept map (`L0 — Map`, artifact `# Local Map`) ve 5 block map (`LOCAL MAP — <block>`, `ula/CONTENT_BUILDER.md` §31).
- Yeni ölçüm map birimini sayar: `maps_local_structured`. Kaynak dağılımı `maps_local_by_source`'tadır. `maps_local_mermaid` yalnız render ölçüsüdür.
- §13.2 kuralı: var olan map'i text'ten Mermaid'e çevirmek `maps_local_structured`'ı değiştirmez. Sonraki VIS issue'ları `0 → N local map` iyileşmesi iddia edemez. Test Q bunu sınar.
- `maps_global` da artık render biçiminden bağımsızdır (MAP section'daki her code fence). Pilot değeri değişmedi: 1.

## 5. Observations (navigation, içerik değil)

| # | Gözlem | Kanıt | İlgili |
|---|---|---|---|
| 1 | Global map yalnız okuma sırasını gösterir. 6 semantic edge haritada yok. | `HIERARCHY=9; NEXT=6`, graph'ta `USES=4; DEPENDS_ON=1; EVIDENCE_FOR=1` | RQ-5, RQ-6, VIS-04 |
| 2 | Related Concepts `NEXT`'i `USES` / `DEPENDS_ON` ile aynı listede, aynı biçimde gösterir. | KN-91d7c2ae Related Concepts | §13.4, VIS-04 |
| 3 | Her concept bir L0 concept map'i taşır; 3 Full concept ayrıca 5 block map taşır. Graph tabanlı local map yoktur: hiyerarşi tek seviyelidir (ROOT section almaz, hiçbir concept 3 child'a ulaşmaz). Local map'ler concept içi yapıyı gösterir, concept'ler arası ilişkiyi göstermez. | `maps_local_by_source: BLOCK=5; CONCEPT_L0=9; GRAPH=0` | RQ-1, RQ-5, VIS-05 |
| 4 | Human Sync section'ları hiç link taşımaz: concept, önceki unit veya index'e dönüş yok. | `links_from_hs: 0` | RQ-4, RQ-7, VIS-02, VIS-03 |
| 5 | Index dışında Knowledge Map veya Quick Index'e dönüş linki yok. | `#knowledge-map` / `#quick-index` linki INDEX dışında 0 | RQ-1, VIS-02 |
| 6 | Breadcrumb'ın kökü link değildir (ROOT section almaz). Tüm concept'ler aynı tek seviyeli breadcrumb'ı taşır. | Satır 1144, 1599, 2004 | RQ-1, VIS-02 |
| 7 | Önceki / sonraki concept navigation'ı yalnız Related Concepts içindeki `NEXT` satırıdır. | KN-91d7c2ae | RQ-7, VIS-02 |
| 8 | Varsayılan görünür yüzey 1019 satırdır. Nesting yalnız 1 seviye. | `lines_visible`, `details_max_depth` | VIS-08 |
| 9 | Pilot'taki global map biçimi reference model'in render'ından farklıdır: label her edge satırında tekrar eder. Rebuild byte'ları farklı olur. | MAP section | VIS-04 (bilgi) |

Gözlemler düzeltilmedi. VIS-01 kapsamı ölçüm ve sözleşmedir.

## 6. Mutations

| id | Bozulan kural | Yakalayan |
|---|---|---|
| VIS-M1 | §13.4 `NEXT` semantic dependency sayılır | Q contract: relation class / NEXT |
| VIS-M2 | §13.5 Markdown view AUTHORITATIVE olur | Q contract: only DERIVED layer |
| VIS-M3 | §13.2 `links_broken` metriği düşer | Q tool = contract metrics |
| VIS-M4 | §6.2 artifact local map projekte edilmez: gerçek local map'ler view'dan düşer | Q local map check'leri (5 FAIL, crash yok) + Test D |

## 7. Authority

- Pilot `docs/learning/` altındaki 62 dosyanın SHA-256'sı çalışma öncesi ve sonrası aynıdır.
- Contract view'ı yalnız DERIVED tanımlar (§13.5). Test Q ve VIS-M2 bunu korur.

## 8. Tests

| suite | sonuç |
|---|---|
| phase3 | 24/24 |
| phase4 | 46/46 |
| phase5 | 74/74 |
| phase6 | 83/83 |
| phase7 | 163/163 |
| integration | 141/141 |
| static | 33/33 |
| isolation | 32/32 |
| sync | 107/107 |
| view | 191/191 (Test Q dahil) |
| distribution | 108/108 |
| **toplam** | **1002/1002** |

Mutation: 55/55 CAUGHT (VIS-M1 – VIS-M4 dahil). `RESULT: PASS`.

Manifest: `09` değiştiği için `distribution/manifest.json` `scripts/build-release.ps1` ile yeniden üretildi. `main`'e göre diff yalnız `references/09_KNOWLEDGE_VIEW.md` sha256 satırıdır (`31ef323d…` → `99176351…`).
