import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_sst_score(sst):
    """Calculate SST score based on temperature"""
    if sst >= 31:
        return np.interp(sst, [31, 35], [8, 10])
    elif 28 <= sst < 31:
        return np.interp(sst, [28, 31], [5, 8])
    elif 26 <= sst < 28:
        return np.interp(sst, [26, 28], [2, 5])
    else:  # sst < 26
        return np.interp(sst, [20, 26], [0, 3])

def calculate_shear_score(shear):
    """Calculate wind shear score"""
    if shear < 5:
        return np.interp(shear, [0, 5], [10, 8])
    elif 5 <= shear < 10:
        return np.interp(shear, [5, 10], [8, 6])
    elif 10 <= shear < 15:
        return np.interp(shear, [10, 15], [6, 4])
    elif 15 <= shear <= 25:
        return np.interp(shear, [15, 25], [4, 2])
    else:
        return np.interp(shear, [25, 40], [2, 0])

def calculate_humidity_score(humidity):
    """Calculate humidity score"""
    if humidity > 75:
        return np.interp(humidity, [75, 100], [8, 10])
    elif 50 <= humidity <= 75:
        return np.interp(humidity, [50, 75], [4, 7])
    elif 40 <= humidity < 50:
        return 3
    else:
        return np.interp(humidity, [0, 40], [0, 2])

def calculate_ohc_score(ohc):
    """Calculate Ocean Heat Content score"""
    if ohc < 25:
        return 1
    elif 25 <= ohc < 75:
        return np.interp(ohc, [25, 74], [2, 4])
    elif 75 <= ohc < 125:
        return np.interp(ohc, [75, 124], [4, 8])
    elif 125 <= ohc < 150:
        return 9
    else:  # ohc >= 150
        return 10

def calculate_divergence_score(divergence):
    """Calculate upper level divergence score"""
    if 0 <= divergence <= 10:
        return np.interp(divergence, [0, 10], [0, 5])
    elif 11 <= divergence <= 20:
        return np.interp(divergence, [11, 20], [5, 7])
    elif 21 <= divergence <= 31:
        return np.interp(divergence, [21, 31], [7, 9])
    else:
        return 10

def calculate_tcipi(sst_score, shear_score, humidity_score, divergence_score, ohc_score):
    """Calculate TCIPI using the updated formula"""
    return (0.35 * sst_score + 0.30 * shear_score + 0.25 * humidity_score + 
            0.05 * divergence_score + 0.05 * ohc_score)

def apply_size_adjustment(tcipi, size, category):
    """Apply tropical cyclone size adjustments"""
    if size == "Small":
        if category in ["Medium", "High", "Very High"]:
            return tcipi + 0.75
        else:
            return tcipi - 0.75
    elif size == "Large":
        if category in ["Medium", "High", "Very High"]:
            return tcipi - 0.5
        else:
            return tcipi + 0.5
    else:  # Average size or no adjustment
        return tcipi

def round_to_nearest_half(value):
    """Round value to nearest 0.5"""
    return round(value * 2) / 2

def get_tcipi_category(tcipi):
    """Get TCIPI category based on value"""
    if tcipi >= 8.0:
        return "Very High", "#FF6B6B", "#FFEBEE"
    elif tcipi >= 6.5:
        return "High", "#FF9800", "#FFF3E0"
    elif tcipi >= 5.0:
        return "Medium", "#FFC107", "#FFFDE7"
    elif tcipi >= 3.5:
        return "Low", "#4CAF50", "#E8F5E8"
    else:
        return "Very Low", "#2196F3", "#E3F2FD"

# Streamlit App
st.set_page_config(
    page_title="TCIPI Calculator",
    page_icon="🌪️",
    layout="wide"
)

st.title("🌪️ Tropical Cyclone Intensification Potential Index (TCIPI)")
st.markdown("---")

