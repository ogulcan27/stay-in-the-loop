# 09 — Knowledge View

**Status:** IMPLEMENTED

## Purpose

Bir project için tek human-facing knowledge dosyasını tanımlar:

```text
ONE PROJECT → ONE HUMAN-FACING KNOWLEDGE FILE → docs/learning/STAY_IN_THE_LOOP.md
```

Kullanıcı projeyi, Human Sync geçmişini, ULA dersini, kavram haritasını ve açık learning debt'i bu dosyadan okur.
Machine state dosyaları kalır. Kullanıcı normalde onları okumaz.

## Responsibility

- View dosyasının yapısı, section marker'ları ve anchor'ları.
- Human Sync record → view section projeksiyonu.
- ULA artifact → concept section projeksiyonu (L0–L4).
- Semantic Graph → breadcrumb, related concepts, global ve local Mermaid map.
- Section-level retrieval ve section-level write.
- Migration ve derived repair.

## Must Not

- Status, checkpoint, lock, project identity, coverage veya integrity kararı için authority olmaz.
- Machine state'i (ledger, queue, sync state, graph tablosu, pass metadata) view içine kopyalamaz.
- Human Sync, ULA, coverage, graph veya persistence semantiğini değiştirmez.
- Per-level, per-concept veya per-sync ayrı user-facing dosya oluşturmaz.
- HTML viewer, JavaScript veya HTML kopyası üretmez. View Markdown + Mermaid'dir.
- Varsayılan olarak bütün dosyayı okumaz veya yeniden yazmaz.

---

## 1. Authority boundary

```text
MACHINE STATE (authoritative)  → status, checkpoint, coverage, graph, debt, identity
STAY_IN_THE_LOOP.md (derived)  → human-facing projection
```

| rule | value |
|---|---|
| view_path | `docs/learning/STAY_IN_THE_LOOP.md` |
| authority | DERIVED |
| read_mode | MARKERS_THEN_SECTION |
| write_mode | SECTION_PATCH |
| write_order | CONTENT_MAP_DEBT_MODEL_INDEX |
| on_write_error | RESTORE_PRE_IMAGE |
| failure_effect | WARNING |
| global_map_depth | 2 |
| local_map_min_children | 3 |
| map_label_max_chars | 48 |
| collapsed | L3; L4; Reference |
| key_terms_max | 5 |
| remember_max | 5 |

| Karar | Authority | View |
|---|---|---|
| Sync status, checkpoint, record version | `sync/HUMAN_SYNC_STATE.md` | Yalnız gösterir |
| Unit mental model | `sync/records/HS-*.md` | Projeksiyon |
| Coverage | `state/COVERAGE_LEDGER.md` | Göstermez |
| Knowledge relation, hierarchy, depth | `maps/SEMANTIC_GRAPH.md` | Türetir |
| Ders içeriği (audit edilmiş) | `passes/<learning-pass-id>/ula/<event-id>/` | Okuma kopyası |
| Knowledge Debt | `state/LEARNING_QUEUE.md` §B | Liste |
| Project identity | `state/LEARNING_CONFIG.md` `project_id` | Header'da gösterir |
| Lock, integrity | `06` §22.1, `07` | Yok |

- View ile state çelişirse state kazanır. View section'ı state'ten yeniden üretilir.
- View silinirse authoritative state'ten yeniden kurulur (§12). Bilgi kaybı olmaz.
- Kullanıcının view içine yazdığı not korunmaz. View elle düzenlenmez.

---

## 2. Creation

- View yalnız sunulacak içerik oluşunca oluşturulur: ilk Human Sync record, ilk concept section veya ilk `OPEN` debt.
- Skill kurulumu veya project initialization (`02` §11) view oluşturmaz. Boş project view almaz.
- Project initialize edilmemişse view yazılmaz. Initialization onay kuralı aynıdır.
- `project_id: UNCONFIGURED` ise view yazılmaz (`08` §12 ile aynı sınır).
- Development repository kuralı geçerlidir: Skill'in kendi repository'sinde view oluşturulmaz.
- Path'te `SITL:VIEW` header'ı olmayan bir dosya varsa overwrite edilmez (V-12). Kullanıcı karar verir.

---

## 3. Structure

