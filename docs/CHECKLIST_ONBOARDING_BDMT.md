# Checklist onboarding BDMT baru

Waktu: sekitar 30-45 menit. Cetak atau salin sebagai to-do.


## A. Disiapkan admin (satu kali per BDMT)
- [ ] Buat folder/Shared Drive "BDMT" (sekali untuk semua BDMT), bagikan ke BDMT sebagai viewer.
- [ ] Impor `template/Performa_Iklan_TEMPLATE.xlsx` ke Google Sheets, beri nama `_TEMPLATE_Performa_Iklan`, simpan di folder itu (sekali).
- [ ] Pasang rumus tab `magic5_harian` dari `template/magic5_formulas.json` (sekali, di `_TEMPLATE`): tempel tiap rumus `row3` ke sel A3:P3 dan `row2` ke B2:P2 (atau minta Claude memasangnya dengan update_formulas). Setelah itu semua duplikat otomatis membawa rumusnya.
- [ ] Duplikat template menjadi `Performa_Iklan_<NamaBDMT>` di folder yang sama.
- [ ] Beri BDMT akses **editor** hanya pada file miliknya.
- [ ] Pastikan BDMT punya akses akun affiliate.id ke toko yang dipakai.

## B. Dikerjakan BDMT
1. **Meta Ads**
   - [ ] Punya ad account sendiri yang aktif (catat ID angkanya).
   - [ ] Di Claude: sambungkan connector Meta Ads dan pilih ad account milik sendiri saja.
   - [ ] Tes: minta Claude "tampilkan ad account saya" dan "spend 7 hari terakhir".
2. **affiliate.id**
   - [ ] Sambungkan connector affiliate.id ke toko yang BDMT punya aksesnya.
   - [ ] Tes: minta Claude "list produk dengan kata kunci <produk saya>" dan pastikan produk muncul.
3. **Google Drive/Sheets**
   - [ ] Sambungkan connector Google Drive dan Sheets, tes membaca `Performa_Iklan_<Nama>`.
4. **Isi sheet**
   - [ ] Tab `_meta`: isi `bdmt`, `project`, `ad_account_id`, `kata_kunci_produk`, `affiliate_id` (boleh kosong).
   - [ ] Tab `parameter`: isi `hpp_persen`, `fee_gateway_persen`, `komisi_dihitung_biaya` sesuai bisnis (0/"tidak" bila tidak ada).
5. **Scheduled task**
   - [ ] Salin prompt dari `prompts/sync-harian.md`, ganti semua `{{PLACEHOLDER}}`.
   - [ ] Buat scheduled task harian (mis. 07:00). Perhatikan: task hanya jalan saat aplikasi Claude terbuka.
   - [ ] Jalankan manual sekali.

## C. Verifikasi (wajib sebelum dianggap selesai)
- [ ] Baris kemarin muncul di tab `campaign`, `adset`, `creative`.
- [ ] Total spend tab `creative` per hari sama dengan total tab `campaign`.
- [ ] Tab `sales` berisi order (SUCCESS dan PENDING) produk BDMT; tidak ada nama pembeli asli (hanya `customer_key`).
- [ ] `magic5_harian` baris TOTAL (baris 2) terisi dan tidak ada `#ERROR`/`#VALUE`.
- [ ] Laporan akhir task menyebut spend, leads, transaksi, omzet, ROAS.

## D. Jangan lupa
- Jangan mengubah header atau nama tab (dashboard membaca berdasarkan nama).
- Jangan menyimpan token, password, atau API key di sheet maupun prompt.
- Bila ad account kena restriksi Meta, task berhenti dengan error: jangan mengarang angka, laporkan ke admin.
