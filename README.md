# Laporan_BDMT

Paket siap-oper untuk laporan performa iklan per BDMT (Business Development Management Trainee), dengan kerangka **5 Magic Numbers**:
Leads x Conversion Rate x Jumlah Transaksi x Rata-rata Nilai Transaksi x Margin = Profit.

Setiap BDMT punya ad account Meta sendiri dan produk sendiri. Data ditarik otomatis oleh Claude (scheduled task) dari **Meta Ads** dan **affiliate.id**, ditulis ke satu Google Sheet per BDMT. Semua sheet dikumpulkan di satu folder Drive, lalu dashboard bos membaca folder itu.

## Alur

```
Ad account Meta (BDMT) ─┐
                        ├─ Claude scheduled task (akun Claude BDMT) ─> Performa_Iklan_<Nama> (Google Sheet)
affiliate.id (BDMT)  ───┘                                                      │
                                                                               ▼
                                          Folder Drive sentral "BDMT Performa Iklan" ─> dashboard bos
```

Prinsip desain: akun tidak digabung. Satu ad account bermasalah hanya menghentikan data BDMT itu, dashboard dan BDMT lain tetap jalan. Tidak ada token Meta terpusat.

## Isi repo

| Path | Fungsi |
|---|---|
| `template/build_template.py` | Pembangun template sheet (sumber kebenaran skema) |
| `template/Performa_Iklan_TEMPLATE.xlsx` | Template bersih hasil build; impor ke Google Sheets |
| `template/magic5_formulas.json` | Rumus tab `magic5_harian` (dipasang sekali ke Google Sheets; tanggal muncul otomatis dari data) |
| `prompts/sync-harian.md` | Prompt scheduled task dengan placeholder per BDMT/produk |
| `docs/SKEMA_SHEET.md` | Kolom tiap tab dan pemetaan ke 5 Magic Numbers |
| `docs/CHECKLIST_ONBOARDING_BDMT.md` | Langkah onboarding BDMT baru dan verifikasinya |

## Mulai cepat (admin)

1. Buat Shared Drive/folder "BDMT Performa Iklan".
2. Impor `template/Performa_Iklan_TEMPLATE.xlsx` ke Google Sheets, simpan di folder itu sebagai `_TEMPLATE_Performa_Iklan`, lalu pasang rumus dari `template/magic5_formulas.json` ke tab `magic5_harian` (sekali; rumus BYROW/LAMBDA tidak bisa diimpor dari xlsx).
3. Untuk tiap BDMT: duplikat template menjadi `Performa_Iklan_<Nama>`, beri akses editor ke BDMT itu saja.
4. Kirim BDMT dua file: `prompts/sync-harian.md` dan `docs/CHECKLIST_ONBOARDING_BDMT.md`.

Ubah skema? Edit `template/build_template.py` lalu jalankan:

```bash
pip install openpyxl
python template/build_template.py template/Performa_Iklan_TEMPLATE.xlsx
```

Setelah skema berubah, perbarui juga `prompts/sync-harian.md` dan tingkatkan `schema_version` di build script.

## Yang dibutuhkan tiap BDMT

- Akun Claude dengan connector **Meta Ads** (ad account milik sendiri), **affiliate.id** (akses ke toko), dan **Google Drive/Sheets**.
- Aplikasi Claude terbuka saat jadwal (task yang terlewat jalan saat aplikasi dibuka lagi).

## Batasan yang diketahui

- Pixel Meta bisa tidak melaporkan purchase; pembelian valid dari affiliate.id.
- Frekuensi beli hanya melihat produk yang dicari lewat `kata_kunci_produk`.
- Respons Meta level ad terpotong sekitar 100 entitas per panggilan; prompt memecah per campaign dan memeriksa total spend.
- Rumus membaca maksimum 5000 baris per tab.

## Keamanan

Repo ini tidak berisi data pembeli, token, atau ID akun. Jangan menambahkan keduanya. Sheet menyimpan `customer_key` (hash nama), bukan nama asli.
