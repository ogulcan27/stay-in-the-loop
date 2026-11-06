# 07 — Integrity Checks

**Status:** §C, §E, §U, §M, §P, §S, §V, §L IMPLEMENTED (Phase 3–8). Final Integrity: §L.

## Purpose

Project learning state tutarlılığını kontrol eder.

## Must Not

- Öğretim içeriğinin learning quality audit'ini yapmaz. Bu iş `ula/LEARNING_AUDITOR.md` rolüne aittir.
- Ledger'daki hatayı sessizce düzeltmez. Raporlar.

---

## C. Coverage Integrity

Ne zaman çalışır:

- Startup'ta, discovery'den önce.
- Her ledger commit'inden sonra.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| C-01 | Duplicate `work_unit_id` | FAIL | Dur. Kullanıcıya göster. |
| C-02 | Unknown `status` | FAIL | Dur. |
| C-03 | Unknown `source_type` | FAIL | Dur. |
| C-04 | Duplicate `seq` aynı `source_type` içinde | FAIL | Dur. |
| C-05 | `COVERED` / `PARTIAL` / `NOT_LEARNING_RELEVANT` ve `learning_pass_id` boş | FAIL | Dur. |
| C-06 | `learning_pass_id: EXTERNAL` | WARNING | Bilgi ver. Devam et. |
| C-07 | `PARTIAL` ve `open_items` boş | WARNING | Bilgi ver. Devam et. |
| C-08 | State sayıları ledger ile uyuşmuyor | WARNING | State'i ledger'dan yeniden üret. `status: REBUILT`. |
| C-09 | Queue §A ile ledger'ın `DEFERRED ∪ PARTIAL` kümesi farklı (fazla veya eksik birim) | WARNING | Queue §A'yı ledger'dan yeniden üret. |
| C-10 | Geçersiz status transition istendi | FAIL | Yazma yapma. Dur. |
| C-11 | Hesaplanan OPEN COVERAGE, ledger'daki bir `DEFERRED` / `UNCOVERED` / `PARTIAL` birimi içermiyor | FAIL | Gap hesaplaması hatalı. Dur. |
| C-12 | `source_ref` artık çözülemiyor (ör. rebase sonrası commit yok) | WARNING | Kullanıcıya sor. Otomatik eşleştirme yapma. |

FAIL olduğunda hiçbir ledger commit'i yapılmaz.

---

## E. Learning Event and Knowledge Debt Integrity

Ne zaman çalışır:

- Handoff write'tan önce (`03_HUMAN_SYNC_PROTOCOL.md` §17). Pass ve queue §B taslağı üzerinde.
- Startup'ta, queue §B üzerinde (E-07, E-08, E-12).
- Ledger'da `PARTIAL` satırı varsa, `open_items` üzerinde (E-10).

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| E-01 | Duplicate `event_id` aynı pass içinde | FAIL | Dur. |
| E-02 | Event `work_unit_ids` boş veya selected scope dışında bir ID içeriyor | FAIL | Dur. |
| E-03 | Unknown `category` veya `secondary_tags` değeri | FAIL | Dur. |
| E-04 | Unknown `knowledge_priority` | FAIL | Dur. |
| E-05 | Unknown `disposition` | FAIL | Dur. |
| E-06 | Disposition Summary içinde `ULA_CANDIDATE` girdisi tanımlı bir `event_id` değil | FAIL | Dur. |
| E-07 | Debt `originating_event_id` boş veya tanımlı bir event değil | FAIL | Dur. |
| E-08 | Duplicate `debt_id` | FAIL | Dur. |
| E-09 | `IMPLEMENTATION_DETAIL` priority ile `ULA_CANDIDATE` veya `KNOWLEDGE_DEBT` disposition | FAIL | Dur. |
| E-10 | `PARTIAL.open_items` bilinmeyen bir `event_id` içeriyor | FAIL | Dur. |
| E-11 | `VERIFIED` iddia evidence ref içermiyor | FAIL | Ref ekle veya status'u düzelt. Sonra tekrar kontrol et. |
| E-12 | Unknown `evidence_status`, debt `priority` veya `debt_status` | FAIL | Dur. |
| E-13 | `KNOWLEDGE_DEBT` disposition event için §B kaydı yok | FAIL | Dur. |
| E-14 | `ULA_CANDIDATE` ve `knowledge_gap` `GAP` değil | WARNING | Kullanıcıya göster. Override kaydı yoksa sor. |
| E-15 | Aynı `concept` için birden fazla `OPEN` debt | WARNING | Kullanıcıya göster. Otomatik birleştirme yapma. |

