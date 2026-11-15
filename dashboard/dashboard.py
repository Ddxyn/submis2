import os
import calendar
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

BASE = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_data():
    day = pd.read_csv(os.path.join(BASE, "main_data.csv"), parse_dates=["dteday"])
    hour = pd.read_csv(os.path.join(BASE, "hour_data.csv"), parse_dates=["dteday"])
    return day, hour


day_df, hour_df = load_data()
MAIN, LIGHT, ACCENT = "#2E86C1", "#AED6F1", "#F39C12"

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("🚲 Bike Sharing")
    min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
    date_range = st.date_input("Rentang waktu", value=[min_d, max_d], min_value=min_d, max_value=max_d)
    seasons = st.multiselect("Musim", ["Spring", "Summer", "Fall", "Winter"],
                             default=["Spring", "Summer", "Fall", "Winter"])

start, end = (date_range if len(date_range) == 2 else (min_d, max_d))
mask_d = (day_df["dteday"].dt.date.between(start, end)) & (day_df["season"].isin(seasons))
mask_h = (hour_df["dteday"].dt.date.between(start, end)) & (hour_df["season"].isin(seasons))
d = day_df[mask_d]
h = hour_df[mask_h]

st.header("Bike Sharing Dashboard (2011–2012)")
if d.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penyewaan", f"{d['cnt'].sum():,}")
c2.metric("Rata-rata / Hari", f"{d['cnt'].mean():,.0f}")
c3.metric("Registered", f"{d['registered'].sum():,}")
c4.metric("Casual", f"{d['casual'].sum():,}")

# ---------------- Pertanyaan 1 ----------------
st.subheader("1. Pengaruh Musim & Cuaca terhadap Penyewaan Harian")
col1, col2 = st.columns(2)
for col, key, title in [(col1, "season", "Musim"), (col2, "weathersit", "Kondisi Cuaca")]:
    data = d.groupby(key)["cnt"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(data.index, data.values, color=[MAIN] + [LIGHT] * (len(data) - 1))
    for i, v in enumerate(data.values):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom")
    ax.set_title(f"Rata-rata Penyewaan Harian per {title}")
    ax.set_ylabel("Rata-rata penyewaan / hari")
    ax.spines[["top", "right"]].set_visible(False)
    col.pyplot(fig)

st.markdown("**Tren bulanan & pertumbuhan 2011 → 2012**")
monthly = d.pivot_table(index="mnth", columns="yr", values="cnt", aggfunc="sum")
fig, ax = plt.subplots(figsize=(12, 4))
colors = {2011: LIGHT, 2012: MAIN}
for yr in monthly.columns:
    ax.plot([calendar.month_abbr[m] for m in monthly.index], monthly[yr], marker="o",
            linewidth=2, color=colors.get(yr, MAIN), label=str(yr))
ax.set_ylabel("Total penyewaan")
ax.set_ylim(0, None)
ax.legend()
ax.spines[["top", "right"]].set_visible(False)
st.pyplot(fig)
if {2011, 2012}.issubset(monthly.columns):
    growth = ((monthly[2012] - monthly[2011]) / monthly[2011] * 100).round(1)
    growth.index = [calendar.month_abbr[m] for m in growth.index]
    st.caption("Pertumbuhan YoY per bulan (%): " + ", ".join(f"{k} {v:+.0f}%" for k, v in growth.items()))

# ---------------- Pertanyaan 2 ----------------
st.subheader("2. Pola Penyewaan per Jam: Hari Kerja vs Hari Libur")
tab1, tab2 = st.tabs(["Working Day", "Holiday/Weekend"])
for tab, wd in [(tab1, "Working Day"), (tab2, "Holiday/Weekend")]:
    hh = h[h["workingday"] == wd].groupby("hr")[["casual", "registered"]].mean()
    with tab:
        if hh.empty:
            st.info("Tidak ada data.")
            continue
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(hh.index, hh["registered"], marker="o", color=MAIN, label="Registered")
        ax.plot(hh.index, hh["casual"], marker="o", color=ACCENT, label="Casual")
        ax.set_xticks(range(0, 24))
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata penyewaan / jam")
        ax.legend()
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig)
        peak = hh.sum(axis=1).nlargest(3).index.tolist()
        st.caption(f"3 jam puncak: {', '.join(f'{p:02d}.00' for p in sorted(peak))}")

# ---------------- Analisis lanjutan ----------------
st.subheader("3. Clustering (Binning): Tingkat Permintaan per Jam & Kelompok Suhu")
col1, col2 = st.columns(2)
order = ["Low (≤50)", "Medium (51-200)", "High (201-500)", "Peak (>500)"]
ct = pd.crosstab(h["hr"], h["demand_level"], normalize="index").reindex(columns=order, fill_value=0) * 100
fig, ax = plt.subplots(figsize=(7, 4))
ct.plot(kind="bar", stacked=True, ax=ax, width=0.9, color=["#D6EAF8", "#85C1E9", MAIN, "#1B4F72"])
ax.set_xlabel("Jam")
ax.set_ylabel("% jam")
ax.legend(fontsize=7, title="Demand")
col1.pyplot(fig)

tg = d.groupby("temp_group")["cnt"].mean()
tg = tg.reindex([g for g in ["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"] if g in tg.index])
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(tg.index, tg.values, color=[MAIN if v == tg.max() else LIGHT for v in tg.values])
ax.set_ylabel("Rata-rata penyewaan / hari")
ax.set_title("Rata-rata Penyewaan per Kelompok Suhu")
ax.spines[["top", "right"]].set_visible(False)
col2.pyplot(fig)

st.caption("Data: Bike Sharing Dataset (Capital Bikeshare, 2011–2012)")
