import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Cargo Route Optimization",
    layout="wide"
)

# ==========================================
# 2. LOAD AI MODEL & ENCODERS
# ==========================================
@st.cache_resource
def load_models():
    try:
        model = joblib.load('cargo_xgboost_model.pkl')
        encoders = joblib.load('cargo_label_encoders.pkl')
        return model, encoders
    except FileNotFoundError:
        st.error("ERROR: Could not find model files. Please ensure 'cargo_xgboost_model.pkl' and 'cargo_label_encoders.pkl' are in the same folder.")
        st.stop()

xgb_model, label_encoders = load_models()

# ==========================================
# 3. SHC MAPPING LOGIC
# ==========================================
CARGO_SHC_MAPPING = {
    "General": ["GEN"],
    "Perishable": ["PER", "ICE", "FRO"],
    "Pharmaceutical": ["ELI", "ICE", "FRO", "PER", "GEN"],
    "Valuable": ["VAL"],
    "Dangerous": ["DGR", "CAO", "ELI"],
    "Heavy": ["HEA", "CAO", "GEN"]
}

# ==========================================
# 4. HEADER UI
# ==========================================
st.title("Cargo Route Optimization System")
st.divider()

# ==========================================
# 5. UNIFORM 5-COLUMN DASHBOARD
# ==========================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    origin_options = sorted(list(label_encoders['origin'].classes_))
    route_options = [f"{org}-JED" for org in origin_options]
    default_route_idx = route_options.index("FRA-JED") if "FRA-JED" in route_options else 0
    selected_route = st.selectbox("Route", route_options, index=default_route_idx)
    
    cargo_type_options = sorted(list(label_encoders['cargo_type'].classes_))
    default_cargo = cargo_type_options.index("Heavy") if "Heavy" in cargo_type_options else 0
    cargo_type = st.selectbox("Cargo Type", cargo_type_options, index=default_cargo)

    priority_options = sorted(list(label_encoders['priority'].classes_))
    default_priority = priority_options.index("Standard") if "Standard" in priority_options else 0
    priority = st.selectbox("Priority Level", priority_options, index=default_priority)

with col2:
    airline_options = sorted(list(label_encoders['airline'].classes_))
    default_airline = airline_options.index("Lufthansa Cargo") if "Lufthansa Cargo" in airline_options else 0
    airline = st.selectbox("Airline", airline_options, index=default_airline)

    season_options = sorted(list(label_encoders['season'].classes_))
    default_season = season_options.index("Winter") if "Winter" in season_options else 0
    season = st.selectbox("Season", season_options, index=default_season)

    model_known_shcs = list(label_encoders['shc_code'].classes_)
    allowed_shcs_for_cargo = CARGO_SHC_MAPPING.get(cargo_type, model_known_shcs)
    valid_shc_options = sorted([shc for shc in allowed_shcs_for_cargo if shc in model_known_shcs])
    if not valid_shc_options:
        valid_shc_options = sorted(model_known_shcs)
    default_shc = valid_shc_options.index("HEA") if "HEA" in valid_shc_options else 0
    shc_code = st.selectbox("SHC Code", valid_shc_options, index=default_shc)

with col3:
    cargo_weight = st.number_input("Cargo Weight (kg)", min_value=10.0, max_value=15000.0, value=8500.0, step=100.0)
    connections = st.selectbox("Number of Connections", [0, 1, 2, 3], index=1)
    distance = st.number_input("Distance (km)", min_value=100.0, max_value=15000.0, value=4800.0, step=100.0)

with col4:
    transit_time = st.number_input("Total Transit Time (Hours)", min_value=1.0, max_value=100.0, value=16.5, step=0.5)
    capacity = st.number_input("Available Capacity (kg)", min_value=0.0, value=12000.0, step=500.0)
    cost = st.number_input("Estimated Cost (SAR)", min_value=0.0, value=28500.0, step=500.0)

with col5:
    reliability = st.slider("Carrier Reliability Score", 0.0, 1.0, 0.92, step=0.01)
    weather = st.slider("Weather Risk Score", 0.0, 1.0, 0.15, step=0.01)
    load_factor = st.slider("Load Factor", 0.0, 1.0, 0.78, step=0.01)

st.divider()

# ==========================================
# 6. PREDICTION LOGIC & RESULTS
# ==========================================
_, center_col, _ = st.columns([1, 2, 1])