E-10 için çözüm: `event_id` içindeki `<learning-pass-id>` ile `docs/learning/passes/<learning-pass-id>/LEARNING_PASS.md` bulunur. Event o dosyada yoksa FAIL.

FAIL olduğunda pass dosyası ve queue §B yazılmaz. Ledger Human Sync sırasında zaten yazılmaz.

Bu bölüm ULA content audit yapmaz.

---

## U. ULA and Pass Integrity

Ne zaman çalışır:

- Startup'ta, active pass taramasında (U-15).
- Her stage geçişinden önce (`04_ULA_PROTOCOL.md` §5).
- Completion Commit'ten önce ve pass `COMPLETE` yazılmadan önce.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| U-01 | Unknown `ula_mode` | FAIL | Dur. |
| U-02 | Unknown `ula_status`, `pass_status` veya `current_stage` | FAIL | Dur. |
| U-03 | Aynı event için birden fazla routing satırı veya aktif LIGHT + FULL artifact | FAIL | Dur. |
| U-04 | Routing satırı veya artifact tanımsız event'e ya da `ULA_CANDIDATE` olmayan event'e bağlı | FAIL | Dur. |
| U-05 | FULL `CONTENT.md` var, `ARCHITECTURE.md` `FROZEN` değil | FAIL | Builder çıktısını kullanma. Dur. |
| U-06 | FULL `AUDIT.md` var, `CONTENT.md` yok | FAIL | Dur. |
| U-07 | `architecture_status: FROZEN`, `approved_by: user` veya `approved_at` yok | FAIL | Dur. Kullanıcı review iste. |
| U-08 | LIGHT artifact'te L0, L1 veya L2 bölümü boş | FAIL | Dur. |
| U-09 | LIGHT `COMPLETE` ve self-check'te FAIL var | FAIL | Dur. |
| U-10 | FULL `COMPLETE` ve son audit round freeze-ready değil | FAIL | Dur. |
| U-11 | Pass `COMPLETE` ve scope unit'inin ledger `open_items` alanı dolu | FAIL | `COMPLETE` yazma. |
| U-12 | Pass `COMPLETE` ve bir ULA event `COMPLETE` değil | FAIL | `COMPLETE` yazma. |
| U-13 | Pass `ABANDONED` ve abandon sonrası ledger'da bu pass ID ile değişiklik var | FAIL | Dur. Kullanıcıya göster. |
| U-14 | Resume sırasında `COMPLETE` / `FROZEN` artifact revision route olmadan yeniden yazıldı | FAIL | Dur. |
| U-15 | İki active pass aynı work unit veya event'i içeriyor | FAIL | `CONFLICT` göster. Yeni pass'i başlatma. |
| U-16 | `ula_status` `PENDING` değil ve artifact path boş veya dosya yok | FAIL | Pass `BLOCKED`. |
| U-17 | Full trigger var ama mode `LIGHT` (user override) | WARNING | Sınırı kullanıcıya bir kez göster. Devam et. |
| U-18 | Event `BLOCKED` (revision limit veya reject) | WARNING | Kullanıcıya raporla. Diğer event'lere devam et. |

FAIL olduğunda stage geçişi, Completion Commit ve pass status değişikliği yapılmaz.

Bu bölüm ULA content audit yapmaz. Content audit `ula/LEARNING_AUDITOR.md` rolüne aittir.

---

## M. MindMap / Semantic Graph Integrity

Ne zaman çalışır:

