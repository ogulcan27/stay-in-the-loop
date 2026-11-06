# 08 — Human Sync State

**Status:** IMPLEMENTED

## Purpose

Human Synchronization çıktısını work unit bazında kalıcı ve incremental yapar.
`/stay-in-the-loop sync` standalone mode'unu tanımlar.
Önceden senkronize edilmiş işi tekrar okumadan proje mental modelini güncel tutar.

## Responsibility

- `docs/learning/sync/` state, record ve rolling context.
- Sync status: `UNSYNCED`, `SYNCED`, `STALE`.
- Evidence checkpoint ve scoped staleness.
- Sync scope ve retrieval plan.
- Standalone sync run loop ve STOP sınırı.
- Full mode Human Sync reuse.

## Must Not

- İkinci bir Human Synchronization tanımı yapmaz. İçerik kuralları `03` §4–§7'dedir.
- Ledger, queue, pass, graph, Concept Home, Experience Note veya personal library yazmaz.
- Learning Event, Knowledge Priority, Knowledge Debt veya ULA üretmez.
- Bütün repository'yi okumaz.
- Başka project'in sync state'ini okumaz veya yazmaz (01 §0).

---

## 1. Semantic boundary

```text
HUMAN SYNCHRONIZATION = project comprehension
ULA                   = technical / theoretical learning
```

Hard invariant:

```text
Human Sync complete ≠ concept learned
Human Sync complete ≠ ULA complete
Human Sync complete ≠ learning coverage complete
```

- Sync status yalnız Human Sync'e aittir. Ledger'a yazılmaz.
- Coverage status (`02` §7) sync yüzünden değişmez.

| Work unit | Human Sync | Learning coverage |
|---|---|---|
| Step 1 | `SYNCED` | `UNCOVERED` |
| Step 2 | `SYNCED` | `COVERED` |
| Step 3 | `SYNCED` | `DEFERRED` |
| Step 4 | `UNSYNCED` | `UNCOVERED` |

Bu tablo geçerli bir durumdur.

---

## 2. Modes

| Komut | Mode | Akış |
|---|---|---|
| `/stay-in-the-loop` | FULL | `01` §1. Human Sync stage'i bu dosyanın reuse kuralını kullanır (§12). |
| `/stay-in-the-loop sync ...` | SYNC_ONLY | §11. Human Sync persist edilir. Sonra STOP. |

İki mode aynı Human Sync protocol'ünü (`03` §4–§7) ve aynı sync state'i kullanır. Ayrı Human Sync history yoktur.

---

## 3. Storage

```text
<ACTIVE_PROJECT_ROOT>/docs/learning/sync/
├── HUMAN_SYNC_STATE.md      ← templates/HUMAN_SYNC_STATE_TEMPLATE.md
├── PROJECT_SYNC_CONTEXT.md  ← templates/PROJECT_SYNC_CONTEXT_TEMPLATE.md
└── records/
    └── HS-xxxxxxxx.md       ← templates/HUMAN_SYNC_RECORD_TEMPLATE.md
```

| Artifact | Authority | Rebuild | İçerik |
|---|---|---|---|
| `HUMAN_SYNC_STATE.md` | AUTHORITATIVE | NO | Sync status, record mapping, checkpoint, evidence paths, dependencies, position |
| `records/HS-*.md` | AUTHORITATIVE | NO | Work unit başına sıkıştırılmış mental model |
| `PROJECT_SYNC_CONTEXT.md` | DERIVED | YES | Projenin şu anki rolling modeli |

- Dosyalar yalnız project initialize edildikten sonra oluşur (`02` §11). Yalnız gerektiğinde oluşur.
- Sync state project state'tir. Personal library'ye yazılmaz.
- Çelişki varsa state kazanır. Context state ve record'lardan yeniden üretilir.

### 3.1 Sync status

| Status | Anlam |
|---|---|
| `UNSYNCED` | Geçerli Human Sync record yok. |
| `SYNCED` | Unit'in evidence'ı için güncel record var. |
| `STALE` | Record var. Unit'in evidence'ı material olarak değişti. |

- Discovery ile bulunan yeni unit `UNSYNCED` olarak eklenir.
- `STALE` record refresh olmadan güncel kabul edilmez.
- Satır silinmez.

### 3.2 State fields

Header: `project_id` (`LEARNING_CONFIG.project_id` ile aynı).

