# Prompt scheduled task: sync harian Performa Iklan

Salin isi blok di bawah ke scheduled task (jadwal: setiap hari, mis. `0 7 * * *`), setelah semua `{{PLACEHOLDER}}` diganti.
Jangan menyimpan token atau password di prompt ini.

| Placeholder | Isi | Contoh |
|---|---|---|
| `{{NAMA_BDMT}}` | Nama BDMT | Raka |
| `{{SPREADSHEET_ID}}` | ID sheet `Performa_Iklan_<Nama>` (potongan URL antara `/d/` dan `/edit`) | `1AbC...` |
| `{{AD_ACCOUNT_ID}}` | ID ad account Meta milik BDMT ini (angka) | `1234567890` |
| `{{KATA_KUNCI_PRODUK}}` | Kata kunci judul produk BDMT di affiliate.id, untuk `list_products` | `Paket Tim Agent` |
| `{{AFFILIATE_ID}}` | Kode affiliate BDMT, hanya dipakai untuk laporan (boleh dikosongkan) | `karyawan-ai` |

```text
TUJUAN: tambahkan data KEMARIN (tanggal lokal WIB) milik BDMT {{NAMA_BDMT}} ke Google Sheet "Performa_Iklan_{{NAMA_BDMT}}" (spreadsheetId {{SPREADSHEET_ID}}, di folder Drive "BDMT"). Hanya menulis ke sheet itu. Jangan mengubah iklan, kampanye, atau produk apa pun. Ini task terjadwal: tidak ada orang yang bisa ditanya, jadi jalankan sampai selesai lalu laporkan ringkas.

STRUKTUR SHEET (header baris 1 JANGAN diubah; tab magic5_harian dan parameter berisi rumus/input manual, JANGAN ditulis; sheet ini dipakai dashboard "5 Magic Numbers"):
- campaign: tanggal,campaign_id,campaign_name,status,spend,impressions,clicks,ctr_pct,cpm,cpc,reach,leads,cost_per_lead,link_clicks,landing_page_views,initiated_checkout_meta,purchases_meta,purchase_value_meta
- adset: tanggal,campaign_id,campaign_name,adset_id,adset_name,status,spend,impressions,clicks,ctr_pct,cpm,cpc,reach,leads,cost_per_lead,link_clicks,landing_page_views,initiated_checkout_meta,purchases_meta,purchase_value_meta
- creative: tanggal,campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,creative_id,status,spend,impressions,clicks,ctr_pct,cpm,cpc,reach,leads,cost_per_lead,link_clicks,landing_page_views,initiated_checkout_meta,purchases_meta,purchase_value_meta
- sales: tanggal,order_id,produk,qty,omzet,affiliate_id,status,customer_key,komisi_persen
- _meta: pasangan key,value. Ubah/tambahkan hanya baris last_sync = tanggal data yang baru ditulis.
Meta ad_account_id = {{AD_ACCOUNT_ID}}.

LANGKAH:
1. Tanggal target T = kemarin (YYYY-MM-DD, zona WIB/Asia/Jakarta).
2. Idempotensi tab campaign, adset, creative: baca kolom A (get_values, mis. campaign!A:A). Jika T sudah ada di tab itu, LEWATI tab itu. Tab sales memakai order_id (langkah 4).
3. Meta (connector Meta Ads, tool ads_get_ad_entities; client_conversation_id acak 20 karakter alfanumerik, client_model = id model kamu, advertiser_job "report_measure_or_look_up", scheduled_task_run true; jangan panggil offer_report). Untuk level campaign, adset, lalu ad: time_range {"since":T,"until":T}, fields: id,name,effective_status,amount_spent,impressions,clicks,ctr,cpm,cpc,reach,lead,cost_per_lead,link_click,landing_page_view,omni_initiated_checkout,omni_purchase,omni_purchase_values (adset menambah campaign_id,campaign_name; ad menambah adset_id,adset_name,campaign_id,campaign_name,creative_id). Pemetaan kolom: link_click->link_clicks, landing_page_view->landing_page_views, omni_initiated_checkout->initiated_checkout_meta, omni_purchase->purchases_meta, omni_purchase_values->purchase_value_meta, lead->leads. Verifikasi nama field dengan ads_get_field_context bila error. Isi tab hanya dengan baris yang spend>0 atau impressions>0. Angka ditulis sebagai angka (ctr tanpa %; null jadi sel kosong). Hasil level ad bisa sangat besar: pecah per campaign dengan filtering [{"field":"campaign.id","operator":"IN","value":[ID]}] untuk tiap campaign yang spend-nya >0, atau baca file hasil yang disimpan memakai python/jq. Respons terpotong sekitar 100 entitas, jadi WAJIB cek: total spend baris ad per hari harus sama dengan spend level campaign. Jika tidak sama, ambil ulang per adset; jika tetap tidak sama, tulis apa adanya dan laporkan selisihnya.
4. Penjualan (connector affiliate.id). JANGAN paging semua order; cari per produk: list_products dengan search "{{KATA_KUNCI_PRODUK}}" (limit 50, ikuti halaman berikutnya bila ada) untuk mendapat SEMUA produk BDMT ini; simpan productId dan commissionPercent tiap produk. Untuk SETIAP productId panggil list_orders: dateFrom = T minus 6 hari, dateTo = T, role "all", limit 50, TANPA filter status, semua halaman sampai hasNext false. Jika panggilan gagal karena jaringan (mis. ERR_NETWORK_CHANGED), ulangi sampai berhasil; jangan dilewati. Tulis ke tab sales order berstatus SUCCESS dan PENDING dari SEMUA affiliate (JANGAN menyaring affiliateId). Satu baris per item: tanggal (createdAt dikonversi ke WIB), orderId, nama produk, quantity, omzet = price x quantity, affiliate_id (nilai asli affiliateId; "(tanpa affiliate)" bila null), status (SUCCESS/PENDING apa adanya), customer_key = 8 karakter hex pertama dari sha1(customerName huruf kecil dengan spasi dirapikan menjadi satu spasi) (jangan menulis nama asli; hitung dengan python hashlib), komisi_persen = 0 bila affiliateId null, selain itu commissionPercent produk. Hanya tambahkan order_id yang BELUM ada di kolom B tab sales. Untuk order_id yang sudah ada dengan status PENDING tetapi sekarang SUCCESS, UBAH sel status-nya (update_values) menjadi SUCCESS. Order berstatus lain (FAILED/EXPIRED) tidak ditulis. Omzet adalah harga penuh, bukan komisi.
5. Tulis dengan append_values (range tab!A1) sesuai urutan kolom header. Setelah selesai, baca balik 2 baris terakhir tiap tab untuk memastikan masuk, dan baca magic5_harian!A1:P2 (baris TOTAL) untuk memastikan rumus tidak error.
6. Laporan akhir 4-7 baris: tanggal T, jumlah baris yang ditulis per tab, spend, leads (landing_page_views), transaksi SUCCESS, omzet semua affiliate dan omzet khusus affiliate "{{AFFILIATE_ID}}" (lewati bagian ini bila kosong), ROAS keduanya, jumlah order PENDING, dan masalah apa pun (tab dilewati, selisih spend, error connector). Jika connector gagal, jangan mengarang angka: tulis error dan berhenti.

CATATAN: attribution lead Meta bisa terlambat; jangan koreksi baris iklan lama. Pembeli sering membuat beberapa order PENDING lalu membayar lewat link tanpa kode affiliate, sehingga order SUCCESS-nya tanpa affiliate; itu sebabnya tidak disaring per affiliate. Pixel Meta bisa saja tidak melaporkan purchase (kolom purchases_meta kosong); data pembelian yang valid berasal dari affiliate.id.
```

## Catatan untuk yang memasang

- Jalankan task sekali secara manual dulu (`Run now`), cek barisnya masuk, baru biarkan terjadwal.
- Task hanya jalan saat aplikasi Claude terbuka; bila tertutup, ia jalan saat aplikasi dibuka lagi.
- Data hanya diambil untuk kemarin. Untuk mengisi riwayat, jalankan prompt yang sama dengan T diganti tanggal lampau (satu tanggal per run).