| order | kind | heading | source |
|---|---|---|---|
| 1 | `VIEW` | `# Stay in the Loop — Project Knowledge` | config `project_id` |
| 2 | `INDEX` | `## Quick Index` | HS + KN section listesi |
| 3 | `MODEL` | `## Project in 60 Seconds` | `sync/PROJECT_SYNC_CONTEXT.md` |
| 4 | `HS` | `## Human Sync` → `### <label>` | state + record |
| 5 | `KN` | `## Learning` → `### <node-id> — <canonical_name>` | graph + ULA artifact |
| 6 | `MAP` | `## Knowledge Map` | graph |
| 7 | `DEBT` | `## Open Learning Debt` | queue §B |

- Sıra sabittir. Format: `templates/KNOWLEDGE_VIEW_TEMPLATE.md`.
- `## Human Sync` ve `## Learning` container heading'leridir. Marker dışında durur. Yeniden yazılmaz.
- HS section'ları `seq` sırasıyla durur. KN section'ları graph `## Nodes` satır sırasıyla durur.
- Yeni HS section bir sonraki HS section'ından veya `## Learning` satırından önce eklenir.
- Yeni KN section bir sonraki KN section'ından veya `MAP` START marker'ından önce eklenir.
- Human Sync ve Learning ayrı kalır. HS section'ı concept öğrenildi demek değildir (`08` §1).

---

## 4. Markers

Marker satırı tek satırdır ve kendi satırında durur.

```text
<!-- SITL:VIEW project_id=<PRJ-xxxxxxxx> -->
<!-- SITL:INDEX:START -->                 ... <!-- SITL:INDEX:END -->
<!-- SITL:MODEL:START -->                 ... <!-- SITL:MODEL:END -->
<!-- SITL:HS:<HS-xxxxxxxx>:START v=<n> --> ... <!-- SITL:HS:<HS-xxxxxxxx>:END -->
<!-- SITL:KN:<KN-xxxxxxxx>:START depth=<L1;L2> --> ... <!-- SITL:KN:<KN-xxxxxxxx>:END -->
<!-- SITL:MAP:START -->                   ... <!-- SITL:MAP:END -->
<!-- SITL:DEBT:START -->                  ... <!-- SITL:DEBT:END -->
```

- Section = START satırından END satırına kadar, iki satır dahil.
- HS ID = `record_id`. KN ID = graph `node_id`. İkisi de opaque ve kalıcıdır.
- `v` = section'ın üretildiği `record_version`. `depth` = section'daki level'lar.
- Section içinde `#`, `##` veya `###` heading olmaz. Artifact heading'leri `####` ve altına kaydırılır (§6.2).
- Her HS ve KN section'ı stable anchor taşır: `<a id="hs-xxxxxxxx"></a>`, `<a id="kn-xxxxxxxx"></a>`. Anchor isimden türemez.
- Marker HTML comment'tir. GitHub preview'da görünmez.

---

## 5. Human Sync section

Kaynak: state satırı + record. Ham evidence okunmaz. Record değişmez. View record part'larını yalnız sıralar ve gösterir. İkinci Human Sync authority oluşmaz.

Okuyucu proje amacını bilir. İç ID'leri ve proje kısaltmalarını ezberlemedi. Haftalar sonra dönmüş olabilir. Section iki katmandır:

```text
HUMAN → anında anlama: ne yapıldı, ne akılda kalmalı, sonraki işte ne değişir
TRACE → karar, evidence, bağımlılık, provenance (katlanmış)
```

Okuyucu work unit'in ne yaptığını TRACE'ten önce anlar.

### 5.1 Parts

| view | record | layer |
|---|---|---|
| `Tek cümlede:` | Purpose | HUMAN |
| `Anahtar kavramlar:` | Technical Translation | HUMAN |
| `Zihinsel Model` | How It Works | HUMAN |
| `Neden Önemli?` | Downstream Impact | HUMAN |
| `Why` | Why It Changed | TRACE |
| `What Changed` | What Changed | TRACE |
| `Key Decisions` | Key Decisions | TRACE |
| `Dependencies` | Dependencies | TRACE |
| `Open Points` | Open / Uncertain Points | TRACE |
| `Evidence` | Evidence / Provenance | TRACE |
| `More Terms` | Technical Translation | TRACE |
| `Record:` | Header | TRACE |

| sync_status | Status line |
|---|---|
| `SYNCED` | `Current` |
| `STALE` | `Needs refresh` |