- Map sync sırasında, aday graph üzerinde, write'tan önce (`05_MINDMAP_PROTOCOL.md` §8–§9).
- `/stay-in-the-loop map` komutlarında, mevcut graph ve view üzerinde (M-12, M-15, M-16).

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| M-01 | Duplicate `node_id` | FAIL | Write yok. Event `BLOCKED`. |
| M-02 | Duplicate `edge_id` | FAIL | Write yok. |
| M-03 | Edge `source_node_id` graph'ta yok | FAIL | Write yok. |
| M-04 | Edge `target_node_id` graph'ta yok | FAIL | Write yok. |
| M-05 | Unknown `relation_type` | FAIL | Write yok. |
| M-06 | Unknown `node_type` | FAIL | Write yok. |
| M-07 | Unknown `node_status` | FAIL | Write yok. |
| M-08 | Combined hierarchy cycle (`parent_id` + `PART_OF` edge birlikte) | FAIL | Write yok. |
| M-09 | Node kendi parent'ı veya kendi `PART_OF` hedefi | FAIL | Write yok. |
| M-10 | `SUPERSEDED` ve `superseded_by` boş veya geçersiz | FAIL | Write yok. |
| M-11 | Duplicate semantic edge (aynı source, relation, target) | FAIL | Write yok. |
| M-12 | View graph'ta olmayan node gösteriyor | WARNING | View'ı yeniden üret. |
| M-13 | `source_artifacts` path'i yok | FAIL | Write yok. |
| M-14 | `available_depth` içindeki seviye için artifact / bölüm yok | FAIL | Write yok. |
| M-15 | `generated_from_graph_version > graph_version` | FAIL | View'ı yeniden üret. Kullanıcıya bildir. |
| M-16 | Stale `HORIZONTAL_MAP` (`generated_from_graph_version < graph_version`) | WARNING | View'ı yeniden üret. |
| M-17 | Bir node veya edge listesinde duplicate `source_event_id` / appearance | FAIL | Write yok. |
| M-18 | `map_sync_status: COMPLETE` ama event graph'ta hiçbir node veya edge'de yok | FAIL | Status'u `PENDING` yap. Sync tekrar. |
| M-19 | `ACTIVE` node veya edge kaynağı `UNRESOLVED` veya tamamlanmamış ULA event | FAIL | Write yok. |
| M-20 | `DEBT` node ve `debt_id` boş ya da §B'de yok | FAIL | Write yok. |
| M-21 | Primary parent ayrıca `PART_OF` edge olarak yazılmış (`node.parent_id = X` ve `node PART_OF X`) | FAIL | Write yok. |
| M-22 | Birden fazla `ROOT` node | FAIL | Write yok. |

FAIL olduğunda graph overwrite edilmez, `graph_version` değişmez, view yeniden üretilmez. Coverage ve pass status değişmez.

---

## P. Knowledge Persistence Integrity

Ne zaman çalışır:

- Persistence sırasında, bütün candidate set üzerinde, write'tan önce (`06_KNOWLEDGE_PERSISTENCE.md` §22).
- Final integrity'de, project state ve yüklenmiş personal dosyalar üzerinde.

Kapsam: Personal library yalnız registry + işlemdeki Home + ilgili map ile kontrol edilir. Bütün library yüklenmez. Map satırlarında yalnız current `project_id` satırları doğrulanır.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| P-01 | Duplicate `concept_id` (registry satırı veya Home dosyası) | FAIL | Write yok. Event `BLOCKED`. |
| P-02 | Duplicate `experience_id` | FAIL | Write yok. |
| P-03 | Registry satırı var, Home dosyası yok | FAIL | Write yok. |
| P-04 | Home dosyası var, registry satırı yok | FAIL | Write yok. |
| P-05 | İki `ACTIVE` registry satırı aynı `Canonical Name` | FAIL | Write yok. Kullanıcı: farklı canonical name veya merge. |
| P-06 | Alias başka bir `ACTIVE` concept'in canonical name veya alias'ı ile çakışıyor | FAIL | Write yok. Kullanıcı kararı. |
| P-07 | Project pointer bilinmeyen `concept_id` gösteriyor | FAIL | Write yok. |
| P-08 | Graph `home_ref` bilinmeyen `concept_id` gösteriyor | FAIL | Write yok. |
| P-09 | Aynı `event_id` için birden fazla Experience Note | FAIL | Write yok. |
| P-10 | Concept Home içinde duplicate Project Appearance (`project_id`, `event_id`) | FAIL | Write yok. |
| P-11 | Experience Note `L0`–`L4` başlığı veya Home section metni taşıyor | FAIL | Write yok. Teoriyi çıkar. |
| P-12 | `RESOLVED` debt: `resolution_ref` ULA `COMPLETE` event değil veya event persistence `COMPLETE` değil veya `concept_home` çözülemiyor | FAIL | Write yok. |
| P-13 | `RESOLVED` debt ve `debt_id` taşıyan graph node hâlâ `DEBT` | FAIL | Write yok. |
| P-14 | Promoted `ACTIVE` node (`debt_id` var, debt `RESOLVED`) ve `home_ref: UNASSIGNED` | FAIL | Write yok. |
| P-15 | `DISMISSED` debt ve `resolution_ref` `user:` kararı değil | FAIL | Write yok. |
| P-16 | Persistence `COMPLETE` ama pass tablosundaki Home / pointer / Experience Note / Decision Record dosyası yok | FAIL | Status `PENDING`. Tekrar persistence. |
| P-17 | `personal_library_path: UNCONFIGURED` ve personal write candidate'i var | FAIL | Write yok. `06` §2.2. |
| P-18 | `LOCAL_TEMPORARY` concept `personal:` olarak işaretli veya personal Home'u yok iken pointer `PERSONAL` | FAIL | Write yok. |
| P-19 | Promotion `concept_id` değiştirdi | FAIL | Write yok. |
| P-20 | SD Experience Map satırı olmayan Experience Note gösteriyor | FAIL | Write yok. |
| P-21 | DSA Experience Map satırı olmayan Experience Note gösteriyor | FAIL | Write yok. |
| P-22 | DSA Experience Map satırı primary category `DSA` olmayan event'e ait | FAIL | Write yok. |
| P-23 | Registry ile Home Identity uyuşmuyor (`Canonical Name`, `Aliases`, `Status`, `Home`) | FAIL | Write yok. |
| P-24 | Library Index veya pointer `Canonical Name` label'ı registry / Home ile uyuşmuyor | WARNING | Index'i ve label'ı yeniden üret. |
| P-25 | Version kuralı ihlali (`06` §9): versioned alan değişti ve `Version` +1 değil, veya versioned alan değişmedi ve `Version` değişti | FAIL | Write yok. |
| P-26 | Dolu Concept Home content section'ında `Provenance:` etiketi yok veya label bilinmiyor | FAIL | Write yok. |
| P-27 | Experience Note claim `VERIFIED` ve ref yok, veya claim status kaynak event'ten güçlü | FAIL | Write yok. |
| P-28 | Project pointer (`Home Mode: PERSONAL`) L0–L4 theory section'ı taşıyor (promotion sonrası duplicate theory) | FAIL | Write yok. |

