import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Peta Kontur HVSR UIN Suka", layout="wide")

st.title("Dashboard Peta Kontur Mikrozonasi HVSR")
st.write("Aplikasi Interaktif Pemetaan Spasial Lokasi UIN Sunan Kalijaga Yogyakarta")

st.markdown("---")

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("Konfigurasi Peta Kontur")

# Upload File CSV
uploaded_file = st.sidebar.file_uploader("Unggah File Data Mikro.csv", type=["csv"])

# Jika file belum di-upload, kita beri opsi membaca template data internal agar aplikasi tidak error di awal
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    data_ready = True
else:
    st.info("💡 Silakan unggah file CSV data mikrotremor kamu di sidebar untuk melihat visualisasi data aslimu!")
    data_ready = False

if data_ready:
    # Cek kecocokan kolom data
    required_cols = ['Titik', 'Longitude', 'Latitude', 'f0', 'A0', 'Kg', 'tg']
    if all(col in df.columns for col in required_cols):
        
        # Pilihan parameter yang mau dibuat konturnya
        parameter_pilihan = st.sidebar.selectbox(
            "Pilih Parameter Kontur:",
            options=['Kg', 'f0', 'A0', 'tg'],
            index=0,
            format_func=lambda x: {
                'Kg': 'Indeks Kerentanan Seismik (Kg)',
                'f0': 'Frekuensi Natural (f0)',
                'A0': 'Faktor Amplifikasi (A0)',
                'tg': 'Periode Dominan Lapisan (tg)'
            }[x]
        )
        
        # Pilihan Metode Interpolasi Spasial
        metode_interpolasi = st.sidebar.radio(
            "Metode Interpolasi:",
            options=['linear', 'cubic', 'nearest'],
            index=0,
            help="Linear biasanya paling stabil untuk jumlah titik terbatas (9 titik). Cubic menghasilkan kontur yang lebih melengkung halus."
        )
        
        # Pilihan Skema Warna (Colormap)
        skema_warna = st.sidebar.selectbox(
            "Skema Warna Peta:",
            options=['Jet', 'Viridis', 'Plasma', 'Rainbow', 'RdBu_r'],
            index=0
        )

        # --- HALAMAN UTAMA ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📋 Ringkasan Tabel Data")
            st.dataframe(df[['Titik', 'Longitude', 'Latitude', parameter_pilihan]], use_container_width=True)
            
            # Statistik deskriptif sederhana
            st.write("**Statistik Singkat:**")
            st.write(f"Nilai Maksimum :  **{df[parameter_pilihan].max():.4f}**")
            st.write(f"Nilai Minimum : **{df[parameter_pilihan].min():.4f}**")
            st.write(f"Nilai Rata-rata : **{df[parameter_pilihan].mean():.4f}**")

        with col2:
            st.subheader(f"🗺️ Peta Kontur Distribusi {parameter_pilihan}")
            
            # Ambil nilai koordinat dan parameter pilihan
            x = df['Longitude'].values
            y = df['Latitude'].values
            z = df[parameter_pilihan].values
            
            # Membuat koordinat jaring-jaring (Grid) matematika 100x100 titik di area UIN Suka
            x_grid = np.linspace(x.min() - 0.0002, x.max() + 0.0002, 100)
            y_grid = np.linspace(y.min() - 0.0002, y.max() + 0.0002, 100)
            grid_x, grid_y = np.meshgrid(x_grid, y_grid)
            
            # Proses Interpolasi Data Acak ke Grid Teratur
            grid_z = griddata((x, y), z, (grid_x, grid_y), method=metode_interpolasi)
            
            # Membuat plot menggunakan Plotly
            fig = go.Figure()
            
            # 1. Menambahkan Lapisan Peta Kontur (Contour Layer)
            fig.add_trace(go.Contour(
                z=grid_z,
                x=x_grid,
                y=y_grid,
                colorscale=skema_warna,
                contours_coloring='heatmap',
                line_width=0.5,
                colorbar=dict(title=parameter_pilihan)
            ))
            
            # 2. Menambahkan Pin Titik Pengukuran Asli (Scatter Layer)
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers+text',
                text=df['Titik'].apply(lambda t: f"T-{t}"),
                textposition="top center",
                marker=dict(size=12, color='white', line=dict(color='black', width=2)),
                name='Titik Pengukuran',
                hovertemplate="<b>Titik %{text}</b><br>Long: %{x}<br>Lat: %{y}<br>Nilai: %{customdata:.4f}<extra></extra>",
                customdata=z
            ))
            
            # Mengatur tampilan tata letak koordinat sumbu
            fig.update_layout(
                xaxis_title="Longitude (Bujur)",
                yaxis_title="Latitude (Lintang)",
                xaxis=dict(tickformat=".5f"),
                yaxis=dict(tickformat=".5f"),
                height=550,
                margin=dict(l=40, r=40, b=40, t=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.error(f"Format kolom CSV tidak cocok! Pastikan kolom Anda memiliki header bernama: 'Titik', 'Longitude', 'Latitude', 'f0', 'A0', 'Kg', 'tg'")