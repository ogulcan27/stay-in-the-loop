# VIS-04 — Semantic Knowledge Map

**Tarih:** 2026-11-06
**Jira:** CLS-5 (Epic CLS-1)
**Branch:** `vis-04-semantic-knowledge-map`
**Bağımlılık:** VIS-01 (CLS-2), VIS-02 (CLS-3); VIS-03 (CLS-4, `main` `21f319b`)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor.

- Soru: Hangi kavram neyi kullanır, neye bağlıdır, neye kanıt verir?
- Global Knowledge Map artık graph'ın semantic edge'lerini çizer. Önceden yalnız `parent_id` ve `NEXT` vardı (VIS-01 baseline gözlem 1).
- Kaynak yalnız Semantic Graph authority'si (`maps/SEMANTIC_GRAPH.md`). Graph, Human Sync, ULA, L0–L4 ve persistence değişmez.
- Değişen view section'ı yalnız `MAP`.

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §1 `global_map_max_nodes`; §7.1 node kapsamı, edge biçim tablosu, map altı satır tablosu, link kuralı; §7.3 Orphan concepts; Authoritative Source `05` §4.1, §5 |
| `references/07_INTEGRITY_CHECKS.md` | V-19 orphan concept (rapor); V-20 MAP graph render'ı ile uyuşmuyor |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | `MAP` bloğu: edge biçimleri ve altı satır |
| `tests/view/view_model.py` | `map_nodes`, `map_scope`, `orphans`, `map_edge_rows`, `map_name`, `reading_chains`, `render_map`; V-19, V-20; repair V-19'u yalnız raporlar |
| `tests/view/readability.py` | `global_map_edges_by_kind`: `-- PART_OF -->` `HIERARCHY` sayılır (`09` §13.4) |
| `tests/view/run_tests.py` | Test U (45 check); I, K, Q, R, S beklentileri (§6) |
| `tests/mutation.py` | VIS-M25 – VIS-M32 |
| `README.md` | View paragrafı: semantic knowledge map |
| `distribution/manifest.json` | 07, 09, template sha256 |
| `docs/audit/VIS_04_SEMANTIC_KNOWLEDGE_MAP.md` | Bu rapor |

## 3. Rendering

Edge biçimi (`09` §7.1):

| edge | kaynak | Mermaid | legend |
|---|---|---|---|
| hierarchy | primary `parent_id` | `-->` | primary parent |
| also part of | `PART_OF` | `-- PART_OF -->` | also part of |
| semantic | `SEMANTIC` (§13.4) | `-- <RELATION> -->` | semantic relation, source → target |
| navigation | `NAVIGATION` (§13.4) | `-. <RELATION> .->` | reading order only, not a dependency |

Map altı, sırayla, boşsa yazılmaz: `Legend`, `Concepts`, `Deeper concepts`, `Relationships`, `Reading order`, `Orphan concepts`, Project Home dönüşü.

HSMM (gerçek pilot kopyası), map altı:

```text
**Legend:** `-->` primary parent · `-- <RELATION> -->` semantic relation, source → target · `-. <RELATION> .->` reading order only, not a dependency

**Concepts:** Flexible-Duration HSMM Study (root) · [Explicit-Duration HSMM](#kn-2b84f1d0) · … · [Total Variation Metric Identity](#kn-d2f8716c)

**Relationships:**

- [Penalized EM with L2 Duration](#kn-91d7c2ae) — USES → [Duration Lattice Inference](#kn-e06a93c5)
- …
- [ADF and KPSS Stationarity Diagnostics](#kn-63d9e0b8) — EVIDENCE_FOR → [Explicit-Duration HSMM](#kn-2b84f1d0)

**Reading order** (navigation only, not a dependency):

- [Explicit-Duration HSMM](#kn-2b84f1d0) → [Duration Lattice Inference](#kn-e06a93c5) → … → [Convergence and Regime Stability](#kn-a15c47f9)
```

## 4. Kararlar