- Sıra tablo sırasıdır. `:` ile biten part kalın satırdır: `**Tek cümlede:** <metin>`. Diğer part'lar `####` heading'dir.
- Status satırı başlıktan hemen sonra gelir: `**Status:** <Current | Needs refresh>`.
- HUMAN part'lar açık durur. TRACE part'lar tek `<details>` bloğundadır: `<summary><strong>Technical Trace</strong></summary>`.
- `Tek cümlede:` Purpose metnidir. Ayrı özet üretilmez. Aynı bilgi iki kez yazılmaz.
- `Anahtar kavramlar:` her `"basit anlam" ↔ Term` satırını `basit anlam (Term)` yazar. Term parantez içeriyorsa `basit anlam — Term` yazar. Ayraç ` · `. İlk `key_terms_max` çift gösterilir.
- `More Terms` kalan çiftleri ve bu biçime uymayan Technical Translation satırlarını taşır.
- `Record:` satırı: `` `record_id` v<record_version> · `work_unit_id` · `checkpoint` ``. Provenance kaybolmaz.
- Record bölümü boşsa (`Yok.`) part gösterilmez. `Tek cümlede:` ve `Record:` her zaman gösterilir.
- Gösterilmez: lock ve integrity detayı.
- `UNSYNCED` unit için section yoktur.
- `STALE` olunca yalnız status satırı ve index satırı değişir. Eski içerik güncel gibi sunulmaz. Eski ve yeni sürüm yan yana tutulmaz.
- Refresh sonrası section record'un yeni sürümünden yeniden üretilir (`v` +1).
- HS section ders anlatmaz. Teorik konu `GENERAL THEORY` cümlesi olarak kalır (`08` §4).

### 5.2 Human-first vocabulary

HUMAN katmanında proje sembolü ilk geçtiği yerde tanımlıdır. Önce düz anlam, sonra iç terim gelir: `benzersiz dinleyici sayısı (N)`, `prediction-time information boundary (S-B)`.

| sembol | örnek | kapsam |
|---|---|---|
| ID | `TF-02`, `S-B` | HUMAN part'lar |
| fonksiyon | `K(t)`, `M(W)` | HUMAN part'lar |
| tek büyük harf | `N`, `C` | HUMAN part'lar, code fence dışı |

- Tanımlı biçim: `<düz anlam> (SYM)`, `<düz anlam> — SYM` veya `SYM = <düz anlam>`. Aynı section'da sonraki geçiş kısa yazılabilir.
- `A` ve `I` tek harf sembol sayılmaz. Başlık, status satırı ve TRACE kapsam dışıdır.
- Genel teknik notasyon yasak değildir. Kural yalnız HUMAN katmanı içindir.
- View record metnini değiştirmez. Tanımsız sembol `07` V-15 WARNING'idir. Düzeltme kaynağı record'dur (`03` §5).

### 5.3 Project in 60 Seconds

`MODEL` section'ı. Kaynak: `sync/PROJECT_SYNC_CONTEXT.md`. Proje haftalar sonra açılınca okuyucu durumu bir dakikada anlar.

| view | context | layer |
|---|---|---|
| What are we building? | Objective | HUMAN |
| Where are we now? | Current Position | HUMAN |
| How does it work at the highest level? | Data / Control Flow | HUMAN |
| Five things to remember | Invariants; Active Decisions | HUMAN |
| What is still unresolved? | Open Points | HUMAN |
| Architecture | Architecture | SNAPSHOT |
| Components | Components | SNAPSHOT |
| Active Decisions | Active Decisions | SNAPSHOT |
| Invariants | Invariants | SNAPSHOT |
| Dependencies | Dependencies | SNAPSHOT |

- Part'lar `####` heading'dir. SNAPSHOT part'ları tek `<details>` bloğundadır: `<summary><strong>Technical Project Snapshot</strong></summary>`.
- `Five things to remember` Invariants ve Active Decisions maddelerinden ilk `remember_max` maddeyi bu sırayla alır.
- Bu maddeler SNAPSHOT'ta tekrar yazılmaz. SNAPSHOT yalnız kalan maddeleri gösterir.
- Boş part gösterilmez. Bütün part'lar boşsa gövde `Yok.` olur.

---

## 6. Learning section

