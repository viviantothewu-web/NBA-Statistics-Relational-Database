import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

st.set_page_config(page_title="NBA Statistics Database", layout="wide")

# connect to SQL database
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

def home_page():
    st.title("NBA Statistics Database (1946-2025)")
    st.write("A relational NBA database built from public Kaggle data.")

    c1, c2, c3, c4, c5 = st.columns(5)

    try:
        total_teams = run_query("SELECT COUNT(*) AS total_num_teams FROM teams").iloc[0]["total_num_teams"]
        total_games = run_query("SELECT COUNT(*) AS total_num_games FROM games").iloc[0]["total_num_games"]
        total_players = run_query("SELECT COUNT(*) AS total_players FROM players").iloc[0]["total_players"]
        avg_points = run_query("SELECT ROUND(AVG(pts), 2) AS avg_pts FROM team_game_stats").iloc[0]["avg_pts"]
        current_teams = 30
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    c1.metric("Total number of teams including historical data", total_teams)
    c2.metric("Total number of current active teams", current_teams)
    c3.metric("Total number of games played", total_games)
    c4.metric("Total number of players", total_players)
    c5.metric("Avg team points", avg_points)

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

    
def current_teams_page():
    st.header("Current Teams")
    st.write("Browse current NBA teams with location and franchise information.")

    # get states for dropdown
    states_df = run_query("""
        SELECT DISTINCT state
        FROM teams
        WHERE nickname IS NOT NULL
          AND city IS NOT NULL
          AND state IS NOT NULL
          AND year_founded IS NOT NULL
        ORDER BY state
    """)

    state_options = ["All"] + states_df["state"].dropna().tolist()

    col1, col2 = st.columns(2)

    with col1:
        search_text = st.text_input("Search team name", key="current_team_search")

    with col2:
        selected_state = st.selectbox(
            "Filter by state",
            state_options,
            key="current_team_state"
        )

    query = """
        SELECT *
        FROM teams
        WHERE nickname IS NOT NULL
          AND city IS NOT NULL
          AND state IS NOT NULL
          AND year_founded IS NOT NULL
          AND (%(search_text)s = '' OR team_name LIKE CONCAT('%%', %(search_text)s, '%%'))
          AND (%(selected_state)s = 'All' OR state = %(selected_state)s)
    """
    #the query is also in SQL, the one in python is slightly different, AI was used to convert the syntax into one that works with streamlit. using (search_text) instead of actual letters in SQL

    params = {
        "search_text": search_text,
        "selected_state": selected_state
    }

    current_teams = run_query(query, params)

    st.subheader("Current Teams")
    st.dataframe(current_teams, use_container_width=True)

    st.subheader("Team Details")
    
    if current_teams.empty:
        st.info("No teams available for the selected filters.")
    else:
        selected_team = st.selectbox(
            "Select a team",
            current_teams["team_name"].tolist(),
            key="selected_current_team"
        )
    
        team_stats = run_query("""
            SELECT
                COUNT(*) AS number_games_played,
                ROUND(AVG(pts), 2) AS average_points,
                ROUND(AVG(reb), 2) AS average_rebounds,
                ROUND(AVG(ast), 2) AS average_assists
            FROM team_game_stats
            WHERE team_name = %s
            GROUP BY team_name
        """, (selected_team,))
    
        if not team_stats.empty:
            stats = team_stats.iloc[0]
    
            c1, c2, c3, c4 = st.columns(4)
    
            c1.metric("Games Played", stats["number_games_played"])
            c2.metric("Average Points", stats["average_points"])
            c3.metric("Average Rebounds", stats["average_rebounds"])
            c4.metric("Average Assists", stats["average_assists"])


