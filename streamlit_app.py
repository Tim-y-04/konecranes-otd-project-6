import streamlit as st
import pandas as pd
import random
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 1. UI SETUP & BRANDING (Enlarged Easter Egg)
# ==========================================
st.set_page_config(page_title="Konecranes OTD Optimizer", layout="wide")
st.markdown("<div style='text-align: center; color: #FFD700; font-size: 18px; font-weight: bold; font-family: monospace; letter-spacing: 3px;'>WAKANDA FOREVER</div>", unsafe_allow_html=True)

st.title("Konecranes OTD Simulation Platform")
st.write("Advanced supply chain analytics comparing the Legacy Baseline against the Intelligent Wakanda 2.0 Framework.")

# ==========================================
# 2. DATA DEFINITIONS & PROFILES
# ==========================================
supplier_profiles = {
    "Nordic Steel Works": {"Commodity": "Steel Structures", "Incoterm": "FCA", "Base_Prob": 0.15, "Base_Fine": 600},
    "Siemens Drives": {"Commodity": "Heavy Motors", "Incoterm": "DAP", "Base_Prob": 0.20, "Base_Fine": 800},
    "Taiwan Semi": {"Commodity": "Microchips", "Incoterm": "FCA", "Base_Prob": 0.35, "Base_Fine": 400},
    "Global Hydraulics": {"Commodity": "Hydraulic Pumps", "Incoterm": "DDP", "Base_Prob": 0.25, "Base_Fine": 500}
}

root_causes = [
    {"cause": "Production Capacity Issue", "type": "Supplier"},
    {"cause": "Quality QA/QC Failure", "type": "Supplier"},
    {"cause": "Raw Material Shortage", "type": "Supplier"},
    {"cause": "Port Congestion / Vessel Delay", "type": "Logistics"},
    {"cause": "Customs Clearance Hold", "type": "Logistics"},
    {"cause": "Extreme Weather / Typhoon", "type": "Force Majeure"}
]

# ==========================================
# 3. SIDEBAR CONTROL PANEL
# ==========================================
st.sidebar.header("Simulation Control Panel")

# Removed "Phase 1, 2, 3" as requested
sim_mode = st.sidebar.selectbox(
    "Select Simulation Mode:",
    [
        "Old System (Baseline)", 
        "Wakanda System 2.0", 
        "Head-to-Head Comparison"
    ]
)

# Drill-down filter
sup_filter = st.sidebar.selectbox(
    "Select View (Drill-down Analysis):",
    ["All Suppliers"] + list(supplier_profiles.keys())
)

orders_per_day = st.sidebar.slider("Daily Average Orders", 10, 30, 15)
learning_rate = st.sidebar.slider("Supplier Learning Rate (%)", 5, 30, 15)
run_btn = st.sidebar.button("Run 90-Day Simulation")

