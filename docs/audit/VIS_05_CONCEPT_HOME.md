# VIS-05 — Concept Home Rendering

**Tarih:** 2026-11-10
**Jira:** CLS-6 (Epic CLS-1), kararlar A–E: yorum `10033`
**Branch:** `feature/cls-6-vis-05-concept-home`
**Base:** `main` `3351c3e` (VIS-04)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor.

- Soru: Okuyucu bir kavrama girince, derinliğe inmeden önce kavramın ne olduğunu, nerede durduğunu ve neyle ilişkili olduğunu görüyor mu?
- Her KN section bir **Concept Home View**'dur. DERIVED'dir; personal library Concept Home'u (`06` §8) değildir.
- Kaynak: Semantic Graph (`short_meaning`, `SEMANTIC` edge'ler, hiyerarşi) ve `COMPLETE` ULA artifact. Graph, ULA, Human Sync ve persistence değişmez.
- Değişen view section'ı yalnız `KN`.

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §1 `collapsed` + Boundary; §6 Concept Home View tanımı; §6.1 parts (In one sentence, Semantic Relationships, Learning Path; Related Concepts kaldırıldı); §6.3 layout + orientation kuralı; §6.4 Semantic Relationships; §6.5 Learning Path; §8 trigger; §11 |
| `references/07_INTEGRITY_CHECKS.md` | V-21 Concept Home graph render'ı ile uyuşmuyor; V-22 eksik `short_meaning` (rapor) |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | KN bloğu: orientation, iki relationship grubu, Learning Path, Boundary collapsed, Related Concepts yok |
| `tests/view/view_model.py` | `orientation`, `relations`, `learning_path`, `render_kn`; `node_sig` `short_meaning`; V-21 `home_stale`, V-22; repair |
| `tests/view/run_tests.py` | Test V (45 check); D, J, K, O, Q, S beklentileri (§6) |
| `tests/mutation.py` | VIS-M34 – VIS-M40; VIEW-M9 regex yeni `collapsed` satırına |
| `README.md` | View paragrafı: concept page |
| `distribution/manifest.json` | 07, 09, template sha256 |
| `docs/audit/VIS_05_CONCEPT_HOME.md` | Bu rapor |

## 3. Rendering

```text
### KN-xxxxxxxx — <canonical_name>
#### Where am I?
  breadcrumb · Parent · Reading order (NEXT) · Also part of (PART_OF)   ← VIS-02, değişmedi
  **In one sentence:** <graph short_meaning, aynen>                     ← B
  Learning depth · Source
  <graph Local Map, yalnız ≥ 3 primary child>                            ← C, değişmedi
#### Semantic Relationships                                              ← D
  **Outgoing** (this concept → other concepts):  - **<node>** — REL → <target>
  **Incoming** (other concepts → this concept):  - <source> — REL → **<node>**
#### Learning Path                                                       ← AC "clear start of learning content"
  L0 → L1 → L2 → L3 (collapsed) → … → Reference (collapsed)
#### L0 — Map … #### L2 — Mechanism  (açık)                              ← C, E
<details> L3 · L4 · Boundary · Reference </details>                      ← E
#### Example · #### Retrieval  (açık, değişmedi)
```

HSMM (gerçek pilot kopyası), `KN-91d7c2ae`:

```text
**In one sentence:** Süre PMF'ini geometrik tabana çekerek tahmin eden EM döngüsü.

#### Semantic Relationships

**Outgoing** (this concept → other concepts):

- **Penalized EM with L2 Duration** — USES → [Duration Lattice Inference](#kn-e06a93c5)

**Incoming** (other concepts → this concept):

- [Convergence and Regime Stability](#kn-a15c47f9) — DEPENDS_ON → **Penalized EM with L2 Duration**

#### Learning Path

L0 → L1 → L2 → L3 (collapsed) → L4 (collapsed) → Retrieval → Reference (collapsed)
```

## 4. Kararlar (CLS-6 yorum 10033 → uygulama)

| # | Karar | Uygulama |
|---|---|---|
| A | KN section = Concept Home View, DERIVED; `06` §8 değil, link hedefi değil; `#kn-` anchor stabil | `09` §6 giriş, §11. Marker, `<a id>`, heading değişmedi. View `CH-` ID'si veya `concepts/` link'i taşımaz (Test V). |
| B | Orientation = graph `short_meaning`, aynen; boş / `-` → satır yok, rapor | `09` §6.1, §6.3. Model değeri olduğu gibi yazar. V-22 WARNING, repair yazmaz. V-21 değiştirilmiş / silinmiş satırı yakalar. |
| C | ULA L0 ve graph Local Map ayrı; eşik 3 değişmez | `local_map_min_children` 3; §7.2 değişmedi. L0 `#### L0 — Map` learning girişinde. Graph map yalnız Where am I? içinde. |
| D | Flat Related Concepts → outgoing / incoming semantic gruplar; stored token, graph yönü; `NEXT` yalnız Reading order | `09` §6.4 tablosu: yalnız `SEMANTIC` sınıfı (§13.4), `edge_id` sırası, tekil, `SUPERSEDED` / eksik uç yok, boşsa `Yok.`. Satır biçimi MAP `Relationships` ile aynı yön dilbilgisi: `source — REL → target`. |
| E | L3, L4, Boundary, Reference collapsed; L0–L2 açık; Example / Retrieval aynı | `09` §1 `collapsed` = `L3; L4; Boundary; Reference`. Mevcut `<details>` primitive'i; yeni primitive yok. |

Ek kararlar (A–E kapsamında):

| # | Karar | Gerekçe |
|---|---|---|
| D-1 | Orientation Where am I? içinde, Also part of'tan sonra, Learning depth'ten önce. | Jira sırası: Breadcrumb → orientation → map. VIS-02 navigation bloğu (V-17) byte-identical kalır. |
| D-2 | Reading order Where am I? içinde kalır (sona taşınmadı). | Kararlar "Parent, breadcrumb … stay as they are" ve "VIS-01 to VIS-04 behaviour unchanged". |
| D-3 | Grup başlıkları yön-nötr: `Outgoing` / `Incoming`. Jira örneğindeki "Uses / Depends On", "Used By / Leads To" kullanılmadı. | Giden edge `EVIDENCE_FOR`, `COMPARED_WITH` olabilir; "Uses" başlığı yanlış iddia olurdu. Relation adı stored token'dır. |
| D-4 | `#### Learning Path`: tek satır, gösterilen part'lar section sırasıyla, collapsed işaretli. | AC "clear start of learning content". İçerik taşımaz; part'ları adlandırır. |
| D-5 | V-21 yalnız graph'tan türeyen kısmı (orientation + relationship grupları) karşılaştırır; ders içeriği okumaz. | `07` §V kapsamı: "Ders içeriği okunmaz". |
| D-6 | Semantic gruplar `SUPERSEDED` ucu göstermez. Eski Related Concepts gösteriyordu. | MAP `Relationships` (VIS-04) ve Reading order ile tutarlı. |

## 5. Scope dışı

VIS-06 Recall Capsules, VIS-07 visual grammar, VIS-08 genel disclosure / density, VIS-09, VIS-10, HTML viewer, yeni relation, graph / Human Sync / persistence authority, OBS-VIS04-4 (superseded section incremental cleanup).

## 6. Mevcut test beklentileri

| Test | Önce | Sonra | Neden |
|---|---|---|---|
| D Light levels | `Where am I?`, L0, L1, L2, Retrieval | + `Semantic Relationships`, `Learning Path` L0'dan önce | Concept Home part'ları (§6.1). |
| J related concepts | `- USES → [Duration Model]` | `- **Hidden-State Models** — USES → [Duration Model]` | §6.4 yönlü satır. |
| K V checks | 20 | 22 | V-21, V-22. |
| O collapsed | L3, L4, Reference | L3, L4, Boundary, Reference | Karar E. |
| Q baseline | 286 / 125 / 35 link / KN 10 link | 300 / 131 / 33 / 8 | 2 KN, boş satır dahil: +4 orientation, +12 Semantic Relationships, +8 Learning Path, −10 Related Concepts (+14; görünür +6). −2 link: Related Concepts'teki `NEXT` girdileri (OBS-VIS04-5). |
| S part order | … Reference, Related Concepts | Semantic Relationships, Learning Path, … Reference | §6.1. |

Başka beklenti değişmedi.

## 7. CLS-6 test plan → Test V

| CLS-6 / 10033 | Test V check |
|---|---|
| L1/L2 only | V shape L1/L2 only |
| L1–L4 | V shape L1-L4 |
| no local map | V shape no local map (2 child); V threshold unchanged |
| multiple dependencies | V shape multiple relationships (3 giden, 2 gelen, DEBT hedef) |
| no semantic dependencies | V shape no semantic relationships (`Yok.`; NEXT / PART_OF terfi etmez) |
| Reference and Boundary | V shape Boundary + Reference |
| ULA bytes / anchors | V every learning line; V collapsed bodies; V Example / Retrieval; V authoritative files byte-identical; V identity; V anchors |
| `NEXT` never in a semantic group; direction, tokens | V NEXT never…; V every listed relation is a stored graph edge…; V relation tokens; V incoming at the target; V PART_OF / SUPERSEDED / missing / duplicate |
| missing `short_meaning` | V missing short_meaning (`-` / boş): satır yok, V-22, repair NOTHING |
| Local Map ≥ 3 | V graph local map (synthetic qualifying); V local map counted as GRAPH, L0 ayrı |
| E collapse set | V shapes; O collapsed parts |
| mutations | VIS-M34 – VIS-M40 |
| real HSMM | §8 |

Ek: orientation verbatim / tek kopya / sıra; V-21 için 6 crafted bozulma; VIS-04 biçimli section → V-21 → repair == rebuild; graph değişiminde yalnız ilgili KN section'ları; template part sırası.

Mutation'lar: VIS-M34 Boundary açık · VIS-M35 orientation `system_role`'den · VIS-M36 outgoing grup ters yön · VIS-M37 outgoing grup `NAVIGATION` (NEXT semantic) · VIS-M38 V-21 yok · VIS-M39 V-22 yok · VIS-M40 template Learning Path yok.

## 8. HSMM review kopyası (pilot dosyaları değişmez)

| Ölçü | VIS-04 | VIS-05 |
|---|---|---|
| Section | 30 | 30 (21 byte-identical; değişen yalnız 9 KN) |
| INDEX, MODEL, JOURNEY, HS (16), MAP, DEBT | — | identical |
| Orientation = `short_meaning` | — | 9/9 |
| Relationship grupları = graph `SEMANTIC` edge'leri (yön, token, tekil) | — | 9/9 |
| `NEXT` semantic listede | 7/9 section (Related Concepts) | 0 |
| Navigation (breadcrumb, parent, reading order) | — | 9/9 değişmedi |
| ULA learning içeriği (sıra + metin) | — | 9/9 identical |
| Graph Local Map | 0 | 0 (KN node'ların primary child'ı yok; `ROOT` section'sız) |
| `lines_total` / `lines_visible` / `lines_collapsed` | 3106 / 1102 / 843 | 3186 / 1083 / 887 |
| `details_blocks` | 38 | 44 (6 Boundary) |
| `links_internal` / broken | 148 / 0 | 136 / 0 |
| Integrity after repair | V-15 | V-15 (VIS-02 öncesi) |

- `lines_visible` −19 = +25 Concept Home başı − 44 Boundary gövdesi (artık collapsed). Ders içeriği kaybı değildir: 44 satır `lines_collapsed`'a geçti.
- `links_internal` −12 = eski Related Concepts'teki 12 `NEXT` girdisi (6 NEXT edge × 2 uç). Semantic link sayısı aynı.
- Kabul edilmiş VIS-04 view'ı VIS-05 kurallarıyla: V-21 yalnız 9 KN section'da; repair yalnız onları yazar; sonuç taze VIS-05 render'ı ile byte-identical.
- Pilot 62 dosya byte-identical.

## 9. Açık gözlemler

- O-1: HSMM graph Local Map yolunu çalıştırmaz (eşik sağlanmaz). Nitelikli Local Map yalnız synthetic fixture ile test edildi.
- O-2: HSMM'de Example part'ı yok; Example açıklığı yalnız synthetic Full fixture ile test edildi.
- O-3: Pilot header blockquote satırı rebuild'den farklı (section dışı; VIS-04 O-4). Değişmedi.
- O-4: VIEW-M9 mutation'ında Test S crash eder (yakalanır). VIS-05 öncesi `main`'de de aynı.
- O-5: OBS-VIS04-4 (`on_map_sync` superseded KN section'ı kaldırmaz) değişmedi, kapsam dışı.
- O-6: Collapse sonrası GitHub `boundary` heading anchor'ı yok (artık `<summary>`); hiçbir link onu göstermiyordu.

## 10. Tests

Tek tam koşu: `uv run --no-project python tests/run_all.py`, 2026-11-10 16:03:56 – 17:02:11 +0300, exit 0, `RESULT: PASS`. Test edilen 8 dosyanın sha256'sı koşu başında kaydedildi ve koşu sonunda aynıydı; sonra yalnız bu rapor (`docs/audit/` taranmaz) güncellendi.

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
| view | 366/366 (VIS-04: 321; + Test V 45) |
| distribution | 108/108 |
| **toplam** | **1177/1177** (VIS-04: 1132) |
| mutation | **91/91 CAUGHT**, 0 MISSED (VIS-04: 84; + VIS-M34 – M40) |
