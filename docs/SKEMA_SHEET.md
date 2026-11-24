# Skema sheet `Performa_Iklan_<Nama>`

Satu file per BDMT. Nama tab dan header WAJIB sama persis di semua file, karena dashboard membaca berdasarkan nama.
Sumber kebenaran skema: `template/build_template.py`.

## Tab

| Tab | Isi | Diisi oleh | Satu baris = |
|---|---|---|---|
| `magic5_harian` | Ringkasan 5 Magic Numbers per hari + baris TOTAL (baris 2). Daftar tanggal otomatis dari tanggal yang ada di `campaign` dan `sales` (kosong bila belum ada data) | rumus, jangan ditulis | satu hari |
| `campaign` | Metrik Meta per campaign | scheduled task | tanggal + campaign_id |
| `adset` | Metrik Meta per ad set | scheduled task | tanggal + adset_id |
| `creative` | Metrik Meta per ad/creative | scheduled task | tanggal + ad_id |
| `sales` | Order affiliate.id (SUCCESS dan PENDING) | scheduled task | order_id |
| `parameter` | HPP, fee, perlakuan komisi, definisi leads | BDMT/bos, manual | - |
| `_meta` | Identitas BDMT (nama, ad account, kata kunci produk, affiliate) | BDMT, manual | - |

Kolom metrik Meta: `spend, impressions, clicks, ctr_pct, cpm, cpc, reach, leads, cost_per_lead` + `link_clicks, landing_page_views, initiated_checkout_meta, purchases_meta, purchase_value_meta`. Nilai kosong berarti Meta tidak melaporkan.

Kolom `sales`: `tanggal` (WIB), `order_id`, `produk`, `qty`, `omzet` (harga penuh), `affiliate_id` (nilai asli; `(tanpa affiliate)` bila null), `status` (SUCCESS/PENDING), `customer_key` (8 hex sha1 nama, bukan nama asli), `komisi_persen`.

## Pemetaan ke 5 Magic Numbers

Leads x Conversion Rate x Jumlah Transaksi x Rata-rata Nilai Transaksi x Margin = Profit

| Angka | Kolom di `magic5_harian` | Rumus |
|---|---|---|
| 1. Leads | `leads_lpv` (juga `klik_link`) | jumlah `landing_page_views` Meta pada tanggal itu |
| 2. Conversion Rate | `konversi_pct` | transaksi SUCCESS / leads_lpv |
| 3. Jumlah transaksi | `transaksi`, `pelanggan_unik`, `frekuensi_beli` | order SUCCESS; pelanggan unik dari `customer_key`; frekuensi = transaksi / pelanggan unik |
| 4. Nilai transaksi | `aov` | omzet / transaksi |
| 5. Margin | `margin_pct` | profit / omzet |
| Profit | `profit` | omzet - biaya_hpp - biaya_fee - biaya_komisi - spend |

`checkout_dibuat` = jumlah order (semua status) pada hari itu; selisihnya dengan `transaksi` adalah checkout yang belum dibayar.

## Batasan yang perlu diketahui pembaca dashboard

- Pixel Meta bisa tidak melaporkan purchase; pembelian valid hanya dari affiliate.id.
- `frekuensi_beli` hanya melihat produk yang dicari lewat `kata_kunci_produk`. Pembeli lama dari produk lain tidak terdeteksi.
- Rumus membaca maksimum 5000 baris per tab dan memakai BYROW/LAMBDA (khusus Google Sheets; tidak jalan di Excel). Arsipkan data lama per kuartal bila mendekati batas (Google Sheets juga membatasi sekitar 10 juta sel per file).
- Total hari pertama/terakhir bisa timpang bila omzet sudah masuk tetapi spend hari itu belum ditarik (spend ditarik pagi berikutnya).
- `leads` default memakai `landing_page_views`. Bila iklan mengarah ke beberapa produk, konversi akan terlihat rendah karena transaksi hanya menghitung produk BDMT.
