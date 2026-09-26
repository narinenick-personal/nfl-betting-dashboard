import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="2026 NFL Betting & Bankroll Dashboard", page_icon="🏈", layout="wide")
st.title("🏈 2026 NFL Casual Stats & Bankroll Dashboard")

# --- SIDEBAR: BANKROLL MANAGEMENT ---
st.sidebar.header("💰 Bankroll Manager")
bankroll = st.sidebar.number_input("Total Bankroll ($)", value=40.0, step=5.0, min_value=1.0)
unit_pct = st.sidebar.slider("Base Unit Size (%)", min_value=1.0, max_value=5.0, value=2.5, step=0.5)

base_unit = bankroll * (unit_pct / 100.0)
st.sidebar.metric("Base Unit Bet Amount", f"${base_unit:.2f}")
st.sidebar.info(f"A standard 1-Unit bet is **${base_unit:.2f}** based on your **${bankroll:.2f}** bankroll.")

# --- 2026 SEASON DATABASE ---
# Team Season Averages (Weeks 1-3)
TEAM_STATS_2026 = {
    "Buffalo Bills": {"ppg": 34.5, "papg": 15.5},
    "Kansas City Chiefs": {"ppg": 30.0, "papg": 22.5},
    "Dallas Cowboys": {"ppg": 28.5, "papg": 27.0},
    "San Francisco 49ers": {"ppg": 31.0, "papg": 13.5},
    "Philadelphia Eagles": {"ppg": 24.0, "papg": 18.5},
    "Detroit Lions": {"ppg": 28.0, "papg": 23.5},
    "Green Bay Packers": {"ppg": 17.0, "papg": 26.0},
    "Baltimore Ravens": {"ppg": 20.5, "papg": 20.5},
    "Cincinnati Bengals": {"ppg": 25.0, "papg": 9.5},
    "Atlanta Falcons": {"ppg": 19.0, "papg": 24.0},
    "New York Jets": {"ppg": 11.5, "papg": 21.5},
    "Chicago Bears": {"ppg": 13.5, "papg": 19.5},
}

# Player Game Logs (2026 Season Games)
PLAYER_LOGS_2026 = {
    "Patrick Mahomes": {"type": "Passing Yards", "logs": [291, 280, 268]},
    "Josh Allen": {"type": "Passing Yards", "logs": [310, 275, 298]},
    "Derrick Henry": {"type": "Rushing Yards", "logs": [84, 92, 68]},
    "Saquon Barkley": {"type": "Rushing Yards", "logs": [105, 88, 112]},
    "Ja'Marr Chase": {"type": "Receiving Yards", "logs": [118, 95, 102]},
    "Amon-Ra St. Brown": {"type": "Receiving Yards", "logs": [88, 74, 91]},
}

# --- TABS ---
tab1, tab2 = st.tabs(["🏟️ 2026 Matchup Simulator", "👤 Player Prop Analyzer"])