Bir graph node'u KN section alır, eğer `node_status: ACTIVE` ve `available_depth` `-` değilse.
`DEBT` node section almaz. Open Learning Debt'te görünür.

### 6.1 Parts

| part | kaynak | koşul |
|---|---|---|
| Where am I? | graph `parent_id` zinciri + `PART_OF` + `available_depth` + `source_event_ids` | Her zaman |
| Local Map | graph primary child'lar + node'un relation'ları | Primary child sayısı ≥ `local_map_min_children` |
| L0 — Map | artifact L0 | Artifact'te doluysa |
| L1 — Simple Mental Model | artifact L1 | `available_depth` içinde |
| L2 — Mechanism | artifact L2 | `available_depth` içinde |
| L3 — Theory | artifact L3 | `available_depth` içinde |
| L4 — Formalism | artifact L4 | `available_depth` içinde |
| Boundary | artifact boundary | Artifact'te doluysa |
| Example | artifact example | Artifact'te doluysa |
| Retrieval | artifact retrieval | Artifact'te doluysa |
| Reference | artifact reference | Artifact'te doluysa |
| Related Concepts | graph edge'leri | Edge varsa |

- Yalnız ULA pass'in gerçekten ürettiği level gösterilir. Light ULA L4 üretmez. Boş level uydurulmaz.
- `collapsed` part'ları `<details>` içinde durur. L0, L1, L2 açık kalır.
- Self-Check, Content Integrity Check, Metadata, Orientation, Oral Version ve Transition gösterilmez. Bunlar audit içindir.

### 6.2 Artifact mapping

| part | Light `LIGHT_ULA.md` | Full `CONTENT.md` |
|---|---|---|
| L0 — Map | `## L0 — Local Map` | `# Local Map` |
| L1 — Simple Mental Model | `## L1 — Simple Explanation` | `# L1 — Simple Explanation` |
| L2 — Mechanism | `## L2 — Mechanism` | `# L2 — Mechanism` |
| L3 — Theory | `## L3 — Theory` | `# L3 — Theory` |
| L4 — Formalism | - | `# L4 — Math / Formalism` |
| Boundary | `## Boundary / Confusion Check` | - |
| Example | - | `# Example` |
| Retrieval | `## Retrieval` | `# Retrieval Check` |
| Reference | `## Reference` | `# R — Reference Links` |

- Kaynak artifact = node `source_artifacts`. Her part için listede en son, o part'ı dolu taşıyan artifact kullanılır.
- Yalnız `COMPLETE` artifact projekte edilir. Taslak, `NEEDS_REVISION` veya superseded artifact projekte edilmez.
- İçerik aynen kopyalanır. Yalnız HTML comment'ler çıkar ve heading'ler kaydırılır: artifact part heading'i `####` olur, alt heading'ler buna göre iner (en fazla `######`).
- Part boşsa (yalnız comment veya boşluk) gösterilmez.

### 6.3 Breadcrumb

- Breadcrumb yalnız primary `parent_id` zincirinden üretilir (`05` §5.4). Bağımsız hiyerarşi yoktur.
- Biçim: `ROOT → … → **<node>**`. Zincirdeki section'lı node link olur.
- Secondary `PART_OF` üyelikleri ayrı satırda: `Also part of:`.

### 6.4 Related Concepts

- Node'a gelen ve node'dan çıkan edge'ler, `PART_OF` hariç. Biçim: çıkan `- <RELATION> → <name>`, gelen `- <name> → <RELATION> → **<node>**`.
- Hedef node'un section'ı varsa ad link olur: `[<name>](#kn-xxxxxxxx)`. `DEBT` node `(DEBT)` etiketi alır.
- Açıklama yazılmaz. Açıklama hedef section'dadır.

---

## 7. Maps

```text
MAP     = WHERE
CONTENT = WHAT / WHY / HOW
```

### 7.1 Global map

- `## Knowledge Map` içinde tek Mermaid bloğu: `flowchart LR`.
- Node'lar: `ROOT` ve `ROOT`'tan `global_map_depth` primary seviye. `SUPERSEDED` node gösterilmez.
- Edge'ler: primary `parent_id` (`-->`) ve iki ucu haritada olan `NEXT` (`-. NEXT .->`).
- Mermaid node ID = node ID'de `-` yerine `_`. Label = `canonical_name (KN-xxxxxxxx)`. `canonical_name` `map_label_max_chars` ile kısaltılır. `DEBT` node label'ı `(DEBT)` alır.
- Label `short_meaning`, `system_role` veya ders cümlesi taşımaz.
- Daha derin seviye global map'e konmaz. Recursive zoom local map ile yapılır.

