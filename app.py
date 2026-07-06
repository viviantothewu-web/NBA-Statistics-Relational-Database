import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

st.set_page_config(page_title="NBA Statistics Database", layout="wide")

# ----------------------------
# MySQL connection
# ----------------------------
config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "nba_database",
    "raise_on_warnings": True,
}

def get_connection():
    return mysql.connector.connect(**config)

def run_query(query, params=None):
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()

def run_execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params or ())
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ----------------------------
# Setup
# ----------------------------
def ensure_favorites_table():
    run_execute("""
        CREATE TABLE IF NOT EXISTS favorite_player (
            favorite_id INT AUTO_INCREMENT PRIMARY KEY,
            player_id BIGINT NOT NULL,
            notes TEXT,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)

def safe_metric(value, digits=1):
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return round(float(value), digits)
    return value

# ----------------------------
# Pages
# ----------------------------
def home_page():
    st.title("NBA Statistics Database (1946-2025)")
    st.write("A relational NBA database built from public Kaggle data.")

    c1, c2, c3, c4, c5 = st.columns(5)

    try:
        total_teams = run_query("SELECT COUNT(*) AS n FROM teams").iloc[0]["n"]
        total_games = run_query("SELECT COUNT(*) AS n FROM games").iloc[0]["n"]
        total_players = run_query("SELECT COUNT(*) AS n FROM players").iloc[0]["n"]
        avg_points = run_query("SELECT AVG(pts) AS avg_pts FROM team_game_stats").iloc[0]["avg_pts"]
        current_teams = 30
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    c1.metric("Total number of teams including historical data", total_teams)
    c2.metric("Total number of current active teams", current_teams)
    c3.metric("Total number of games played", total_games)
    c4.metric("Total number of players", total_players)
    c5.metric("Avg team points", safe_metric(avg_points))

    st.header("Project Overview")

    st.write("""
    Welcome to the **NBA Statistics Database Dashboard**, an interactive analytics platform designed to explore over
    75 years of NBA history. The application integrates historical game, team, and player data into a normalized
    MySQL database and provides users with an easy-to-use interface for searching, filtering, and analyzing NBA statistics.
    """)
    
    st.header("Project Features")
    
    st.markdown("""
    - 🏀 Browse NBA teams, games, and player information
    - 📊 Explore interactive statistical visualizations
    - 🔍 Search and filter historical NBA data
    - ⭐ Create and manage a personalized player watchlist
    - ✏️ Add, edit, and delete notes for favorite players (CRUD)
    - 💾 Demonstrates relational database design and SQL querying
    """)

def teams_page():
    st.header("Teams")

    search = st.text_input("Search team name, nickname, or abbreviation")

    query = "SELECT * FROM teams"
    params = None

    if search:
        query += """
            WHERE team_name LIKE %s
               OR nickname LIKE %s
               OR abbreviation LIKE %s
        """
        params = (f"%{search}%", f"%{search}%", f"%{search}%")

    query += " ORDER BY team_name"

    teams = run_query(query, params)
    st.dataframe(teams, use_container_width=True)

def games_page():
    st.header("Games")

    col1, col2 = st.columns(2)
    with col1:
        season_type = st.selectbox(
            "Season type",
            ["All", "Regular Season", "Pre Season", "Playoffs", "Play In"]
        )
    with col2:
        team_search = st.text_input("Search team name")

    query = """
        SELECT
            game_id, season_id, game_date, season_type,
            team_name_home, team_name_away,
            team_abbreviation_home, team_abbreviation_away,
            pts_home, pts_away, wl_home, wl_away
        FROM games_clean
        WHERE 1=1
    """
    params = []

    if season_type != "All":
        query += " AND season_type = %s"
        params.append(season_type)

    if team_search:
        query += " AND (team_name_home LIKE %s OR team_name_away LIKE %s)"
        params.extend([f"%{team_search}%", f"%{team_search}%"])

    query += " ORDER BY game_date DESC LIMIT 200"

    games = run_query(query, tuple(params) if params else None)
    st.dataframe(games, use_container_width=True)

    if not games.empty:
        chart_df = games.head(30).copy()
        chart_df["total_points"] = chart_df["pts_home"] + chart_df["pts_away"]

        fig = px.bar(
            chart_df,
            x="game_date",
            y="total_points",
            hover_data=["team_name_home", "team_name_away"],
            title="Recent Games: Total Points"
        )
        st.plotly_chart(fig, use_container_width=True)

def analytics_page():
    st.header("Analytics")

    # get available seasons
    seasons_df = run_query("""
        SELECT DISTINCT season_id
        FROM team_game_stats
        ORDER BY season_id DESC
    """)

    season_options = ["All"] + seasons_df["season_id"].dropna().astype(int).tolist()
    selected_season = st.selectbox("Filter by season", season_options)

    min_games = st.slider(
        "Minimum games for team ranking",
        min_value=1,
        max_value=500,
        value=100,
        step=10
    )

    # ----------------------------
    # Top teams by average points
    # ----------------------------
    top_query = """
        SELECT
            team_name,
            COUNT(*) AS games_played,
            AVG(pts) AS avg_points
        FROM team_game_stats
        WHERE 1=1
    """
    params = []

    if selected_season != "All":
        top_query += " AND season_id = %s"
        params.append(int(selected_season))

    top_query += """
        GROUP BY team_name
        HAVING COUNT(*) >= %s
        ORDER BY avg_points DESC
        LIMIT 10
    """
    params.append(min_games)

    top_teams = run_query(top_query, tuple(params))

    st.subheader("Top 10 Teams by Average Points")
    st.dataframe(top_teams, use_container_width=True)

    if not top_teams.empty:
        fig1 = px.bar(
            top_teams,
            x="team_name",
            y="avg_points",
            title="Top 10 Teams by Average Points"
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ----------------------------
    # Home vs Away
    # ----------------------------
    home_away_query = """
        SELECT
            is_home,
            AVG(pts) AS avg_points,
            AVG(reb) AS avg_rebounds,
            AVG(ast) AS avg_assists
        FROM team_game_stats
        WHERE 1=1
    """
    params2 = []

    if selected_season != "All":
        home_away_query += " AND season_id = %s"
        params2.append(int(selected_season))

    home_away_query += """
        GROUP BY is_home
        ORDER BY is_home DESC
    """

    home_away = run_query(home_away_query, tuple(params2) if params2 else None)
    home_away["location"] = home_away["is_home"].map({1: "Home", 0: "Away"})

    st.subheader("Home vs Away Averages")
    st.dataframe(
        home_away[["location", "avg_points", "avg_rebounds", "avg_assists"]],
        use_container_width=True
    )

    if not home_away.empty:
        fig2 = px.bar(
            home_away,
            x="location",
            y="avg_points",
            title="Home vs Away Average Points"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------
    # Highest scoring games
    # ----------------------------
    high_query = """
        SELECT
            game_id,
            game_date,
            team_name_home,
            team_name_away,
            pts_home,
            pts_away,
            (pts_home + pts_away) AS total_points
        FROM games_clean
        WHERE 1=1
    """
    params3 = []

    if selected_season != "All":
        high_query += " AND season_id = %s"
        params3.append(int(selected_season))

    high_query += """
        ORDER BY total_points DESC
        LIMIT 10
    """

    high_scoring = run_query(high_query, tuple(params3) if params3 else None)

    st.subheader("Highest Scoring Games")
    st.dataframe(high_scoring, use_container_width=True)

def favorites_page():
    st.header("Favorites/ Notes")

    players = run_query("""
        SELECT player_id, player_name
        FROM players
        ORDER BY player_name
    """)

    if players.empty:
        st.warning("No players found.")
        return

    player_map = dict(zip(players["player_name"], players["player_id"]))
    selected_player = st.selectbox("Select player", list(player_map.keys()))
    notes = st.text_area("Notes")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Add to Favorites"):
            pid = int(player_map[selected_player])
            run_execute(
                "INSERT INTO favorite_players (player_id, notes) VALUES (%s, %s)",
                (pid, notes)
            )
            st.success("Favorite added.")
            st.rerun()

    with col2:
        if st.button("Refresh List"):
            st.rerun()

    favs = run_query("""
        SELECT
            f.favorite_player_id,
            p.player_name,
            f.notes,
            f.date_added
        FROM favorite_players AS f
        JOIN players p ON f.player_id = p.player_id
        ORDER BY f.date_added DESC
    """)

    st.subheader("Saved Favorites")
    st.dataframe(favs, use_container_width=True)

    if not favs.empty:
        st.subheader("Update or Delete a Favorite")
        fav_id = st.selectbox("Choose favorite_player_id", favs["favorite_player_id"].tolist())

        selected_row = favs[favs["favorite_player_id"] == fav_id].iloc[0]
        new_notes = st.text_area("Edit notes", value=str(selected_row["notes"] or ""))

        col3, col4 = st.columns(2)

        with col3:
            if st.button("Update Notes"):
                run_execute(
                    "UPDATE favorite_players SET notes = %s WHERE favorite_player_id = %s",
                    (new_notes, int(fav_id))
                )
                st.success("Notes updated.")
                st.rerun()

        with col4:
            if st.button("Delete Favorite"):
                run_execute(
                    "DELETE FROM favorite_players WHERE favorite_player_id = %s",
                    (int(fav_id),)
                )
                st.success("Favorite deleted.")
                st.rerun()

# ----------------------------
# Sidebar navigation
# ----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Teams", "Games", "Analytics", "Favorites"])

# ----------------------------
# Render selected page
# ----------------------------
if page == "Home":
    home_page()
elif page == "Teams":
    teams_page()
elif page == "Games":
    games_page()
elif page == "Analytics":
    analytics_page()
elif page == "Favorites":
    favorites_page()