def historical_teams_page():
    st.header("Historical Teams")
    st.write("Browse historical NBA franchises that no longer have complete location data.")

    search_text = st.text_input(
        "Search historical team name",
        key="hist_team_search"
    )

    query = """
        SELECT *
        FROM teams
        WHERE state IS NULL
          AND (%s = '' OR team_name LIKE CONCAT('%%', %s, '%%'))
    """

    params = (
        search_text,
        search_text
    )

    historical_teams = run_query(query, params)

    st.subheader("Historical Teams")
    st.dataframe(historical_teams, use_container_width=True)

    st.subheader("Team Details")

    if historical_teams.empty:
        st.info("No teams available for the selected filters.")
    else:
        selected_team = st.selectbox(
            "Select a historical team",
            historical_teams["team_name"].tolist(),
            key="selected_historical_team"
        )
    
        team_stats = run_query("""
            SELECT
                COUNT(*) AS number_games_played,
                ROUND(AVG(pts), 2) AS average_points,
                ROUND(AVG(reb), 2) AS average_rebounds,
                ROUND(AVG(ast), 2) AS average_assists
            FROM team_game_stats
            WHERE team_name = %s
            GROUP BY team_name
        """, (selected_team,))
    
        if not team_stats.empty:
            stats = team_stats.iloc[0]
    
            c1, c2, c3, c4 = st.columns(4)
    
            c1.metric("Games Played", stats["number_games_played"])
            c2.metric("Average Points", stats["average_points"])
            c3.metric("Average Rebounds", stats["average_rebounds"])
            c4.metric("Average Assists", stats["average_assists"])