### 7.2 Local map

- KN section'ının Where am I? part'ında durur.
- Yalnız primary child sayısı ≥ `local_map_min_children` ise üretilir.
- Node'lar: section node'u + primary child'lar + node'un `PART_OF` ve `NEXT` dışındaki relation hedefleri.
- Edge'ler: child (`-->`) ve relation (`-- RELATION -->`). Label kuralı §7.1 ile aynıdır.

```text
GLOBAL MAP (depth 1–2) → KN section → LOCAL MAP (children) → child KN section
```

- Map içerik deposu değildir. Graph'ın görünümüdür (`05` §1). Ayrı knowledge graph yoktur.
- `maps/HORIZONTAL_MAP.md` terminal `map` komutu için internal view olarak kalır.

---

## 8. Triggers

| trigger | sections |
|---|---|
| Human Sync record write (`08` §11.1, `08` §12) | HS (yeni / refresh), MODEL, INDEX |
| Staleness state write (`08` §6, §6.1) | HS (status line), MODEL, INDEX |
| Map sync graph write (`05` §8) | KN (yeni / değişen depth / rename), parent KN (local map), MAP, INDEX |
| Queue §B debt write (`03` §17, `06` §20) | DEBT |
| Derived repair (`07` §L.3) | Yalnız V check'in gösterdiği section'lar |

- Trigger dışındaki section okunmaz ve yazılmaz.
- Sync-only run yalnız HS, MODEL ve INDEX yazar (`08` §11). KN, MAP ve DEBT yazmaz.
- View write authoritative write'tan sonra gelir. View hatası authoritative sonucu geri almaz.

---

## 9. Section-level retrieval

```text
STATE FIRST → TARGET → MINIMUM CONTEXT → RELEVANT SECTION
```

| request | read | never |
|---|---|---|
| `HS` | `MARKERS`, `INDEX`, `TARGET`, `DEP_SECTIONS` | `WHOLE_VIEW`, `OTHER_SECTIONS` |
| `KN` | `MARKERS`, `INDEX`, `TARGET`, `DEP_SECTIONS` | `WHOLE_VIEW`, `OTHER_SECTIONS` |
| `MAP` | `MARKERS`, `TARGET` | `WHOLE_VIEW`, `OTHER_SECTIONS` |
| `WRITE` | `MARKERS`, `TARGET` | `WHOLE_VIEW`, `OTHER_SECTIONS` |

| code | anlam |
|---|---|
| `MARKERS` | `SITL:` marker satırları ve satır numaraları (grep) |
| `INDEX` | `INDEX` section'ı |
| `TARGET` | İstenen section'ın START–END satır aralığı |
| `DEP_SECTIONS` | HS: `depends_on` unit'lerinin section'ı. KN: `REQUIRES` / `DEPENDS_ON` hedeflerinin section'ı. Yalnız soru gerektiriyorsa. |
| `WHOLE_VIEW` | Bütün dosya |
| `OTHER_SECTIONS` | Hedef ve dependency dışındaki section'lar |

- Okuma satır aralığı iledir: önce marker satır numaraları, sonra yalnız o aralık.
- Bütün dosya yalnız tam rebuild (§12) veya V-03 / V-02 teşhisi için okunur.
- Machine state okuma kuralları değişmez (`08` §8, `05` §16, `06` §25).

---

## 10. Section-level write

```text
READ        MARKERS + hedef section'ın pre-image'ı
↓
BUILD       yeni section metni bellekte
↓
INTEGRITY   07 §V candidate üzerinde
↓
WRITE       content section'ları → MAP → DEBT → MODEL → INDEX
↓
VERIFY      07 §V yazılmış dosya üzerinde
```

- Write birimi tam bir marker bloğudur. Eski START–END bloğu yeni blok ile değiştirilir. Yeni blok §3 ekleme noktasına eklenir.
- Hedef dışındaki byte'lar değişmez.
- INDEX en son yazılır. Index var olmayan section'ı göstermez.
- Candidate V FAIL → view write yok. Authoritative write geçerli kalır. Sonuç WARNING ve sonraki derived repair.
- Write hatası → dosya pre-image ile geri yüklenir. Yarım section, açık Mermaid fence veya tek marker kalmaz.
- İçerik değişmediyse section yazılmaz.