| # | Karar | Gerekçe |
|---|---|---|
| D-1 | Relation adı stored token'dır (`05` §4.1, 12 token). `COMPARED_WITH` kullanılır. `COMPARES_WITH` ve `EVALUATED_BY` eklenmez. | Jira "where available"; vocabulary genişlemesi yok (CLS-5 yorum 10000). |
| D-2 | Üç çizgi biçimi: hierarchy `-->` (etiketsiz), semantic `-- REL -->` (düz, etiketli), navigation `-. REL .->` (noktalı). Secondary `PART_OF` etiketli düz çizgi, legend'da `also part of`. | Okuyucu ayrımı çizgi biçiminden ve etiketten görür. Biçimler VIS-02 local map ve mevcut Mermaid alt kümesiyle aynıdır (`mermaid_errors`). |
| D-3 | `NEXT` hiçbir zaman düz çizgiyle çizilmez ve `Relationships` listesine girmez. Ayrı `Reading order` satırında, "navigation only, not a dependency" etiketiyle durur. | AC "NEXT cannot silently become DEPENDS_ON"; `09` §13.4. |
| D-4 | `global_map_max_nodes` = 30. Aşılırsa derinlik 2 → 1. Derinlik 1 de aşıyorsa harita sırasıyla ilk 30 node çizilir (D-11, review revizyonu). | Spec'te genişlik sınırı yoktu. Değer bir review varsayılanıdır, ölçümle türetilmedi. HSMM 10 node. Test kuralı sınar, sayıyı değil; değer review'da onaylanmalı. |
| D-5 | Çizilmeyen her node `Deeper concepts` listesinde primary parent'ı altında link ile durur (D-12, review revizyonu). Local map ek zoom'dur. `Relationships` ve `Reading order` derinlikten bağımsızdır; çizilmeyen edge kaybolmaz. | AC "decomposed into global and local views"; node ve edge kaybı yok. |
| D-6 | Link hedefi mevcut KN section anchor'ıdır (`#kn-xxxxxxxx`). Mermaid node'u link taşımaz. `Concepts` satırı haritadaki her node'u harita sırasıyla listeler. Section'ı olmayan node link'siz: `(root)`, `(DEBT)`, `(no section)`. | AC "Every rendered node links to its Concept Home". Mermaid link'i GitHub'da güvenilir değil. Personal library Concept Home (`06` §8) ve VIS-05 kapsam dışı. |
| D-7 | Orphan: `ROOT` olmayan, `SUPERSEDED` olmayan, `parent_id` zinciri `ROOT`'a ulaşmayan node (`09` §7.3). Durumlar: unplaced, missing parent, superseded parent, hierarchy cycle, orphan ancestor. | Spec'te tanım yoktu. En yakın kavram `05` §5.1 unplaced. Derinlik veya edge sayısı orphan'ı belirlemez. |
| D-8 | Orphan view'da `Orphan concepts` satırında görünür, V-19 WARNING ile raporlanır. Repair düzeltmez. | Düzeltme graph authority'sindedir (`05` §5). |
| D-9 | V-20: MAP section'ı graph render'ından farklıysa WARNING, rebuild MAP. | Değiştirilmiş, ters, çift, uydurma veya hedefsiz edge'i yakalar (V-18 deseni). |
| D-10 | Cycle: combined hierarchy cycle (M-08, M-09) graph write'ta FAIL kalır; view'da `hierarchy cycle` orphan'ı. `DEPENDS_ON` cycle geçerlidir, çizilir, uyarı yok. | `05` §5.2. |

## 5. Scope dışı

- Yeni relation, graph authority değişikliği, model tarafından çıkarılmış edge.
- Human Sync, ULA, L0–L4, persistence.
- KN section içeriği. Related Concepts `NEXT`'i hâlâ semantic relation'larla aynı listede gösterir (VIS-01 baseline gözlem 2). Concept page işi CLS-6 / VIS-05 ile örtüşür; davranış korunur.
- Local map (§7.2) biçimi değişmez.
- Adaptive geometry, HTML viewer, VIS-05+.

## 6. Mevcut test beklentileri

