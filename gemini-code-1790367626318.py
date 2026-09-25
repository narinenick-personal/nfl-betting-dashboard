import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# --- HELPER FUNCTIONS ---
def american_to_implied_prob(odds: float) -> float:
    if odds < 0:
        return (abs(odds) / (abs(odds) + 100)) * 100
    else:
        return (100 / (odds + 100)) * 100

def american_to_decimal(odds: float) -> float:
    if odds < 0:
        return 1 + (100 / abs(odds))
    else:
        return 1 + (odds / 100)

def calculate_ev(sim_win_pct: float, american_odds: float) -> float:
    decimal_odds = american_to_decimal(american_odds)
    p_win = sim_win_pct / 100.0
    p_loss = 1.0 - p_win
    profit = decimal_odds - 1.0
    ev = (p_win * profit) - (p_loss * 1.0)
    return ev * 100

@st.cache_data(ttl=600)  # Cache API call for 10 minutes to conserve requests
def fetch_nfl_odds(api_key):
    url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'bookmakers': 'draftkings,fanduel',
        'oddsFormat': 'american'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching odds: {response.json().get('message', 'Unknown error')}")
        return []

# --- PAGE CONFIG ---
st.set_page_config(page_title="NFL 10k Monte Carlo & Auto Odds", page_icon="🏈", layout="wide")
st.title("🏈 Automated NFL Matchup & Player Prop 10,000 Sim Dashboard")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("🔑 API & Matchup Configuration")
api_key = st.sidebar.text_input("The Odds API Key", type="password", help="Enter key from the-odds-api.com")

live_games = []
selected_game = None

if api_key:
    odds_data = fetch_nfl_odds(api_key)
    if odds_data:
        live_games = [f"{game['away_team']} @ {game['home_team']}" for game in odds_data]
        selected_game_str = st.sidebar.selectbox("Select Upcoming Matchup", live_games)
        
        # Find raw game dict
        selected_game = next((g for g in odds_data if f"{g['away_team']} @ {g['home_team']}" == selected_game_str), None)

st.sidebar.divider()

if selected_game:
    home_team = selected_game['home_team']
    away_team = selected_game['away_team']
    
    # Extract FanDuel / DraftKings lines
    dk_book = next((b for b in selected_game['bookmakers'] if b['key'] == 'draftkings'), None)
    fd_book = next((b for b in selected_game['bookmakers'] if b['key'] == 'fanduel'), None)
    
    st.sidebar.success("Auto-Fetched Lines Loaded!")
    
    # Parse Spread & Total from DK or FD
    active_book = dk_book or fd_book
    spread_val, spread_odds_val, total_val, total_odds_val = -3.0, -110, 47.5, -110
    
    if active_book:
        for market in active_book['markets']:
            if market['key'] == 'spreads':
                home_outcome = next((o for o in market['outcomes'] if o['name'] == home_team), None)
                if home_outcome:
                    spread_val = home_outcome['point']
                    spread_odds_val = home_outcome['price']
            elif market['key'] == 'totals':
                over_outcome = next((o for o in market['outcomes'] if o['name'] == 'Over'), None)
                if over_outcome:
                    total_val = over_outcome['point']
                    total_odds_val = over_outcome['price']
else:
    home_team = st.sidebar.text_input("Home Team Name", "Kansas City Chiefs")
    away_team = st.sidebar.text_input("Away Team Name", "Buffalo Bills")
    spread_val, spread_odds_val, total_val, total_odds_val = -3.0, -110, 47.5, -110

st.sidebar.subheader("Team Baseline Parameters")
home_mean_pts = st.sidebar.number_input(f"{home_team} Expected Pts", value=26.5, step=0.5)
home_std_pts = st.sidebar.number_input(f"{home_team} Pts Std Dev", value=7.0, step=0.5)

away_mean_pts = st.sidebar.number_input(f"{away_team} Expected Pts", value=24.0, step=0.5)
away_std_pts = st.sidebar.number_input(f"{away_team} Pts Std Dev", value=7.0, step=0.5)

st.sidebar.subheader("Sportsbook Lines (Auto or Manual)")
vegas_spread = st.sidebar.number_input("Home Spread", value=float(spread_val), step=0.5)
home_spread_odds = st.sidebar.number_input("Home Spread Odds", value=int(spread_odds_val), step=5)
vegas_total = st.sidebar.number_input("Game Total Line", value=float(total_val), step=0.5)
over_odds = st.sidebar.number_input("Over Odds", value=int(total_odds_val), step=5)

# --- TABS FOR ANALYSIS ---
tab1, tab2 = st.tabs(["🏟️ Auto-Odds & Game Simulation", "👤 Player Props Engine"])

