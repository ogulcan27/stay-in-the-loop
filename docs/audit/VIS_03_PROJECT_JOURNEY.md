# VIS-03 — Project Journey Renderer

**Tarih:** 2026-11-05
**Jira:** CLS-4 (Epic CLS-1)
**Branch:** `vis-03-project-journey`
**Bağımlılık:** VIS-01 (CLS-2), VIS-02 (CLS-3, `main` `647291f`)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor.

- Soru: Proje bugünkü durumuna nasıl geldi?
- Yeni DERIVED section `JOURNEY` (`## Project Journey`), MODEL ile Human Sync arasında (`09` §3, §5.4).
- Kaynak yalnız Human Sync authority'si: state `## Work Units` + record Purpose.
- Human Sync state / record, ULA, L0–L4 ve Knowledge Map değişmez.

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §3 `JOURNEY` satırı + structural bullet; §3.1 Start here link'i + dönüş; §3.2 `project-journey` anchor; §4 marker; §5.4 Project Journey; §8 trigger'lar; §9 retrieval satırı; §10 write sırası; §13.3 `HUMAN_SYNC` domain |
| `references/07_INTEGRITY_CHECKS.md` | V-08 eksik `JOURNEY`; V-18 journey Human Sync ile uyuşmuyor |
| `references/08_HUMAN_SYNC_STATE.md` | §11 sync-only view scope: `JOURNEY` eklendi (yalnız view write listesi; state / record kuralı değişmez) |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | `JOURNEY` bloğu; Project Home `[Project Journey]` |
| `tests/view/view_model.py` | `step_id`, `journey_tree`, `journey_line`, `render_journey`; marker, sıra, insertion, trigger; V-08 / V-18; repair |
| `tests/view/run_tests.py` | Test T: 30 check. B, F, K, O, P, Q, R, S beklentileri güncellendi (§6) |
| `tests/mutation.py` | VIS-M17 – VIS-M24 |
| `distribution/manifest.json` | `07`, `08`, `09`, template sha256 (`scripts/build-release.ps1`) |
| `README.md` | Knowledge view cümlesi: Project Journey |

## 3. Rendering

```text
## Project Journey

- [<label>](#hs-xxxxxxxx) — <Problem> → <Action> → **<Result>**
  - Revision: [<label>](#hs-xxxxxxxx) — <Problem> → <Action> → **<Result>**
- [<label>](#hs-xxxxxxxx) — <Problem> → <Action> → **<Result>** · **Current position**

Not yet synced: <label>, <label>

[↑ Project Home](#project-home)
```

Satır sırası = `seq`. Bir satırın Result'ı ile sonraki satırın Problem'i okuma sırasıdır; "problem → operation → result → next problem" yolu böyle görünür. Neden-sonuç yazılmaz.

## 4. Kararlar