| Alan | Anlam |
|---|---|
| `work_unit_id` | `02` §4 normalized ID. Ledger ile aynı ID. |
| `seq` | `02` §2 sırası |
| `label` | Kısa ad |
| `sync_status` | §3.1 |
| `record_id` | `HS-xxxxxxxx` veya `-` |
| `record_version` | Tam sayı veya `-`. Her refresh +1. |
| `checkpoint` | §5 |
| `evidence_paths` | `;` ile ayrılmış project-relative path listesi (§5.1) |
| `depends_on` | `;` ile ayrılmış `work_unit_id` listesi veya `-` |
| `synced_at` | `YYYY-MM-DD` veya `-` |

`position` = record'u olan (`SYNCED` veya `STALE`) en yüksek `seq`. Record yoksa `0`. Saklanmaz; tablodan hesaplanır.

---

## 4. Record

Format: `templates/HUMAN_SYNC_RECORD_TEMPLATE.md`.

- `record_id` = `HS-` + `sha256(work_unit_id)` ilk 8 hex karakter. Work unit başına tek record.
- Record alanları `03` §5 alanlarıdır, unit seviyesinde. Ek alanlar: Dependencies, Downstream Impact, Checkpoint.
- Record kod, uzun kaynak metin veya teori dersi taşımaz. Teorik konu `GENERAL THEORY` etiketiyle bir cümle olur.
- Amaç: Proje aylar sonra açılınca bu unit ham geçmiş okunmadan anlaşılır.
- Refresh mevcut record'u günceller. Yeni record açmaz.
- Record `checkpoint` = record içeriğinin üretildiği checkpoint. State `checkpoint` = son doğrulanmış checkpoint. Non-material değişimde yalnız state ilerler (§6).

---

## 5. Checkpoint

| Durum | `checkpoint` | Değişim kontrolü |
|---|---|---|
| Git repository, en az bir commit, `evidence_paths` temiz | `git:<HEAD ilk 12 hex>` | `git diff --quiet <commit> -- <evidence_paths>` |
| Diğer | `fp:<16 hex>` | Fingerprint yeniden hesaplanır ve karşılaştırılır |

Fingerprint: `evidence_paths` altındaki her dosya için `<relative path>\t<sha256(file bytes)>` satırı. Satırlar sıralanır. `sha256(satırlar)` ilk 16 hex.

- File modification time checkpoint değildir.
- Repository HEAD değişimi tek başına unit'i değiştirmez. Kontrol yalnız o unit'in `evidence_paths` değerine bakar.

### 5.1 Evidence paths

- Unit'in evidence'ının oluşturduğu veya değiştirdiği dosya / dizinler.
- Path project-relative olur. `<ACTIVE_PROJECT_ROOT>` dışını gösteremez.
- Work unit listesini tutan ortak doküman (ör. phase-doc kaynağı) path olarak eklenmez. Böylece bir step metni diğer unit'leri bozmaz.
- Liste boş kalamaz. Dosya evidence'ı yoksa unit'in source dokümanı kullanılır.

---

## 6. Staleness

Startup'ta her `SYNCED` unit için §5 değişim kontrolü çalışır. Bu kontrol içerik okumaz.

```text
değişim yok  → SYNCED kalır
değişim var  → yalnız delta okunur → materiality kararı
```

Delta: `git diff <commit> -- <evidence_paths>` veya değişen dosyalar. Unit'in eski evidence'ının tamamı okunmaz.

| Delta türü | Sonuç |
|---|---|
| `BEHAVIOUR` | `STALE` |
| `INTERFACE` | `STALE` |
| `FLOW` | `STALE` |
| `DECISION` | `STALE` |
| `DEPENDENCY` | `STALE` |
| `FORMAT` | `SYNCED`; checkpoint ilerler, record değişmez |
| `TYPO` | `SYNCED`; checkpoint ilerler, record değişmez |
| `COMMENT` | `SYNCED`; checkpoint ilerler, record değişmez |
| `UNKNOWN` | `STALE` |

- Unit'in `evidence_paths` değerine dokunmayan değişiklik o unit'i değiştirmez.
- `STALE` dependent unit'lere otomatik yayılmaz. Yalnız §6.1 impact kararı ile yayılır.
- Sonraki bir unit, önceki unit'in dosyalarını değiştirirse önceki unit kendi kontrolü ile `STALE` olur.
- Staleness sonucu (`STALE` veya checkpoint ilerlemesi) hedef boş olsa da state'e yazılır (§11.1).