FAIL olduğunda hiçbir persistence dosyası yazılmaz. Event persistence `BLOCKED`. Coverage, ledger ve pass status değişmez.

---

## S. Human Sync State Integrity

Ne zaman çalışır:

- `/stay-in-the-loop sync` startup'ında, sync state okunduktan sonra (`08_HUMAN_SYNC_STATE.md` §11 adım 4).
- Sync record write'tan önce candidate set üzerinde ve write'tan sonra (`08` §11.1).
- Full mode record write'ta aynı sırayla (`08` §12).

Kapsam: Yalnız active project root altındaki `docs/learning/sync/` ve `LEARNING_CONFIG.project_id`. Başka project okunmaz.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| S-01 | `SYNCED` veya `STALE` unit ve `record_id` dosyası yok | FAIL | Write yok. Kullanıcıya göster. |
| S-02 | `SYNCED` unit: state veya record `checkpoint` boş veya format geçersiz | FAIL | Write yok. |
| S-03 | Record `work_unit_id` state satırı ile uyuşmuyor | FAIL | Write yok. |
| S-04 | Record `project_id` config `project_id` ile uyuşmuyor | FAIL | Write yok. Record kullanılmaz. |
| S-05 | State header `project_id` config `project_id` ile uyuşmuyor | FAIL | Write yok. Sync state kullanılmaz. |
| S-06 | Record `record_version` state değeri ile uyuşmuyor | FAIL | Write yok. |
| S-07 | Bilinmeyen `sync_status` | FAIL | Write yok. |
| S-08 | Duplicate `work_unit_id` veya `record_id` | FAIL | Write yok. |
| S-09 | `evidence_paths` boş, absolute veya project root dışında | FAIL | Write yok. |
| S-10 | `depends_on` state'te olmayan unit gösteriyor | FAIL | Write yok. |
| S-11 | Context `project_id` config `project_id` ile uyuşmuyor | FAIL | Context kullanılmaz. Yeniden üretim yalnız kullanıcı onayı ile ve yalnız active project record'larından. |
| S-12 | State satırı olmayan record dosyası | WARNING | Bilgi ver. Silme kullanıcı kararıdır. |
| S-13 | Context `source_records` state'teki `SYNCED` `record_id@record_version` seti ile uyuşmuyor | WARNING | Context'i active project record'larından yeniden üret. |
| S-14 | Context 120 satırdan uzun | WARNING | Context'i yeniden üret. |
| S-15 | Sync-only run ledger, queue, pass, map, concept, experience veya personal library dosyası değiştirdi | FAIL | Pre-image'ları geri yükle. `08` §11. |
| S-16 | Candidate record mevcut bir record'un üzerine yazıyor ve `record_version` pre-image değeri + 1 değil | FAIL | Write yok. State path ile tekrar okunur (`08` §11). |

