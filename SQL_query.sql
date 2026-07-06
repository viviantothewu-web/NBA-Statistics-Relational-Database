CREATE DATABASE nba_project;

SHOW TABLES;

# add primary keys
ALTER TABLE players_clean
ADD PRIMARY KEY (player_id);

ALTER TABLE teams_clean
ADD PRIMARY KEY (team_id);

ALTER TABLE games_clean
ADD PRIMARY KEY (game_id);

# team stats doesnt have a primary key, adding an auto incre id
ALTER TABLE team_game_stats_clean
ADD COLUMN stat_id INT AUTO_INCREMENT PRIMARY KEY FIRST;

#checking
SELECT * 
FROM team_game_stats_clean;


# add foreign key
ALTER TABLE games_clean
ADD CONSTRAINT fk_games_home_team
FOREIGN KEY (team_id_home) REFERENCES teams_clean(team_id);

ALTER TABLE games_clean
ADD CONSTRAINT fk_games_away_team
FOREIGN KEY (team_id_away) REFERENCES teams_clean(team_id);

ALTER TABLE team_game_stats_clean
ADD CONSTRAINT fk_stats_game
FOREIGN KEY (game_id) REFERENCES games_clean(game_id);

ALTER TABLE team_game_stats_clean
ADD CONSTRAINT fk_stats_team
FOREIGN KEY (team_id) REFERENCES teams_clean(team_id);

#adding a fav playor table so users can demonstrate CRUD
CREATE TABLE favorite_players (
    favorite_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    notes TEXT,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players_clean(player_id)
);

#trying queries
SELECT team_name, AVG(pts) AS avg_points
FROM team_game_stats_clean
GROUP BY team_name
ORDER BY avg_points DESC;

SELECT is_home, AVG(pts) AS avg_points
FROM team_game_stats_clean
GROUP BY is_home;

# creating view 
CREATE VIEW v_game_results AS
SELECT
    g.game_id,
    g.game_date,
    t1.team_name AS home_team,
    t2.team_name AS away_team,
    g.pts_home,
    g.pts_away
FROM games_clean g
JOIN teams_clean t1 ON g.team_id_home = t1.team_id
JOIN teams_clean t2 ON g.team_id_away = t2.team_id;