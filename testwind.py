import requests
import streamlit as st

API_KEY = "158ed687eaf18fce7453607f364f1a95"

CITIES = {
    "Miami, FL": (25.7617, -80.1918),
    "Tampa, FL": (27.9506, -82.4572),
    "New Orleans, LA": (29.9511, -90.0715),
    "Houston, TX": (29.7604, -95.3698),
    "Jacksonville, FL": (30.3322, -81.6557),
    "Charleston, SC": (32.7765, -79.9311),
    "Savannah, GA": (32.0809, -81.0912),
    "Virginia Beach, VA": (36.8529, -75.9780),
    "Wilmington, NC": (34.2257, -77.9447),
    "Cape Hatteras, NC": (35.2510, -75.5280),
    "Norfolk, VA": (36.8508, -76.2859),
    "Galveston, TX": (29.3013, -94.7977),
    "Port Arthur, TX": (29.8849, -93.9399),
    "Fort Lauderdale, FL": (26.1224, -80.1373),
    "Pensacola, FL": (30.4213, -87.2169),
    "Biloxi, MS": (30.3960, -88.8853),
    "Mobile, AL": (30.6954, -88.0399),
    "Key West, FL": (24.5551, -81.7800),
    "Cocoa, FL": (28.3861, -80.7420),
"Sarasota": (27.3364, -82.5307),
}


st.set_page_config(page_title="East Coast & Gulf Wind Speeds", page_icon="🌬️", layout="wide")
st.title("🌬️ Wind Speed, Direction, Precipitation & Pressure")

st.markdown("""
<style>
/* ── Box container ───────────────────────────────────────────── */
.station-box{
    background-color:#ADD8E6;
    color:#000000;
    border-radius:10px;
    box-shadow:2px 2px 10px rgba(0,0,0,.2);
    padding:10px 15px 24px 15px;      /* tighter bottom padding */
    margin:4px;
     margin-right: 5px;

    width:100%;
    max-width:320px;         /* ← new: prevents stretching */
    height:160px;                     /* enough room for 3 lines */
    overflow:hidden;
    text-align: left;

    font-weight:bold;
}


/* ── Header: city + arrow ────────────────────────────────────── */
.station-box .header{
    display:flex;
    align-items:center;
    gap:6px;                          /* small space city↔arrow  */
    font-size:22px;                   /* slightly smaller header */
    margin-bottom:2px;                /* pulls wind speed up     */
    white-space:nowrap;
}

/* ── Wind speed line ─────────────────────────────────────────── */
.station-box strong{
    font-size:30px;
    line-height:1.1;
    margin-bottom:2px;                /* trims gap above extras   */
}

/* ── Extra info lines ────────────────────────────────────────── */
.station-box .small-info{
    font-size:20px;                   /* bigger text here         */
    line-height:1.3;
    margin-top:1px;
}
            

</style>
""", unsafe_allow_html=True)



def get_border_color(speed_mph):
    if speed_mph >= 111:
        return '#800080'  # Purple (Major Hurricane)
    elif speed_mph >= 74:
        return '#FF0000'  # Red (Hurricane)
    elif speed_mph >= 39:
        return '#FFA500'  # Orange (Tropical Storm)
    elif speed_mph >= 0:
        return "#002835"  # Light Blue (Tropical Depression)
    else:
        return '#ADD8E6'  # Default Light Blue


def wind_direction_arrow(degree):
    # Use 8 cardinal directions mapped to arrows
    directions = [
        (0, "↑"), (45, "↗"), (90, "→"), (135, "↘"),
        (180, "↓"), (225, "↙"), (270, "←"), (315, "↖"), (360, "↑")
    ]
    for angle, arrow in directions:
        # Allow a range of ±22.5 degrees for each direction
        if abs(degree - angle) <= 22.5 or abs(degree - (angle-360)) <= 22.5:
            return arrow
    return "↺"  # fallback

def fetch_wind_data(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        speed_m_s = data["wind"]["speed"]
        speed_kmh = speed_m_s * 3.6
        speed_mph = speed_kmh * 0.621371
        direction = data["wind"].get("deg", 0)

        pressure = data["main"].get("pressure", "N/A")

        # Precipitation intensity - check rain 1h or 3h, else 0
        precipitation = 0
        if "rain" in data and "1h" in data["rain"]:
            precipitation = data["rain"]["1h"]
        elif "rain" in data and "3h" in data["rain"]:
            precipitation = data["rain"]["3h"]

        return speed_mph, speed_kmh, direction, precipitation, pressure
    except Exception as e:
        return None, None, None, None, None

cols_per_row = 4
cities_list = list(CITIES.items())

for i in range(0, len(cities_list), cols_per_row):
    cols = st.columns([1, 1, 1, 1, 1])
    for j, (city, (lat, lon)) in enumerate(cities_list[i:i+cols_per_row]):
        mph, kmh, deg, precip, pressure = fetch_wind_data(lat, lon)
        if mph is not None:
            border_color = get_border_color(kmh)
            arrow = wind_direction_arrow(deg)
            with cols[j]:
                st.markdown(f"""
                <div class="station-box" style="border-left: 9px solid {border_color};">
                    <div class="header">
                        <span>{city}</span>
                        <span style="font-size: 28px;">{arrow}</span>
                    </div>
                    <strong>{mph:.1f} mph</strong>
                    <div class="small-info">Precipitation: {precip} mm/hr</div>
                    <div class="small-info">Pressure: {pressure} hPa</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with cols[j]:
                st.error(f"Could not fetch data for {city}")