# Create two columns for input and results
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📊 Input Parameters")
    
    # Input fields
    sst = st.number_input(
        "Sea Surface Temperature (°C)",
        min_value=15.0,
        max_value=35.0,
        value=28.0,
        step=0.1,
        help="Enter sea surface temperature in Celsius"
    )
    
    wind_shear = st.number_input(
        "Wind Shear (knots)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.5,
        help="Enter wind shear in knots"
    )
    
    humidity = st.number_input(
        "Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=65.0,
        step=1.0,
        help="Enter relative humidity as percentage"
    )
    
    upper_divergence = st.number_input(
        "Upper Level Divergence",
        min_value=0.0,
        max_value=50.0,
        value=15.0,
        step=0.5,
        help="Enter upper level divergence value"
    )
    
    ohc = st.number_input(
        "Ocean Heat Content (kJ/cm²)",
        min_value=0.0,
        max_value=200.0,
        value=75.0,
        step=1.0,
        help="Enter ocean heat content in kJ/cm²"
    )
    
    # Optional tropical cyclone size
    st.markdown("---")
    st.subheader("🌀 Optional: Tropical Cyclone Size")
    
    size_adjustment = st.selectbox(
        "Tropical Cyclone Size",
        options=["None (No Adjustment)", "Small", "Average", "Large"],
        index=0,
        help="Select cyclone size for additional scoring adjustment"
    )

