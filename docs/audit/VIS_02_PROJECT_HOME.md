# VIS-02 — Project Home and Navigation Architecture

**Tarih:** 2026-11-03
**Jira:** CLS-3 (Epic CLS-1)
**Branch:** `vis-02-project-home`
**Bağımlılık:** VIS-01 (CLS-2, `main` `34c77ab`)

## 1. Status

Revision 1 tamam (§9). Final human review: PASS. Full ULA compatibility fix bu audit altında kalır (ayrı Jira issue yok).

- Project Home: `09` §3.1. Anchor sözleşmesi: `09` §3.2.
- Concept navigation: `09` §6.3 (breadcrumb, parent, reading order).
- Integrity: `07` V-01 genişledi, V-16 ve V-17 eklendi.
- Authoritative state değişmez. Yalnız DERIVED view render'ı değişir (`09` §13.5).

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §3 INDEX = `## Project Home`; §3 `DEBT` structural; §3.1 Project Home; §3.2 Anchors; §6.1 Where am I? kaynağına `NEXT`; §6.2 block-structured Full; §6.3 Breadcrumb and navigation; §8 navigation komşusu |
| `references/07_INTEGRITY_CHECKS.md` | V-01 her internal link; V-08 eksik `DEBT`; V-16 duplicate navigation anchor; V-17 navigation graph ile uyuşmuyor |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | Project Home, KN navigation satırları, HS / MAP / DEBT dönüş link'i |
| `tests/view/view_model.py` | Render, anchor / slug, V-01 / V-08 `DEBT` / V-16 / V-17, repair, incremental komşu imzası, block-structured Full projection |
| `tests/view/run_tests.py` | Test R: 35 check; Test S: 11 check. J, K, P, Q beklentileri güncellendi (§6) |
| `tests/mutation.py` | VIS-M5 – VIS-M16 |
| `distribution/manifest.json` | `07`, `09`, template sha256 (`scripts/build-release.ps1`) |
| `README.md` | Knowledge view cümlesi: Project Home, concept navigation |

## 3. Rendering

Project Home (`INDEX`):

```text
## Project Home
**Start here:** [Project in 60 Seconds] · [Current Position]
**Human Sync** — HS listesi
**Learning** — KN listesi
**Knowledge Architecture:** [Knowledge Map]
**Open Questions / Learning Debt:** [Open Questions] · [Open Learning Debt]
```

Concept (`KN`) Where am I?:

```text
[Project Home](#project-home) → [Knowledge Map](#knowledge-map) → Project Root → [Estimation](#kn-000000a1) → **Backward Pass**

Parent: [Estimation](#kn-000000a1)

Reading order — Previous: [Forward Pass](#kn-000000b1) · Next: [Smoothing](#kn-000000b3)
```

HS, MAP, DEBT son satırı: `[↑ Project Home](#project-home)`.

## 4. Kararlar

| # | Karar | Neden |
|---|---|---|
| 1 | Previous / Next yalnız `NAVIGATION` sınıfından (`NEXT`) | `05` §3: PREVIOUS / NEXT = `NEXT` edge'leri. `09` §13.4: `NEXT` bağımlılık değildir. Satır "Reading order" adını taşır |
| 2 | Parent = primary `parent_id` | `05` §5.4: tek primary navigation location |
| 3 | Fixed anchor = GitHub heading slug; HS / KN anchor = opaque ID | Mevcut `#knowledge-map` sözleşmesi korunur. Label veya ad değişince anchor değişmez |
| 4 | `Current Position` / `Open Questions` yalnız MODEL part'ı varsa link | Boş part anchor üretmez. Kırık link yerine düz metin |
| 5 | MODEL write INDEX'i de yazar | Kök neden: Test P'de context değişince yalnız MODEL yazıldı; Project Home `Open Questions` link'i eski kaldı (diff ile kanıtlandı). Bütün §8 trigger'ları zaten MODEL + INDEX yazar |
| 6 | Incremental imzaya komşu `node_status` / `available_depth` eklendi | `DEBT → ACTIVE` veya `SUPERSEDED` komşu link'i değiştirir; yalnız ad karşılaştırması yetmez |

## 5. Scope dışı bırakılanlar