FAIL olduğunda sync dosyası yazılmaz. Unit önceki status'unda kalır. Eksik veya bozuk state başka project'ten yeniden kurulmaz. Coverage ve ledger değişmez.

---

## V. Knowledge View Integrity

Ne zaman çalışır:

- Her view write'tan önce candidate üzerinde ve write'tan sonra (`09_KNOWLEDGE_VIEW.md` §10).
- Final Integrity içinde (§L.3) ve `/stay-in-the-loop integrity` ile.

Kapsam: Yalnız active project root altındaki `docs/learning/STAY_IN_THE_LOOP.md`. Kaynak olarak config, sync state, graph ve queue §B okunur. Ders içeriği okunmaz.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| V-01 | Internal link dosyada üretilmeyen anchor'ı gösteriyor (`09` §3.2) | WARNING | rebuild `KNOWLEDGE_VIEW` link'i taşıyan section |
| V-02 | Aynı HS veya KN section ID'si birden fazla | FAIL | View write yok. Kullanıcıya göster. |
| V-03 | Marker eşleşmesi bozuk: END'siz START, START'sız END, iç içe section veya bilinmeyen `SITL:` marker | FAIL | View write yok. Kullanıcıya göster. |
| V-04 | KN marker ID, anchor ve heading ID farklı; veya KN ID graph'ta yok | FAIL | View write yok. Kullanıcıya göster. |
| V-05 | `SITL:VIEW` `project_id` config ile farklı; veya HS ID bu project'in sync state'inde yok | FAIL | View kullanılmaz. Write yok. |
| V-06 | HS status satırı state `sync_status` ile uyuşmuyor (`09` §5) | WARNING | rebuild `KNOWLEDGE_VIEW` HS section |
| V-07 | Section eski: HS `v` ≠ `record_version`; KN `depth` ≠ `available_depth`; KN adı ≠ `canonical_name` | WARNING | rebuild `KNOWLEDGE_VIEW` section |
| V-08 | İçerik var ama section yok: `SYNCED` / `STALE` record, depth'li `ACTIVE` node, `OPEN` debt; view var ama `DEBT` veya `JOURNEY` section yok (`09` §3); veya view yok | WARNING | rebuild `KNOWLEDGE_VIEW` section (`09` §12) |
| V-09 | Section içinde kapanmamış code fence veya dengesiz `<details>` | FAIL | View write yok. Kullanıcıya göster. |
| V-10 | HS / KN section'ında kendi `###` heading'i dışında `#`–`###` heading; diğer section'da kendi `##` heading'i dışında `#`–`###` heading | FAIL | View write yok. Kullanıcıya göster. |
| V-11 | `UNSYNCED` unit için HS section; `DEBT` / `SUPERSEDED` node için KN section; veya `available_depth` dışında level | WARNING | rebuild `KNOWLEDGE_VIEW` section |
| V-12 | Dosya var ama `SITL:VIEW` header'ı yok | FAIL | Overwrite yok. Kullanıcı karar verir. |
| V-13 | Sync-only run KN, MAP veya DEBT section'ı değiştirdi | FAIL | Pre-image geri yüklenir (`08` §11). |
| V-14 | MAP node'u graph'ta yok veya label `map_label_max_chars` sınırını aşıyor | WARNING | rebuild `KNOWLEDGE_VIEW` MAP |
| V-15 | HS HUMAN katmanında ilk geçişte tanımsız proje sembolü (`09` §5.2) | WARNING | Rapor edilir. Record sonraki refresh'te düzeltilir (`03` §5). |
| V-16 | Navigation anchor'ı (`09` §3.2) birden fazla üretiliyor | WARNING | Rapor edilir. Çakışan heading kaynağında düzeltilir. |
| V-17 | Section navigation'ı graph veya `09` §3.1 / §6.3 ile uyuşmuyor: breadcrumb, parent, reading order veya Project Home dönüşü | WARNING | rebuild `KNOWLEDGE_VIEW` section |
| V-18 | `JOURNEY` Human Sync state veya record Purpose ile uyuşmuyor: node, sıra, revision grubu, status, current position veya link (`09` §5.4) | WARNING | rebuild `KNOWLEDGE_VIEW` JOURNEY |

