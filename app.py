import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Page Configuration
st.set_page_config(page_title="Pro Room Acoustic Simulator", layout="wide")

# --- DATABASE: Absorption Coefficients (125Hz to 4000Hz) ---
materials = {
    "Concrete": [0.01, 0.01, 0.02, 0.02, 0.03, 0.05],
    "Brick": [0.02, 0.02, 0.03, 0.04, 0.05, 0.07],
    "Glass": [0.35, 0.25, 0.18, 0.12, 0.07, 0.04],
    "Carpet": [0.02, 0.05, 0.10, 0.25, 0.45, 0.60],
    "Wood Panel": [0.28, 0.22, 0.17, 0.09, 0.10, 0.11],
    "Acoustic Foam": [0.15, 0.30, 0.75, 0.85, 0.95, 0.90],
    "Plasterboard": [0.29, 0.10, 0.05, 0.04, 0.07, 0.09]
}
freqs = [125, 250, 500, 1000, 2000, 4000]

st.title("🏛️ Advanced Room Acoustic & Ray Simulator")
st.write("Analyze Reverberation Time, Clarity, and Sound Distribution.")

# --- SIDEBAR: Room Parameters ---
with st.sidebar:
    st.header("1. Room Geometry (Meters)")
    L = st.number_input("Length (L)", value=8.0)
    W = st.number_input("Width (W)", value=6.0)
    H = st.number_input("Height (H)", value=3.0)
    
    st.header("2. Surface Materials")
    m_wall = st.selectbox("Wall Material", list(materials.keys()))
    m_floor = st.selectbox("Floor Material", list(materials.keys()), index=3)
    m_ceil = st.selectbox("Ceiling Material", list(materials.keys()), index=0)
    
    st.header("3. Acoustic Treatment")
    panel_count = st.slider("Number of Panels", 0, 40, 10)
    m_panel = st.selectbox("Panel Material", list(materials.keys()), index=5)
    panel_area_each = 1.2 # Standard 1.2m x 1m panel

# --- CALCULATIONS ---
V = L * W * H
S_total = 2*(L*W + L*H + W*H)

def calculate_acoustics():
    results = []
    for i in range(6):
        # Surface Areas
        area_fc = L * W # Floor/Ceiling
        area_w = 2 * (L*H + W*H) # Total Walls
        total_panel_area = panel_count * panel_area_each
        
        # Absorption Calculation
        abs_total = (area_fc * materials[m_floor][i]) + \
                    (area_fc * materials[m_ceil][i]) + \
                    ((area_w - total_panel_area) * materials[m_wall][i]) + \
                    (total_panel_area * materials[m_panel][i])
        
        # RT60 Sabine Formula
        rt60 = (0.161 * V) / abs_total
        
        # Clarity C50 (Simplified estimation based on RT)
        c50 = 10 * np.log10((1 - np.exp(-0.691/rt60)) / (np.exp(-0.691/rt60) + 0.0001))
        
        results.append([freqs[i], round(rt60, 2), round(c50, 1)])
    return results

data = calculate_acoustics()
df = pd.DataFrame(data, columns=["Frequency (Hz)", "RT60 (s)", "Clarity C50 (dB)"])

# --- OUTPUTS ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Acoustic Performance Metrics")
    st.table(df)
    
    avg_rt = df["RT60 (s)"].mean()
    sti = max(0, min(1, 1 - (avg_rt/3)))
    st.metric("Speech Transmission Index (STI)", round(sti, 2))
    
    if avg_rt > 1.5:
        st.warning("Room is too reverberant. Add more panels.")
    elif avg_rt < 0.4:
        st.info("Room is 'Dead'. Good for recording, maybe too dry for music.")

with col2:
    st.subheader("Ray Tracing (Visual Path)")
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim([0, L]); ax.set_ylim([0, W]); ax.set_zlim([0, H])
    
    # Simple Ray Plotting from Center Source
    for _ in range(15):
        # Random bounces within box
        rx = [L/2, np.random.uniform(0, L), np.random.uniform(0, L)]
        ry = [W/2, np.random.uniform(0, W), np.random.uniform(0, W)]
        rz = [1.5, np.random.uniform(0, H), np.random.uniform(0, H)]
        ax.plot(rx, ry, rz, color='orange', alpha=0.5)
    
    st.pyplot(fig)