# ==========================================
# TAB 1: GAMELINE SIMULATION
# ==========================================
with tab1:
    st.header(f"Matchup: {away_team} @ {home_team}")
    
    if selected_game and 'bookmakers' in selected_game:
        st.subheader("📡 Live FanDuel vs DraftKings Comparison")
        book_rows = []
        for b in selected_game['bookmakers']:
            sp_m = next((m for m in b['markets'] if m['key'] == 'spreads'), None)
            tot_m = next((m for m in b['markets'] if m['key'] == 'totals'), None)
            
            sp_str, tot_str = "N/A", "N/A"
            if sp_m:
                h_o = next((o for o in sp_m['outcomes'] if o['name'] == home_team), None)
                if h_o: sp_str = f"{h_o['point']:+} ({h_o['price']:+d})"
            if tot_m:
                o_o = next((o for o in tot_m['outcomes'] if o['name'] == 'Over'), None)
                if o_o: tot_str = f"O {o_o['point']} ({o_o['price']:+d})"
                
            book_rows.append({"Sportsbook": b['title'], "Home Spread": sp_str, "Total": tot_str})
        st.dataframe(pd.DataFrame(book_rows), use_container_width=True)

    if st.button("🚀 Run 10,000 Game Simulations", key="run_game_sim"):
        sim_home_pts = np.maximum(0, np.random.normal(home_mean_pts, home_std_pts, 10000))
        sim_away_pts = np.maximum(0, np.random.normal(away_mean_pts, away_std_pts, 10000))
        
        margins = sim_home_pts - sim_away_pts
        totals = sim_home_pts + sim_away_pts
        
        home_cover_pct = ((margins + vegas_spread) > 0).mean() * 100
        away_cover_pct = 100 - home_cover_pct
        over_pct = (totals > vegas_total).mean() * 100
        under_pct = 100 - over_pct

        home_implied = american_to_implied_prob(home_spread_odds)
        over_implied = american_to_implied_prob(over_odds)

        home_edge = home_cover_pct - home_implied
        over_edge = over_pct - over_implied

        home_ev = calculate_ev(home_cover_pct, home_spread_odds)
        over_ev = calculate_ev(over_pct, over_odds)

        st.subheader("📊 Model Recommendations & Value Edge")
        col1, col2, col3 = st.columns(3)
        col1.metric("Projected Score", f"{sim_away_pts.mean():.1f} - {sim_home_pts.mean():.1f}")
        col2.metric(f"{home_team} {vegas_spread:+} Cover Rate", f"{home_cover_pct:.1f}%", delta=f"{home_edge:+.1f}% Edge (EV: {home_ev:+.1f}%)")
        col3.metric(f"Over {vegas_total} Rate", f"{over_pct:.1f}%", delta=f"{over_edge:+.1f}% Edge (EV: {over_ev:+.1f}%)")

        # Visual
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=margins, name="Point Margin", nbinsx=50, marker_color='#1f77b4'))
        fig.add_vline(x=-vegas_spread, line_dash="dash", line_color="red", annotation_text="Spread Line")
        fig.update_layout(title="10,000 Simulated Point Margins", xaxis_title="Home Margin", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: PLAYER PROPS ENGINE
# ==========================================
with tab2:
    st.header("Player Prop Simulation Engine")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        player_name = st.text_input("Player Name", "Josh Allen")
        prop_type = st.selectbox("Prop Metric", ["Passing Yards", "Rushing Yards", "Receiving Yards", "Passing TDs"])
        player_mean = st.number_input(f"Expected Mean {prop_type}", value=255.0, step=1.0)
        player_std = st.number_input(f"{prop_type} Standard Deviation", value=40.0, step=1.0)
    with col_p2:
        prop_line = st.number_input(f"Sportsbook Line for {prop_type}", value=245.5, step=0.5)
        prop_over_odds = st.number_input("Over Odds (American)", value=-115, step=5)

    if st.button("🚀 Run 10,000 Player Prop Simulations", key="run_prop_sim"):
        sim_props = np.maximum(0, np.random.normal(player_mean, player_std, 10000))
        over_hit_pct = (sim_props > prop_line).mean() * 100
        over_implied_prob = american_to_implied_prob(prop_over_odds)
        over_edge = over_hit_pct - over_implied_prob
        over_ev = calculate_ev(over_hit_pct, prop_over_odds)

        st.metric(f"OVER {prop_line} ({prop_over_odds:+d})", f"Hit Rate: {over_hit_pct:.1f}%", delta=f"{over_edge:+.1f}% Edge (EV: {over_ev:+.1f}%)")

        fig_prop = px.histogram(sim_props, nbins=40, labels={'value': prop_type}, title=f"10,000 Simulation Runs for {player_name}")
        fig_prop.add_vline(x=prop_line, line_dash="dash", line_color="red", annotation_text=f"Prop Line ({prop_line})")
        st.plotly_chart(fig_prop, use_container_width=True)