### 6.1 Dependency freshness

Bir unit bu run'da material değişimle `STALE` olursa (§6), ona açıkça bağlı record'lar değerlendirilir.

| rule | value |
|---|---|
| edges | EXPLICIT_DEPENDS_ON |
| evidence | RECORDS_FIRST |
| transitive | ON_MATERIAL_IMPACT |

- Edge yalnız state'teki `depends_on` değeridir. Sonraki `seq`, yakın dosya veya benzer ad dependency değildir.
- Impact girdisi: upstream delta + upstream record + dependent record. Dependent'ın ham evidence'ı okunmaz.
- Soru: Dependent record'un dayandığı bir şey upstream delta ile değişti mi?

| Impact | Dependent sonucu |
|---|---|
| `CONTRACT` | `STALE` |
| `DATA_SEMANTICS` | `STALE` |
| `INVARIANT` | `STALE` |
| `IO_BEHAVIOUR` | `STALE` |
| `DECISION_REVERSAL` | `STALE` |
| `DEPENDENCY_BEHAVIOUR` | `STALE` |
| `NONE` | `SYNCED` |
| `UNKNOWN` | `STALE` |

- `NONE`: Dependent record değişen şeye dayanmıyor (ör. ilgisiz internal refactor).
- `UNKNOWN`: Record'lar kararı vermeye yetmiyor. Sonuç `STALE`. Karar için ham evidence okunmaz.
- Upstream değişimi non-material ise (§6 `FORMAT`, `TYPO`, `COMMENT`) değerlendirme yapılmaz.
- Transitive: Değerlendirme yalnız `STALE` olan dependent'tan devam eder. `NONE` sonucu zinciri durdurur.
- Her unit bir run'da en fazla bir kez değerlendirilir.
- Dependency ile `STALE` olan unit'in refresh delta'sı upstream delta'dır (§8 `DELTA`).
- Context yeniden üretilir. Yeni `STALE` record current context kaynağı olmaz (§10).

---

## 7. Sync scope

Scope dili `02` §8.1 ile aynıdır. Hedef set'ler sync status üzerinden hesaplanır.

| Argüman | Hedef | Soru |
|---|---|---|
| `sync` | `UNSYNCED_AFTER ∪ STALE` | Sorma |
| `sync latest` | `CURRENT` | Sorma |
| `sync pending` | `UNSYNCED_BEFORE ∪ STALE` | Sorma |
| `sync catch-up` | `UNSYNCED_AFTER ∪ UNSYNCED_BEFORE ∪ STALE` | Sorma |
| `sync <work-unit-id>` / aralık | `MATCH` | Eşleşme yoksa sor |

| Set | Tanım |
|---|---|
| `UNSYNCED_AFTER` | `seq > position` ve `UNSYNCED` |
| `UNSYNCED_BEFORE` | `seq ≤ position` ve `UNSYNCED` |
| `STALE` | Bütün `STALE` unit'ler |
| `CURRENT` | En yüksek `seq` unit. `SYNCED` ise hedef boştur. |
| `MATCH` | Argümanla eşleşen unit'ler |

- Hedefler `seq` sırasıyla işlenir.
- Record'u olmayan project'te `position = 0`. Bu nedenle `sync` bütün unit'leri current noktaya kadar işler.
- Hedef dışındaki unit'in status'u değişmez. Sync scope ledger'a Scope Commit yazmaz.
- Hedef boşsa ve `STALE` yoksa: "Human Sync güncel." de. STOP.
- Hedef boş ama `STALE` varsa: `STALE` unit'leri göster ve `sync pending` öner. Refresh yapma.

---

## 8. Retrieval plan

Evidence okumadan önce plan kurulur.

```text
STATE FIRST → TARGET SELECTION → MINIMUM CONTEXT → TARGETED EVIDENCE → DELTA PROCESSING → COMPRESSED PERSISTENCE
```

| Hedef status | Okunur | Okunmaz |
|---|---|---|
| `UNSYNCED` | `CONTEXT`, `DEP_RECORDS`, `RAW_EVIDENCE` | `OTHER_RAW_EVIDENCE`, `UNRELATED_RECORDS` |
| `STALE` | `CONTEXT`, `DEP_RECORDS`, `OWN_RECORD`, `DELTA` | `RAW_EVIDENCE`, `OTHER_RAW_EVIDENCE`, `UNRELATED_RECORDS` |
| `SYNCED` | — | `RAW_EVIDENCE`, `OWN_RECORD` |