# ==========================================
# TAB 1: GAMELINE MATCHUPS
# ==========================================
with tab1:
    st.header("Team Game Line Evaluator")
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", list(TEAM_STATS_2026.keys()), index=0)
        home_ppg = st.number_input(f"{home_team} Avg PPG", value=TEAM_STATS_2026[home_team]["ppg"], step=0.5)
        home_papg = st.number_input(f"{home_team} Avg Points Allowed", value=TEAM_STATS_2026[home_team]["papg"], step=0.5)

    with col2:
        away_team = st.selectbox("Away Team", list(TEAM_STATS_2026.keys()), index=1)
        away_ppg = st.number_input(f"{away_team} Avg PPG", value=TEAM_STATS_2026[away_team]["ppg"], step=0.5)
        away_papg = st.number_input(f"{away_team} Avg Points Allowed", value=TEAM_STATS_2026[away_team]["papg"], step=0.5)

    st.divider()
    st.subheader("Sportsbook Line Inputs")
    c1, c2 = st.columns(2)
    with c1:
        spread = st.number_input("Home Team Spread (e.g. -3.5)", value=-3.0, step=0.5)
    with c2:
        total = st.number_input("Game Total (Over/Under)", value=48.5, step=0.5)

    # Calculate Projections
    proj_home = (home_ppg + away_papg) / 2
    proj_away = (away_ppg + home_papg) / 2
    proj_total = proj_home + proj_away
    proj_margin = proj_home - proj_away

    st.divider()
    st.subheader("📊 Projected Matchup Summary")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Score", f"{away_team} {proj_away:.1f} - {proj_home:.1f} {home_team}")
    m2.metric("Projected Total Points", f"{proj_total:.1f} Pts")
    m3.metric("Projected Home Margin", f"{proj_margin:+.1f} Pts")

    # Recommendations & Wager Amount
    st.subheader("💡 Recommendations & Wager Sizing")
    
    # Spread Recommendation
    spread_diff = proj_margin - (-spread)
    if spread_diff >= 2.0:
        wager = base_unit * 1.0
        st.success(f"🎯 **RECOMMENDATION:** Bet **${wager:.2f}** on **{home_team} {spread:+}**. Projected cover by {spread_diff:.1f} pts.")
    elif spread_diff <= -2.0:
        wager = base_unit * 1.0
        st.success(f"🎯 **RECOMMENDATION:** Bet **${wager:.2f}** on **{away_team} +{-spread}**. Projected cover by {abs(spread_diff):.1f} pts.")
    else:
        st.info("⚡ **SPREAD:** Line is too close to projection. Pass on spread.")

    # Total Recommendation
    total_diff = proj_total - total
    if total_diff >= 2.5:
        wager = base_unit * 1.0
        st.success(f"🔥 **RECOMMENDATION:** Bet **${wager:.2f}** on **OVER {total}**. Projected total is {proj_total:.1f} pts.")
    elif total_diff <= -2.5:
        wager = base_unit * 1.0
        st.success(f"❄️ **RECOMMENDATION:** Bet **${wager:.2f}** on **UNDER {total}**. Projected total is {proj_total:.1f} pts.")
    else:
        st.info("⚡ **TOTAL:** Projected total is right on the line. Pass on total.")

# ==========================================
# TAB 2: PLAYER PROPS
# ==========================================
with tab2:
    st.header("Player Props & 2026 Game Logs")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        player_name = st.selectbox("Select Player", list(PLAYER_LOGS_2026.keys()))
        player_data = PLAYER_LOGS_2026[player_name]
        stat_type = player_data["type"]
        prop_line = st.number_input(f"Sportsbook Line for {stat_type}", value=255.5, step=0.5)

    with col_p2:
        logs = player_data["logs"]
        st.write(f"**2026 Game Log ({stat_type}):**")
        df_logs = pd.DataFrame({"Game": [f"Week {i+1}" for i in range(len(logs))], stat_type: logs})
        st.dataframe(df_logs, use_container_width=True)

    # Compute Statistics
    avg_stat = sum(logs) / len(logs)
    times_over = sum(1 for x in logs if x > prop_line)
    hit_rate = (times_over / len(logs)) * 100

    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("2026 Season Average", f"{avg_stat:.1f} {stat_type}")
    r2.metric("Prop Line", f"{prop_line}")
    r3.metric("2026 Over Hit Rate", f"{hit_rate:.0f}% ({times_over}/{len(logs)} Games)")

    st.subheader("💡 Prop Wager Recommendation")
    if avg_stat > prop_line and hit_rate >= 66:
        wager = base_unit * (1.25 if hit_rate == 100 else 1.0)
        st.success(f"🔥 **BET RECOMMENDATION:** Wager **${wager:.2f}** on **{player_name} OVER {prop_line} {stat_type}**. Hit in {times_over}/{len(logs)} games this season.")
    elif avg_stat < prop_line and hit_rate <= 33:
        wager = base_unit * (1.25 if hit_rate == 0 else 1.0)
        st.success(f"❄️ **BET RECOMMENDATION:** Wager **${wager:.2f}** on **{player_name} UNDER {prop_line} {stat_type}**. Stayed under in {len(logs) - times_over}/{len(logs)} games this season.")
    else:
        st.info(f"⚡ **PASS:** Results are too inconsistent across 2026 games. Save your bankroll.")
