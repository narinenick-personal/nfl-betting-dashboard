import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="NFL Casual Stats & Bets", page_icon="🏈", layout="wide")
st.title("🏈 NFL Casual Betting Helper")
st.caption("No complex math. Just core stats, recent averages, and fun $0.50 - $1 recommendations.")

tab1, tab2 = st.tabs(["🏟️ Game Lines (Spreads & Totals)", "👤 Player Props"])

# ==========================================
# TAB 1: GAMELINES & TEAM STATS
# ==========================================
with tab1:
    st.header("Matchup Stat Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("Home Team", "Kansas City Chiefs")
        home_ppg = st.number_input(f"{home_team} Avg Points Scored", value=27.5, step=0.5)
        home_papg = st.number_input(f"{home_team} Avg Points Allowed", value=20.0, step=0.5)
        
    with col2:
        away_team = st.text_input("Away Team", "Buffalo Bills")
        away_ppg = st.number_input(f"{away_team} Avg Points Scored", value=26.0, step=0.5)
        away_papg = st.number_input(f"{away_team} Avg Points Allowed", value=22.5, step=0.5)

    st.divider()
    st.subheader("Sportsbook Lines")
    c1, c2 = st.columns(2)
    with c1:
        spread = st.number_input("Home Team Spread (e.g., -3.5)", value=-3.0, step=0.5)
    with c2:
        total = st.number_input("Game Total (Over/Under)", value=49.5, step=0.5)

    # --- CALCULATIONS ---
    # Projected Score based on offensive & defensive averages
    proj_home = (home_ppg + away_papg) / 2
    proj_away = (away_ppg + home_papg) / 2
    proj_total = proj_home + proj_away
    proj_margin = proj_home - proj_away  # Positive means home is winning by this much

    st.divider()
    st.subheader("📊 Projected Outcome")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Final Score", f"{away_team} {proj_away:.1f} - {proj_home:.1f} {home_team}")
    m2.metric("Projected Total Points", f"{proj_total:.1f} Pts")
    m3.metric("Projected Home Margin", f"{proj_margin:+.1f} Pts")

    # --- SIMPLE RECOMMENDATIONS ---
    st.subheader("💡 Recommendations")
    
    # Spread Logic
    if proj_margin > (-spread + 1.5):
        st.success(f"🎯 **SPREAD PICK:** Take **{home_team} {spread:+}**. Stats project them to cover by {(proj_margin - (-spread)):.1f} points.")
    elif proj_margin < (-spread - 1.5):
        st.success(f"🎯 **SPREAD PICK:** Take **{away_team} +{-spread}**. Stats project them to cover.")
    else:
        st.info("⚡ **SPREAD:** Line is too close to stats prediction. Pass or pick your favorite team.")

    # Total Logic
    if proj_total >= total + 2.0:
        st.success(f"🔥 **TOTAL PICK:** Take **OVER {total}**. Both teams average a combined {proj_total:.1f} points.")
    elif proj_total <= total - 2.0:
        st.success(f"❄️ **TOTAL PICK:** Take **UNDER {total}**. Both defenses hold teams to a combined {proj_total:.1f} points.")
    else:
        st.info("⚡ **TOTAL:** Projected total is right on the line. Pass.")

# ==========================================
# TAB 2: PLAYER PROPS
# ==========================================
with tab2:
    st.header("Player Recent Performance Check")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        player_name = st.text_input("Player Name", "Patrick Mahomes")
        stat_type = st.selectbox("Stat Type", ["Passing Yards", "Rushing Yards", "Receiving Yards", "Passing TDs"])
        prop_line = st.number_input(f"Sportsbook Line ({stat_type})", value=255.5, step=0.5)

    with col_p2:
        st.write("Enter stats from last 3-5 games:")
        g1 = st.number_input("Game 1 Stat", value=270.0, step=1.0)
        g2 = st.number_input("Game 2 Stat", value=240.0, step=1.0)
        g3 = st.number_input("Game 3 Stat", value=290.0, step=1.0)
        g4 = st.number_input("Game 4 Stat (0 if N/A)", value=265.0, step=1.0)

    # Calculate Recent Averages
    games = [g for g in [g1, g2, g3, g4] if g > 0]
    avg_stat = sum(games) / len(games) if games else 0
    times_hit_over = sum(1 for g in games if g > prop_line)
    hit_rate = (times_hit_over / len(games)) * 100 if games else 0

    st.divider()
    st.subheader(f"📈 Analysis for {player_name}")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("Recent Average", f"{avg_stat:.1f} {stat_type}")
    r2.metric("Prop Line", f"{prop_line}")
    r3.metric("Recent Over Hit Rate", f"{hit_rate:.0f}% ({times_hit_over}/{len(games)} games)")

    # Prop Recommendation
    if avg_stat > prop_line and hit_rate >= 66:
        st.success(f"🔥 **BET RECOMMENDATION:** Take **OVER {prop_line} {stat_type}**. {player_name} has hit the over in {times_hit_over} of his last {len(games)} games.")
    elif avg_stat < prop_line and hit_rate <= 33:
        st.success(f"❄️ **BET RECOMMENDATION:** Take **UNDER {prop_line} {stat_type}**. {player_name} has stayed under in {len(games) - times_hit_over} of his last {len(games)} games.")
    else:
        st.info(f"⚡ **PASS:** Results are mixed across recent games. Too risky for a bet.")