- Candidate FAIL → view yazılmaz. Authoritative write geri alınmaz. Sonuç WARNING olarak raporlanır.
- Mevcut dosyada FAIL → Final Integrity FAIL. View bozuk veya yanıltıcıdır. Tam rebuild yalnız kullanıcı onayı ile yapılır (`09` §12).
- WARNING repair yalnız gösterilen section'ı yazar. Diğer section'lar değişmez.
- V-15 view repair ile düzelmez. View record metnini değiştirmez. Repair V-15 için section yazmaz.
- V-16 view repair ile düzelmez. Çakışma artifact, record veya label metnindedir. Repair V-16 için section yazmaz.

---

## L. Learning State / Cross-Layer Integrity

Final Integrity bu bölümdür. Run loop'un son adımıdır (`01` §1 adım 15). `/stay-in-the-loop integrity` aynı işi yapar (§L.6).

§C, §E, §U, §M, §P, §V kurallarını tekrar etmez. Yalnız layer'lar arası invariant'ları kontrol eder. Bir L check bir alt check ile aynı sonucu veriyorsa satırda kaynak check yazılır.

### L.1 Authority model

| Artifact | Class | Konum | Kaynak | Auto repair |
|---|---|---|---|---|
| `LEARNING_CONFIG` | AUTHORITATIVE | `state/LEARNING_CONFIG.md` | kullanıcı | NO |
| `COVERAGE_LEDGER` | AUTHORITATIVE | `state/COVERAGE_LEDGER.md` | Discovery / Scope / Completion Commit | NO |
| `LEARNING_QUEUE §B` | AUTHORITATIVE | `state/LEARNING_QUEUE.md` §B | Handoff, persistence | NO |
| `LEARNING_PASS` | AUTHORITATIVE | `passes/<learning-pass-id>/LEARNING_PASS.md` | Human Sync, ULA, completion, sync | NO |
| `ULA_ARTIFACT` | AUTHORITATIVE | `passes/<learning-pass-id>/ula/<event-id>/` | ULA | NO |
| `SEMANTIC_GRAPH` | AUTHORITATIVE | `maps/SEMANTIC_GRAPH.md` | map sync, persistence `home_ref` | NO |
| `CONCEPT_REGISTRY` | AUTHORITATIVE | `<personal_library_path>/registry/CONCEPT_REGISTRY.md` | persistence | NO |
| `CONCEPT_HOME` | AUTHORITATIVE | personal `concepts/` veya `LOCAL_TEMPORARY` project `concepts/` | persistence | NO |
| `CONCEPT_POINTER` | AUTHORITATIVE | project `concepts/` | persistence | NO (yalnız label: P-24) |
| `EXPERIENCE_NOTE` | AUTHORITATIVE | project `experiences/EX-*.md` | persistence | NO |
| `DECISION_RECORD` | AUTHORITATIVE | project `experiences/DR-*.md` | persistence | NO |
| `EXPERIENCE_MAP` | AUTHORITATIVE | personal `experience-maps/` | persistence | NO |
| `LEARNING_STATE` | DERIVED | `state/LEARNING_STATE.md` | `COVERAGE_LEDGER` | YES |
| `LEARNING_QUEUE §A` | DERIVED | `state/LEARNING_QUEUE.md` §A | `COVERAGE_LEDGER` | YES |
| `HORIZONTAL_MAP` | DERIVED | `maps/HORIZONTAL_MAP.md` | `SEMANTIC_GRAPH` | YES |
| `LIBRARY_INDEX` | DERIVED | `<personal_library_path>/LIBRARY_INDEX.md` | registry + Concept Home | YES |
| `KNOWLEDGE_VIEW` | DERIVED | `docs/learning/STAY_IN_THE_LOOP.md` | sync record + state, graph, `COMPLETE` ULA artifact, queue §B (`09` §1) | YES (section) |
| `WRITE_LOCK` | LOCK | `<personal_library_path>/.learning-write-lock/` | persistence | NO (kullanıcı kararı, `06` §22.1) |

- `DERIVED` artifact bozuksa kaynağından yeniden üretilir. Kaynak değişmez.
- `AUTHORITATIVE` artifact için otomatik semantic repair yoktur. Sonuç FAIL. Kullanıcı review eder.
- Tek istisna §P içinde zaten tanımlıdır: `CONCEPT_POINTER` label yeniden üretimi (P-24).

### L.2 Final integrity result

