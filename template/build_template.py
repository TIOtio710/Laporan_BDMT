"""Bangun Performa_Iklan_TEMPLATE.xlsx (kosong, tanpa data BDMT mana pun) dan magic5_formulas.json.

Pakai:  pip install openpyxl && python build_template.py [output.xlsx]

Langkah setelah build:
1. Impor xlsx ke Google Sheets (Drive > New > File upload > buka dengan Google Sheets).
2. Pasang rumus tab magic5_harian dari magic5_formulas.json: tempel tiap rumus ke sel yang tercantum
   (A3:P3 dan B2:P2). Rumus memakai BYROW/LAMBDA yang tidak bisa diimpor dari xlsx, jadi dipasang sekali
   langsung di Google Sheets. Tanggal di kolom A muncul otomatis dari data tab campaign dan sales.
3. Isi tab _meta dan parameter.

Ini sumber kebenaran skema: ubah di sini, bukan di sheet.
"""
import json
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Font

OUT = sys.argv[1] if len(sys.argv) > 1 else "Performa_Iklan_TEMPLATE.xlsx"
R = 5000  # batas baris yang dibaca rumus

M = ["spend", "impressions", "clicks", "ctr_pct", "cpm", "cpc", "reach", "leads", "cost_per_lead"]
X = ["link_clicks", "landing_page_views", "initiated_checkout_meta", "purchases_meta", "purchase_value_meta"]

HEADERS = {
    "campaign": ["tanggal", "campaign_id", "campaign_name", "status"] + M + X,
    "adset": ["tanggal", "campaign_id", "campaign_name", "adset_id", "adset_name", "status"] + M + X,
    "creative": ["tanggal", "campaign_id", "campaign_name", "adset_id", "adset_name",
                 "ad_id", "ad_name", "creative_id", "status"] + M + X,
    "sales": ["tanggal", "order_id", "produk", "qty", "omzet", "affiliate_id", "status",
              "customer_key", "komisi_persen"],
}
MAGIC5_HEADER = ["tanggal", "spend", "klik_link", "leads_lpv", "checkout_dibuat", "transaksi", "konversi_pct",
                 "omzet", "aov", "pelanggan_unik", "frekuensi_beli", "biaya_hpp", "biaya_fee", "biaya_komisi",
                 "profit", "margin_pct"]

PARAM = [
    ("hpp_persen", 0, "HPP sebagai desimal dari omzet, mis. 0.10 = 10%. Isi sesuai bisnis BDMT; 0 = tidak ada HPP"),
    ("fee_gateway_persen", 0, "Fee payment gateway, desimal dari omzet. 0 = tidak dihitung"),
    ("komisi_dihitung_biaya", "tidak", '"ya" = komisi_persen order ber-affiliate dihitung sebagai biaya; "tidak" = tidak'),
    ("definisi_leads", "landing_page_view", "Leads di ringkasan = kolom landing_page_views. Alternatif: link_clicks (ubah rumus kolom D di magic5_formulas.json)"),
]
META = [
    ("bdmt", "ISI_NAMA_BDMT"),
    ("project", "ISI_NAMA_PROJECT"),
    ("ad_account_id", "ISI_AD_ACCOUNT_ID"),
    ("kata_kunci_produk", "ISI_KATA_KUNCI_PRODUK"),
    ("affiliate_id", "ISI_AFFILIATE_ID_ATAU_KOSONGKAN"),
    ("schema_version", "2"),
    ("last_sync", ""),
]

# --- rumus magic5_harian (Google Sheets) -----------------------------------
DATE = f'TEXT(campaign!$A$2:$A${R},"yyyy-mm-dd")'
SDATE = f'TEXT(sales!$A$2:$A${R},"yyyy-mm-dd")'
OK = f'(sales!$G$2:$G${R}="SUCCESS")'


def byrow(expr):
    return f'=BYROW($A$3:$A,LAMBDA(d,IF(d="","",{expr})))'


def arr(expr):
    return f'=ARRAYFORMULA(IF($A$3:$A="","",{expr}))'


UNIQ = (f"(COUNTIFS(sales!$A$2:$A${R},sales!$A$2:$A${R},sales!$H$2:$H${R},sales!$H$2:$H${R},"
        f'sales!$G$2:$G${R},sales!$G$2:$G${R})+(sales!$A$2:$A${R}=""))')

