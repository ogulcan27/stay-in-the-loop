# VIS-07 — Markdown Visual Grammar

**Tarih:** 2026-11-12
**Jira:** CLS-8 (Epic CLS-1)
**Branch:** `feature/cls-8-vis-07-visual-grammar`
**Base:** `main` `23be2e8` (VIS-06)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor.

- Soru: Aynı bilgi türü her yerde aynı Markdown biçimiyle mi görünüyor, ve biçim anlamı değiştirmeden okumayı kolaylaştırıyor mu?
- Mekanizma: `09` §14 grammar tablosu. View'ın ürettiği her bilgi türü tek primitive alır. Renderer kuralları spec'ten okur.
- Yeni authority, yeni alan, graph veya ULA değişikliği yok. Kopyalanan içerik aynen kalır.

## 2. Grammar

| primitive | Markdown | amaç | view kullanımı |
|---|---|---|---|
| `DIAGRAM` | Mermaid `flowchart LR` | Hiyerarşi ve relation ağı | Knowledge Map, Local Map |
| `PATH` | `A → B → C` | Dallanmayan sıra | breadcrumb, Reading order, Learning Path, Journey adımı |
| `NOTE` | `> [!NOTE]` | Hatırlatma | Recall |
| `IMPORTANT` | `> [!IMPORTANT]` | Korunacak invariant / karar | Five things to remember |
| `WARNING` | `> [!WARNING]` | Sık hata, kavram sınırı | Boundary |
| `DETAILS` | `<details>` | Derin / destek içerik, kapalı | L3, L4, Reference, Technical Trace, Technical Project Snapshot |
| `TABLE` | Markdown table | Karşılaştırma | View üretmez |

Değişen sunum (yalnız üç part):

| part | VIS-06 | VIS-07 |
|---|---|---|
| Recall | düz liste | aynı satırlar tek `NOTE` callout içinde |
| Boundary | `<details>` (kapalı) | açık `WARNING` callout |
| Five things to remember | düz liste | aynı maddeler `IMPORTANT` callout içinde |