| Result | Şart | DONE |
|---|---|---|
| `PASS` | FAIL yok. WARNING yok. | YES |
| `PASS_WITH_WARNINGS` | FAIL yok. En az bir WARNING var. | YES |
| `FAIL` | En az bir FAIL var. | NO |

- Sonuç derived repair sonrası ikinci çalıştırmadan alınır (L-20).
- WARNING repair ile kapandıysa ve yeni WARNING yoksa sonuç `PASS` olur.

### L.3 Procedure

```text
LOAD        §L.7 sırası; yalnız gereken artifact
↓
CHECK 1     §C + §E + §U + §M + §P (mevcut state) + §V + §L checks
↓
FAIL var?   evet → sonuç FAIL. Repair yok. Kullanıcıya göster. Dur.
↓
REPAIR      yalnız DERIVED artifact; aksiyonu "rebuild" olan WARNING
↓
CHECK 2     bütün check'ler tekrar
↓
RESULT      CHECK 2 sonucu (§L.2)
```

- FAIL varken derived repair yapılmaz. Bozuk authoritative kaynaktan derived üretilmez.
- Run loop adım 15 derived repair'ı onaysız yapar. `/stay-in-the-loop integrity` önce listeyi gösterir ve onay ister.

### L.4 Coverage independence

Pass `COMPLETE` iken `Map Sync` veya `Experience Persistence` `BLOCKED` / `PENDING` olabilir. Bu bir post-completion enrichment açığıdır. FAIL değildir. Coverage yeniden açılmaz. Pass status değişmez (`05` §10.2, `06` §19.1).

### L.5 Checks

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| L-01 | `LEARNING_STATE` sayıları ledger'dan farklı (kaynak: C-08) | WARNING | rebuild `LEARNING_STATE` |
| L-02 | Queue §A ≠ ledger `DEFERRED ∪ PARTIAL` (kaynak: C-09) | WARNING | rebuild `LEARNING_QUEUE §A` |
| L-03 | §B debt `originating_event_id` hiçbir pass dosyasındaki event'e çözülmüyor (kaynak: E-07) | FAIL | Dur. Kullanıcı review. |
| L-04 | `RESOLVED` debt: `resolution_ref` event'inin persistence'ı `COMPLETE` değil, `concept_home` registry'de veya `LOCAL_TEMPORARY` Home'larda yok, `debt_id` taşıyan node `ACTIVE` değil, veya node `home_ref` ≠ `concept_home` | FAIL | Dur. Kullanıcı review. |
| L-05 | Pass `selected_scope` içindeki `work_unit_id` ledger'da yok | FAIL | Dur. Kullanıcı review. |
| L-06 | Event `Work Units` kendi pass `selected_scope` dışında (kaynak: E-02) | FAIL | Dur. Kullanıcı review. |
| L-07 | Pass `COMPLETE` ve: scope unit ledger satırı `PARTIAL` veya `open_items` dolu, ULA event `COMPLETE` değil, veya `UNRESOLVED` event var (kaynak: U-11, U-12) | FAIL | Dur. Kullanıcı review. |
| L-08 | Pass `COMPLETE` ve event `Map Sync` veya `Experience Persistence` `BLOCKED` / `PENDING` (§L.4) | WARNING | Bilgi ver. Coverage ve pass değişmez. |
| L-09 | `Map Sync: COMPLETE` ve event ID graph'ta hiçbir node / edge `source_event_ids` içinde yok, veya pass `Node IDs` graph'ta yok (kaynak: M-18) | FAIL | Dur. Kullanıcı review. |
| L-10 | `Experience Persistence: COMPLETE` ve routing'in istediği Concept Home / pointer / Experience Note yok; veya `NOT_APPLICABLE` ve routing artifact istiyor (kaynak: P-16) | FAIL | Dur. Kullanıcı review. |
| L-11 | Graph `home_ref: CH-...` registry'de ve `LOCAL_TEMPORARY` Home'larda yok (kaynak: P-08) | FAIL | Dur. Kullanıcı review. |
| L-12 | Pointer `personal:CH-...` registry'de yok veya registry satırı Home dosyasına çözülmüyor. Configured library erişilemiyorsa sonuç WARNING. | FAIL | Dur. Kullanıcı review. |
| L-13 | Current project Experience Map satırı (`PRJ-x/EX-y`) project `experiences/` içinde dosyaya çözülmüyor (kaynak: P-20, P-21) | FAIL | Dur. Kullanıcı review. |
| L-14 | Decision Record ↔ Experience Note çift yönlü değil: note `Decision Record` dosyası yok, veya DR `Experience ID` note'u bu DR'yi göstermiyor | FAIL | Dur. Kullanıcı review. |
| L-15 | İki active pass (`IN_PROGRESS` / `WAITING_USER` / `BLOCKED`) aynı work unit'i içeriyor (kaynak: U-15) | FAIL | Dur. `CONFLICT`. |
| L-16 | `ABANDONED` pass: ledger satırı bu pass ID ile `COVERED` / `NOT_LEARNING_RELEVANT`, veya ledger `open_items` bu pass'in event'ini gösteriyor ve event pass dosyasında yok | FAIL | Dur. Kullanıcı review. |
| L-17 | Config `project_id` ile Experience Note, Decision Record, bu project'in note'una bağlı Home appearance veya map satırı farklı `project_id` taşıyor. Project rename `project_id` değiştirmez. | FAIL | Dur. Kullanıcı review. |
| L-18 | `HORIZONTAL_MAP` `generated_from_graph_version` < `graph_version` (kaynak: M-16) | WARNING | rebuild `HORIZONTAL_MAP` |
| L-19 | `LIBRARY_INDEX` registry + Home'lardan üretilen index ile aynı değil | WARNING | rebuild `LIBRARY_INDEX` |
| L-20 | Derived repair yapıldı ve check'ler tekrar çalışmadı | FAIL | CHECK 2'yi çalıştır. |
| L-21 | Bu session'ın `.learning-write-lock/` dizini persistence bittikten sonra hâlâ var (release başarısız) | WARNING | Lock bilgisini göster. Silme kararı kullanıcıdadır (`06` §22.1). |
| L-22 | Experience Note `Concept ID` (`CH-...`) registry'de ve `LOCAL_TEMPORARY` Home'larda yok | FAIL | Dur. Kullanıcı review. |
| L-23 | Experience Note `Event ID` pass dosyasında yok, veya pass `## Knowledge Persistence` satırı başka `Experience ID` gösteriyor | FAIL | Dur. Kullanıcı review. |