| Kod | Anlam |
|---|---|
| `CONTEXT` | `PROJECT_SYNC_CONTEXT.md` |
| `DEP_RECORDS` | Yalnız `depends_on` unit'lerinin record'ları |
| `RAW_EVIDENCE` | Hedef unit'in evidence'ı (`03` §4) |
| `OWN_RECORD` | Hedef unit'in mevcut record'u |
| `DELTA` | §6 delta; dependency ile `STALE` olan unit için upstream delta (§6.1) |
| `OTHER_RAW_EVIDENCE` | Başka unit'lerin ham evidence'ı |
| `UNRELATED_RECORDS` | `depends_on` dışındaki record'lar |

Dependency tespiti ham evidence okumadan önce yapılır:

1. Unit'in özet kaynağını oku: step metni, commit mesajı, değişen path listesi.
2. Açık referans: Özet önceki bir unit'i adlandırıyorsa dependency'dir.
3. Path overlap: Değişen path önceki bir unit'in `evidence_paths` değeri içindeyse dependency'dir. Bu kontrol yalnız state'i okur.
4. Dependency `STALE` ise önce o unit refresh edilir.

Kaçınılmaz geniş okuma: State yokken discovery work unit kaynağını listeler (`02` §3). Bu adım içerik okumaz.

---

## 9. Human Sync generation

- Her hedef unit için record `03` §4–§7 kurallarıyla üretilir.
- Kullanıcıya scope başına **bir** Human Synchronization çıktısı gösterilir (`03` §5, §6). Bu çıktı hedef record'lardan sıkıştırılır.
- Record kalıcı unit hafızasıdır. Kullanıcıya work unit başına ayrı anlatım olarak gösterilmez.
- `STALE` refresh: mevcut record + delta. Değişen bölümler güncellenir. `record_version` +1.

---

## 10. Rolling context

`PROJECT_SYNC_CONTEXT.md` şu soruyu cevaplar: Proje **şu anda** nerede?

- Kaynak: yalnız `SYNCED` record'lar ve state. `STALE` record context kaynağı değildir. `STALE` unit "Open Points" altında listelenir.
- Header `source_records`: `record_id@record_version` listesi.
- Her bölüm en fazla 7 madde. Dosya en fazla 120 satır.
- Append edilmez. Her sync sonrası yeniden yazılır. Tarih detayı record'larda kalır.
- Objective, Current Position ve Open Points düz dille yazılır. İç ID tek başına yazılmaz (`03` §5 human-first yazım).
- View bu dosyayı `Project in 60 Seconds` olarak gösterir (`09` §5.3).

---

## 11. Sync-only run loop

```text
/stay-in-the-loop sync [argüman]
↓
 1. ROOT          01 §0. Belirlenemezse BLOCKED.
 2. STATE         config + state oku; yoksa initialization (02 §11)
 3. PROJECT ID    UNCONFIGURED ise 06 §2.1 (kullanıcı onayı); onay yoksa BLOCKED
 4. SYNC STATE    HUMAN_SYNC_STATE + PROJECT_SYNC_CONTEXT path ile oku; 07 §S
 5. DISCOVERY     02 §3–§4, salt okuma; yeni unit → UNSYNCED (bellekte)
 6. STALENESS     §6
 7. SCOPE         §7
 8. PLAN          §8
 9. EVIDENCE      yalnız plandaki kaynaklar
10. HUMAN SYNC    §9
11. WRITE         §11.1
12. OUTPUT        scope-level Human Sync + §13 footer
↓
STOP
```

- Adım 4 dosyayı tam path ile okur: `docs/learning/sync/HUMAN_SYNC_STATE.md`. Directory listing, kısaltılmış (truncated) çıktı veya hafıza yokluk kanıtı değildir. "Sync geçmişi yok" kararı yalnız bu path okununca dosya yoksa verilir.
- Active pass kontrolü (`04` §10) çalışmaz. Pass açılmaz.
- STOP sonrası Learning Event, Knowledge Priority, Knowledge Debt, ULA, Completion, map sync ve persistence çalışmaz.
- Teorik konu Knowledge Debt'e dönüşmez. Mevcut debt değişmez.
- Kullanıcıya ULA kararı sorulmaz.

