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

def calculate_convergence_score(convergence):
    """Calculate lower level convergence score"""
    if 0 <= convergence <= 10:
        return np.interp(convergence, [0, 10], [0, 5])
    elif 11 <= convergence <= 20:
        return np.interp(convergence, [11, 20], [5, 7])
    elif 21 <= convergence <= 31:
        return np.interp(convergence, [21, 31], [7, 9])
    else:
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

def calculate_tcipi(sst_score, shear_score, humidity_score, divergence_score, convergence_score):
    """Calculate TCIPI using the given formula"""
    return (0.35 * sst_score + 0.30 * shear_score + 0.25 * humidity_score + 
            0.05 * divergence_score + 0.05 * convergence_score)

def round_to_nearest_half(value):
    """Round value to nearest 0.5"""
    return round(value * 2) / 2

def get_tcipi_category(tcipi):
    """Get TCIPI category based on value"""
    if tcipi >= 8.5:
        return "Very High", "#FF6B6B", "#FFEBEE"
    elif tcipi >= 7.0:
        return "High", "#FF9800", "#FFF3E0"
    elif tcipi >= 5.5:
        return "Medium", "#FFC107", "#FFFDE7"
    elif tcipi >= 4.0:
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
    
    lower_convergence = st.number_input(
        "Lower Level Convergence",
        min_value=0.0,
        max_value=50.0,
        value=20.0,
        step=0.5,
        help="Enter lower level convergence value"
    )

with col2:
    st.header("📈 Results")
    
    # Calculate scores (rounded to nearest 0.5)
    sst_score = round_to_nearest_half(calculate_sst_score(sst))
    shear_score = round_to_nearest_half(calculate_shear_score(wind_shear))
    humidity_score = round_to_nearest_half(calculate_humidity_score(humidity))
    divergence_score = round_to_nearest_half(calculate_divergence_score(upper_divergence))
    convergence_score = round_to_nearest_half(calculate_convergence_score(lower_convergence))
    
    # Calculate TCIPI (rounded to nearest 0.5)
    tcipi = round_to_nearest_half(calculate_tcipi(sst_score, shear_score, humidity_score, divergence_score, convergence_score))
    category, color, bg_color = get_tcipi_category(tcipi)
    
    # TCIPI Visual Scale
    st.markdown("###  Estimated Potential")
    
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
                VERY LOW<br>
            </div>
            <div style="flex: 1; background: #4CAF50; opacity: {low_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                LOW<br>
            </div>
            <div style="flex: 1; background: #FFC107; opacity: {medium_opacity}; display: flex; align-items: center; justify-content: center; color: black; font-weight: bold;">
                MEDIUM<br>
            </div>
            <div style="flex: 1; background: #FF9800; opacity: {high_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                HIGH<br>
            </div>
            <div style="flex: 1; background: #FF6B6B; opacity: {very_high_opacity}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                VERY HIGH<br>
            </div>
        </div>
    </div>
    """
    
    st.markdown(scale_html, unsafe_allow_html=True)
    
    # Definitions for each category
    definitions = {
    "Very High": "Significant intensification is expected, with potential for rapid intensification.",
    "High": "Steady intensification is expected.",
    "Medium": "Limited intensification expected.",
    "Low": "Intensification is unlikely.",
    "Very Low": "Intensification is very unlikely."
}

    # Display TCIPI result with explanation
    st.markdown(f"""
    <div style="background: #F5F5F5; border: 3px solid {color}; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
    <h2 style="color: black; font-family: ''Noto Sans Black', sans-serif; margin: 0;">TCIPI: {tcipi}</h2>
    <h3 style="color: black; font-family: 'Noto Sans Black', sans-serif; margin: 5px 0 10px 0;">{category} Intensification Potential</h3>
    <p style="color: black; margin:0;font-size:26px;line-height:1.3; font-weight:900;">{definitions.get(category, "")}</p>
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
            "LOWER CONVERGENCE"
        ],
        "SCORE": [
            f"{sst_score}",
            f"{shear_score}",
            f"{humidity_score}",
            f"{divergence_score}",
            f"{convergence_score}"
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
        r=[sst_score, shear_score, humidity_score, divergence_score, convergence_score],
        theta=["SST", "Wind Shear", "Humidity", "Upper Div.", "Lower Conv."],
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
        x=["SST", "Wind Shear", "Humidity", "Upper Div.", "Lower Conv."],
        y=[sst_score, shear_score, humidity_score, divergence_score, convergence_score],
        marker_color=['red', 'blue', 'green', 'orange', 'purple'],
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
TCIPI = (0.35 \times SST_{score}) + (0.30 \times Shear_{score}) + (0.25 \times Humidity_{score}) + (0.05 \times Divergence_{score}) + (0.05 \times Convergence_{score})
''')

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
    
    ### Upper/Lower Level Convergence & Divergence
    - **0-10**: 0-5 score (respectively)
    - **11-20**: 5-7 score
    - **21-31**: 7-9 score
    - **Above 31**: 10 score
    """)

st.markdown("---")
st.markdown("*Developed for Tropical Cyclone Intensification Analysis*")