import re
import unicodedata
import io
from io import BytesIO
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="BGTK | Analisis TO 1 & TO 2", page_icon="📊", layout="wide")

SUBJECTS = {
    "Bahasa Indonesia": {
        "raw": ["DATA 1_B. INDONESIA", "DATA 1_B. INDO"],
        "indicator": [
            "ANALISIS INDIKATOR B.INDO",
            "ANALISIS REKAP INDIKATOR B.INDO",
            "ANLISIS REKAP INDKTR. B INDO",
            "REKAP INDIKATOR BAHASA INDONESIA",
            "ANALISIS REKAP INDIKATOR BAHASA INDONESIA",
        ],
    },
    "Bahasa Inggris": {
        "raw": ["DATA 1_B. INGGRIS"],
        "indicator": [
            "ANLISIS REKAP INDKTR. B INGGRIS",
            "ANALISIS REKAP INDIKATOR B INGGRIS",
            "REKAP INDIKATOR BAHASA INGGRIS",
            "ANALISIS REKAP INDIKATOR BAHASA INGGRIS",
            "ANALISIS INDIKATOR B.INGGRIS",
        ],
    },
    "Matematika": {
        "raw": ["DATA 1_MATEMATIKA"],
        "indicator": [
            "ANLISIS REKAP INDKTR. MATEMTK",
            "ANALISIS REKAP INDIKATOR MATEMATIKA",
            "REKAP INDIKATOR MATEMATIKA",
            "ANALISIS INDIKATOR MATEMATIKA",
            "ANALISIS REKAP INDIKATOR MATEMATIKA",
        ],
    },
}

DISTRICTS = [
    "Bombana", "Buton", "Buton Selatan", "Buton Tengah", "Buton Utara",
    "Kolaka", "Kolaka Timur", "Kolaka Utara", "Konawe",
    "Konawe Kepulauan", "Konawe Selatan", "Konawe Utara",
    "Muna", "Muna Barat", "Wakatobi", "Kota Baubau", "Kota Kendari",
    "Belum dipetakan",
]
# Pemetaan khusus sekolah yang sudah dikonfirmasi berada di Kabupaten Bombana.
# Alias digunakan agar variasi nama pada nama file/lembar Excel tetap dikenali.
SCHOOL_DISTRICT_ALIASES = {
    "Bombana": [
        "smas al wahdah bombana",
        "smas al wahdah",
        "smas islam nusantara bombana",
        "smas nusantara bombana",
        "smas matabundu bombana",
        "smas matabundu",
        "smas tongkoseng bombana",
        "smas tongkoseng",
        "smas tontonunu bombana",
        "smas tontonunu",
    ],
}
ALIASES = {
    "Konawe Kepulauan": ["konawe kepulauan", "konawe kep"],
    "Konawe Selatan": ["konawe selatan", "konsel"],
    "Konawe Utara": ["konawe utara", "konut"],
    "Kolaka Utara": ["kolaka utara", "kolut"],
    "Kolaka Timur": ["kolaka timur", "koltim"],
    "Buton Selatan": ["buton selatan", "busel"],
    "Buton Tengah": ["buton tengah", "buteng"],
    "Buton Utara": ["buton utara", "butur"],
    "Muna Barat": ["muna barat", "mubar"],
    "Kota Kendari": ["kota kendari", "kendari"],
    "Kota Baubau": ["kota baubau", "baubau"],
    "Bombana": ["bombana"], "Wakatobi": ["wakatobi"],
    "Kolaka": ["kolaka"], "Konawe": ["konawe"],
    "Buton": ["buton"], "Muna": ["muna"],
}
COLORS = {
    "Bahasa Indonesia": "#2563EB",
    "Bahasa Inggris": "#0F766E",
    "Matematika": "#F59E0B",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#F4F7FB;}
[data-testid="stSidebar"] {background:#14243D;}
[data-testid="stSidebar"] * {color:#F8FAFC;}
/* PERBAIKAN NAMA FILE UPLOAD AGAR TERLIHAT */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border-radius: 10px;
    padding: 10px;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: #14243D !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    color: #FFFFFF !important;
    background: #1D4E89 !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] div {
    color: #14243D !important;
}
/* PERBAIKAN WARNA FILTER KABUPATEN DAN PUTARAN */
[data-testid="stSidebar"] [data-testid="stSelectbox"] label {
    color: #F8FAFC !important;
}

/* Kotak pilihan yang sedang tampil */
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
}

/* Tulisan nilai yang sedang dipilih */
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #14243D !important;
}

/* Tulisan pilihan di menu dropdown */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] {
    background-color: #FFFFFF !important;
    color: #14243D !important;
}