---

## 11. Duplication

| katman | rol |
|---|---|
| HS section | Projede ne oldu (project comprehension) |
| KN section | Reusable kavram (technical learning) |
| Map | Konum ve ilişki |
| Pass artifact | Audit, resume, provenance |

- Aynı ders metni iki section'da yazılmaz. HS section kavramı öğretmez; KN section'a link verebilir.
- Map node'u paragraf taşımaz.
- HS section'da her record satırı bir kez görünür: HUMAN veya TRACE katmanında. Özet eklenmez; yalnız sıralama ve katlama vardır.
- Pass artifact audit kaydıdır. Auditor kararı ve resume bu metne bağlıdır. Bu nedenle değişmez ve silinmez.
- View, `COMPLETE` artifact'in okuma kopyasıdır. Kullanıcı dersi view'dan okur. Artifact'i normalde okumaz.
- Concept Home (`06` §8) cross-project kalıcı kaynaktır. View project'e bağlı okuma yüzeyidir.

---

## 12. Migration ve rebuild

Mevcut project'te view yoksa ama içerik varsa (record, `ACTIVE` node, `OPEN` debt):

1. V-08 WARNING verir. Action: rebuild.
2. View authoritative state'ten kurulur: record'lar → HS, graph + `COMPLETE` artifact'ler → KN, graph → MAP, queue §B → DEBT.
3. Pass artifact, record, graph ve Concept Home değişmez, taşınmaz, silinmez.
4. Eski ULA çıktısı view'da okuma kopyası olur. Kaynak path Where am I? satırında kalır (provenance).
5. Run loop adım 15 bunu onaysız yapar. `/stay-in-the-loop integrity` önce listeyi gösterir ve onay ister (`07` §L.6).

- Rebuild deterministiktir. Aynı state aynı byte'ları üretir. Incremental sonuç ile rebuild sonucu aynıdır.
- `SITL:VIEW` header'ı olmayan mevcut dosya rebuild edilmez (V-12).
- Tam rebuild yalnız dosya yoksa veya V-02 / V-03 sonrası kullanıcı onayı ile yapılır.

---

## 13. Readability contract

View'ın okunabilirlik ve navigation sözleşmesidir. Görünüş değil, okuyucunun yolunu bulma maliyeti ölçülür.
Yeni bir presentation değişikliği bu sözleşmeye göre değerlendirilir. Gereksinim başka yerde yeniden tanımlanmaz.

### 13.1 Reader questions

| id | question |
|---|---|
| RQ-1 | Where am I? |
| RQ-2 | What is this? |
| RQ-3 | Why does it matter? |
| RQ-4 | What came before? |
| RQ-5 | What does this depend on? |
| RQ-6 | Where is this used? |
| RQ-7 | Where do I go next? |

- Her HS ve KN section'ı bu soruları cevaplamaya hizmet eder. Cevap view'da yoksa bu bir navigation açığıdır, içerik hatası değil.

### 13.2 Metrics

| metric | meaning |
|---|---|
| `lines_total` | Dosyadaki bütün satırlar |
| `lines_visible` | Varsayılan görünümde okunan boş olmayan satırlar: `<details>` dışı + `<summary>` satırı. Comment, anchor ve `<details>` tag'i sayılmaz. |
| `lines_collapsed` | `<details>` içindeki boş olmayan satırlar |
| `details_blocks` | `<details>` blok sayısı |
| `details_max_depth` | En derin iç içe `<details>` seviyesi |
| `hs_units` | HS section sayısı |
| `kn_concepts` | KN section sayısı |
| `graph_nodes` | Semantic Graph node sayısı |
| `graph_edges` | Semantic Graph edge sayısı |
| `graph_edges_by_relation` | Edge sayısı, `relation_type` başına |
| `links_internal` | `](#anchor)` link sayısı |
| `links_broken` | Hedef anchor'ı dosyada olmayan link sayısı |
| `links_from_index` | INDEX section'ındaki link sayısı |
| `links_from_hs` | HS section'larındaki link sayısı |
| `links_from_kn` | KN section'larındaki link sayısı |
| `kn_without_outgoing_link` | Hiç link taşımayan KN section sayısı |
| `maps_global` | MAP section'ındaki map bloğu sayısı (her code fence) |
| `maps_local_structured` | KN section'larındaki local map sayısı, render biçiminden bağımsız |
| `maps_local_by_source` | `maps_local_structured`, kaynak başına: `BLOCK`, `CONCEPT_L0`, `GRAPH` |
| `maps_local_mermaid` | KN section'larındaki Mermaid blok sayısı (yalnız render ölçüsü) |
| `global_map_edges_by_kind` | Global map edge'leri: `HIERARCHY`, `NEXT`, `RELATION` |