with col2:
    st.header("📈 Results")
    
    # Calculate scores (rounded to nearest 0.5)
    sst_score = round_to_nearest_half(calculate_sst_score(sst))
    shear_score = round_to_nearest_half(calculate_shear_score(wind_shear))
    humidity_score = round_to_nearest_half(calculate_humidity_score(humidity))
    divergence_score = round_to_nearest_half(calculate_divergence_score(upper_divergence))
    ohc_score = round_to_nearest_half(calculate_ohc_score(ohc))
    
    # Calculate base TCIPI (rounded to nearest 0.5)
    base_tcipi = round_to_nearest_half(calculate_tcipi(sst_score, shear_score, humidity_score, divergence_score, ohc_score))
    base_category, _, _ = get_tcipi_category(base_tcipi)
    
    # Apply size adjustment if selected
    if size_adjustment != "None (No Adjustment)" and size_adjustment != "Average":
        adjusted_tcipi = apply_size_adjustment(base_tcipi, size_adjustment, base_category)
        final_tcipi = round_to_nearest_half(adjusted_tcipi)
        # Ensure final score stays within 0-10 range
        final_tcipi = max(0, min(10, final_tcipi))
    else:
        final_tcipi = base_tcipi
    
    category, color, bg_color = get_tcipi_category(final_tcipi)
    
    # TCIPI Visual Scale
    st.markdown("### 🎯 TCIPI Scale Visualization")
    
    # Determine opacity for each category
    very_low_opacity = "1.0" if category == "Very Low" else "0.3"
    low_opacity = "1.0" if category == "Low" else "0.3"
    medium_opacity = "1.0" if category == "Medium" else "0.3"
    high_opacity = "1.0" if category == "High" else "0.3"
    very_high_opacity = "1.0" if category == "Very High" else "0.3"
    
    # Create the visual scale
    scale_html = f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; height: 60px; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <div style="flex: 1; background: #2196F3; opacity: {very_low_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                VERY LOW<br><small>0-3.4</small>
            </div>
            <div style="flex: 1; background: #4CAF50; opacity: {low_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                LOW<br><small>3.5-4.9</small>
            </div>
            <div style="flex: 1; background: #FFC107; opacity: {medium_opacity}; display: flex; align-items: center; justify-content: center; color: black; font-weight: bold;">
                MEDIUM<br><small>5.0-6.4</small>
            </div>
            <div style="flex: 1; background: #FF9800; opacity: {high_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                HIGH<br><small>6.5-7.9</small>
            </div>
            <div style="flex: 1; background: #FF6B6B; opacity: {very_high_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                VERY HIGH<br><small>8.0-10</small>
            </div>
        </div>
    </div>
    """
    
    st.markdown(scale_html, unsafe_allow_html=True)
    
    # Display TCIPI result with light grey background
    if size_adjustment != "None (No Adjustment)" and size_adjustment != "Average" and final_tcipi != base_tcipi:
        st.markdown(f"""
        <div style="background: #F5F5F5; border: 3px solid {color}; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
            <h2 style="color: {color}; margin: 0;">TCIPI: {final_tcipi}</h2>
            <h3 style="color: {color}; margin: 5px 0 0 0;">{category} Intensification Potential</h3>
            <p style="color: #666; margin: 10px 0 0 0; font-size: 14px;">
                Base Score: {base_tcipi} | Size Adjusted ({size_adjustment}): {final_tcipi}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: #F5F5F5; border: 3px solid {color}; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
            <h2 style="color: {color}; margin: 0;">TCIPI: {final_tcipi}</h2>
            <h3 style="color: {color}; margin: 5px 0 0 0;">{category} Intensification Potential</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Display individual scores in blue table format
    st.subheader("Individual Scores:")
    
    # Create a styled dataframe
    scores_data = {
        "FACTOR": [
            "SEA SURFACE TEMPERATURE",
            "WIND SHEAR", 
            "HUMIDITY",
            "UPPER DIVERGENCE",
            "OCEAN HEAT CONTENT"
        ],
        "SCORE": [
            f"{sst_score}",
            f"{shear_score}",
            f"{humidity_score}",
            f"{divergence_score}",
            f"{ohc_score}"
        ]
    }
    
    df_scores = pd.DataFrame(scores_data)
    
    # Apply custom styling
    st.markdown("""
    <style>
    .score-table {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0);
        border-radius: 10px;
        padding: 0;
        overflow: hidden;
    }
    .score-table th {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 15px !important;
        border: none !important;
    }
    .score-table td {
        color: white !important;
        font-weight: bold !important;
        padding: 12px 20px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        text-align: left !important;
    }
    .score-table td:last-child {
        text-align: center !important;
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        df_scores,
        use_container_width=True,
        hide_index=True
    )

# Visualization section
st.markdown("---")
st.header("📊 Score Visualization")

# Create radar chart for scores
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Individual Scores", "Score Distribution"),
    specs=[[{"type": "scatterpolar"}, {"type": "bar"}]]
)

# Radar chart
fig.add_trace(
    go.Scatterpolar(
        r=[sst_score, shear_score, humidity_score, divergence_score, ohc_score],
        theta=["SST", "Wind Shear", "Humidity", "Upper Div.", "Ocean Heat"],
        fill='toself',
        name='Scores',
        line_color='blue'
    ),
    row=1, col=1
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 10]
        )
    ),
    showlegend=False
)

# Bar chart
fig.add_trace(
    go.Bar(
        x=["SST", "Wind Shear", "Humidity", "Upper Div.", "Ocean Heat"],
        y=[sst_score, shear_score, humidity_score, divergence_score, ohc_score],
        marker_color=['red', 'blue', 'green', 'orange', 'teal'],
        name='Scores'
    ),
    row=1, col=2
)

fig.update_layout(height=500, title_text="TCIPI Component Analysis")
st.plotly_chart(fig, use_container_width=True)

# TCIPI Formula display
st.markdown("---")
st.header("📐 TCIPI Formula")
st.latex(r'''
TCIPI = (0.35 \times SST_{score}) + (0.30 \times Shear_{score}) + (0.25 \times Humidity_{score}) + (0.05 \times Divergence_{score}) + (0.05 \times OHC_{score})
''')

# Size adjustment info
if size_adjustment != "None (No Adjustment)" and size_adjustment != "Average":
    st.markdown("### 🌀 Size Adjustment Applied")
    st.markdown(f"""
    **Selected Size**: {size_adjustment}
    
    **Size Adjustment Rules**:
    - **Small cyclones**: +0.75 if ≥Medium category, -0.75 if <Medium category
    - **Large cyclones**: -0.5 if ≥Medium category, +0.5 if <Medium category
    """)

# Scoring criteria
with st.expander("📋 Scoring Criteria"):
    st.markdown("""
    ### Sea Surface Temperature (SST)
    - **Above 31°C**: 8-10 score
    - **28-30°C**: 5-8 score  
    - **26-28°C**: 2-5 score
    - **Below 26°C**: 0-3 score
    
    ### Wind Shear
    - **Below 5 knots**: 8-10 score
    - **5-10 knots**: 6-8 score
    - **10-15 knots**: 4-6 score
    - **15-25 knots**: 2-4 score
    - **Above 25 knots**: 0-2 score
    
    ### Humidity
    - **Above 75%**: 8-10 score
    - **50-75%**: 4-7 score
    - **40-50%**: 3 score
    - **Below 40%**: 0-2 score
    
    ### Ocean Heat Content (kJ/cm²)
    - **<25**: 1 score
    - **25-74**: 2-4 score
    - **75-124**: 4-8 score
    - **125-149**: 9 score
    - **≥150**: 10 score
    
    ### Upper Level Divergence
    - **0-10**: 0-5 score
    - **11-20**: 5-7 score
    - **21-31**: 7-9 score
    - **Above 31**: 10 score
    
    ### Tropical Cyclone Size Adjustments
    - **Small**: +0.75 if ≥Medium category, -0.75 if <Medium category
    - **Large**: -0.5 if ≥Medium category, +0.5 if <Medium category
    - **Average**: No adjustment
    """)

st.markdown("---")
st.markdown("*Developed for Tropical Cyclone Intensification Analysis*")