| Test | Önce | Sonra | Neden |
|---|---|---|---|
| I long label | `long_name not in imap` (MAP section) | Aynı kontrol Mermaid bloğunda | Tam ad artık `Concepts` / `Relationships` link metninde. Mermaid label hâlâ kısaltılır. |
| I no USES | Global map `USES` çizmez | `-- USES -->` çizilir, `NEXT` noktalı kalır | VIS-04'ün amacı; eski kural sequence-heavy map'ti. |
| K | 18 V check | 20 V check | V-19, V-20. |
| Q baseline | 273 / 118 / 29 link; `HIERARCHY=3; NEXT=1` | 286 / 125 / 35 link; `RELATION=1` eklendi | MAP'e USES edge (+1), Legend, Concepts, Relationships (1), Reading order (1): +13 satır, +7 görünür, +6 link (2 Concepts, 2 Relationships, 2 Reading order). |
| R pre-VIS-02 view | V-01, V-08, V-17 | + V-20 | Fixture her section'dan Project Home dönüşünü siler; MAP render'dan farklı. Repair == rebuild kalır. |
| R legacy (no DEBT / JOURNEY) | V-01, V-08, V-17 | + V-20 | Aynı sebep. |
| S pre-VIS-02 Full ULA | V-01, V-08, V-17 | + V-20 | Aynı sebep. |

Başka beklenti değişmedi.

## 7. CLS-5 test plan → Test U

| CLS-5 | Test U check |
|---|---|
| simple chain | U chain: semantic edge'ler düz + etiketli, yön, sıra; NEXT noktalı; hierarchy; Mermaid; Relationships; Reading order tek zincir |
| shared dependency | U shared dependency |
| multiple parents | U multiple parents: primary `-->`, secondary `-- PART_OF -->`, legend, breadcrumb değişmez |
| evidence relationship | U evidence: yön kanıt → iddia |
| comparison relationship | U comparison: `COMPARED_WITH`; `COMPARES_WITH` / `EVALUATED_BY` yok; vocabulary 12 token |
| orphan node | U orphans (5 durum), derin node orphan değil, V-19 rapor, repair NOTHING |
| cycle where prohibited | U prohibited hierarchy cycle → `hierarchy cycle`; U `DEPENDS_ON` cycle allowed; phase6 M-08 |
| large graph requiring decomposition | U large graph: 41 node → derinlik 1, 35 deeper, gizli edge Relationships / Reading order'da, local map ile erişim; sınır 30 / 32 |
| Mutation: swap edge type | U swapped edge type → V-20; VIS-M26 |
| Mutation: remove target | U map edge to a node not in the graph → V-20; U edge target superseded → V-20, map sync temizler; U missing endpoint not drawn |
| Mutation: duplicate edge | U duplicate edge line → V-20; U duplicate graph edge çizilir bir kez |
| Mutation: render NEXT as dependency | U NEXT rendered as dependency → V-20; VIS-M25 |

Ek: section'ı olmayan node'lar, link çözümü, provenance, determinism, incremental == rebuild, ters yön, uydurma relationship satırı, template sırası.

Mutation'lar: VIS-M25 NEXT bağımlılık biçiminde · VIS-M26 edge türü değişti · VIS-M27 semantic satırı yok · VIS-M28 V-20 yok · VIS-M29 V-19 yok · VIS-M30 superseded parent orphan değil · VIS-M31 büyük graph bölünmez · VIS-M32 Relationships satırı yok.

## 8. HSMM review kopyası (repair, pilot dosyaları değişmez)

| Ölçü | VIS-03 | VIS-04 |
|---|---|---|
| Section | 30 | 30 (29 byte-identical; değişen yalnız `MAP`) |
| HS / KN identical | — | 16/16 · 9/9 (KN satır 1827 → 1827) |
| INDEX, MODEL, JOURNEY, DEBT | — | identical |
| `global_map_edges_by_kind` | `HIERARCHY=9; NEXT=6` | `HIERARCHY=9; NEXT=6; RELATION=6` |
| `links_internal` | 120 | 148 (MAP 29 link, çözülmeyen 0) |
| `lines_total` / `lines_visible` | 3083 / 1085 | 3106 / 1102 |
| Orphan | — | 0 |
| Integrity after repair | V-15 | V-15 (VIS-02 öncesi) |