| source | local map |
|---|---|
| `CONCEPT_L0` | `L0 — Map` part'ı (§6.1, §6.2; `04` L0 — LOCAL MAP) |
| `BLOCK` | `LOCAL MAP — <block>` başlığı (`ula/CONTENT_BUILDER.md` §31) |
| `GRAPH` | Where am I? içindeki Mermaid local map (§7.2) |

- Ölçüm read-only ve deterministiktir. Aynı dosya aynı sonucu verir. Mermaid satırları kaynak satır olarak sayılır.
- Map, okuyucunun gördüğü map birimi olarak sayılır, render teknolojisi olarak değil. ASCII / text map de map'tir.
- Var olan bir map'in biçimini değiştirmek (text → Mermaid) `maps_local_structured`'ı değiştirmez. Local map iyileşmesi yalnız `maps_local_structured` ile iddia edilir. `maps_local_mermaid` iyileşme ölçüsü değildir.

### 13.3 Navigation domains

| domain | sections | role |
|---|---|---|
| `HUMAN_SYNC` | `MODEL`, `HS` | Project comprehension: projede ne oldu |
| `LEARNING` | `KN`, `MAP`, `DEBT` | Technical learning: reusable kavram |

- İki domain ayrı navigation alanıdır. Bir HS section'ını okumak kavramı öğrenmek değildir (§3, `08` §1).
- HS section KN section'a link verebilir. Ders metni domain'ler arasında kopyalanmaz (§11).

### 13.4 Navigation order and semantic dependency

| class | relations | meaning |
|---|---|---|
| `NAVIGATION` | `NEXT` | Okuma sırası. Bağımlılık değildir. |
| `HIERARCHY` | `PART_OF` | Konum: kavram neyin parçası |
| `SEMANTIC` | `REQUIRES`, `PRODUCES`, `CAUSES`, `USES`, `DEPENDS_ON`, `ALTERNATIVE_TO`, `COMPARED_WITH`, `EVIDENCE_FOR`, `FAILS_WHEN`, `IMPLEMENTED_BY` | Anlam ilişkisi |

- Primary `parent_id` `HIERARCHY` sınıfındadır.
- `NEXT` hiçbir zaman ön koşul veya bağımlılık olarak gösterilmez veya yorumlanmaz.
- "What does this depend on?" (RQ-5) yalnız `SEMANTIC` edge'lerden cevaplanır.

### 13.5 Authority

| layer | authority | source |
|---|---|---|
| Authoritative state | AUTHORITATIVE | `state/`, `sync/HUMAN_SYNC_STATE.md` |
| Human Sync records | AUTHORITATIVE | `sync/records/HS-*.md` |
| ULA content | AUTHORITATIVE | `passes/<learning-pass-id>/ula/<event-id>/` |
| Semantic Graph | AUTHORITATIVE | `maps/SEMANTIC_GRAPH.md` |
| Markdown view | DERIVED | `STAY_IN_THE_LOOP.md` |

- Readability değişikliği yalnız DERIVED katmanı değiştirir. Authority kuralı §1'dedir.
- Her yeni human-facing öğe (harita, yön satırı, hatırlatma) authoritative state'ten türetilir ve rebuild ile yeniden üretilir. İkinci authority oluşmaz.

---

## Authoritative Source

- `08_HUMAN_SYNC_STATE.md` §1, §3, §4, §11.1, §12 (record, status, write sırası).
- `05_MINDMAP_PROTOCOL.md` §1, §3, §5.4, §12, §13 (graph, hierarchy, zoom).
- `04_ULA_PROTOCOL.md` §9 (artifact yapısı).
- `07_INTEGRITY_CHECKS.md` §V, §L.