Diğer her şey değişmedi. Mermaid kullanımı aynı (yalnız map'ler).

## 3. Kararlar

- **D-1 Kapsam:** Grammar view'ın ürettiği yapıları yönetir. ULA, record ve context gövdeleri aynen kopyalanır (§6.2). View kopyalanan text pipeline'ı Mermaid'e veya içerik tablosunu başka biçime çevirmez. Aksi `04` içeriğini ve "content aynen" kuralını değiştirirdi.
- **D-2 Pipeline / decision branch:** Kart adayı "pipeline → Mermaid". View'ın ürettiği sıralar dallanmaz (breadcrumb, Learning Path, Journey adımı). Bunlara Mermaid çizmek bilgi eklemez (AC: dekoratif diyagram yok). Bu yüzden `PATH` satırı kalır. Mermaid yalnız ağ yapısı (map) içindir. Decision branch view'da üretilmez.
- **D-3 Boundary:** Light ULA Boundary / Confusion Check gövdesi "COMMON MISTAKE / CORRECT MODEL" taşır. Kart "common mistake → warning/caution callout" der. Boundary `collapsed` listesinden çıktı ve açık `WARNING` callout oldu.
- **D-4 Recall:** Kart "Recall Capsule → note-style callout" der. Recall part'ı tek `NOTE` callout'tur. Capsule satırları değişmedi. Bir part için tek kutu, capsule başına kutu yığını yok.
- **D-5 Callout sözdizimi:** GitHub alert (`> [!KIND]`). Destek yoksa blockquote görünür; metin kaybolmaz.
- **D-6 Nesting:** View primitive'leri iç içe koymaz. `<details>` derinliği 1. Callout `<details>` içinde durmaz (GitHub orada alert render etmez).
- **D-7 Integrity:** Yeni V-25 (WARNING, rebuild section). VIS-06 biçimli view'ın Boundary / Five things part'ları başka check ile görünmezdi; V-25 upgrade yolunu sağlar.
- **D-8 Dil:** VIS-06 D-10 "language harmonization VIS-07'de" diyordu. CLS-8 kartı dil uyumu istemiyor. HS part adları Türkçe, KN part adları İngilizce kaldı. Açık karar olarak raporlandı (§7).

## 4. Files Changed

| dosya | değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §1 `collapsed` (Boundary çıktı); §5.3, §6.1, §6.6 grammar notları; yeni §14 Visual grammar |
| `references/07_INTEGRITY_CHECKS.md` | V-25 visual grammar drift |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | Five things `IMPORTANT`, Recall `NOTE`, Boundary `WARNING`; Learning Path satırı |
| `tests/view/view_model.py` | §14 tablosu, `callout`, Recall / Boundary / Five things render, `grammar_stale` (V-25), repair |
| `tests/view/run_tests.py` | Test X (22 check); `plain` fallback helper; beklenti güncellemesi K, O, P, Q, V, W |
| `tests/mutation.py` | VIS-M54 – VIS-M59; VIEW-M9, VIS-M34, VIS-M51 yeni metne taşındı |
| `README.md` | view paragrafı: Boundary warning |
| `distribution/manifest.json` | 07, 09, template sha256 |
| `docs/audit/VIS_07_VISUAL_GRAMMAR.md` | bu rapor (yeni) |

## 5. Verification

Kart için risk tabanlı pilot politika: **STANDARD**. Gerekçe: paylaşılan renderer yüzeyi (bütün KN ve MODEL section'ları) değişti; authority, persistence, graph veya ULA semantiği değişmedi.

| kontrol | sonuç |
|---|---|
| View suite | 429 / 429 (VIS-06: 407; +22 Test X) |
| Full suite (mutation hariç, bir kez) | 1240 / 1240, 11 suite, `RESULT: PASS` (distribution manifest kontrolü dahil) |
| Mutation hedefleri | 110 / 110 hedef tekil ve uygulanabilir |
| View suite'i bekleyen mutation'lar | 76 / 76 CAUGHT (yeni VIS-M54 – VIS-M59 ve taşınan VIEW-M9, VIS-M34, VIS-M51 dahil) |
| Tam mutation koşusu | Koşulmadı (STANDARD). Diğer suite'leri bekleyen mutation'ların hedef dosyaları değişmedi. |

Card test plan snapshot'ları (Test X): pipeline, hierarchy, comparison, warning, recall, collapsed theory, renderer fallback.

## 6. HSMM real project

İzole kopya. Pilot dosyaları önce / sonra sha256 aynı.

| kontrol | sonuç |
|---|---|
| VIS-06 baseline render | Kabul edilmiş VIS-06 render ile byte-identical |
| VIS-06 view → VIS-07 integrity | V-23 (5 Recall section), V-25 (MODEL + 7 KN section); V-15 önceden vardı |
| Repair | 8 section yeniden yazıldı (MODEL + 7 KN); sonuç == VIS-07 fresh render |
| Okuyucu metni (işaretler çıkarılınca) | VIS-06 ile aynı: metin, sıra |
| Internal link'ler | 141 hedef, aynı sırada; broken 0 |
| Anchor'lar | Hiçbiri silinmedi; 41 navigation anchor tekil. Eklenen: 6 `boundary` heading slug'ı (navigation değil) |
| Callout | 12: 6 Boundary `WARNING`, 5 Recall `NOTE`, 1 Five things `IMPORTANT` |
| Mermaid | 1 → 1 (yalnız global map); statik Mermaid hatası yok |
| `<details>` | 44 → 38 blok; derinlik 1 → 1 |
| Satır | toplam 3211 → 3205; görünür 1098 → 1166; kapalı 887 → 843 |

## 7. Açık noktalar

- **O-10 Dil uyumu:** HS part adları Türkçe (`Tek cümlede`, `Zihinsel Model`), diğer etiketler İngilizce. Kart kapsamı dışında; insan kararı.
- **O-11 Görünür satır artışı:** Boundary açık olduğu için HSMM'de görünür satır arttı. Bilinçli: sık hata içeriği kapalı kalmamalı. Yoğunluk yönetimi VIS-08'dedir.
- **O-9:** VIS-04 / VIS-05 semantic satır sırası bağımlılığı değişmedi; CLS-8 kapsamı dışında.
