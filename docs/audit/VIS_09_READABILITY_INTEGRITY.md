# VIS-09 — Readability and Navigation Integrity

**Tarih:** 2026-11-17
**Jira:** CLS-10 (Epic CLS-1)
**Branch:** `feature/cls-10-vis-09-readability-integrity`
**Base:** `main` `01dfd8a` (VIS-08)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor. Risk: **STANDARD** (paylaşılan `07` §V integrity mantığı; renderer çıktısı, authority, graph, ULA, persistence değişmedi).

## 2. Kart check'leri → repository check'leri

| kart | check | durum |
|---|---|---|
| R-01 Concept anchor exists | V-04, V-01, V-16 | vardı |
| R-02 Breadcrumb resolves | V-17, V-01 | vardı |
| R-03 Semantic link resolves | V-21, V-01 | vardı |
| R-04 / R-05 Recall target / derived content | V-23, V-24 | vardı |
| R-06 No duplicate semantic edge | M-11 (graph), V-20 (MAP), V-21 (KN) | vardı |
| R-07 Progressive disclosure contract | V-25, V-26 | vardı |
| R-08 Journey covers Human Sync units | V-18, V-08 | vardı |
| R-09 Knowledge Map agrees with graph | V-20 | vardı |
| R-10 Local map does not contradict graph | **V-27** | **yeni** |
| R-11 No orphan Concept Home | V-19 | vardı |
| R-12 Navigation cycle rules | M-08 / M-09 (graph), V-19 `CYCLE` | vardı |
| — Learning Path / Learning depth / Also part of | **V-27** | **yeni** |
| Failure diagnostics | **bulgu yeri** (`07` §V) | **yeni** |

## 3. Kararlar

- **D-1 V-27:** HSMM render'ında kanıtlandı: Learning Path'ten L2 silmek veya Learning depth seviyesini değiştirmek hiçbir V check'i tetiklemiyordu. Local map ve `Also part of` hiçbir check tarafından okunmuyordu. V-27 graph'tan türeyen satırları render ile, Learning Path'i section'ın gösterdiği part'larla karşılaştırır. İçerik okunmaz (`07` §V kapsam).
- **D-2 Bulgu yeri:** `diagnose()` her bulguyu `(check, sonuç, yer)` olarak verir. `integrity()` sözleşmesi aynıdır.
- **D-3 Yeni R-ID yok:** Kart R-01–R-12'nin repository adlandırmasına uymasını istiyor; mevcut V / M check'lerine eşlendi. Yalnız boşluk yeni check aldı.
- **D-4 Test R V-16 fixture'ı:** Source heading çakışması part heading'i yeniden adlandırarak değil, part gövdesine heading ekleyerek simüle edilir (V-27 artık heading değişimini doğru raporlar). Test amacı (V-16 only, repair yok) aynı.

## 4. Files Changed

| dosya | değişiklik |
|---|---|
| `references/07_INTEGRITY_CHECKS.md` | V-27; bulgu yeri kuralı; §L.6 rapor |
| `references/09_KNOWLEDGE_VIEW.md` | §6.5, §7.2 V-27 işaretleri |
| `tests/view/view_model.py` | `diagnose`, `structure_stale` (V-27), `broken_links`, `ViewBlocked.where`, repair |
| `tests/view/run_tests.py` | Test Z (28 check); K, R, V, X beklentileri |
| `tests/mutation.py` | VIS-M69 (V-27), VIS-M70 (V-04) |
| `distribution/manifest.json` | 07, 09 sha256 |

## 5. Açık noktalar

- **O-13 Header note:** HSMM pilot view'ının dosya başı not satırı eski ifadedir; section repair marker dışını yazmaz (`09` §10). `repair == rebuild` yalnız bu satırda farklı (VIS-07'den beri). Check veya repair kapsamı insan kararı.
- **O-9, O-10:** Değişmedi; CLS-10 kapsamı dışında.
- VIS-06 ve VIS-08 sınırlı kabulleri aynen geçerli.