12 graph edge'inin 12'si stored relation ve yönle çizilir. 6 semantic edge (USES 4, DEPENDS_ON 1, EVIDENCE_FOR 1) VIS-03 map'inde yoktu. Pilot 62 dosya byte-identical.

## 9. Açık gözlemler (scope dışı)

- O-1: `global_map_max_nodes` = 30 review varsayılanıdır (D-4).
- O-2: `on_map_sync` yeni `SUPERSEDED` olan node'un KN section'ını kaldırmaz; rebuild kaldırır (V-11). VIS-02 öncesi davranış. Test U yalnız MAP'i rebuild ile karşılaştırır.
- O-3: Related Concepts `NEXT`'i semantic relation'larla birlikte listeler (VIS-01 gözlem 2). VIS-05 ile örtüşür.
- O-4: Pilot header blockquote satırı rebuild'den farklıdır (section dışı). `main`'de de aynı.
- O-5: (Review revizyonunda kapandı, R1 / D-11.) İlk pakette derinlik 1 `global_map_max_nodes`'u aşarsa map sınırsız genişti.
- O-6: `Deeper concepts`, `Concepts`, `Relationships` gibi metin satırıdır; çok büyük graph'ta uzar. Mermaid diyagramı sınırlıdır, metin listesi graph boyutuyla büyür.

## 10. Tests

İlk paket koşusu: 2026-11-06 18:19:58 – 19:09:49, 1123/1123, 83/83. Review revizyonu sonrası tek tam koşu: `uv run --no-project python tests/run_all.py`, 2026-11-07 14:56:15 – 15:51:05, exit 0, `RESULT: PASS`. Test edilen dosyaların hepsi koşu başlangıcından önce son kez değişti; sonra yalnız bu rapor (`docs/audit/` taranmaz) güncellendi.

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
| view | 321/321 (VIS-03: 267; + Test U 54: ilk paket 45, revizyon 9) |
| distribution | 108/108 |
| **toplam** | **1132/1132** (VIS-03: 1078; ilk VIS-04 paketi: 1123) |
| mutation | **84/84 CAUGHT**, 0 MISSED (VIS-03: 75; + VIS-M25 – M33) |

## 11. Review revizyonu (R1, R2)

**Tarih:** 2026-11-07. İlk paket (`VIS_04_REVIEW.zip`, `01a0d727…`) review'dan geçti; iki büyük-graph açığı için revizyon istendi. Kabul edilen semantic edge render'ı, provenance ve HSMM sonucu değişmez.

### 11.1 Reproduction (ilk paketin `view_model.py`'si ile)

| Durum | Fixture | Gözlenen |
|---|---|---|
| R1 | `ROOT` + 35 doğrudan child | Global Mermaid 36 node çizer; sınır 30. Derinlik zaten 1, azaltılamaz. Test U "depth 1 still too wide" bu davranışı 32 node ile kabul ediyordu. |
| R2 | 6 domain, fan-out 12 / 12 / 2 / 1 / 0 / 3, iki derin node; derinlik 1 | 32 gizli node. Local map yalnız ≥ 3 child'lı 3 section'da. 5 gizli node map'ten link / local map yoluyla erişilemez: `Domain 2` (2 child) ve `Domain 3` (1 child) altındakiler, derin iki node. Bunlardan biri section'sızdır ve hiçbir yerde adı geçmez. |

Kanıt: `R1_R2_REPRO_BEFORE.txt`, `R1_R2_RENDERS_BEFORE.md`.

### 11.2 Kararlar