| # | Karar | Neden |
|---|---|---|
| 1 | Adım metni = record Purpose | `03` §5 One-Sentence Summary: Purpose `Problem → Action → Result` biçimindedir. HSMM'de 16 / 16 record bu biçimde. Yeni özet üretilmez; karar uydurulamaz |
| 2 | Purpose üç parçaya bölünmezse olduğu gibi yazılır | Parça uydurmak "unsupported claim" olur |
| 3 | Revision = native step ID `<P>-R<n>` | Spec'te ayrı revision alanı yok. `02` §4 step ID dokümanda yazıldığı gibidir. HSMM'de Q4 ve Q4-R1 farklı dosyalardadır, bu yüzden path değil step ID kullanılır. `depends_on` zinciri parent göstermez (HSMM'de doğrusal) |
| 4 | Revision kök node'un altında, kendi `seq` sırasıyla | Q4, Q5, Q4-R1 sırasında da Q4-R1 Q4'e aittir. Revision of revision aynı kök altında kalır |
| 5 | Parent node yoksa revision üst seviyede ` · revision of <P>` | Parent uydurulmaz; eksiklik görünür kalır |
| 6 | Current = `08` §3.2 `position` | Mevcut tanım: record'u olan en yüksek `seq` |
| 7 | `UNSYNCED` node değil; tek `Not yet synced:` satırı | Record yok, link verilecek section yok. Unit yine tam bir kez görünür |
| 8 | `STALE` ` · Needs refresh` | `09` §5.1 status satırı ile aynı söz; eski Purpose güncel gibi sunulmaz |
| 9 | `JOURNEY` structural (DEBT gibi) | Project Home her zaman link verir. Legacy view V-08 ile repair'de journey alır |
| 10 | V-18 = section ≠ render | Journey deterministik türetilir. Sıra, grup, status, current, link veya uydurma satır farkı yakalanır |
| 11 | HS trigger'ları JOURNEY'i de yazar; sync-only scope'a eklendi | Journey HS state / record'dan türer. Yazılmazsa sync sonrası eskir |

## 5. Scope dışı

- Semantic Knowledge Map, ULA içeriği, L0–L4 anlamı: değişmedi.
- Human Sync state / record yazımı: değişmedi. `08` değişikliği yalnız view write listesidir.
- Adaptive Plinko / teaching geometry: yok.
- Project Home density (VIS-02 gözlemi): değişmedi. Journey Home'a tek link ekler; HS listesi aynı kalır.
- Key Decisions / Downstream Impact journey'de kullanılmaz (karar 1).

## 6. Mevcut test beklentileri

| test | eski | yeni | neden |
|---|---|---|---|
| B sync sonrası değişen section | `INDEX`, `MODEL` | + `JOURNEY` | §8 trigger |
| F sync-only scope | `HS`, `MODEL`, `INDEX` | + `JOURNEY` | `08` §11 |
| K V check sayısı | 17 | 18 | V-18 |
| K STALE crafted | V-06 | V-06, V-18 | Journey de status'u taşır |
| K repair | HS + INDEX | + JOURNEY | Aynı neden |
| K write failure / retry | `update([hs, MODEL, INDEX])` | + `JOURNEY` | Test eski trigger listesini elle veriyordu (kök neden: V-18 retry sonrası) |
| O structure order | 7 kind | 8 kind | §3 |
| P stale | `INDEX`, `MODEL` | + `JOURNEY` | §8 |
| Q metrics | `lines_total 263`, `lines_visible 113`, `links_internal 24`, `links_from_index 9` | `273`, `118`, `29`, `10` | Journey section: +10 satır, +5 görünür, +5 link (3 node, dönüş, Home link'i). Elle sayıldı |
| Q domains | `MODEL`, `HS` | `MODEL`, `JOURNEY`, `HS` | §13.3 |
| R Project Home hedefleri | 4 | + `project-journey` | §3.1 |
| R / S pre-VIS-02 view | JOURNEY section'ı vardı | JOURNEY yok (gerçekçi legacy); V-01 + V-08 + V-17; legacy broken link 1 → 2 | Eski view journey taşımaz |

## 7. CLS-4 test plan → Test T

| plan | check |
|---|---|
| purely sequential project | `T sequential …`, `T node = Problem → Action → **Result** …`, `T current position = 08 §3.2 position …` |
| project with revisions | `T revisions: R unit nested …` |
| stale Human Sync unit | `T stale unit: Needs refresh …` |
| missing intermediate phase | `T missing intermediate phase …`, `T UNSYNCED parent …` |
| multiple units sharing one parent | `T multiple revisions share one parent …`, `T revision of a revision …` |
| mutation: reorder units | VIS-M17; `T wrong order -> V-18` |
| mutation: remove revision parent | VIS-M18; `T revision ungrouped -> V-18` |
| mutation: unsupported journey claim | VIS-M19; `T no unsupported claim …`, `T Downstream Impact claim never enters …`, `T invented journey line -> V-18` |
| mutation: broken Human Sync link | VIS-M20; `T broken HS link in the journey -> V-01 + V-18` |

| acceptance | check |
|---|---|
| Yalnız Human Sync authority'sinden | `T journey independent of graph and context …`, `T no unsupported claim …` |
| Her unit bir kez veya parent altında | `T every synced unit exactly once`, `T UNSYNCED parent …` |
| Revision görsel olarak ayrı | `T revisions …` (`  - Revision: `) |
| Current position belli | `T current position …` (2 check) |
| Her node HS section'a link | `T every node links its own HS section …` |
| Karar uydurulamaz | `T no unsupported claim …`, `T Purpose not Problem → Action → Result …` |
| Journey hatası HS state'i bozmaz | `T journey write failure …` |

Ek: VIS-M21 (V-18), VIS-M22 (JOURNEY structural), VIS-M23 (template), VIS-M24 (`08` §11 scope).

## 8. HSMM review kopyası (repair, pilot dosyaları değişmez)

| ölçü | önce | sonra |
|---|---|---|
| integrity | V-08, V-15, V-17 | V-15 (VIS-02 öncesi) |
| links_broken | 0 | 0 |
| links_internal | 50 | 120 |
| journey | yok | 22 satır: 9 phase, 7 revision, Current position = Yayın hazırlığı (Q7) |

- Q2-R1 → Q2; Q4-R1, R2, R3 → Q4; Q5-R1 → Q5; Q6-R1, R2 → Q6. D1 revision değildir (step ID `18Q-D1`).
- Repaired section'lar rebuild ile aynı. Kopyadaki `sync/` pilot ile byte-byte aynı.

## 9. Açık gözlem (scope dışı)

- Revision yalnız step ID adlandırmasından bulunur. Proje revision'ı başka biçimde adlandırırsa (`Q4b`, `Q4 fix`) gruplama olmaz; unit üst seviyede kalır. Kural genişletmesi ayrı karar ister.
- HSMM'de 16 unit için journey 22 satırdır. Çok büyük projede journey de uzar; density işi (VIS-02 gözlemi) ile birlikte ele alınabilir.

## 10. Tests

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
| view | 267/267 (Test T: 30) |
| distribution | 108/108 |
| **toplam** | **1078/1078** |

Mutation: 75/75 CAUGHT (VIS-M17 – VIS-M24 dahil). `RESULT: PASS`. Toplamlar script ile toplandı.

Full run sonrası yalnız bir check adı düzeltildi (`T V-18 repair rewrites only JOURNEY; == rebuild`); view suite tekrar 267/267.

Manifest: `scripts/build-release.ps1` ile yeniden üretildi. Diff yalnız `07`, `08`, `09` ve `KNOWLEDGE_VIEW_TEMPLATE.md` sha256 satırlarıdır.