# ==========================================
# 4. SIMULATION ENGINE (Fixed Seed for Fairness)
# ==========================================
if run_btn:
    random.seed(42) # Absolute fairness between modes
    
    data = []
    start_date = datetime(2024, 1, 1)
    current_probs = {name: info["Base_Prob"] for name, info in supplier_profiles.items()}
    
    for day in range(90):
        current_date = start_date + timedelta(days=day)
        
        for _ in range(orders_per_day):
            sup_name = random.choice(list(supplier_profiles.keys()))
            sup_info = supplier_profiles[sup_name]
            
            event_seed = random.random()
            days_late_shared = random.randint(1, 21)
            issue_shared = random.choice(root_causes)

            # --- OLD SYSTEM ---
            is_delayed_old = event_seed < sup_info["Base_Prob"]
            
            # --- WAKANDA SYSTEM 2.0 ---
            is_delayed_wakanda = event_seed < current_probs[sup_name]
            
            wak_penalty, wak_days = 0, 0
            wak_action, wak_accountable, wak_cause = "None", "None", "None"
            
            if is_delayed_wakanda:
                wak_days = days_late_shared
                wak_cause = issue_shared['cause']
                wak_accountable = issue_shared['type']
                
                if issue_shared['type'] == 'Logistics':
                    if sup_info['Incoterm'] in ['DAP', 'DDP']:
                        wak_accountable = 'Supplier (Transit Liability)'
                    elif sup_info['Incoterm'] in ['FCA']:
                        wak_accountable = 'Konecranes Freight Forwarder'
                
                if wak_accountable == 'Force Majeure':
                    wak_action = "Exempt (Act of God)"
                elif wak_accountable == 'Konecranes Freight Forwarder':
                    wak_action = "Freight Claim"
                    wak_penalty = wak_days * 200
                else: 
                    if wak_days <= 3:
                        wak_action = "Tier 1: Warning & 8D"
                    elif wak_days <= 14:
                        wak_action = "Tier 2: Financial Penalty"
                        wak_penalty = wak_days * sup_info['Base_Fine']
                        current_probs[sup_name] = max(0.05, current_probs[sup_name] * (1 - (learning_rate/100)))
                    else:
                        wak_action = "Tier 3: Termination Review"
                        wak_penalty = wak_days * sup_info['Base_Fine'] * 1.5
                        current_probs[sup_name] = max(0.05, current_probs[sup_name] * 0.5)

            data.append({
                "Date": current_date,
                "Supplier": sup_name,
                "Incoterm": sup_info['Incoterm'],
                "Old_Delayed": 1 if is_delayed_old else 0,
                "Wakanda_Delayed": 1 if is_delayed_wakanda else 0,
                "Wakanda_Cause": wak_cause,
                "Wakanda_Days": wak_days,
                "Wakanda_Accountable": wak_accountable,
                "Wakanda_Action": wak_action,
                "Wakanda_Penalty": wak_penalty
            })

    df = pd.DataFrame(data)
    df_filtered = df if sup_filter == "All Suppliers" else df[df['Supplier'] == sup_filter]

    # ==========================================
    # 5. DASHBOARD: OTD% TRENDLINE
    # ==========================================
    st.header(f"Dashboard: {sim_mode}")
    
    st.subheader("On-Time Delivery (OTD%) Trendline")
    daily_stats = df_filtered.groupby('Date').agg(
        Total=('Supplier', 'count'),
        Old_D=('Old_Delayed', 'sum'),
        Wak_D=('Wakanda_Delayed', 'sum')
    ).reset_index()
    
    daily_stats['Old_OTD'] = ((daily_stats['Total'] - daily_stats['Old_D']) / daily_stats['Total']) * 100
    daily_stats['Wak_OTD'] = ((daily_stats['Total'] - daily_stats['Wak_D']) / daily_stats['Total']) * 100
    daily_stats['Old_Avg'] = daily_stats['Old_OTD'].rolling(7).mean()
    daily_stats['Wak_Avg'] = daily_stats['Wak_OTD'].rolling(7).mean()

    if "Old System" in sim_mode:
        fig_otd = px.line(daily_stats, x='Date', y='Old_Avg', title="Old System OTD% Performance", color_discrete_sequence=["#ef553b"])
    elif "Wakanda System" in sim_mode:
        fig_otd = px.line(daily_stats, x='Date', y='Wak_Avg', title="Wakanda System 2.0 OTD% Performance", color_discrete_sequence=["#00cc96"])
    else:
        fig_otd = px.line(daily_stats, x='Date', y=['Old_Avg', 'Wak_Avg'], title="Comparison: Old vs. Wakanda 2.0",
                          color_discrete_map={"Old_Avg": "#ef553b", "Wak_Avg": "#00cc96"})
    st.plotly_chart(fig_otd, use_container_width=True)

    # ==========================================
    # 6. DELIVERY ACCURACY & RISK ANALYSIS
    # ==========================================
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Delivery Accuracy (OTD%) by Supplier")
        sup_accuracy = df.groupby('Supplier').agg(
            Total=('Supplier', 'count'),
            Old_D=('Old_Delayed', 'sum'),
            Wak_D=('Wakanda_Delayed', 'sum')
        ).reset_index()
        sup_accuracy['Old_OTD'] = ((sup_accuracy['Total'] - sup_accuracy['Old_D']) / sup_accuracy['Total']) * 100
        sup_accuracy['Wakanda_OTD'] = ((sup_accuracy['Total'] - sup_accuracy['Wak_D']) / sup_accuracy['Total']) * 100

        if "Old System" in sim_mode:
            fig_acc = px.bar(sup_accuracy, x='Supplier', y='Old_OTD', color_discrete_sequence=["#ef553b"])
        elif "Wakanda System" in sim_mode:
            fig_acc = px.bar(sup_accuracy, x='Supplier', y='Wakanda_OTD', color_discrete_sequence=["#00cc96"])
        else:
            fig_acc = px.bar(sup_accuracy.melt(id_vars='Supplier', value_vars=['Old_OTD', 'Wakanda_OTD']), 
                             x='Supplier', y='value', color='variable', barmode='group',
                             color_discrete_map={'Old_OTD': '#ef553b', 'Wakanda_OTD': '#00cc96'})
        st.plotly_chart(fig_acc, use_container_width=True)

    with c2:
        if "Old System" not in sim_mode:
            st.subheader("Risk Analysis: Delay Root Causes")
            df_wak_delayed = df_filtered[df_filtered['Wakanda_Delayed'] == 1]
            if not df_wak_delayed.empty:
                fig_risk = px.pie(df_wak_delayed, names='Wakanda_Cause', hole=0.4, 
                                 title=f"Root Causes for {sup_filter}")
                st.plotly_chart(fig_risk, use_container_width=True)
            else:
                st.write("No delays detected in the selected period.")

    # ==========================================
    # 7. AUTOMATED RISK DETECTION
    # ==========================================
    if "Old System" not in sim_mode:
        st.markdown("---")
        st.subheader("Automated Risk Detection")
        df_wak_total_delayed = df[df['Wakanda_Delayed'] == 1]
        
        cards = st.columns(len(supplier_profiles))
        for idx, (name, info) in enumerate(supplier_profiles.items()):
            sup_data = df_wak_total_delayed[df_wak_total_delayed['Supplier'] == name]
            delays, t3 = len(sup_data), len(sup_data[sup_data['Wakanda_Action'] == 'Tier 3: Termination Review'])
            cause = sup_data['Wakanda_Cause'].mode()[0] if not sup_data.empty else "None"
            
            with cards[idx]:
                if t3 > 3 or delays > 25:
                    st.error(f"🚨 **Critical: {name}**\n- Delays: {delays}\n- Tier 3: {t3}\n- Main Cause: {cause}\n\n**Action:** Immediate SAP Lead Time Adjustment.")
                elif delays > 10:
                    st.warning(f"⚠️ **Warning: {name}**\n- Delays: {delays}\n- Main Cause: {cause}\n\n**Action:** Audit Required.")
                else:
                    st.success(f"✅ **Stable: {name}**\n- Delays: {delays}\n- Performance Healthy.")

        # ==========================================
        # 8. ENFORCEMENT AUDIT LOG
        # ==========================================
        st.markdown("---")
        st.subheader("Audit Log (Wakanda System 2.0)")
        
        log_filter = st.selectbox("Filter Log by Action:", ["All", "Tier 1: Warning & 8D", "Tier 2: Financial Penalty", "Tier 3: Termination Review", "Freight Claim"])
        df_log = df_wak_total_delayed[['Date', 'Supplier', 'Incoterm', 'Wakanda_Cause', 'Wakanda_Days', 'Wakanda_Accountable', 'Wakanda_Action', 'Wakanda_Penalty']].copy()
        
        if log_filter != "All":
            df_log = df_log[df_log['Wakanda_Action'].str.contains(log_filter.split(":")[0])]

        # FIXED: Using .map() instead of .applymap() for Pandas 2.1.0+
        def color_map(val):
            if 'Tier 3' in str(val): return 'background-color: #ff4b4b; color: white'
            if 'Tier 2' in str(val): return 'background-color: #ffad15; color: black'
            return ''
        
        styled_log = df_log.sort_values('Date', ascending=False).style.map(color_map, subset=['Wakanda_Action'])
        st.dataframe(styled_log, use_container_width=True)
        st.download_button("📥 Download Audit Log (CSV)", df_log.to_csv(index=False), "wakanda_audit_log.csv", "text/csv")

else:
    st.info("👈 Use the Sidebar to set simulation parameters and click 'Run'.")
