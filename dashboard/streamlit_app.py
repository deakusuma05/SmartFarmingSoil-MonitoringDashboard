
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configure seaborn for consistent styling
sns.set_theme(style="whitegrid")
sns.set_palette("Greens")

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="Soil Moisture Dashboard",
    layout="wide"
)

# ------------------------------------------------
# CUSTOM STYLE
# ------------------------------------------------

st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */

[data-testid="stAppViewContainer"] {
background: linear-gradient(180deg,#E3F2FD 0%,#E8F5E9 100%);
}

/* ===== SIDEBAR ===== */

[data-testid="stSidebar"] {
background: #F1F8E9;
border-right: 2px solid #C8E6C9;
}

/* ===== TITLE ===== */

h1 {
color:#2E7D32;
font-weight:700;
}

/* ===== SECTION TITLE ===== */

h2, h3 {
color:#2E7D32;
}

/* ===== KPI CARD ===== */

[data-testid="metric-container"] {
background:white;
border-radius:12px;
border:1px solid #C8E6C9;
padding:15px;
box-shadow:0px 2px 6px rgba(0,0,0,0.05);
}

/* ===== BUTTON ===== */

.stButton>button {
background:#66BB6A;
color:white;
border-radius:8px;
border:none;
padding:8px 16px;
font-weight:500;
}

.stButton>button:hover {
background:#4CAF50;
color:white;
}

/* ===== ALERT BOX ===== */

.stAlert {
border-radius:10px;
}

/* ===== DATAFRAME ===== */

[data-testid="stDataFrame"] {
border-radius:10px;
border:1px solid #C8E6C9;
}

/* ===== EXPANDER ===== */

[data-testid="stExpander"] {
border-radius:10px;
border:1px solid #C8E6C9;
}

/* ===== CHART AREA ===== */

.element-container {
background:white;
padding:10px;
border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():
    # Memastikan path file yang benar
    df_loaded = pd.read_csv("outputs/cleaned_data.csv")
    # Menggunakan kolom 'datetime' yang sudah ada
    df_loaded['datetime'] = pd.to_datetime(df_loaded['datetime'])
    return df_loaded

df = load_data()

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.title("🌱 Smart Farming Soil Monitoring Dashboard")

st.markdown("""
<div style="
background:linear-gradient(90deg,#4FC3F7,#66BB6A);
padding:20px;
border-radius:12px;
color:white;
font-size:18px;
margin-bottom:20px;
">

🌱 **AI Smart Farming Monitoring System**

Sistem ini membantu memonitor kelembaban tanah secara real-time menggunakan sensor IoT  
dan memberikan analisis untuk membantu keputusan irigasi yang lebih optimal.

</div>
""", unsafe_allow_html=True)

st.caption(
"""
Dashboard ini menampilkan analisis kelembaban tanah berdasarkan data sensor.
Tujuan dashboard ini adalah untuk memonitor kondisi tanah dan membantu analisis
pola kelembaban tanaman.
"""
)

# ------------------------------------------------
# DETECT MOISTURE SENSOR COLUMNS
# ------------------------------------------------

moisture_cols = [col for col in df.columns if "moisture" in col.lower()]

# --- INITIALIZE SESSION STATE FOR FILTERS ---
if 'filter_button_pressed' not in st.session_state:
    st.session_state.filter_button_pressed = False
if 'current_vases' not in st.session_state:
    st.session_state.current_vases = df["source_file"].unique()
if 'current_sensors' not in st.session_state:
    st.session_state.current_sensors = moisture_cols
if 'current_date_range' not in st.session_state:
    st.session_state.current_date_range = (df["datetime"].min().date(), df["datetime"].max().date())

# ------------------------------------------------
# SIDEBAR FILTER - Inputs
# ------------------------------------------------

st.sidebar.header("⚙️ Filter Data")

# Collect input values
selected_vases_input = st.sidebar.multiselect(
    "Pilih Vas",
    df["source_file"].unique(),
    default=st.session_state.current_vases
)

selected_sensors_input = st.sidebar.multiselect(
    "Pilih Sensor",
    moisture_cols,
    default=st.session_state.current_sensors
)

date_range_input = st.sidebar.date_input(
    "Pilih Rentang Waktu",
    value=st.session_state.current_date_range,
    min_value=df["datetime"].min().date(),
    max_value=df["datetime"].max().date()
)

# --- Apply Filters Button ---
if st.sidebar.button('Terapkan Filter'):
    st.session_state.current_vases = selected_vases_input
    st.session_state.current_sensors = selected_sensors_input
    st.session_state.current_date_range = date_range_input
    st.session_state.filter_button_pressed = True
    st.rerun() # Force rerun to apply filters

# ------------------------------------------------
# FILTER DATAFRAME - Apply filters from session state
# ------------------------------------------------

df_filtered = df[df["source_file"].isin(st.session_state.current_vases)]

if len(st.session_state.current_date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered["datetime"].dt.date >= st.session_state.current_date_range[0]) &
        (df_filtered["datetime"].dt.date <= st.session_state.current_date_range[1])
    ]
elif len(st.session_state.current_date_range) == 1:
    df_filtered = df_filtered[
        (df_filtered["datetime"].dt.date >= st.session_state.current_date_range[0])
    ]

# Add check if selected_sensors is empty *after* user interaction
if not st.session_state.current_sensors:
    st.warning("Pilih setidaknya satu sensor untuk menampilkan data.")
    st.stop()

# ------------------------------------------------
# MELT DATA
# ------------------------------------------------

df_melted = df_filtered.melt(
    id_vars=["datetime", "source_file", "irrgation"], # Menambahkan 'irrgation'
    value_vars=st.session_state.current_sensors,
    var_name="sensor",
    value_name="moisture"
)

# ================================================
# CEK JIKA DATAFRAME KOSONG SETELAH FILTER
# ================================================
if df_filtered.empty:
    st.warning("Tidak ada data untuk ditampilkan. Data yang difilter berdasarkan vas dan rentang waktu kosong. Harap sesuaikan filter Anda.")
    st.stop()
if df_melted.empty:
    st.warning("Tidak ada data untuk ditampilkan. DataFrame yang dilebur (df_melted) kosong, kemungkinan karena tidak ada data sensor yang dipilih atau data sensor yang dipilih kosong setelah filter. Harap sesuaikan filter Anda.")
    st.stop()


# ------------------------------------------------
# KPI METRICS
# ------------------------------------------------

st.subheader("📊 Key Metrics")

avg_moisture = round(df_melted["moisture"].mean(), 2)
max_moisture = round(df_melted["moisture"].max(), 2)
min_moisture = round(df_melted["moisture"].min(), 2)
total_data = len(df_melted)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average Moisture", avg_moisture)
col2.metric("Max Moisture", max_moisture)
col3.metric("Min Moisture", min_moisture)
col4.metric("Total Sensor Data", total_data)

# ------------------------------------------------
# ALERT SYSTEM
# ------------------------------------------------

st.subheader("Status Kelembaban Tanah")

# Ambil nilai kelembaban terbaru dari sensor yang dipilih
# Pastikan selected_sensors tidak kosong sebelum mengakses selected_sensors[0]
if st.session_state.current_sensors:
    current_value = df_filtered[st.session_state.current_sensors[0]].iloc[-1]

    if current_value < 0.3:
        st.error(f"⚠ Kelembaban sensor {st.session_state.current_sensors[0]} saat ini ({current_value:.2f}) KRITIS - Irigasi Direkomendasikan!")
    elif current_value < 0.5:
        st.warning(f"⚠ Kelembaban sensor {st.session_state.current_sensors[0]} saat ini ({current_value:.2f}) CUKUP RENDAH - Pertimbangkan Irigasi.")
    else:
        st.success(f"✅ Kelembaban sensor {st.session_state.current_sensors[0]} saat ini ({current_value:.2f}) NORMAL.")
else:
    st.info("Pilih setidaknya satu sensor untuk melihat status kelembaban.")


# ------------------------------------------------
# LINE CHART
# ------------------------------------------------

st.subheader("📈 Soil Moisture Trend")

fig, ax = plt.subplots(figsize=(12,5))

sns.lineplot(
    data=df_melted,
    x="datetime", # Menggunakan 'datetime'
    y="moisture",
    hue="sensor",
    # palette="Greens", # Palette is set globally by sns.set_palette("Greens")
    ax=ax
)

plt.xticks(rotation=45)
plt.title('Tren Kelembaban dari Waktu ke Waktu per Sensor dan per Vas (Setelah Pembersihan)')
plt.xlabel('Waktu')
plt.ylabel('Nilai Kelembaban')
plt.grid(True)
plt.tight_layout()
st.pyplot(fig)

st.caption("Grafik ini menunjukkan perubahan kelembaban tanah dari waktu ke waktu.")

# ------------------------------------------------
# BOXPLOT DISTRIBUTION
# ------------------------------------------------

st.subheader("📦 Soil Moisture Distribution")

fig2, ax2 = plt.subplots(figsize=(10,5))

sns.boxplot(
    data=df_melted,
    x="sensor",
    y="moisture",
    # palette="Greens", # Palette is set globally by sns.set_palette("Greens")
    ax=ax2
)

plt.title("Distribusi Soil Moisture per Sensor")

st.pyplot(fig2)

# ------------------------------------------------
# BAR CHART: Average Moisture per Vase
# ------------------------------------------------

st.subheader("📊 Average Moisture per Vase")

avg_vase = df_melted.groupby("source_file")["moisture"].mean().reset_index()

fig3, ax3 = plt.subplots()

sns.barplot(
    data=avg_vase,
    x="source_file",
    y="moisture",
    # palette="Greens", # Palette is set globally by sns.set_palette("Greens")
    ax=ax3
)

plt.title("Average Soil Moisture per Vase")

st.pyplot(fig3)

# ------------------------------------------------
# HEATMAP CORRELATION
# ------------------------------------------------

st.subheader("🔥 Sensor Correlation")

# Menggunakan df_filtered untuk korelasi yang sudah difilter
# Pastikan ada cukup kolom sensor untuk menghitung korelasi (minimal 2)
if len(st.session_state.current_sensors) > 1:
    corr = df_filtered[st.session_state.current_sensors].corr()

    fig4, ax4 = plt.subplots(figsize=(8,6))

    sns.heatmap(
        corr,
        annot=True,
        cmap="Greens",
        fmt=".2f", # Format angka menjadi 2 desimal
        ax=ax4
    )
    plt.title("Korelasi Antar Sensor yang Dipilih")
    st.pyplot(fig4)
else:
    st.info("Pilih setidaknya dua sensor untuk melihat heatmap korelasi.")

# ------------------------------------------------
# IRRIGATION ANALYSIS (Boxplot by Irrigation)
# ------------------------------------------------

st.subheader("💧 Kelembaban Berdasarkan Irigasi")

fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_melted, x="irrgation", y="moisture", palette="Blues", ax=ax5)
ax5.set_title("Distribusi Kelembaban Saat dan Tanpa Irigasi")
ax5.set_xlabel("Irigasi (True/False)")
ax5.set_ylabel("Nilai Kelembaban")
st.pyplot(fig5)

# ------------------------------------------------
# DATA TABLE
# ------------------------------------------------

st.subheader("📋 Sensor Data Table")

st.dataframe(df_filtered)

# ------------------------------------------------
# INSIGHT SECTION
# ------------------------------------------------

with st.expander("🔎 Insight Analysis"): # Menggunakan nama 'Insight Analysis' pada expander

    st.write("""
### Insight 1
Beberapa sensor menunjukkan fluktuasi kelembaban yang cukup besar,
yang dapat menandakan kondisi tanah yang tidak stabil.

### Insight 2
Jika terdapat vas dengan nilai moisture rata-rata rendah,
tanaman tersebut mungkin membutuhkan penyiraman tambahan.

### Insight 3
Distribusi soil moisture yang relatif sempit menunjukkan
kondisi kelembaban tanah yang stabil.

### Insight 4
Korelasi antar sensor dapat membantu mengidentifikasi apakah
sensor memberikan pembacaan yang konsisten.
"""
)

# ------------------------------------------------
# FOOTER
# ------------------------------------------------

st.markdown("---")

st.caption("Dashboard dibuat menggunakan Streamlit untuk analisis soil moisture data.")