ROW3 = {
    "A3": (f'=IFERROR(SORT(UNIQUE(ARRAYFORMULA(TEXT(FILTER({{campaign!$A$2:$A${R};sales!$A$2:$A${R}}},'
           f'{{campaign!$A$2:$A${R};sales!$A$2:$A${R}}}<>""),"yyyy-mm-dd")))),"")'),
    "B3": byrow(f"SUMPRODUCT(({DATE}=d)*campaign!$E$2:$E${R})"),
    "C3": byrow(f"SUMPRODUCT(({DATE}=d)*campaign!$N$2:$N${R})"),
    "D3": byrow(f"SUMPRODUCT(({DATE}=d)*campaign!$O$2:$O${R})"),
    "E3": byrow(f'SUMPRODUCT(({SDATE}=d)*(sales!$B$2:$B${R}<>""))'),
    "F3": byrow(f"SUMPRODUCT(({SDATE}=d)*{OK})"),
    "G3": arr("IFERROR($F$3:$F/$D$3:$D,0)"),
    "H3": byrow(f"SUMPRODUCT(({SDATE}=d)*{OK}*sales!$E$2:$E${R})"),
    "I3": arr("IFERROR($H$3:$H/$F$3:$F,0)"),
    "J3": byrow(f"SUMPRODUCT(({SDATE}=d)*{OK}/{UNIQ})"),
    "K3": arr("IFERROR($F$3:$F/$J$3:$J,0)"),
    "L3": arr("$H$3:$H*parameter!$B$2"),
    "M3": arr("$H$3:$H*parameter!$B$3"),
    "N3": byrow(f'IF(parameter!$B$4="ya",SUMPRODUCT(({SDATE}=d)*{OK}*sales!$E$2:$E${R}*sales!$I$2:$I${R}/100),0)'),
    "O3": arr("$H$3:$H-$L$3:$L-$M$3:$M-$N$3:$N-$B$3:$B"),
    "P3": arr("IFERROR($O$3:$O/$H$3:$H,0)"),
}
ROW2 = {
    "B2": "=SUM(B3:B)", "C2": "=SUM(C3:C)", "D2": "=SUM(D3:D)", "E2": "=SUM(E3:E)", "F2": "=SUM(F3:F)",
    "G2": "=IFERROR(F2/D2,0)", "H2": "=SUM(H3:H)", "I2": "=IFERROR(H2/F2,0)",
    "J2": (f'=SUMPRODUCT({OK}/(COUNTIFS(sales!$H$2:$H${R},sales!$H$2:$H${R},sales!$G$2:$G${R},'
           f'sales!$G$2:$G${R})+(sales!$H$2:$H${R}="")))'),
    "K2": "=IFERROR(F2/J2,0)", "L2": "=SUM(L3:L)", "M2": "=SUM(M3:M)", "N2": "=SUM(N3:N)",
    "O2": "=SUM(O3:O)", "P2": "=IFERROR(O2/H2,0)",
}

wb = Workbook()
ws = wb.active
ws.title = "magic5_harian"
ws.append(MAGIC5_HEADER)
ws.append(["TOTAL"])
for cell in list(ws[1]) + list(ws[2]):
    cell.font = Font(bold=True)
for r in range(2, 1001):
    ws[f"G{r}"].number_format = "0.00%"
    ws[f"P{r}"].number_format = "0.0%"

for name, header in HEADERS.items():
    w = wb.create_sheet(name)
    w.append(header)
    for cell in w[1]:
        cell.font = Font(bold=True)

w = wb.create_sheet("parameter")
w.append(["key", "value", "catatan"])
for row in PARAM:
    w.append(list(row))

w = wb.create_sheet("_meta")
w.append(["key", "value"])
for row in META:
    w.append(list(row))

wb.save(OUT)
json_path = os.path.join(os.path.dirname(os.path.abspath(OUT)), "magic5_formulas.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"sheet": "magic5_harian", "row3": ROW3, "row2": ROW2}, f, ensure_ascii=False, indent=2)
print("OK", OUT, json_path)