[data-baseweb="popover"] [role="option"] * {
    color: #14243D !important;
}
.hero {background:linear-gradient(115deg,#14243D,#1D4E89 58%,#0F766E);
border-radius:18px;padding:25px 30px;color:white;margin-bottom:20px;}
.hero h1 {color:white;font-size:28px;margin:0 0 5px;font-weight:800;}
.hero p {color:#DCEAFE;margin:0;font-size:14px;}
.section-title {color:#14243D;font-size:19px;font-weight:800;margin:18px 0 10px;}
.metric {background:white;border:1px solid #E5EAF2;border-radius:15px;padding:17px 19px;min-height:105px;box-shadow:0 3px 12px rgba(15,23,42,.035);}
.metric-label {color:#64748B;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;}
.metric-value {color:#14243D;font-size:27px;font-weight:800;margin-top:8px;}
.metric-note {color:#94A3B8;font-size:11px;margin-top:2px;}
.info {background:#EFF6FF;border-left:4px solid #2563EB;padding:12px 15px;border-radius:8px;color:#1E3A8A;font-size:13px;margin:8px 0 16px;}
.main .block-container {max-width:1600px;padding-top:1.5rem;padding-bottom:3rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>School Assessment Analytics</h1><p>Dashboard pemantauan hasil Try Out 1 dan Try Out 2 · BGTK</p></div>', unsafe_allow_html=True)


def norm(v):
    return re.sub(r"\s+", " ", str(v).replace("\n", " ").strip()).casefold()


def clean_school(v, fallback="Nama sekolah tidak tersedia"):
    if pd.isna(v) or not str(v).strip():
        return fallback
    s = re.sub(r"\s+", " ", str(v)).strip()
    s = re.sub(r"\s*\.\s*", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(?i)^SMAN\s*", "SMAN ", s)
    return s.upper() if s.casefold().startswith("sman ") else s


def parse_number(v):
    if pd.isna(v):
        return np.nan
    if isinstance(v, (int, float, np.number)):
        return float(v)
    s = str(v).strip().replace("%", "")
    # Format angka Indonesia: 1.234,50
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else np.nan


def find_sheet(sheet_names, candidates):
    lookup = {norm(x): x for x in sheet_names}
    for candidate in candidates:
        if norm(candidate) in lookup:
            return lookup[norm(candidate)]
    for candidate in candidates:
        key = norm(candidate)
        for sheet in sheet_names:
            if key in norm(sheet) or norm(sheet) in key:
                return sheet
    return None


def find_col(columns, names=(), contains=()):
    for name in names:
        for col in columns:
            if norm(col) == norm(name):
                return col
    for col in columns:
        if contains and all(term in norm(col) for term in contains):
            return col
    return None


def identify_district(school):
    s = re.sub(r"[^a-z0-9\s]", " ", norm(school))
    s = re.sub(r"\s+", " ", s).strip()
    # Pemetaan sekolah yang telah dikonfirmasi diprioritaskan agar nama
    # sekolah tanpa kata "Bombana" tidak tertinggal sebagai belum dipetakan.
    for district, aliases in SCHOOL_DISTRICT_ALIASES.items():
        for alias in aliases:
            alias_norm = re.sub(r"\s+", " ", norm(alias)).strip()
            if s == alias_norm or re.search(r"(?<![a-z0-9])" + re.escape(alias_norm) + r"(?![a-z0-9])", s):
                return district, "Otomatis"
    found = []
    for district, aliases in ALIASES.items():
        for alias in aliases:
            if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", s):
                found.append(district)
                break
    found = list(dict.fromkeys(found))
    return (found[0], "Otomatis") if len(found) == 1 else ("Belum dipetakan", "Perlu diperiksa")


def subject_for_raw(sheet):
    s = norm(sheet)
    if "data 1" not in s:
        return None
    if "indonesia" in s or "indo" in s:
        return "Bahasa Indonesia"
    if "inggris" in s:
        return "Bahasa Inggris"
    if "matematika" in s:
        return "Matematika"
    return None


def read_students(xls, sheet, filename, round_name):
    df = pd.read_excel(xls, sheet_name=sheet)
    if df.empty:
        return pd.DataFrame()
    df.columns = [str(c).strip() for c in df.columns]
    school_col = find_col(df.columns, ["Nama Sekolah", "Sekolah"])
    district_col = find_col(df.columns, ["Kabupaten", "Kabupaten/Kota", "Kabupaten Kota", "Kota", "Nama Kabupaten/Kota"])
    name_col = find_col(df.columns, ["Nama", "Name"])
    nis_col = find_col(df.columns, ["NIS", "NISN", "Nomor Induk"])
    class_col = find_col(df.columns, contains=["kelas"])
    score_col = find_col(df.columns, ["Total score", "Total skor", "Total nilai", "Nilai"])
    school_hint = re.sub(r"\.(xlsx|xls)$", "", filename, flags=re.I)
    out = pd.DataFrame()
    out["Sekolah"] = df[school_col].apply(clean_school) if school_col else clean_school(school_hint)
    out["Kabupaten/Kota"] = df[district_col].astype("string").str.strip() if district_col else "Belum dipetakan"
    out["Nama Siswa"] = df[name_col].astype("string").str.strip() if name_col else "Tidak tersedia"
    out["NIS"] = df[nis_col].astype("string").str.strip() if nis_col else ""
    out["Kelas"] = df[class_col].astype("string").str.strip() if class_col else "Tidak tersedia"
    out["Nilai"] = df[score_col].apply(parse_number) if score_col else np.nan
    time_col = find_col(df.columns, ["Timestamp", "Cap waktu", "Waktu Pengumpulan"])
    out["Waktu Pengumpulan"] = pd.to_datetime(df[time_col], errors="coerce") if time_col else pd.NaT
    out["Mata Pelajaran"] = subject_for_raw(sheet)
    out["Try Out"] = round_name
    out = out[out["Nama Siswa"].notna() & (out["Nama Siswa"].astype(str).str.strip() != "") & out["Nilai"].notna()]
    return out



def read_indicators(xls, sheet, school, subject, round_name):
    df = pd.read_excel(xls, sheet_name=sheet)

    if df.empty:
        return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.columns]

    def find_indicator_col(columns, aliases):
        # Normalisasi nama kolom: abaikan spasi, titik, tanda kurung, dan simbol
        normalized = {
            re.sub(r"[^a-z0-9]", "", norm(col)): col
            for col in columns
        }

        for alias in aliases:
            key = re.sub(r"[^a-z0-9]", "", norm(alias))
            if key in normalized:
                return normalized[key]

        # Pencarian berdasarkan kata kunci
        for col in columns:
            key = re.sub(r"[^a-z0-9]", "", norm(col))
            for alias in aliases:
                alias_key = re.sub(r"[^a-z0-9]", "", norm(alias))
                if alias_key and alias_key in key:
                    return col

        return None

    mapping = {
        "No Soal": ["NO SOAL", "NOMOR SOAL"],
        "No Indikator": ["NO INDIKATOR", "NOMOR INDIKATOR"],
        "Rata-rata": ["RATA RATA", "RATA-RATA"],
        "Ketercapaian": [
            "KETERCAPAIAN",
            "PERSENTASE KETERCAPAIAN",
            "KETERCAPAIAN (%)",
            "PERSENTASE",
            "PERSENTASE (%)",
            "CAPAIAN",
        ],
        "Kategori Soal": ["KATEGORI SOAL", "KATEGORI"],
        "Indikator": ["INDIKATOR"],
        "Kompetensi": ["KOMPETENSI", "KOMOETENSI"],
        "Sub Elemen": ["SUB ELEMEN"],
        "Elemen": ["ELEMEN"],
    }

    rename = {}

    for standard, aliases in mapping.items():
        col = find_indicator_col(df.columns, aliases)
        if col:
            rename[col] = standard

    df = df.rename(columns=rename)

    if "Ketercapaian" in df.columns:
        df["Ketercapaian"] = df["Ketercapaian"].apply(parse_number)

    if "Rata-rata" in df.columns:
        df["Rata-rata"] = df["Rata-rata"].apply(parse_number)

    df["Sekolah"] = clean_school(school)
    df["Mata Pelajaran"] = subject
    df["Try Out"] = round_name

    return df


def process_uploads(files, round_name):
    students, indicators, logs = [], [], []
    for file in files or []:
        try:
            xls = pd.ExcelFile(BytesIO(file.getvalue()))
            parts = []
            for sheet in xls.sheet_names:
                subject = subject_for_raw(sheet)
                if subject:
                    part = read_students(xls, sheet, file.name, round_name)
                    if not part.empty:
                        parts.append(part)
            if parts:
                combined = pd.concat(parts, ignore_index=True)
                students.append(combined)
                schools = sorted(combined["Sekolah"].dropna().unique())
            else:
                schools = [clean_school(re.sub(r"\.(xlsx|xls)$", "", file.name, flags=re.I))]
            indicator_count = 0
            for subject, cfg in SUBJECTS.items():
                indicator_sheet = find_sheet(xls.sheet_names, cfg["indicator"])
                if indicator_sheet:
                    for school in schools:
                        ind = read_indicators(xls, indicator_sheet, school, subject, round_name)
                        if not ind.empty:
                            indicators.append(ind)
                    indicator_count += 1
            logs.append({
                "Try Out": round_name, "Nama file": file.name,
                "Status": "Berhasil" if parts else "Sheet data siswa tidak ditemukan",
                "Jumlah siswa": sum(len(x) for x in parts),
                "Jumlah sekolah": len(schools), "Sheet indikator terbaca": indicator_count,
            })
        except Exception as exc:
            logs.append({"Try Out": round_name, "Nama file": file.name, "Status": f"Gagal dibaca: {exc}",
                         "Jumlah siswa": 0, "Jumlah sekolah": 0, "Sheet indikator terbaca": 0})
    sdf = pd.concat(students, ignore_index=True) if students else pd.DataFrame()
    idf = pd.concat(indicators, ignore_index=True) if indicators else pd.DataFrame()
    return sdf, idf, pd.DataFrame(logs)


def school_subject_means(df):
    return (df.groupby(["Sekolah", "Mata Pelajaran"], as_index=False)
              .agg(Rata_rata=("Nilai", "mean"), Jumlah_peserta=("Nilai", "count")))


def ranking_tables(df):
    required = list(SUBJECTS.keys())

    # Rata-rata setiap sekolah untuk masing-masing mata pelajaran
    means = (
        df.groupby(
            ["Sekolah", "Mata Pelajaran"],
            as_index=False
        )
        .agg(
            Rata_rata=("Nilai", "mean"),
            Jumlah_peserta=("Nilai", "count")
        )
    )

    # Membuat tabel rata-rata tiga mata pelajaran
    pivot = means.pivot(
        index="Sekolah",
        columns="Mata Pelajaran",
        values="Rata_rata"
    )

    # Pastikan ketiga mapel tersedia
    for subject in required:
        if subject not in pivot.columns:
            pivot[subject] = np.nan

    # Hanya sekolah yang memiliki ketiga mapel
    complete = pivot.dropna(subset=required).copy()

    # Peringkat gabungan tiga mata pelajaran
    if not complete.empty:

        complete["Rata-rata 3 Mapel"] = (
            complete[required].mean(axis=1)
        )

        overall = complete.reset_index()

        overall = overall.sort_values(
            "Rata-rata 3 Mapel",
            ascending=False
        ).reset_index(drop=True)

        overall.insert(
            0,
            "Peringkat",
            range(1, len(overall) + 1)
        )

    else:
        overall = pd.DataFrame(
            columns=[
                "Peringkat",
                "Sekolah",
                *required,
                "Rata-rata 3 Mapel"
            ]
        )

    # Peringkat masing-masing mata pelajaran
    subject_rankings = {}

    for subject in required:

        one = means[
            means["Mata Pelajaran"] == subject
        ].copy()

        one = one.sort_values(
            "Rata_rata",
            ascending=False
        ).reset_index(drop=True)

        one.insert(
            0,
            "Peringkat",
            range(1, len(one) + 1)
        )

        subject_rankings[subject] = one

    return overall, subject_rankings, means



def metric_card(label, value, note=""):
    st.markdown(
        f'<div class="metric"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def fmt_table(df):
    return df.round(2) if not df.empty else df


def show_dataframe(df, *args, **kwargs):
    """Menampilkan tabel tanpa menambahkan tombol unduh terpisah."""
    st.dataframe(df, *args, **kwargs)


# Sidebar uploads: dua putaran terpisah
with st.sidebar:
    st.markdown("## 📊 BGTK Analytics")
    st.caption("SCHOOL ASSESSMENT MONITORING")
    st.divider()
    to1_files = st.file_uploader("📁 Upload Excel TO 1", type=["xlsx", "xls"], accept_multiple_files=True, key="to1")
    to2_files = st.file_uploader("📁 Upload Excel TO 2", type=["xlsx", "xls"], accept_multiple_files=True, key="to2")
    st.caption("Unggah workbook sekolah sesuai putaran masing-masing.")
    st.divider()
    page = st.radio("NAVIGASI", [
        "Dashboard Utama", "Analisis Per Sekolah", "Perbandingan Sekolah",
        "Analisis Mata Pelajaran", "Peringkat per Mata Pelajaran",
        "Perbandingan TO 1 dan TO 2", "Analisis Indikator",
        "Rekap Per Kabupaten", "Data Peserta Didik", "Manajemen & Eksplorasi Data",
    ])

if not to1_files and not to2_files:
    st.info("Unggah file Excel TO 1 dan/atau TO 2 melalui panel kiri untuk memulai analisis.")
    st.markdown("**Fitur:** peringkat kabupaten/kota, peringkat per mapel, analisis indikator, dan perbandingan dua putaran.")
    st.stop()

with st.spinner("Membaca workbook Excel..."):
    s1, i1, l1 = process_uploads(to1_files, "TO 1")
    s2, i2, l2 = process_uploads(to2_files, "TO 2")
students = pd.concat([s1, s2], ignore_index=True) if not s1.empty or not s2.empty else pd.DataFrame()
indicators = pd.concat([i1, i2], ignore_index=True) if not i1.empty or not i2.empty else pd.DataFrame()
logs = pd.concat([l1, l2], ignore_index=True) if not l1.empty or not l2.empty else pd.DataFrame()

if students.empty:
    st.error("Data siswa belum terbaca. Periksa nama sheet DATA 1_B. INDONESIA, DATA 1_B. INGGRIS, dan DATA 1_MATEMATIKA serta kolom Total score/Nilai.")
    if not logs.empty:
        show_dataframe(logs, use_container_width=True, hide_index=True)
    st.stop()

students = students.drop_duplicates(
    subset=["Try Out", "Sekolah", "Mata Pelajaran", "NIS", "Nama Siswa", "Kelas", "Nilai", "Waktu Pengumpulan"],
    keep="first"
).copy()

# Gabungkan pemetaan kabupaten/kota dari kolom sumber dan deteksi nama sekolah.
school_names = sorted(students["Sekolah"].dropna().unique().tolist())
if "district_mapping" not in st.session_state:
    mapping_rows = []
    for school in school_names:
        in_source = students.loc[students["Sekolah"] == school, "Kabupaten/Kota"]
        explicit = in_source.dropna().astype(str).str.strip()
        explicit = [x for x in explicit if x and x.casefold() not in ["belum dipetakan", "nan", "none"]]
        district, status = identify_district(school)
        if status != "Otomatis" and explicit:
            district, status = explicit[0], "Dari kolom Excel"
        mapping_rows.append({"Sekolah": school, "Kabupaten/Kota": district, "Status Identifikasi": status})
    st.session_state["district_mapping"] = pd.DataFrame(mapping_rows)
else:
    old = st.session_state["district_mapping"].copy()
    old_names = set(old["Sekolah"].astype(str))
    additions = []
    for school in school_names:
        district, status = identify_district(school)
        if school not in old_names:
            additions.append({"Sekolah": school, "Kabupaten/Kota": district, "Status Identifikasi": status})
        elif status == "Otomatis":
            # Perbarui juga pemetaan lama yang mungkin tersimpan di sesi aktif.
            row_mask = old["Sekolah"].astype(str) == str(school)
            old.loc[row_mask, "Kabupaten/Kota"] = district
            old.loc[row_mask, "Status Identifikasi"] = status
    if additions:
        old = pd.concat([old, pd.DataFrame(additions)], ignore_index=True)
    st.session_state["district_mapping"] = old
mapping = st.session_state["district_mapping"].copy()

with st.sidebar:
    st.divider()
    district_values = sorted([x for x in mapping["Kabupaten/Kota"].dropna().unique() if x != "Belum dipetakan"])
    district_choice = st.selectbox("Pilih Kabupaten/Kota", ["Semua Kabupaten/Kota"] + district_values)
    round_choice = st.selectbox("Pilih putaran", ["TO 1", "TO 2", "Gabungan TO 1 & TO 2"])

district_lookup = dict(zip(mapping["Sekolah"], mapping["Kabupaten/Kota"]))
students["Kabupaten/Kota"] = students["Sekolah"].map(district_lookup).fillna("Belum dipetakan")
if not indicators.empty:
    indicators["Kabupaten/Kota"] = indicators["Sekolah"].map(district_lookup).fillna("Belum dipetakan")

def choose_round(df, choice):
    return df.copy() if choice == "Gabungan TO 1 & TO 2" else df[df["Try Out"] == choice].copy()

selected = choose_round(students, round_choice)
if district_choice != "Semua Kabupaten/Kota":
    selected = selected[selected["Kabupaten/Kota"] == district_choice]
selected_ind = choose_round(indicators, round_choice) if not indicators.empty else pd.DataFrame()
if not selected_ind.empty and district_choice != "Semua Kabupaten/Kota":
    selected_ind = selected_ind[selected_ind["Kabupaten/Kota"] == district_choice]


if page == "Dashboard Utama":
    st.subheader("Dashboard Kabupaten/Kota")
    st.caption(f"Cakupan: {district_choice} · Data: {round_choice}")
    if selected.empty:
        st.warning("Belum ada data untuk kabupaten/kota dan putaran yang dipilih.")
    else:
        overall, subject_rankings, means = ranking_tables(selected)
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Sekolah terpilih", f"{selected['Sekolah'].nunique():,}", "Sekolah dalam filter aktif")
        with c2: metric_card("Jumlah peserta", f"{len(selected):,}", "Baris nilai valid")
        with c3: metric_card("Rata-rata nilai", f"{selected['Nilai'].mean():.2f}", "Skala mengikuti file sumber")
        with c4: metric_card("Mata pelajaran", f"{selected['Mata Pelajaran'].nunique()}", "Mapel terdeteksi")
        subject_summary = selected.groupby("Mata Pelajaran", as_index=False).agg(Rata_rata=("Nilai", "mean"), Jumlah_peserta=("Nilai", "count"))
        left, right = st.columns([1.4, 1])
        with left:
            fig = px.bar(subject_summary, x="Mata Pelajaran", y="Rata_rata", color="Mata Pelajaran", text=subject_summary["Rata_rata"].map(lambda v:f"{v:.2f}"), color_discrete_map=COLORS, title="Rata-rata nilai per mata pelajaran")
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.pie(subject_summary, names="Mata Pelajaran", values="Jumlah_peserta", hole=.55, color="Mata Pelajaran", color_discrete_map=COLORS, title="Komposisi peserta per mapel")
            st.plotly_chart(fig, use_container_width=True)
        
        # =====================================================
        # PERINGKAT SEKOLAH BERDASARKAN RATA-RATA 3 MAPEL
        # =====================================================
        st.markdown("### 🏆 Peringkat Sekolah — Rata-rata 3 Mata Pelajaran")
        st.caption(
            f"Peringkat sekolah di {district_choice} · {round_choice} · "
            "Diurutkan dari nilai tertinggi ke terendah"
        )

        if overall.empty:
            st.warning(
                "Peringkat gabungan belum dapat dihitung. "
                "Setiap sekolah harus memiliki data ketiga mata pelajaran."
            )
        else:
            overall_sorted = overall.sort_values(
                "Rata-rata 3 Mapel", ascending=False
            ).copy()

            fig = px.bar(
                overall_sorted,
                x="Sekolah",
                y="Rata-rata 3 Mapel",
                text=overall_sorted["Rata-rata 3 Mapel"].map(
                    lambda x: f"{x:.2f}"
                ),
                color="Rata-rata 3 Mapel",
                color_continuous_scale="Blues",
                title="Peringkat Sekolah Berdasarkan Rata-rata 3 Mapel"
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                xaxis_tickangle=-40,
                xaxis_title="Nama Sekolah",
                yaxis_title="Rata-rata Nilai",
                coloraxis_showscale=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### Tabel Peringkat Gabungan")
            show_dataframe(
                fmt_table(overall_sorted),
                use_container_width=True,
                hide_index=True
            )

        # =====================================================
        # PERINGKAT SEKOLAH BERDASARKAN MASING-MASING MAPEL
        # =====================================================
        st.markdown("---")
        st.markdown("### 📚 Peringkat Sekolah per Mata Pelajaran")
        st.caption(
            "Setiap mata pelajaran memiliki pemeringkatan tersendiri "
            "berdasarkan rata-rata nilai sekolah."
        )

        for subject in SUBJECTS:
            st.markdown(f"#### 🏅 Peringkat {subject}")

            tab = subject_rankings[subject].copy()

            if tab.empty:
                st.info(f"Belum tersedia data untuk {subject}.")
                continue

            # Urutkan nilai dari tertinggi ke terendah
            tab = tab.sort_values(
                "Rata_rata", ascending=False
            ).reset_index(drop=True)

            # Perbarui nomor peringkat
            tab["Peringkat"] = range(1, len(tab) + 1)

            # Grafik peringkat sekolah
            fig = px.bar(
                tab,
                x="Sekolah",
                y="Rata_rata",
                text=tab["Rata_rata"].map(
                    lambda x: f"{x:.2f}"
                ),
                color="Rata_rata",
                color_continuous_scale="Blues",
                title=f"Peringkat Rata-rata {subject} per Sekolah",
                hover_data=["Peringkat", "Jumlah_peserta"]
            )

            fig.update_traces(
                textposition="outside",
                marker_line_width=0
            )

            fig.update_layout(
                xaxis_title="Nama Sekolah",
                yaxis_title="Rata-rata Nilai",
                xaxis_tickangle=-40,
                coloraxis_showscale=False,
                height=480,
                margin=dict(t=65, b=100)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # Tabel peringkat
            st.markdown(f"**Tabel Peringkat {subject}**")

            show_dataframe(
                fmt_table(tab),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Sebaran nilai peserta didik")
        left, right = st.columns(2)
        with left:
            fig = px.histogram(selected, x="Nilai", color="Mata Pelajaran", nbins=15, barmode="overlay", opacity=.78, title="Distribusi frekuensi nilai")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.box(selected, x="Mata Pelajaran", y="Nilai", color="Mata Pelajaran", color_discrete_map=COLORS, points="outliers", title="Sebaran nilai per mata pelajaran")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Analisis Per Sekolah":
    st.subheader("Analisis Mendalam per Sekolah")
    available = sorted(selected["Sekolah"].dropna().unique().tolist())
    if not available:
        st.warning("Tidak ada sekolah pada filter aktif.")
    else:
        chosen = st.selectbox("Pilih sekolah yang ingin dianalisis", available)
        school_df = selected[selected["Sekolah"] == chosen].copy()
        scores = school_df["Nilai"].dropna()
        a,b,c,d = st.columns(4)
        with a: metric_card("Peserta", f"{len(scores):,}")
        with b: metric_card("Rata-rata", f"{scores.mean():.2f}" if len(scores) else "—")
        with c: metric_card("Nilai tertinggi", f"{scores.max():.2f}" if len(scores) else "—")
        with d: metric_card("Nilai terendah", f"{scores.min():.2f}" if len(scores) else "—")
        by_subject = school_df.groupby("Mata Pelajaran", as_index=False).agg(Rata_rata=("Nilai","mean"), Peserta=("Nilai","count"))
        left,right = st.columns(2)
        with left:
            fig=px.bar(by_subject,x="Mata Pelajaran",y="Rata_rata",color="Mata Pelajaran",color_discrete_map=COLORS,title="Rata-rata nilai per mata pelajaran")
            st.plotly_chart(fig,use_container_width=True)
        with right:
            fig=px.pie(by_subject,names="Mata Pelajaran",values="Peserta",hole=.55,title="Komposisi peserta")
            st.plotly_chart(fig,use_container_width=True)
        class_summary=school_df.groupby(["Mata Pelajaran","Kelas"],as_index=False).agg(Jumlah=("Nilai","count"),Rata_rata=("Nilai","mean"))
        fig=px.bar(class_summary,x="Kelas",y="Rata_rata",color="Mata Pelajaran",barmode="group",title="Perbandingan rata-rata nilai antarkelas")
        st.plotly_chart(fig,use_container_width=True)
        show_dataframe(fmt_table(class_summary),use_container_width=True,hide_index=True)

elif page == "Perbandingan Sekolah":
    st.subheader("Perbandingan Performa Antarsekolah")
    if selected.empty:
        st.warning("Tidak ada data pada filter aktif.")
    else:
        subject_cmp=st.selectbox("Mata pelajaran untuk dibandingkan",["Semua mata pelajaran"]+list(SUBJECTS.keys()))
        cmp=selected if subject_cmp=="Semua mata pelajaran" else selected[selected["Mata Pelajaran"]==subject_cmp]
        summary=cmp.groupby("Sekolah",as_index=False).agg(Jumlah_peserta=("Nilai","count"),Rata_rata=("Nilai","mean"),Median=("Nilai","median"),Tertinggi=("Nilai","max"),Terendah=("Nilai","min")).sort_values("Rata_rata",ascending=False)
        summary.insert(0,"Peringkat",range(1,len(summary)+1))
        fig=px.bar(summary,x="Sekolah",y="Rata_rata",color="Rata_rata",color_continuous_scale="Tealgrn",title="Peringkat rata-rata nilai sekolah")
        fig.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig,use_container_width=True)
        show_dataframe(fmt_table(summary),use_container_width=True,hide_index=True)
        subj=cmp.groupby(["Sekolah","Mata Pelajaran"],as_index=False)["Nilai"].mean()
        fig=px.bar(subj,x="Sekolah",y="Nilai",color="Mata Pelajaran",barmode="group",color_discrete_map=COLORS,title="Perbandingan nilai berdasarkan mata pelajaran")
        fig.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig,use_container_width=True)

elif page == "Analisis Mata Pelajaran":
    st.subheader("Analisis Mata Pelajaran")
    if selected.empty:
        st.warning("Tidak ada data pada filter aktif.")
    else:
        subject=st.selectbox("Pilih mata pelajaran",list(SUBJECTS.keys()),key="analysis_subject")
        part=selected[selected["Mata Pelajaran"]==subject].copy()
        scores=part["Nilai"].dropna()
        a,b,c,d=st.columns(4)
        with a: metric_card("Jumlah peserta",f"{len(scores):,}")
        with b: metric_card("Rata-rata",f"{scores.mean():.2f}" if len(scores) else "—")
        with c: metric_card("Median",f"{scores.median():.2f}" if len(scores) else "—")
        with d: metric_card("Rentang nilai",f"{scores.min():.1f}–{scores.max():.1f}" if len(scores) else "—")
        school_subject=part.groupby("Sekolah",as_index=False).agg(Rata_rata=("Nilai","mean"),Peserta=("Nilai","count")).sort_values("Rata_rata",ascending=False)
        fig=px.bar(school_subject,x="Sekolah",y="Rata_rata",color="Rata_rata",color_continuous_scale="Blues",title=f"Rata-rata {subject} per sekolah")
        fig.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig,use_container_width=True)
        left,right=st.columns(2)
        with left:
            fig=px.histogram(part,x="Nilai",nbins=15,title="Distribusi nilai")
            st.plotly_chart(fig,use_container_width=True)
        with right:
            fig=px.box(part,y="Nilai",points="all",title="Sebaran nilai")
            st.plotly_chart(fig,use_container_width=True)

elif page == "Peringkat per Mata Pelajaran":
    st.subheader("Peringkat Sekolah per Mata Pelajaran")
    st.caption(f"Cakupan: {district_choice} · Data: {round_choice}")
    subject = st.selectbox("Pilih mata pelajaran", list(SUBJECTS.keys()))
    if selected.empty:
        st.warning("Tidak ada data pada filter yang dipilih.")
    else:
        overall, ranks, means = ranking_tables(selected)
        rank = ranks[subject]
        if rank.empty:
            st.warning(f"Belum ada data untuk {subject}.")
        else:
            st.metric(f"Rata-rata kabupaten/kota — {subject}", f"{selected.loc[selected['Mata Pelajaran']==subject, 'Nilai'].mean():.2f}")
            show_dataframe(fmt_table(rank), use_container_width=True, hide_index=True)
            fig = px.bar(rank, x="Sekolah", y="Rata_rata", text=rank["Rata_rata"].map(lambda x: f"{x:.2f}"),
                         color="Rata_rata", color_continuous_scale="Blues",
                         title=f"Peringkat {subject} — tertinggi ke terendah")
            fig.update_traces(textposition="outside")
            fig.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Perbandingan TO 1 dan TO 2":
    st.subheader("Perbandingan Hasil TO 1 dan TO 2")
    if district_choice == "Semua Kabupaten/Kota":
        st.caption("Perbandingan seluruh kabupaten/kota. Pilih kabupaten/kota di sidebar untuk mempersempit hasil.")

    # Samakan identitas sekolah berdasarkan nama yang sudah dinormalisasi.
    # Perbedaan huruf besar/kecil dan spasi tidak akan membuat sekolah terpisah.
    def school_match_key(value):
        """Normalisasi nama sekolah agar variasi kapitalisasi/penulisan tergabung."""
        if pd.isna(value):
            return ""
        name = unicodedata.normalize("NFKC", str(value))
        name = name.replace("\u200b", "").replace("\ufeff", "").replace("\xa0", " ")
        name = re.sub(r"\s+", " ", name).strip().casefold()
        # SMA SWASTA X dan SMAS X dianggap nama sekolah yang sama.
        name = re.sub(r"^sma\s+swasta\b", "smas", name)
        # Abaikan tanda baca serta samakan kembali spasi.
        name = re.sub(r"[^\w\s]", " ", name, flags=re.UNICODE)
        name = re.sub(r"\s+", " ", name).strip()
        # Alias khusus yang sudah dikonfirmasi pengguna:
        # "SMA Kingdom akademik" (TO 1) dan
        # "SMAS Kingdom Akademi" (TO 2) adalah sekolah yang sama.
        confirmed_aliases = {
            "sma kingdom akademik": "kingdom akademi",
            "smas kingdom akademi": "kingdom akademi",
        }
        return confirmed_aliases.get(name, name)

    a = s1.copy()
    b = s2.copy()

    # Peta nama kanonis: jika sekolah muncul di kedua putaran dengan kapitalisasi
    # berbeda, gunakan satu nama tampilan yang sama (prioritas nama dari TO 1).
    all_school_names = pd.concat(
        [a["Sekolah"], b["Sekolah"]], ignore_index=True
    ).dropna().astype(str)
    canonical_school_names = {}
    for school_name in all_school_names:
        key = school_match_key(school_name)
        if key and key not in canonical_school_names:
            canonical_school_names[key] = clean_school(school_name)

    # Nama tampilan baku untuk sekolah Kingdom Akademi.
    if "kingdom akademi" in canonical_school_names:
        canonical_school_names["kingdom akademi"] = "SMAS Kingdom Akademi"

    if not a.empty:
        a["_school_key"] = a["Sekolah"].map(school_match_key)
        a["Sekolah"] = a["_school_key"].map(canonical_school_names)
    if not b.empty:
        b["_school_key"] = b["Sekolah"].map(school_match_key)
        b["Sekolah"] = b["_school_key"].map(canonical_school_names)

    # Pemetaan kabupaten/kota juga dicocokkan tanpa membedakan kapitalisasi.
    district_by_school_key = {
        school_match_key(school): district
        for school, district in zip(mapping["Sekolah"], mapping["Kabupaten/Kota"])
    }
    if not a.empty:
        a["Kabupaten/Kota"] = a["Sekolah"].map(
            lambda name: district_by_school_key.get(school_match_key(name), "Belum dipetakan")
        )
    if not b.empty:
        b["Kabupaten/Kota"] = b["Sekolah"].map(
            lambda name: district_by_school_key.get(school_match_key(name), "Belum dipetakan")
        )

    if district_choice != "Semua Kabupaten/Kota":
        a = a[a["Kabupaten/Kota"] == district_choice]
        b = b[b["Kabupaten/Kota"] == district_choice]

    if a.empty or b.empty:
        st.warning("Untuk membandingkan, unggah data TO 1 dan TO 2 terlebih dahulu.")
    else:
        def means_round(df, label):
            x = school_subject_means(df)
            x["Try Out"] = label
            return x

        comp = pd.concat([means_round(a, "TO 1"), means_round(b, "TO 2")], ignore_index=True)

        # Rata-rata gabungan dihitung dari mapel yang tersedia agar sekolah dengan
        # data belum lengkap tetap tampil. Jumlah mapel tersedia ditampilkan transparan.
        overall_rounds = []
        for label, frame in [("TO 1", a), ("TO 2", b)]:
            _, _, subject_means = ranking_tables(frame)
            if subject_means.empty:
                continue
            pivot_round = subject_means.pivot_table(
                index="Sekolah", columns="Mata Pelajaran", values="Rata_rata", aggfunc="mean"
            )
            available_subjects = [sub for sub in SUBJECTS if sub in pivot_round.columns]
            if available_subjects:
                values = pivot_round[available_subjects]
                overall_rounds.append(pd.DataFrame({
                    "Sekolah": pivot_round.index,
                    f"Rata-rata {label}": values.mean(axis=1, skipna=True).values,
                    f"Jumlah mapel {label}": values.notna().sum(axis=1).values,
                    "Try Out": label
                }))
        if overall_rounds:
            overall_comp = pd.concat(overall_rounds, ignore_index=True)
            overall_pivot = overall_comp.pivot_table(
                index="Sekolah", columns="Try Out",
                values=["Rata-rata TO 1", "Rata-rata TO 2", "Jumlah mapel TO 1", "Jumlah mapel TO 2"],
                aggfunc="first"
            )
            overall_pivot.columns = [f"{metric}" for metric, round_name in overall_pivot.columns]
            overall_pivot = overall_pivot.reset_index()
            for col in ["Rata-rata TO 1", "Rata-rata TO 2", "Jumlah mapel TO 1", "Jumlah mapel TO 2"]:
                if col not in overall_pivot:
                    overall_pivot[col] = np.nan
            overall_pivot["Perubahan rata-rata"] = overall_pivot["Rata-rata TO 2"] - overall_pivot["Rata-rata TO 1"]
            st.markdown("### Perbandingan rata-rata gabungan mata pelajaran")
            st.caption("Rata-rata dihitung dari mapel yang tersedia pada masing-masing sekolah. Kolom jumlah mapel menunjukkan kelengkapan data (maksimal 3 mapel).")
            show_dataframe(
                fmt_table(overall_pivot.sort_values("Rata-rata TO 2", ascending=False, na_position="last")),
                use_container_width=True, hide_index=True
            )

        piv = comp.pivot_table(index=["Sekolah", "Mata Pelajaran"], columns="Try Out", values="Rata_rata").reset_index()
        if "TO 1" not in piv: piv["TO 1"] = np.nan
        if "TO 2" not in piv: piv["TO 2"] = np.nan
        piv["Perubahan Nilai"] = piv["TO 2"] - piv["TO 1"]
        piv["Keterangan"] = np.select([piv["Perubahan Nilai"] > 0, piv["Perubahan Nilai"] < 0],
                                       ["Meningkat", "Menurun"], default="Tetap")
        st.markdown("### Perbandingan rata-rata per sekolah dan mapel")
        show_dataframe(fmt_table(piv.sort_values(["Mata Pelajaran", "TO 2"], ascending=[True, False])),
                     use_container_width=True, hide_index=True)
        subject = st.selectbox("Grafik perbandingan mapel", list(SUBJECTS.keys()))
        chart = piv[piv["Mata Pelajaran"] == subject].melt(
            id_vars="Sekolah", value_vars=["TO 1", "TO 2"], var_name="Putaran", value_name="Rata-rata")
        fig = px.bar(chart, x="Sekolah", y="Rata-rata", color="Putaran", barmode="group",
                     title=f"Perbandingan {subject}: TO 1 vs TO 2")
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### Perubahan peringkat sekolah (mapel terpilih)")
        old = piv[piv["Mata Pelajaran"] == subject][["Sekolah", "TO 1"]].dropna().sort_values("TO 1", ascending=False)
        new = piv[piv["Mata Pelajaran"] == subject][["Sekolah", "TO 2"]].dropna().sort_values("TO 2", ascending=False)
        old["Peringkat TO 1"] = range(1, len(old) + 1)
        new["Peringkat TO 2"] = range(1, len(new) + 1)
        shift = old[["Sekolah", "Peringkat TO 1"]].merge(new[["Sekolah", "Peringkat TO 2"]], on="Sekolah", how="outer")
        shift["Perubahan peringkat"] = shift["Peringkat TO 1"] - shift["Peringkat TO 2"]
        show_dataframe(shift.sort_values("Peringkat TO 2"), use_container_width=True, hide_index=True)

elif page == "Analisis Indikator":
    st.subheader("Analisis Ketercapaian Indikator")
    if selected_ind.empty or "Ketercapaian" not in selected_ind.columns:
        st.warning("Data indikator belum terbaca pada file/putaran/filter ini. Pastikan sheet rekap indikator tersedia.")
    else:
        subject = st.selectbox("Pilih mata pelajaran", list(SUBJECTS.keys()))
        ind = selected_ind[selected_ind["Mata Pelajaran"] == subject].copy()
        school_opts = ["Semua sekolah"] + sorted(ind["Sekolah"].dropna().unique().tolist())
        school = st.selectbox("Pilih sekolah", school_opts)
        if school != "Semua sekolah":
            ind = ind[ind["Sekolah"] == school]
        valid = ind.dropna(subset=["Ketercapaian"]).copy()
        if valid.empty:
            st.warning("Tidak ada nilai ketercapaian indikator yang valid.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Jumlah baris indikator", len(valid))
            c2.metric("Rata-rata ketercapaian", f"{valid['Ketercapaian'].mean():.2f}%")
            c3.metric("Ketercapaian terendah", f"{valid['Ketercapaian'].min():.2f}%")
            label = "Indikator" if "Indikator" in valid.columns else ("No Indikator" if "No Indikator" in valid.columns else valid.columns[0])
            valid[label] = valid[label].fillna("Tidak tercantum").astype(str)
            chart = valid.sort_values("Ketercapaian")
            fig = px.bar(chart, x="Ketercapaian", y=label, orientation="h", color="Ketercapaian",
                         color_continuous_scale="RdYlGn", hover_data=[c for c in
                         ["Sekolah", "No Soal", "Kategori Soal", "Kompetensi", "Sub Elemen", "Elemen"]
                         if c in chart], title="Ketercapaian setiap indikator (%)")
            fig.update_layout(yaxis={"automargin": True}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            left, right = st.columns(2)
            with left:
                st.markdown("**Indikator dengan ketercapaian terendah**")
                show_dataframe(fmt_table(chart.head(10)), use_container_width=True, hide_index=True)
            with right:
                st.markdown("**Indikator dengan ketercapaian tertinggi**")
                show_dataframe(fmt_table(chart.tail(10).sort_values("Ketercapaian", ascending=False)),
                             use_container_width=True, hide_index=True)
            st.markdown("### Rekap lengkap indikator")
            show_dataframe(valid, use_container_width=True, hide_index=True)
            # Perbandingan indikator TO 1 vs TO 2 jika keduanya tersedia.
            if {"TO 1", "TO 2"}.issubset(set(indicators["Try Out"].unique())):
                st.markdown("### Perbandingan indikator TO 1 dan TO 2")
                all_ind = indicators[(indicators["Mata Pelajaran"] == subject)].copy()
                if district_choice != "Semua Kabupaten/Kota":
                    all_ind = all_ind[all_ind["Kabupaten/Kota"] == district_choice]
                keys = [c for c in ["Sekolah", "Mata Pelajaran", "No Indikator", "Indikator", "Elemen", "Sub Elemen"] if c in all_ind.columns]
                if keys:
                    ip = all_ind.pivot_table(index=keys, columns="Try Out", values="Ketercapaian", aggfunc="mean").reset_index()
                    if "TO 1" in ip and "TO 2" in ip:
                        ip["Perubahan ketercapaian"] = ip["TO 2"] - ip["TO 1"]
                        show_dataframe(fmt_table(ip), use_container_width=True, hide_index=True)

elif page == "Rekap Per Kabupaten":
    st.subheader("Rekapitulasi Hasil Asesmen per Kabupaten/Kota")
    st.info(
        "Pemetaan kabupaten/kota dapat diperiksa dan diperbaiki melalui "
        "menu Manajemen & Eksplorasi Data. Rekap mengikuti kabupaten/kota "
        "yang dipilih pada sidebar."
    )

    district_data = selected.copy()
    district_data = district_data[
        district_data["Kabupaten/Kota"] != "Belum dipetakan"
    ]

    if district_data.empty:
        st.warning("Belum ada data yang terpetakan pada filter aktif.")

    else:
        # =====================================================
        # RINGKASAN KABUPATEN/KOTA
        # =====================================================
        district_summary = (
            district_data.groupby("Kabupaten/Kota", as_index=False)
            .agg(
                Jumlah_sekolah=("Sekolah", "nunique"),
                Jumlah_peserta=("Nilai", "count"),
                Rata_rata_nilai=("Nilai", "mean"),
                Median_nilai=("Nilai", "median"),
                Nilai_tertinggi=("Nilai", "max"),
                Nilai_terendah=("Nilai", "min")
            )
            .sort_values("Rata_rata_nilai", ascending=False)
        )

        a, b, c, d = st.columns(4)

        with a:
            metric_card(
                "Kabupaten/Kota",
                f"{district_data['Kabupaten/Kota'].nunique()}"
            )

        with b:
            metric_card(
                "Jumlah sekolah",
                f"{district_data['Sekolah'].nunique()}"
            )

        with c:
            metric_card(
                "Jumlah peserta",
                f"{len(district_data):,}"
            )

        with d:
            metric_card(
                "Rata-rata nilai",
                f"{district_data['Nilai'].mean():.2f}"
            )

        # =====================================================
        # GRAFIK RATA-RATA NILAI KABUPATEN/KOTA
        # =====================================================
        st.markdown("### 📊 Grafik Rekap Kabupaten/Kota")

        fig = px.bar(
            district_summary,
            x="Kabupaten/Kota",
            y="Rata_rata_nilai",
            color="Rata_rata_nilai",
            color_continuous_scale="Blues",
            text=district_summary["Rata_rata_nilai"].map(
                lambda v: f"{v:.2f}"
            ),
            title="Rata-rata Nilai per Kabupaten/Kota"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Kabupaten/Kota",
            yaxis_title="Rata-rata Nilai",
            coloraxis_showscale=False,
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                district_summary,
                x="Kabupaten/Kota",
                y="Jumlah_sekolah",
                text="Jumlah_sekolah",
                title="Jumlah Sekolah per Kabupaten/Kota"
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                district_summary,
                x="Kabupaten/Kota",
                y="Jumlah_peserta",
                text="Jumlah_peserta",
                title="Jumlah Peserta Didik per Kabupaten/Kota"
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        # =====================================================
        # PERBANDINGAN MATA PELAJARAN PER KABUPATEN
        # =====================================================
        st.markdown("### 📚 Perbandingan Mata Pelajaran per Kabupaten/Kota")

        subject_district = (
            district_data.groupby(
                ["Kabupaten/Kota", "Mata Pelajaran"],
                as_index=False
            )
            .agg(
                Rata_rata=("Nilai", "mean"),
                Peserta=("Nilai", "count")
            )
        )

        fig = px.bar(
            subject_district,
            x="Kabupaten/Kota",
            y="Rata_rata",
            color="Mata Pelajaran",
            barmode="group",
            color_discrete_map=COLORS,
            text=subject_district["Rata_rata"].map(
                lambda v: f"{v:.2f}"
            ),
            title="Rata-rata Setiap Mata Pelajaran"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Kabupaten/Kota",
            yaxis_title="Rata-rata Nilai",
            height=480
        )
        st.plotly_chart(fig, use_container_width=True)

        show_dataframe(
            fmt_table(district_summary),
            use_container_width=True,
            hide_index=True
        )

        # =====================================================
        # PERINGKAT SEKOLAH BERDASARKAN RATA-RATA 3 MAPEL
        # =====================================================
        st.markdown("---")
        st.markdown("### 🏆 Peringkat Sekolah — Rata-rata 3 Mata Pelajaran")
        st.caption(
            f"Wilayah: {district_choice} · Data: {round_choice} · "
            "Urutan dari rata-rata tertinggi ke terendah."
        )

        overall, subject_rankings, means = ranking_tables(district_data)

        if overall.empty:
            st.warning(
                "Peringkat gabungan belum dapat dihitung. "
                "Sekolah harus memiliki data Bahasa Indonesia, "
                "Bahasa Inggris, dan Matematika."
            )
        else:
            overall_sorted = overall.sort_values(
                "Rata-rata 3 Mapel",
                ascending=False
            ).reset_index(drop=True)

            fig = px.bar(
                overall_sorted,
                x="Sekolah",
                y="Rata-rata 3 Mapel",
                text=overall_sorted["Rata-rata 3 Mapel"].map(
                    lambda v: f"{v:.2f}"
                ),
                color="Rata-rata 3 Mapel",
                color_continuous_scale="Blues",
                title="Peringkat Sekolah Berdasarkan Rata-rata 3 Mapel",
                hover_data=["Peringkat"]
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                xaxis_title="Nama Sekolah",
                yaxis_title="Rata-rata Nilai",
                xaxis_tickangle=-40,
                coloraxis_showscale=False,
                height=520,
                margin=dict(t=65, b=110)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### Tabel Peringkat Gabungan Sekolah")
            show_dataframe(
                fmt_table(overall_sorted),
                use_container_width=True,
                hide_index=True
            )

        # =====================================================
        # PERINGKAT SEKOLAH UNTUK SETIAP MAPEL
        # =====================================================
        st.markdown("---")
        st.markdown("### 📖 Peringkat Sekolah per Mata Pelajaran")

        for subject in SUBJECTS:
            st.markdown(f"#### 🥇 Peringkat {subject}")

            rank_subject = subject_rankings[subject].copy()

            if rank_subject.empty:
                st.info(f"Belum tersedia data untuk {subject}.")
                continue

            rank_subject = rank_subject.sort_values(
                "Rata_rata",
                ascending=False
            ).reset_index(drop=True)

            rank_subject["Peringkat"] = range(
                1, len(rank_subject) + 1
            )

            fig = px.bar(
                rank_subject,
                x="Sekolah",
                y="Rata_rata",
                text=rank_subject["Rata_rata"].map(
                    lambda v: f"{v:.2f}"
                ),
                color="Rata_rata",
                color_continuous_scale="Blues",
                title=f"Peringkat Sekolah — {subject}",
                hover_data=["Peringkat", "Jumlah_peserta"]
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                xaxis_title="Nama Sekolah",
                yaxis_title="Rata-rata Nilai",
                xaxis_tickangle=-40,
                coloraxis_showscale=False,
                height=480,
                margin=dict(t=65, b=110)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**Tabel Peringkat {subject}**")
            show_dataframe(
                fmt_table(rank_subject),
                use_container_width=True,
                hide_index=True
            )

        # =====================================================
        # RINCIAN SEKOLAH
        # =====================================================
        st.markdown("---")
        st.markdown("### 🏫 Rincian Nilai Setiap Sekolah")

        school_detail = (
            district_data.groupby(
                ["Kabupaten/Kota", "Sekolah", "Mata Pelajaran"],
                as_index=False
            )
            .agg(
                Jumlah_peserta=("Nilai", "count"),
                Rata_rata=("Nilai", "mean")
            )
            .sort_values(
                ["Kabupaten/Kota", "Mata Pelajaran", "Rata_rata"],
                ascending=[True, True, False]
            )
        )

        show_dataframe(
            fmt_table(school_detail),
            use_container_width=True,
            hide_index=True
        )

        # =====================================================
        # DOWNLOAD REKAP
        # =====================================================
        st.download_button(
            "⬇️ Unduh rekap kabupaten/kota CSV",
            district_summary.to_csv(index=False).encode("utf-8-sig"),
            "rekap_kabupaten_kota.csv",
            "text/csv"
        )
elif page == "Data Peserta Didik":
    st.subheader("Data Peserta Didik")
    view = selected.copy()
    c1, c2, c3 = st.columns(3)
    search = c1.text_input("Cari nama/NIS")
    classes = sorted(view["Kelas"].dropna().astype(str).unique())
    chosen_classes = c2.multiselect("Filter kelas", classes, default=classes)
    sort = c3.selectbox("Urutan", ["Nilai tertinggi", "Nilai terendah", "Nama A-Z"])
    view = view[view["Kelas"].astype(str).isin(chosen_classes)]
    if search:
        mask = view["Nama Siswa"].astype(str).str.contains(search, case=False, na=False)
        mask |= view["NIS"].astype(str).str.contains(search, case=False, na=False)
        view = view[mask]
    view = view.sort_values("Nama Siswa" if sort == "Nama A-Z" else "Nilai",
                            ascending=(sort == "Nilai terendah" if sort != "Nama A-Z" else True))
    cols = ["Try Out", "Kabupaten/Kota", "Sekolah", "Mata Pelajaran", "Nama Siswa", "NIS", "Kelas", "Nilai"]
    show_dataframe(view[cols], use_container_width=True, hide_index=True, height=520)
    st.download_button("Unduh CSV", view[cols].to_csv(index=False).encode("utf-8-sig"),
                       "data_peserta.csv", "text/csv")

elif page == "Manajemen & Eksplorasi Data":
    st.subheader("Manajemen & Status Pemrosesan")
    st.markdown("#### Status file yang diunggah")
    if not logs.empty:
        show_dataframe(logs, use_container_width=True, hide_index=True)
    st.markdown("#### Pemetaan sekolah ke kabupaten/kota")
    edited = st.data_editor(st.session_state["district_mapping"], use_container_width=True, hide_index=True,
                            num_rows="fixed",
                            column_config={
                                "Sekolah": st.column_config.TextColumn(disabled=True),
                                "Kabupaten/Kota": st.column_config.SelectboxColumn(options=DISTRICTS),
                                "Status Identifikasi": st.column_config.TextColumn(disabled=True),
                            }, key="district_editor")
    if not edited.equals(st.session_state["district_mapping"]):
        previous = st.session_state["district_mapping"].set_index("Sekolah")["Kabupaten/Kota"].to_dict()
        edited = edited.copy()
        for idx, row in edited.iterrows():
            if row["Kabupaten/Kota"] != previous.get(row["Sekolah"]):
                edited.at[idx, "Status Identifikasi"] = "Manual"
        st.session_state["district_mapping"] = edited
        st.rerun()
    st.caption("Perubahan pemetaan manual langsung disimpan selama sesi dashboard aktif. Setelah perubahan, pilih ulang filter kabupaten/kota di sidebar bila diperlukan.")
    st.markdown("#### Ringkasan jumlah data")
    st.write(f"Data siswa: **{len(students):,}** baris · Data indikator: **{len(indicators):,}** baris")
    if not indicators.empty:
        with st.expander("Lihat seluruh data indikator"):
            show_dataframe(indicators, use_container_width=True, hide_index=True)
    if not students.empty:
        with st.expander("Lihat seluruh data siswa"):
            show_dataframe(students, use_container_width=True, hide_index=True)
st.divider()
st.caption("BGTK · School Assessment Analytics | Hasil bersifat deskriptif dan mengikuti struktur workbook yang diunggah.")