if center_col.button("Analyze Route", use_container_width=True):
    
    origin, destination = selected_route.split('-')
    
    # 1. Package inputs into a Dictionary
    input_dict = {
        'cargo_weight_kg': [cargo_weight],
        'num_connections': [connections],
        'distance_km': [distance],
        'total_transit_time_hours': [transit_time],
        'capacity_available_kg': [capacity],
        'reliability_score': [reliability],
        'weather_risk_score': [weather],
        'load_factor': [load_factor],
        'cost_sar': [cost],
        'origin': [origin],
        'destination': [destination],
        'cargo_type': [cargo_type],
        'priority': [priority],
        'airline': [airline],
        'season': [season],
        'shc_code': [shc_code]
    }
    
    df_input = pd.DataFrame(input_dict)
    
    # 2. Encode categorical variables
    categorical_features = ['origin', 'destination', 'cargo_type', 'priority', 'airline', 'season', 'shc_code']
    
    for col in categorical_features:
        df_input[col] = label_encoders[col].transform(df_input[col].astype(str))
            
    # 3. Align columns to match the EXACT order expected by the XGBoost model
    features_ordered = [
        'origin', 
        'destination', 
        'cargo_type', 
        'cargo_weight_kg', 
        'priority', 
        'airline', 
        'season', 
        'shc_code', 
        'num_connections', 
        'distance_km', 
        'total_transit_time_hours', 
        'capacity_available_kg', 
        'reliability_score', 
        'weather_risk_score', 
        'load_factor', 
        'cost_sar'
    ]
    df_ready = df_input[features_ordered]
    
    # 4. Generate prediction with clipping correction
    with st.spinner('Calculating optimization score...'):
        raw_score = xgb_model.predict(df_ready)[0]
        score = max(0.0, min(1.0, float(raw_score)))
    
    # 5. Display Clean Split Layout
    out_col1, out_col2 = st.columns([1.2, 1.0])
    
    with out_col1:
        # Fixed the keyword argument parameter here to unsafe_allow_html=True
        st.markdown(
            f"""
            <div style="
                font-family: monospace; 
                border: 1px solid #2d3139; 
                padding: 20px; 
                background-color: #0e1117; 
                border-radius: 6px; 
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
                white-space: pre-wrap;
                color: #e0e0e0;
                line-height: 1.5;
            ">REQUESTED RAW METRICS:
-------------------------------------------
Cost (SAR)          : <span style="color: #59b2ff; font-weight: bold;">{cost:,.2f}</span>
Transit Time (hrs)  : <span style="color: #59b2ff; font-weight: bold;">{transit_time:.2f}</span>
Reliability         : <span style="color: #59b2ff; font-weight: bold;">{reliability:.3f}</span>
Capacity Available  : <span style="color: #59b2ff; font-weight: bold;">{capacity:,.2f} kg</span></div>
            """, 
            unsafe_allow_html=True
        )
        
    with out_col2:
        if score >= 0.70:
            gauge_color = "#2efc03" 
        elif score >= 0.40:
            gauge_color = "#fca103" 
        else:
            gauge_color = "#fc0303" 
            
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            number = {'valueformat': '.4f', 'font': {'size': 24, 'color': gauge_color, 'family': 'monospace'}},
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ROUTE OPTIMIZATION LEVEL", 'font': {'size': 14, 'color': '#ffffff', 'family': 'monospace, sans-serif'}},
            gauge = {
                'axis': {'range': [0.0, 1.0], 'tickwidth': 1, 'tickcolor': "#888888", 'tickformat': '.2f'},
                'bar': {'color': gauge_color, 'thickness': 0.25},
                'bgcolor': "#2d3139",
                'borderwidth': 1,
                'bordercolor': "#4a4a4a",
                'steps': [
                    {'range': [0.0, 0.40], 'color': 'rgba(252, 3, 3, 0.1)'},
                    {'range': [0.40, 0.70], 'color': 'rgba(252, 161, 3, 0.1)'},
                    {'range': [0.70, 1.00], 'color': 'rgba(46, 252, 3, 0.1)'}
                ]
            }
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=10),
            height=160,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    st.divider()
    
    # 6. Display System Verdict Alert Banner Directly Below
    st.markdown("### System Verdict")
    
    if score >= 0.70:
        st.success(f"HIGHLY RECOMMENDED | Optimization Score: {score:.4f}")
        st.info("This route meets high-performance logistical criteria based on cost, reliability, and transit factors.")
    elif score >= 0.40:
        st.warning(f"PROCEED WITH CAUTION | Optimization Score: {score:.4f}")
        st.info("This route is viable but contains operational risks or inefficiencies.")
    else:
        st.error(f"REJECT ROUTE | Optimization Score: {score:.4f}")
        st.info("This route is heavily penalized due to poor efficiency, high risk, or excessive constraints.")