| # | Karar | Gerekçe |
|---|---|---|
| D-11 | Derinlik 1'de de node sayısı `global_map_max_nodes`'u aşarsa harita sırasıyla ilk `global_map_max_nodes` node çizilir. Harita sırası: `ROOT`, unplaced node'lar, sonra `parent_id` child'ları seviye seviye, graph sırasıyla. | Sınırlı ve deterministik. Yeni node, gruplama veya "+N more" yer tutucusu uydurulmaz. Graph sırası graph authority'sinin sırasıdır; önem sıralaması yoktur (önem ölçüsü spec'te yok). Edge'i kesilen node'un edge'leri `Relationships` / `Reading order`'da kalır. |
| D-12 | `**Deeper concepts:**` satırı sayının yanında çizilmeyen her node'u primary parent'ı altında listeler: `- <parent> → <child> · <child>`, parent'lar harita sırasıyla. Ad biçimi `Concepts` ile aynı (link veya `(no section)` / `(DEBT)`). | En küçük çözüm: local map kuralı (`local_map_min_children`) ve KN section'lar değişmez. `parent_id` hiyerarşisi korunur. Section'sız node link almaz, adıyla görünür; anchor uydurulmaz. Liste D-11'de kesilen node'ları da kapsar. |

Değerlendirilip seçilmeyen: `local_map_min_children`'ı düşürmek (VIS-01/02 local map davranışı ve HSMM KN section'ları değişirdi; section'sız parent ve section'sız child yine kalırdı); gizli child'ı olan her section'a local map (KN section'ları değiştirir, Mermaid node'u link taşımaz, section'sız node'a yine yol yok).

Mimari karar gerekmedi: sınır, global / local ayrımı, graph authority ve `09` §7.2 local map kuralı korunur.

### 11.3 Değişiklikler

| Dosya | Değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §7.1 node cap kuralı, harita sırası, Deeper concepts satırı; §7.2 tek cümle (local map'i olmayan node'un gizli child'ları Deeper concepts'te) |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | Deeper concepts örneği |
| `tests/view/view_model.py` | `map_scope` ilk `global_map_max_nodes` node'u tutar; `deeper_groups`; `render_map` Deeper listesi |
| `tests/view/run_tests.py` | Test U +9 check; 3 beklenti değişti (§11.4) |
| `tests/mutation.py` | VIS-M33 Deeper concepts satırı silindi |
| `distribution/manifest.json` | 09 ve template sha256 |

### 11.4 Test beklentileri

| Test | Önce | Sonra | Neden |
|---|---|---|---|
| U depth-omitted node | `1 not drawn at map depth 2. Open a concept section to zoom in.` | `1 not drawn (map depth 2, at most 30 nodes), by primary parent:` + `- [Level Two] → [Level Three]` | D-12 biçimi; artık node'un kendisi de listede. |
| U large graph | `35 not drawn at map depth 1. …` | Yeni başlık; ayrı check: 5 domain satırı, her biri 7 topic | D-12. |
| U depth 1 still too wide | 32 node çizilir | 30 node; `C29`, `C30` `Project Root (root)` altında listelenir | R1 kusurunun kendisi; beklenti kusuru kodluyordu. |

Yeni check'ler: R1 sınır (genişlik 29, 30, 31, 35, 60: çizilen ≤ 30, çizilen + listelenen = tüm canlı node); R1 kesme + edge + orphan (kesilen node'un edge'i listelerde, unplaced orphan'lar orphan kalır, V-19 tek bulgu, incremental == rebuild); R2 fixture (local map'ler yalnız ≥ 3 child'da, kural değişmedi); R2 her gizli node bir kez listede; local map'siz parent'ların child'ları erişilebilir; uydurma anchor yok, link'ler çözülür, view temiz; silinen Deeper satırı → V-20.

### 11.5 Sonrası

Kanıt: `R1_R2_REPRO_AFTER.txt`, `R1_R2_RENDERS_AFTER.md`. R1: 30 node çizilir, 6 node listede, erişilemeyen 0. R2: 32 gizli node'un 31'i map'ten link ile erişilir; section'sız 1 node adıyla `(no section)` olarak listede (anchor yok). Gizli kayıp 0.

HSMM (pilot kopyası): revizyonlu view ilk paketin VIS-04 view'ı ile byte-identical (`STAY_IN_THE_LOOP.HSMM.VIS-04.md`, `KNOWLEDGE_MAP.HSMM.VIS-04.md`). HSMM 10 node, derinlik 2, gizli node yok; R1 / R2 yolları HSMM'de tetiklenmez. Pilot 62 dosya byte-identical.