- Project Journey üretimi (Project Home'da yer almaz).
- Knowledge Map ve Related Concepts tasarımı. Related Concepts `NEXT` satırını göstermeye devam eder (VIS-01 gözlem 2).
- Recall Capsules.
- HS section'larında concept veya önceki unit link'i. Yalnız Project Home dönüşü eklendi (VIS-01 gözlem 4'ün index kısmı).

## 6. Mevcut test beklentileri

| test | eski | yeni | neden |
|---|---|---|---|
| J breadcrumb | `Machine Learning → …` | `[Project Home] → [Knowledge Map] → Machine Learning → …` | §6.3 |
| K V check sayısı | 15 | 17 | V-16, V-17 |
| P model update | `["MODEL"]` | `["INDEX", "MODEL"]` | Karar 5 |
| Q fixture | `lines_total 241`, `links_internal 11`, `links_from_hs 0`, `links_from_kn 4`, `links_from_index 7` | `263`, `24`, `3`, `10`, `9` | Yeni navigation satırları. Fark section başına elle sayıldı: +22 satır, +13 link |

## 7. Test plan (CLS-3) → Test R

| plan | check |
|---|---|
| broken anchors | `R broken anchor in a concept -> V-01`, `R Project Home anchor gone -> V-01`, `R no broken internal link` |
| duplicate anchors | `R duplicate navigation anchor -> V-16 only`, `R every navigation anchor at most once` |
| wrong parent link | `R wrong parent link -> V-17`, `R V-17 repair rewrites only the wrong section` |
| invalid previous / next | `R invalid previous / next -> V-17`, `R previous / next from NEXT only` |
| rebuild stability | `R anchors deterministic`, `R rename keeps every anchor`, `R rename incremental == rebuild` |
| concept added / removed | `R concept added: changed sections`, `R concept removed: neighbours drop it …` |
| empty Learning state | `R empty Learning: …` (2 check) |

## 8. Açık gözlem (scope dışı, mevcut davranış)

- `SUPERSEDED` olan concept'in KN section'ı view'dan silinmez. `09` silme kuralı tanımlamaz; V-11 WARNING verir, repair section yazmaz. VIS-02 komşu navigation'ını ve Project Home'u doğru günceller; kırık link oluşmaz.
- Local map çocuk listesi V check ile denetlenmez. Graph değişikliği map sync trigger'ı (§8) ile yansır.
- Mevcut view'lar (HSMM pilot) eski biçimdedir. V-17 eski KN / HS / MAP / DEBT section'larını gösterir; derived repair yalnız onları yeniden yazar. Eksik `DEBT` V-08 ile eklenir (§9.1).
- Project Home her Human Sync unit'ini ayrı listeler (HSMM: 16). VIS-02 için kabul. Büyük projede Home yoğunlaşabilir; Project Journey / sonraki density işine girdi.
- Section-level repair view header'ındaki note satırını yeniden yazmaz. HSMM'de bu satır rebuild'den farklıdır (VIS-02 öncesi).

## 9. Revision 1 — real-project migration blockers

Review: REVISION REQUIRED. Navigation tasarımı kabul. HSMM review kopyası iki migration blocker gösterdi.

### 9.1 Blocker 1 — Open Learning Debt link'i kırık

- Kök neden: HSMM view'da `DEBT` section yok (`OPEN` debt yok, V-08 istemiyordu). Project Home her zaman `#open-learning-debt` link'i üretir. Repair `DEBT` eklemez. V-01 action'ı INDEX'i yeniden yazar, aynı link geri gelir.
- Çözüm: `09` §3 `DEBT` structural top-level destination'dır; view varken her zaman durur (`Yok.` + Project Home dönüşü). Eksikse `MAP` END'den sonra eklenir. `07` V-08: view var ama `DEBT` section yok.
- Model: `integrity` V-08, `repair` eksik `DEBT`'i yazar, `patch` `MAP` sonrasına ekler. Kural `09` §3 bullet'ından okunur.
- Test: `R legacy view without DEBT …` ve `R legacy repair inserts DEBT …`.

### 9.2 Blocker 2 — Full ULA projection migration'da kayboluyor

- Kök neden (VIS-02 öncesi): `09` §6.2 Full mapping yalnız tek-block template'i tanır (`# L1 — …`). HSMM `CONTENT.md` builder çıktısı block-structured'dır (`# Bx — …` altında `## L1 — …` – `## L4 — …`, `# LOCAL MAP — …`, `# R — Reference`). Model L1–L4 bulamaz. `main` model'i de aynı section'ı 25 satır üretir. VIS-02 V-17 repair'i bu section'ları yeniden yazınca gövde kaybolur.
- Çözüm (dar, ULA redesign değil): `09` §6.2'ye block-structured Full tablosu. Level part'ı her block'un o level gövdesini `##### <block heading>` altında toplar. `# LOCAL MAP — …` L0'a girer. `**Orientation.**` / `**Transition.**` paragrafları gösterilmez (§6.1). Standart dışı level adı (`NO L4 REQUIRED`) gövdenin ilk satırı olur. Tek-block template ve Light değişmez.
- Ayrı tutuldu: ayrı bölüm, ayrı mutation'lar (VIS-M13 – VIS-M16), Test S. İstenirse ayrı commit veya Jira card olarak ayrılabilir.
- Test S: HSMM şekilli fixture; part sırası, L0 + LOCAL MAP, block toplama, alt heading kayması, `NO L4 REQUIRED`, gösterilmeyenler, artifact'in her öğrenme satırı view'da, pre-VIS-02 + `DEBT`'siz view migration'ı gövdeyi korur.

### 9.3 HSMM review kopyası (repair, pilot dosyaları değişmez)

| ölçü | önce | sonra |
|---|---|---|
| integrity | V-08, V-15, V-17 | V-15 (VIS-02 öncesi) |
| links_broken | 0 | 0 |
| links_internal | 50 | 102 |
| repaired section == rebuild | - | evet (header note satırı hariç; section dışı, VIS-02 öncesi) |

| concept | önce | sonra | gövde |
|---|---|---|---|
| KN-2b84f1d0 (Full) | 453 | 457 | aynı; yalnız collapsed L3/L4 block heading `#####` → `######` |
| KN-e06a93c5 (Full) | 403 | 407 | aynı; aynı heading farkı |
| KN-91d7c2ae (Full) | 386 | 390 | aynı; aynı heading farkı |
| 6 Light concept | 79–107 | +2 / +4 | aynı (0 fark) |

+4 / +2 satır = navigation satırları (Parent, Reading order). Heading farkı mevcut collapse kuralından gelir (`<details>` içi heading'ler bir iner); metin aynıdır.

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
| view | 237/237 (Test R: 35, Test S: 11) |
| distribution | 108/108 |
| **toplam** | **1048/1048** |

Mutation: 67/67 CAUGHT (VIS-M5 – VIS-M16 dahil). `RESULT: PASS`. Toplamlar script ile toplandı.

Manifest: `scripts/build-release.ps1` ile revision 1 sonrası yeniden üretildi. Diff yalnız `07`, `09` ve `KNOWLEDGE_VIEW_TEMPLATE.md` sha256 satırlarıdır.