def games_page():
    st.header("Games")
    st.write("Browse NBA games, filter results, and explore game-level statistics.")

    # get season types for dropdown
    season_types_df = run_query("""
        SELECT DISTINCT season_type
        FROM games
        ORDER BY season_type
    """)

    season_type_options = ["All"] + season_types_df["season_type"].dropna().tolist()

    col1, col2 = st.columns(2)

    with col1:
        selected_season_type = st.selectbox(
            "Filter by season type",
            season_type_options,
            key="games_season_type"
        )

    with col2:
        search_text = st.text_input(
            "Search team name",
            key="games_team_search"
        )

    query = """
        SELECT
            game_date,
            season_type,
            team_name_home,
            team_name_away,
            pts_home,
            pts_away,
            wl_home,
            wl_away
        FROM games
        WHERE (%s = 'All' OR season_type = %s)
          AND (
                %s = ''
                OR team_name_home LIKE CONCAT('%%', %s, '%%')
                OR team_name_away LIKE CONCAT('%%', %s, '%%')
              )
        ORDER BY game_date DESC
    """

    params = (
        selected_season_type,
        selected_season_type,
        search_text,
        search_text,
        search_text
    )

    games = run_query(query, params)

    st.subheader("Games Table")
    st.dataframe(games, use_container_width=True)


    st.subheader("Games Chart")

    if not games.empty:
        chart_df = games.copy()
        chart_df["total_points"] = chart_df["pts_home"] + chart_df["pts_away"]

        fig = px.bar(
            chart_df.head(20),
            x="game_date",
            y="total_points",
            hover_data=["team_name_home", "team_name_away"],
            title="Total Points by Game"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No games available for the selected filters.")


def analytics_page():
    st.header("Analytics")
    st.write("Explore NBA trends, team performance, and game scoring patterns.")


    # get distinct Season for dropdown
    season_types_df = run_query("""
        SELECT DISTINCT season_type
        FROM team_game_stats
        WHERE season_type IS NOT NULL
        ORDER BY season_type
    """)

    season_type_options = ["All"] + season_types_df["season_type"].dropna().tolist()

    selected_season_type = st.selectbox(
        "Filter by season type",
        season_type_options,
        key="analytics_season_type"
    )

  
    # Top teams by average points
    top_teams_query = """
        SELECT
            team_name,
            COUNT(*) AS games_played,
            AVG(pts) AS average_points
        FROM team_game_stats
        WHERE (%s = 'All' OR season_type = %s)
        GROUP BY team_name
        ORDER BY average_points DESC
        LIMIT 10
    """

    top_teams = run_query(
        top_teams_query,
        (selected_season_type, selected_season_type)
    )

    st.subheader("Top Teams by Average Points")
    st.dataframe(top_teams, use_container_width=True)

    if not top_teams.empty:
        fig1 = px.bar(
            top_teams,
            x="team_name",
            y="average_points",
            title="Top Teams by Average Points"
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Home vs away averages
    home_away_query = """
        SELECT
            is_home,
            AVG(pts) AS avg_points,
            AVG(reb) AS avg_rebounds,
            AVG(ast) AS avg_assists
        FROM team_game_stats
        WHERE (%s = 'All' OR season_type = %s)
        GROUP BY is_home
        ORDER BY is_home DESC
    """

    home_away = run_query(
        home_away_query,
        (selected_season_type, selected_season_type)
    )

    if not home_away.empty:
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

    # Highest scoring games
    highest_scoring_query = """
        SELECT
            game_date,
            team_name_home,
            team_name_away,
            pts_home,
            pts_away,
            pts_home + pts_away AS total_points
        FROM games
        WHERE (%s = 'All' OR season_type = %s)
        ORDER BY total_points DESC
        LIMIT 10
    """

    highest_scoring_games = run_query(
        highest_scoring_query,
        (selected_season_type, selected_season_type)
    )

    st.subheader("Highest Scoring Games")
    st.dataframe(highest_scoring_games, use_container_width=True)

    if not highest_scoring_games.empty:
        fig3 = px.bar(
            highest_scoring_games,
            x="game_date",
            y="total_points",
            hover_data=["team_name_home", "team_name_away"],
            title="Highest Scoring Games"
        )
        st.plotly_chart(fig3, use_container_width=True)

    
def favorite_player_page():
    st.header("Favorites")
    st.write("Create and manage a personal watchlist of NBA players.")


    # Query 1: player dropdown data
    players_df = run_query("""
        SELECT player_id, player_name
        FROM players
        ORDER BY player_name
    """)

    if players_df.empty:
        st.warning("No players found.")
        return

    player_map = dict(zip(players_df["player_name"], players_df["player_id"]))

    col1, col2 = st.columns(2)

    with col1:
        selected_player_name = st.selectbox(
            "Select player",
            list(player_map.keys()),
            key="favorite_player_select"
        )

    with col2:
        notes = st.text_area(
            "Notes",
            key="favorite_notes"
        )

    # Add favorite

    if st.button("Add to Favorites"):
        selected_player_id = player_map[selected_player_name]

        run_execute(
            """
            INSERT INTO favorite_player (player_id, notes)
            VALUES (%s, %s)
            """,
            (selected_player_id, notes)
        )
        st.success("Player added to favorites.")
        st.rerun()


    # Query 2: saved favorites table

    favorites_df = run_query("""
        SELECT fp.favorite_player_id, p.player_name, fp.notes, fp.date_added
        FROM favorite_player AS fp
        JOIN players AS p
        ON fp.player_id = p.player_id
        ORDER BY fp.date_added DESC
    """)

    st.subheader("Saved Favorites")
    st.dataframe(favorites_df, use_container_width=True)

    #  Update / Delete
    if not favorites_df.empty:
        st.subheader("Update or Delete a Favorite")

        favorite_player_id = st.selectbox(
            "Choose favorite record",
            favorites_df["favorite_player_id"].tolist(),
            key="favorite_player_id_select"
        )

        selected_row = favorites_df[
            favorites_df["favorite_player_id"] == favorite_player_id
        ].iloc[0]

        updated_notes = st.text_area(
            "Edit notes",
            value=str(selected_row["notes"] or ""),
            key="updated_favorite_notes"
        )

        col3, col4 = st.columns(2)

        with col3:
            if st.button("Update Notes"):
                run_execute(
                    """
                    UPDATE favorite_player
                    SET notes = %s
                    WHERE favorite_player_id = %s
                    """,
                    (updated_notes, favorite_player_id)
                )
                st.success("Favorite updated.")
                st.rerun()

        with col4:
            if st.button("Delete Favorite"):
                run_execute(
                    """
                    DELETE FROM favorite_player
                    WHERE favorite_player_id = %s
                    """,
                    (favorite_player_id,)
                )
                st.success("Favorite deleted.")
                st.rerun()

            

#set up structure of each page
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Current Teams", "All Historical Teams", "Games", "Analytics", "Favorites"]
)

if page == "Home":
    home_page()
elif page == "Current Teams":
    current_teams_page()
elif page == "All Historical Teams":
    historical_teams_page()
elif page == "Games":
    games_page()
elif page == "Analytics":
    analytics_page()
elif page == "Favorites":
    favorite_player_page()