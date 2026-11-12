# VIS-06 — Recall Capsules

**Tarih:** 2026-11-10
**Jira:** CLS-7 (Epic CLS-1), kararlar D-1 – D-14: yorum `10034`
**Branch:** `feature/cls-7-vis-06-recall-capsules`
**Base:** `main` `a7d183f` (VIS-05)

## 1. Status

Implementation tamam. Commit yok; human review bekliyor.

- Soru: Okuyucu bir kavramda daha önce okuduğu bir kavrama dayanınca, o bölüme dönmeden "bu neydi, burada ne için kullanılıyor, tam hali nerede" sorularını cevaplayabiliyor mu?
- Mekanizma: graph'tan türeyen, rebuild edilebilir `#### Recall` part'ı. Yeni authority, yeni alan, ULA metni yok.
- İçerik yeterliliği mekanizmadan ayrı ölçüldü (§8). HSMM'de 5 capsule'dan 2'si yeterli, 2'si zayıf, 1'i yetersiz. Bu graph `meaning` verisinin özelliğidir; view düzeltmez (D-13, D-14).

## 2. Files Changed

| dosya | değişiklik |
|---|---|
| `references/09_KNOWLEDGE_VIEW.md` | §1 `recall_relations`, `recall_evidence`; §6.1 Recall satırı; §6.4 not; yeni §6.6 Recall; §8 trigger; §11 not |
| `references/07_INTEGRITY_CHECKS.md` | V-23 (Recall drift, rebuild), V-24 (capsule eksik metin yüzünden yazılmadı, yalnız rapor) |
| `templates/KNOWLEDGE_VIEW_TEMPLATE.md` | KN bloğunda Semantic Relationships ile Learning Path arasında Recall |
| `tests/view/view_model.py` | `recall_capsules` (edge'ler açıkça `edge_id` sırasıyla), `recall`, render yeri, `node_sig` recall bağımlılığı, `recall_stale` (V-23), V-24, repair |
| `tests/view/run_tests.py` | Test W (41 check); beklenti güncellemesi K, Q, V template sırası |
| `tests/mutation.py` | VIS-M41 – VIS-M53 |
| `README.md` | view paragrafı: recall |
| `distribution/manifest.json` | 07, 09, template sha256 |
| `docs/audit/VIS_06_RECALL_CAPSULES.md` | bu rapor (yeni) |

## 3. Rendering

```text
### KN-xxxxxxxx — <canonical_name>
#### Where am I?            (değişmedi)
#### Semantic Relationships (değişmedi)
#### Recall                 ← yeni; yalnız capsule varsa
- [<önceki hedef>](#kn-…) — <hedef short_meaning, aynen>          ← "Bu neydi?" + "Tam hali nerede?"
  - **Used here:** <edge meaning, aynen> (<RELATION>)              ← "Burada ne için?"
#### Learning Path          (değişmedi; Recall ULA değildir, path'te yok)
#### L0 — Map …             (değişmedi)
```

Capsule koşulu (§6.6): source = bu node; `REQUIRES` / `USES` / `DEPENDS_ON`; `evidence_status` `VERIFIED`; hedef KN section'ı var ve section sırasında önce. Hedef başına bir capsule; aynı hedefin edge'leri `edge_id` sırasıyla `Used here` satırı.

## 4. Kararlar (CLS-7 yorum 10034 → uygulama)

| karar | uygulama |
|---|---|
| D-1 yalnız KN | Recall yalnız `render_kn` içinde. HS, MAP, INDEX yok. |
| D-2 relation | `recall_relations` = `REQUIRES; USES; DEPENDS_ON`. `NEXT`, `PART_OF` ve diğer 8 token capsule üretmez. |
| D-3 önceki | `kn_nodes` sırası; hedef index < kaynak index. Zaman / nedensellik çıkarılmaz. |
| D-4 hatırlatma | Hedef `short_meaning` aynen. |
| D-5 bağlam | Edge `meaning` aynen, etiket `Used here:`. |
| D-6 evidence | `recall_evidence` = `VERIFIED` (prefix). `INFERRED`, `GENERAL THEORY` capsule üretmez. |
| D-7 yer | Semantic Relationships'ten sonra, Learning Path'ten önce. ULA kopyasının dışında. Anchor'lar değişmez. |
| D-8 tekilleştirme | Hedef başına bir capsule; edge'ler `edge_id` sırası (graph satır sırasından bağımsız, §7.1); capsule'lar ilk edge'lerinin `edge_id` sırası; aynı triple bir kez. |
| D-9 eksik veri | DEBT, SUPERSEDED, graph'ta olmayan, section'sız hedef → capsule yok. Hedef `short_meaning` veya edge `meaning` boş / `-` → o capsule yok, V-24 raporlar (hedef için V-22 de). Metin uydurulmaz. |
| D-10 etiket | İngilizce kısa etiket; açık (collapse yok). |
| D-11 integrity | V-23 drift → KN section rebuild. `node_sig` render edilen Recall'u içerir: hedef `short_meaning` / ad / durum, edge `meaning` / `evidence_status`, section sırası değişince kaynak section yeniden yazılır. Incremental == rebuild. |
| D-12 yoğunluk | Sayı sınırı yok. |
| D-13 yeterlilik | §8: mekanizma, veri kalitesi, insan faydası ayrı. |
| D-14 graph verisi | Graph, ULA, alan değişmedi. Takip önerileri §9. |

## 5. Scope dışı

VIS-07 görsel dil / dil birliği, VIS-08 yoğunluk, VIS-09, VIS-10, yeni graph alanı, `meaning` yeniden yazımı, ULA cümle seçimi, Human Sync, persistence, HTML/JS, OBS-VIS04-4.

## 6. Mevcut test beklentileri (bilinçli güncelleme)

| test | önce | sonra | neden |
|---|---|---|---|
| K | 22 V check | 24 V check | V-23, V-24 |
| Q baseline fixture | 300 / 131 satır, 33 link, KN 8 | 305 / 134, 34, KN 9 | Fixture'da Walk-Forward → USES → Temporal Leakage (önce, VERIFIED): 1 capsule = +5 satır, +3 görünür, +1 link |
| V template KN sırası | Where am I?, Semantic Relationships, Learning Path, … | + Recall (Semantic Relationships ile Learning Path arası) | template |

Test V'nin kendi fixture'ında capsule yok (USES / DEPENDS_ON ileri; geri yöndekiler COMPARED_WITH / EVIDENCE_FOR); VIS-05 beklentileri değişmedi.

## 7. CLS-7 test plan → Test W

| kart | Test W |
|---|---|
| direct prerequisite | EM Loop REQUIRES Lattice → capsule (tam blok) |
| reused output | Positions USES Lattice → capsule, meaning aynen |
| mentioned, recall gereksiz | Selection ULA metni Lattice adını anar; yalnız EVIDENCE_FOR / INFERRED edge → Recall yok |
| repeated concept | REQUIRES + USES + tekrar USES → tek capsule, iki `Used here`, triple bir kez |
| circular graph | A↔B, A→B→C→A: yalnız sonraki section hatırlar; çift yönlü capsule çifti yok; self-recall yok |
| missing target | ileri, DEBT, SUPERSEDED, olmayan, section'sız hedef → capsule yok, kırık link yok |
| mutation: unsupported fact | VIS-M44, VIS-M45; crafted: değiştirilmiş hatırlatma / Used here → V-23 |
| mutation: incorrect target | VIS-M46; crafted: yanlış anchor → V-23 |
| mutation: duplicated capsule | VIS-M47; crafted: tekrar capsule → V-23 |
| mutation: missing backlink | VIS-M43; crafted: link kaldırıldı → V-23 |

Ek: NEXT / desteklenmeyen relation / INFERRED / GENERAL THEORY guard, eksik metin (V-24, V-22), section sırası, incremental (hedef `short_meaning`, edge `meaning`, evidence değişimi) == rebuild, V-23 için 9 bozulma, VIS-05 view → V-23 → repair == rebuild, authority byte-identical, template. Ek mutation: VIS-M41 (NEXT), VIS-M42 (evidence), VIS-M48 (önce kuralı), VIS-M49 / M50 (V-23 / V-24), VIS-M51 (template).

`node_sig` kanıtı: Recall bağımlılığı çıkarılınca (yalnız scratch kopya) 4 Test W check'i FAIL (incremental ≠ rebuild).

### 7.1 `edge_id` sırası (review düzeltmesi)

- Bulgu (independent review): §6.6 `edge_id` sırası ister; `recall_capsules` graph satır sırasıyla geziyordu.
- Kanıt: `05` §4 `edge_id` için yalnız "benzersiz, Max + 1, yeniden kullanılmaz" der; template "Satır silinmez" der. Satırların `edge_id` sırasında olması kural değildir; M-01 – M-22 arasında sıra kontrolü yoktur (M-02 yalnız duplicate). Yani sıra garanti değildir.
- Önce test: karışık satırlı fixture ile 2 yeni check FAIL (405 / 407): `Used here` satırları ve capsule'lar satır sırasını izledi. V-23 bunu görmedi (aynı fonksiyon).
- Düzeltme: `recall_capsules` edge'leri `edge_id` sayısal değeriyle sıralar; kural §6.6'nın iki cümlesinden okunur. Tekilleştirme ve gruplama aynı; aynı triple'da en küçük `edge_id` kalır.
- Test W +4 check: karışık fixture ön koşulu; karışık satırlar → bütün Recall part'ları sıralı fixture ile aynı, view clean; capsule sırası ilk edge `edge_id` (section veya satır sırası değil), `Used here` `edge_id` sırası; aynı edge'ler sıralı satırla aynı blok.
- Mutation: VIS-M52 (`used` satırları satır sırası), VIS-M53 (capsule'lar satır sırası); ikisi de fixture'larla yakalanır.
- HSMM: graph satırları zaten KE-0001 – KE-0012 sırasında; render düzeltmeden sonra byte-identical; pilot 62 dosya değişmedi.

## 8. HSMM review kopyası (pilot dosyaları değişmez)

- Önce = kabul edilmiş VIS-05 render'ı (byte-identical). Sonra = VIS-06 render'ı.
- 30 section'dan 5'i değişti (EM, Validation, Economic, Convergence, TV), 25'i byte-identical. Recall blokları silinince VIS-06 == VIS-05.
- Capsule mekanizması 5 / 5: hatırlatma aynen, `Used here` aynen, hedef önce, backlink var. Kırık link 0.
- KE-0011 (ADF EVIDENCE_FOR HSMM) D-2 gereği capsule almaz.
- Metric: `lines_total` 3186 → 3211 (+25 = 5 × 5), `lines_visible` 1083 → 1098 (+15 = 5 × 3), `links_internal` 136 → 141 (+5), `links_from_kn` 42 → 47. Diğer metric'ler değişmedi.
- Upgrade: VIS-05 view → V-23 yalnız bu 5 section → repair == taze VIS-06 render.
- Yeterlilik (reviewer yargısı, okuyucu ölçümü değil): KE-0008, KE-0009 yeterli; KE-0007, KE-0012 zayıf; KE-0010 yetersiz. Her capsule hedef link'ini Outgoing satırında zaten var olan şekilde tekrarlar; katkısı hedef `short_meaning` ve edge `meaning`'dir. Lattice hatırlatması üç section'da aynı genel cümledir.

## 9. Açık gözlemler

- O-1: Kartın "why the concept matters in the current section" kriteri HSMM'de verilen veriyle 2 / 5 capsule'da karşılanır. Mekanizma doğru; eksik graph `meaning` metnindedir. Kabul human kararıdır (D-13).
- O-2: Kart örneği (`eta = beklenen süre-giriş sayıları`) graph'ta yok; yalnız ULA 02:297'de. Graph-only capsule bunu üretmez.
- O-3: Takip önerisi (uygulanmadı): KE-0007, KE-0010, KE-0012 `meaning` metnini normal graph düzeltme yoluyla özelleştirmek; isteğe bağlı `05` `meaning` yazım kuralı.
- O-4: Recall link'i Outgoing satırındaki link'i tekrarlar (+3 görünür satır / capsule).
- O-5: Etiketler İngilizce, değerler Türkçe (VIS-05 O-3, VIS-07).
- O-6: Pilot header blockquote rebuild'den farklı (VIS-04 O-4), değişmedi.
- O-7: VIEW-M9 Test S crash (VIS-05 O-5) değişmedi.
- O-8: OBS-VIS04-4 değişmedi, kapsam dışı.
- O-9: Aynı satır sırası bağımlılığı VIS-05 Semantic Relationships (§6.4) part'ında da var: aynı edge'ler farklı satır sırasıyla farklı satır sırası verir (probe). §6.4 ve §7.1 de `edge_id` sırası der. VIS-01 – VIS-05 davranışı scope dışı olduğu için değiştirilmedi; ayrı human kararı. Bugünkü writer'lar Max + 1 ile ekler, HSMM satırları sıralı.

## 10. Tests

Son tam koşu (`edge_id` sırası düzeltmesinden sonra) `uv run tests/run_all.py`, 2026-11-11 02:24:09 → 03:33:44 +0300, `RESULT: PASS`, exit 0. Koşu sonunda aday dosyaların sha256'sı başlangıçla aynı.

| suite | sonuç |
|---|---|
| phase3 | 24 / 24 |
| phase4 | 46 / 46 |
| phase5 | 74 / 74 |
| phase6 | 83 / 83 |
| phase7 | 163 / 163 |
| integration | 141 / 141 |
| static | 33 / 33 |
| isolation | 32 / 32 |
| sync | 107 / 107 |
| view | 407 / 407 (VIS-05: 366 + Test W 41) |
| distribution | 108 / 108 |
| **toplam** | **1218 / 1218** (VIS-05: 1177) |

Mutation: 104 / 104 CAUGHT (VIS-05: 91 + VIS-M41 – VIS-M53). Toplamlar log'dan script ile toplandı.

İlk review koşusu (düzeltmeden önce, 2026-11-10 23:10:23 → 2026-11-11 00:21:08): 1214 / 1214, 102 / 102.

Test W'deki yerleşim / template kontrolleri `in_order` yardımcısını kullanır; VIS-M40 ve VIS-M51 altında Test W artık crash değil, FAIL verir.
