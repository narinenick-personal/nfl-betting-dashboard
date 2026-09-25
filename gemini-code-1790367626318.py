import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NFL 10k Monte Carlo Betting Dashboard",
    page_icon="🏈",
    layout="wide"
)

st.title("🏈 NFL Matchup & Player Prop 10,000 Simulation Engine")
st.markdown("Run Monte Carlo simulations to find edge against sportsbook gamelines and player prop lines.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ Game Setup")

# Teams
home_team = st.sidebar.text_input("Home Team Name", "Kansas City Chiefs")
away_team = st.sidebar.text_input("Away Team Name", "Buffalo Bills")

st.sidebar.subheader("Team Baseline Stats")
home_mean_pts = st.sidebar.number_input(f"{home_team} Expected Points", value=26.5, step=0.5)
home_std_pts = st.sidebar.number_input(f"{home_team} Points Std Dev", value=7.0, step=0.5)

away_mean_pts = st.sidebar.number_input(f"{away_team} Expected Points", value=24.0, step=0.5)
away_std_pts = st.sidebar.number_input(f"{away_team} Points Std Dev", value=7.0, step=0.5)

# Sportsbook Lines
st.sidebar.subheader("Sportsbook Lines")
vegas_spread = st.sidebar.number_input("Sportsbook Spread (Home Team perspective, e.g. -3.5)", value=-3.0, step=0.5)
vegas_total = st.sidebar.number_input("Sportsbook Game Total (Over/Under)", value=49.5, step=0.5)

# --- TABS FOR ANALYSIS ---
tab1, tab2 = st.tabs(["🏟️ Game Lines Simulation", "👤 Player Props Simulation"])

# ==========================================
# TAB 1: GAMELINE SIMULATION (10,000 RUNS)
# ==========================================
with tab1:
    st.header(f"Game Simulation: {away_team} @ {home_team}")
    
    if st.button("🚀 Run 10,000 Game Simulations", key="run_game_sim"):
        with st.spinner("Simulating 10,000 games..."):
            # Monte Carlo Simulation
            sim_home_pts = np.random.normal(home_mean_pts, home_std_pts, 10000)
            sim_away_pts = np.random.normal(away_mean_pts, away_std_pts, 10000)
            
            # Ensure points cannot be negative
            sim_home_pts = np.maximum(0, sim_home_pts)
            sim_away_pts = np.maximum(0, sim_away_pts)
            
            margins = sim_home_pts - sim_away_pts
            totals = sim_home_pts + sim_away_pts
            
            # Calculate Hit Rates
            home_win_pct = (margins > 0).mean() * 100
            away_win_pct = (margins < 0).mean() * 100
            
            # Spread outcomes (Home covers if margin + spread > 0)
            home_cover_pct = ((margins + vegas_spread) > 0).mean() * 100
            away_cover_pct = 100 - home_cover_pct
            
            # Total outcomes
            over_pct = (totals > vegas_total).mean() * 100
            under_pct = 100 - over_pct

        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Projected Score", f"{sim_away_pts.mean():.1f} - {sim_home_pts.mean():.1f}")
        col2.metric(f"{home_team} Win %", f"{home_win_pct:.1f}%")
        col3.metric(f"Home Cover ({vegas_spread})", f"{home_cover_pct:.1f}%")
        col4.metric(f"Over {vegas_total} Pts", f"{over_pct:.1f}%")

        # Recommendations Box
        st.subheader("💡 Recommendations")
        rec_cols = st.columns(2)
        
        with rec_cols[0]:
            st.markdown("### Spread Recommendation")
            if home_cover_pct > 55.0:
                st.success(f"**STRONG BUY:** {home_team} {vegas_spread} (Hits in {home_cover_pct:.1f}% of simulations)")
            elif away_cover_pct > 55.0:
                st.success(f"**STRONG BUY:** {away_team} +{-vegas_spread} (Hits in {away_cover_pct:.1f}% of simulations)")
            else:
                st.warning("NO EDGE on the spread (Simulations close to 50/50). Pass.")

        with rec_cols[1]:
            st.markdown("### Total Recommendation")
            if over_pct > 55.0:
                st.success(f"**STRONG BUY:** OVER {vegas_total} (Hits in {over_pct:.1f}% of simulations)")
            elif under_pct > 55.0:
                st.success(f"**STRONG BUY:** UNDER {vegas_total} (Hits in {under_pct:.1f}% of simulations)")
            else:
                st.warning("NO EDGE on total. Pass.")

        # Distribution Chart
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=margins, name="Point Margin (Home - Away)", nbinsx=50, marker_color='#1f77b4'))
        fig.add_vline(x=-vegas_spread, line_dash="dash", line_color="red", annotation_text="Vegas Spread Line")
        fig.update_layout(title="Distribution of Point Margins across 10,000 Games", xaxis_title="Home Margin", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: PLAYER PROPS SIMULATION
# ==========================================
with tab2:
    st.header("Player Prop Simulation Engine")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        player_name = st.text_input("Player Name", "Patrick Mahomes")
        prop_type = st.selectbox("Prop Metric", ["Passing Yards", "Rushing Yards", "Receiving Yards", "Passing TDs"])
    with col_p2:
        player_mean = st.number_input(f"Expected Mean {prop_type}", value=268.5, step=1.0)
        player_std = st.number_input(f"{prop_type} Standard Deviation", value=45.0, step=1.0)
        prop_line = st.number_input(f"Sportsbook Line for {prop_type}", value=255.5, step=0.5)

    if st.button("🚀 Run 10,000 Player Prop Simulations", key="run_prop_sim"):
        with st.spinner("Simulating player performances..."):
            sim_props = np.random.normal(player_mean, player_std, 10000)
            sim_props = np.maximum(0, sim_props) # Cannot have negative yards/stats
            
            over_hit_pct = (sim_props > prop_line).mean() * 100
            under_hit_pct = 100 - over_hit_pct
            med_projection = np.median(sim_props)

        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Median Simulated Stat", f"{med_projection:.1f}")
        col2.metric(f"OVER {prop_line} Hit Rate", f"{over_hit_pct:.1f}%")
        col3.metric(f"UNDER {prop_line} Hit Rate", f"{under_hit_pct:.1f}%")

        # Recommendation
        st.subheader("💡 Prop Recommendation")
        if over_hit_pct >= 56.0:
            st.success(f"🔥 **BET OVER:** {player_name} OVER {prop_line} {prop_type} (Hit Rate: {over_hit_pct:.1f}%)")
        elif under_hit_pct >= 56.0:
            st.success(f"🔥 **BET UNDER:** {player_name} UNDER {prop_line} {prop_type} (Hit Rate: {under_hit_pct:.1f}%)")
        else:
            st.info(f"⚡ **PASS:** Fair line. Simulation indicates no significant value edge.")

        # Plotly Visual
        fig_prop = px.histogram(sim_props, nbins=40, labels={'value': prop_type}, title=f"10,000 Simulation Runs for {player_name}")
        fig_prop.add_vline(x=prop_line, line_dash="dash", line_color="red", annotation_text=f"Prop Line ({prop_line})")
        st.plotly_chart(fig_prop, use_container_width=True)