Identity chain (golden path):

```text
WORK UNIT → LEARNING EVENT → ULA ARTIFACT → GRAPH NODE → CONCEPT HOME → EXPERIENCE NOTE → EXPERIENCE MAP
```

Her halka bir check ile çözülür: L-05 / L-06, U-16, L-09, L-11 / L-12, L-22 / L-23, L-13. Kırık halka FAIL verir.

Kapsam: Personal library yalnız configured ise ve check gerektiriyorsa yüklenir. Map satırlarında yalnız current `project_id` satırları doğrulanır.

### L.6 Command

`/stay-in-the-loop integrity`:

- Yeni Learning Pass başlatmaz.
- Coverage, ledger, pass, graph ve Concept Home yazmaz.
- ULA çalıştırmaz.
- §L.3 akışını çalıştırır. Derived repair listesini gösterir. Kullanıcı onayı ile yalnız `DERIVED` artifact yazar.
- Sonuç: `PASS` / `PASS_WITH_WARNINGS` / `FAIL` ve check listesi.

### L.7 Load order

```text
SKILL.md
↓
07_INTEGRITY_CHECKS.md
↓
LEARNING_CONFIG + LEARNING_STATE
↓
COVERAGE_LEDGER + LEARNING_QUEUE
↓
yalnız gereken pass, graph, view, concepts/, experiences/, `STAY_IN_THE_LOOP.md` marker satırları
↓
personal registry + ilgili Home + ilgili map + index  (yalnız configured ve gerekli ise)
```

Yüklenmez: `00_MASTER_SYSTEM_SPEC.md`, `ula/` rol dosyaları, example / historical material, ULA artifact içeriği (yalnız varlık kontrolü), diğer project'lerin Experience Note'ları.

---

## Authoritative Source

- Phase 1 audit: Bölüm 15.1, 17 (M-16), 18.
- `references/02_COVERAGE_PROTOCOL.md` §1, §9, §10.
- `references/03_HUMAN_SYNC_PROTOCOL.md` §7, §9, §13, §14, §15.
- `references/04_ULA_PROTOCOL.md` §2, §5, §7, §9, §10, §11.
- `references/05_MINDMAP_PROTOCOL.md` §3–§11.
- `references/06_KNOWLEDGE_PERSISTENCE.md` §4–§22.
- `references/09_KNOWLEDGE_VIEW.md` §1–§12.
- Cross-layer ve final integrity: Phase 8 audit.
- Content audit: `ula/LEARNING_AUDITOR.md`.