| Artifact | Sync-only write |
|---|---|
| `docs/learning/sync/` | YES |
| `STAY_IN_THE_LOOP.md` | Yalnız HS, JOURNEY, MODEL, INDEX section'ları (`09` §8) |
| `LEARNING_CONFIG.md` | Yalnız `project_id` (`06` §2.1 onayı) |
| `COVERAGE_LEDGER.md` | NO |
| `LEARNING_STATE.md` | NO |
| `LEARNING_QUEUE.md` | NO |
| `passes/` | NO |
| `maps/` | NO |
| `concepts/` | NO |
| `experiences/` | NO |
| Personal Technical Library | NO |

First run initialization (`02` §11) bu tablonun dışındadır. Kendi onay kuralını kullanır.

### 11.1 Write

| rule | value |
|---|---|
| write_mode | ALL_OR_NOTHING |
| integrity | BEFORE_ANY_WRITE |
| on_write_error | RESTORE_PRE_IMAGES |
| commit_point | HUMAN_SYNC_STATE |

```text
READ        hedef dosyaların pre-image'ı (path ile; mevcut record'un record_version değeri dahil)
↓
BUILD       record'lar, state, context bellekte
↓
INTEGRITY   07 §S candidate set üzerinde
↓
WRITE       1. records/  2. PROJECT_SYNC_CONTEXT.md  3. HUMAN_SYNC_STATE.md
↓
VERIFY      07 §S yazılmış dosyalar üzerinde
↓
VIEW        09 §10: yalnız değişen HS section'ları + MODEL + INDEX (derived)
```

- Integrity FAIL → write yok. Unit önceki status'unda kalır.
- Write hatası → pre-image'lar geri yüklenir. Unit `SYNCED` yazılmaz.
- State en son yazılır. Unit yalnız state yazılınca `SYNCED` olur.
- Mevcut bir record yeniden üretilmez. Pre-image varsa yeni `record_version` = pre-image + 1 (`07` S-16).
- VIEW adımı state commit'inden sonradır. View hatası WARNING'dir. Unit `SYNCED` kalır. Önceki HS section'ları değişmez.
- Hedef boş ama staleness state'e yazıldıysa VIEW yalnız etkilenen HS status satırını, MODEL ve INDEX'i yazar.

---

## 12. Full mode reuse

Full mode Human Sync stage'inde (`03` §2 adım 3) her selected unit için:

| Unit sync durumu | Human Sync kaynağı |
|---|---|
| `SYNCED` ve §5 değişim yok | `OWN_RECORD` |
| `SYNCED` ve değişim var | §6 kararı; `STALE` ise `OWN_RECORD` + `DELTA` (önce refresh) |
| `STALE` | `OWN_RECORD` + `DELTA` (önce refresh) |
| `UNSYNCED` | `RAW_EVIDENCE` |

- Reuse yalnız Human Sync üretimini kısaltır. Learning Event, priority, disposition, ULA, Completion ve coverage kuralları değişmez.
- Event extraction record'u kullanır. Ham evidence yalnız `VERIFIED` iddia kontrolü gerekirse okunur.
- Handoff write'tan sonra (`03` §17) üretilen veya refresh edilen record'lar §11.1 ile yazılır.
- `project_id: UNCONFIGURED` ise full mode record yazmaz ve soru sormaz. Pass akışı aynıdır.

---

## 13. Output footer

```text
Human Sync: COMPLETE
Mode: SYNC ONLY
Work Units Synced: <liste veya —>
Work Units Reused: <sayı>
Stale Records Refreshed: <liste veya —>
ULA: NOT RUN
Learning Coverage: UNCHANGED
```

İsteğe bağlı tek satır: "Öğrenme için daha sonra `/stay-in-the-loop` çalıştırabilirsin."

---

## Authoritative Source

- `03_HUMAN_SYNC_PROTOCOL.md` §4–§7 (Human Sync içeriği).
- `02_COVERAGE_PROTOCOL.md` §3, §4, §8.1 (discovery, ID, scope dili).
- `06_KNOWLEDGE_PERSISTENCE.md` §2.1, §22 (project_id, atomic write).
- `01_OPERATIONAL_CORE.md` §0 (project root).
- `09_KNOWLEDGE_VIEW.md` §5, §8 (human-facing HS section).
