# VIS-08 — Progressive Disclosure and Density Control

**Tarih:** 2026-11-13
**Jira:** CLS-9 (Epic CLS-1)
**Branch:** `feature/cls-9-vis-08-progressive-disclosure`
**Base:** `main` `aebd0d7` (VIS-07)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor. Risk: **STANDARD** (paylaşılan KN renderer yüzeyi; authority, graph, ULA, persistence değişmedi).

- Soru: Okuyucu ana öğrenme yolunu açma yapmadan okuyabiliyor mu, ileri içerik tek açma ile bulunuyor mu?
- Mekanizma: `09` §15 visibility hierarchy. `§1` kuralları: `collapsed`, `primary`, `details_max_depth`. `07` V-26. `§13.2` `primary_expansions`.

## 2. Visibility hierarchy

| layer | default | view |
|---|---|---|
| NAVIGATION | OPEN | Project Home, Journey, Knowledge Map, Debt; breadcrumb, Reading order, Learning Path |
| ORIENTATION | OPEN | 60 Seconds HUMAN; HS HUMAN; KN Where am I?, Semantic Relationships, Recall |
| PRIMARY | OPEN | L0, L1, L2, Boundary, Example |
| PRACTICE | COLLAPSED | Retrieval (yeni) |
| DEEP | COLLAPSED | L3, L4, Reference, Technical Trace, Technical Project Snapshot |

Değişen sunum yalnız Retrieval'dır: açık `#### Retrieval` → `<details>` + `<summary>`; Learning Path `Retrieval (collapsed)`.

## 3. Kararlar

- **D-1 Retrieval kapalı:** Okuma sonrası pratiktir, L1 / L2 ön koşulu değildir. Soru metni aynen `<details>` içinde.
- **D-2 Boundary açık kalır (O-11 değerlendirmesi):** COMMON MISTAKE / CORRECT MODEL doğrudan L1 / L2 modelini düzeltir. GitHub `<details>` içinde alert render etmez. VIS-07 D-3 korunur; +68 satır bilinçli kalır.
- **D-3 HS HUMAN katmanı açık kalır:** Journey satırı HS section'ına link verir. Zihinsel Model kapalı olsaydı her drill-down ikinci açma isterdi. `09` §5 / `03` HUMAN sözleşmesi değişmez.
- **D-4 Recall açık kalır:** Ön koşul hatırlatmasıdır (AC: ön koşul gizlenmez). Pilotta 5 section, 20 satır; tekrar değil.
- **D-5 L2 / L0 içerik ayrıştırılmaz:** "Deep implementation notes" için ULA'da işaret yok. Blok adından tahmin yeni authority olurdu.
- **D-6 Dil:** Yeni etiket yok. O-10 değişmedi.

## 4. Files Changed

| dosya | değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §1 `collapsed` + Retrieval, `primary`, `details_max_depth`; §6.1; §13.2 `primary_expansions`; §14 DETAILS amacı; yeni §15 |
| `references/07_INTEGRITY_CHECKS.md` | V-26 progressive disclosure ihlali |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | Retrieval `<details>`; Learning Path |
| `tests/view/view_model.py` | `primary`, `short_part`, `primary_expansions`, `disclosure_stale` (V-26), repair |
| `tests/view/readability.py` | `primary_expansions` metriği |
| `tests/view/run_tests.py` | Test Y (18 check); D, K, O, Q, V, W, X beklentileri |
| `tests/mutation.py` | VIS-M60 – VIS-M68; VIEW-M9, VIS-M34, VIS-M59 yeni kurala taşındı |
| `README.md` | view paragrafı |
| `distribution/manifest.json` | 07, 09, template sha256 |

## 5. Verification

| kontrol | sonuç |
|---|---|
| View suite | 447 / 447 (VIS-07: 429; +18 Test Y) |
| Full suite (mutation hariç, bir kez) | 1258 / 1258, 11 suite, `RESULT: PASS` (distribution manifest kontrolü dahil) |
| Mutation hedefleri | 119 / 119 hedef tekil ve uygulanabilir |
| View suite'i bekleyen mutation'lar | 85 / 85 CAUGHT (yeni VIS-M60 – VIS-M68 ve taşınan VIEW-M9, VIS-M34, VIS-M59 dahil) |
| Tam mutation koşusu | Koşulmadı (STANDARD). Diğer suite'leri bekleyen mutation'ların hedef dosyaları değişmedi. |

## 6. HSMM real project

İzole kopya. Pilot `docs/learning/` 62 dosya sha256 önce / sonra aynı. VIS-07 render `main`'den yeniden üretildi; kabul edilmiş render ile byte-identical.

| kontrol | VIS-07 | VIS-08 |
|---|---|---|
| `lines_visible` | 1166 | 1121 |
| `lines_collapsed` | 843 | 888 |
| `primary_expansions` | 0 | 0 |
| `details_max_depth` | 1 | 1 |
| `details_blocks` | 38 | 47 |
| KN görünür | 794 | 749 |
| HS / INDEX / MODEL / JOURNEY / MAP / DEBT görünür | 240 / 31 / 29 / 18 / 47 / 3 | aynı |

- Upgrade: VIS-07 view → V-25 (9 KN). Repair yalnız 9 KN section'ı yazdı; sonuç == VIS-08 fresh render.
- Okuyucu metni (işaretler çıkarılınca), 141 internal link, 32 navigation anchor: aynı, aynı sıra; broken 0.
- Silinen anchor: 9 `retrieval` heading slug'ı (navigation değil); hiçbir link bunlara gitmez.
- HTML: yalnız `a`, `details`, `summary`, `strong`. JavaScript yok.

## 7. Açık noktalar

- **O-12 AC "VIS-01 baseline'dan materyal düşüş" karşılanmadı:** VIS-01 1019, VIS-08 1121. VIS-02 – VIS-07 bilinçli navigation ekledi (Project Home, Journey, Concept Home, Recall, açık Boundary). Ana yol açık kalırken kalan büyük kaldıraç HS HUMAN katmanıdır (240 satır). Simülasyon: HS Zihinsel Model + Neden Önemli? kapalı → 993 (VIS-01'e göre −2.6%). D-3 nedeniyle uygulanmadı; insan kararı.
- **O-9, O-10, O-11:** O-11 D-2 ile değerlendirildi. O-9 ve O-10 değişmedi; CLS-9 kapsamı dışında.
