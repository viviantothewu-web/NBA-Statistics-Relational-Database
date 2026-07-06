CREATE DATABASE nba_database;

#import all csv with import wizard (all cleaned csv files in "cleaned_csv" folder
SHOW TABLES;

#add 1 more table favortie_player so users can demonstrate CRUD
CREATE TABLE IF NOT EXISTS favorite_player(
	favorite_player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL, #link to player
    notes TEXT, 
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;
#eer diagram 1 (revered engineer to inspect eer diagram)

#add primary keys
ALTER TABLE games
ADD PRIMARY KEY (game_id);

ALTER TABLE players
ADD PRIMARY KEY (player_id);

# team stats doesnt have a primary key, adding an auto incre id
ALTER TABLE team_game_stats
ADD COLUMN stat_id INT AUTO_INCREMENT PRIMARY KEY;

ALTER TABLE teams
ADD PRIMARY KEY (team_id);

#realized my csv did not import somehow for team_game_stats and games, reimporting and checking
SELECT * FROM team_game_stats;
SELECT * FROM teams;
#eer diagram 2 (check diagram again)

# add foreign keys
ALTER TABLE favorite_player
ADD CONSTRAINT fk_fav_player_players
FOREIGN KEY (player_id)
REFERENCES players(player_id);


ALTER TABLE team_game_stats
ADD CONSTRAINT fk_team_game_stats_games
FOREIGN KEY (game_id)
REFERENCES games(game_id);
#eer diagram 3 

#does not work, showing error code 1452
ALTER TABLE team_game_stats
ADD CONSTRAINT fk_team_game_stats_teams
FOREIGN KEY (team_id)
REFERENCES teams(team_id);
#the number of teams(team_id) and game_stats(team id) does not match. game_stats has historical teams as well, teams(team_id) only has 30 teams)

SELECT COUNT(team_id)
FROM teams;

SELECT COUNT(team_id_home) + COUNT(team_id_away) AS total_num_team
FROM games;

#need to insert historical team to teams (from games)
#dropping teams table, reinserting csv with historical team info

DROP TABLE teams;

#inserting new fixed_teams.csv
SELECT *
FROM teams;

#add primary key again
ALTER TABLE teams
ADD PRIMARY KEY (team_id);

#add foreign key again
ALTER TABLE team_game_stats
ADD CONSTRAINT fk_team_game_stats_teams
FOREIGN KEY (team_id)
REFERENCES teams(team_id);
#eer diagram 4

#looked at eer diagram, connecting games and teams
ALTER TABLE games
ADD CONSTRAINT fk_games_teams
FOREIGN KEY (team_id_home)
REFERENCES teams(team_id);

ALTER TABLE GAMES
ADD CONSTRAINT fk_games_teams_away
FOREIGN KEY (team_id_away)
REFERENCES teams(team_id);
#eer diagram 5

SELECT *
FROM team_game_stats;

#realized i've lost the team location info on the way, need to go back and add it to the teams table. 
#importing csv with location info and merging
SELECT * FROM teams_location_info;
DESCRIBE teams_location_info;
DESCRIBE teams;

ALTER TABLE teams
ADD COLUMN nickname VARCHAR(50),
ADD COLUMN city VARCHAR(50),
ADD COLUMN state VARCHAR(50),
ADD COLUMN year_founded INT;

UPDATE teams AS t
JOIN teams_location_info AS tl
ON t.team_id = tl.team_id
SET
    t.nickname = tl.nickname,
    t.city = tl.city,
    t.state = tl.state,
    t.year_founded = tl.year_founded;
#eer 6
SELECT * FROM teams;
#queries for streamlit

#filter for the states (need a state drop down, searching for unique states)
SELECT DISTINCT state
FROM teams
WHERE state IS NOT NULL;

#query for main teams table
#1. show all team who has info on city, nickname, state, and year_founded (current teams)
SELECT *
FROM teams
WHERE nickname IS NOT NULL
  AND city IS NOT NULL
  AND state IS NOT NULL
  AND year_founded IS NOT NULL;
  
#2. show all teams that dont have state info (historic teams)
SELECT *
FROM teams
WHERE STATE IS NULL;

# get distinct states from teams for user to search (for current page)
SELECT DISTINCT state
FROM teams
WHERE state IS NOT NULL
ORDER BY state;

# display current team and return user search (for current page)
SELECT *
FROM teams
WHERE nickname IS NOT NULL
AND city IS NOT NULL
AND state IS NOT NULL
AND year_founded IS NOT NULL
AND team_name LIKE '%Lake%'
AND state = 'California';

#game states for selected team (current page)
SELECT COUNT(*) AS number_games_played, 
	ROUND(AVG(pts),2) AS average_points, 
	ROUND(AVG(reb),2) AS average_rebounds, 
	ROUND(AVG(ast),2) AS average_assists
FROM team_game_stats
WHERE team_name LIKE '%lake%'
GROUP BY team_name;

SELECT *
FROM team_game_stats;

#query for search bar (for historical team page)
SELECT *
FROM teams
WHERE state IS NULL
AND team_name LIKE '%husk%';

#team statistics (for historical team page)
SELECT COUNT(*) AS number_games_played,
ROUND(AVG(pts), 2) AS average_points,
ROUND(AVG(reb), 2) AS average_rebounds,
ROUND(AVG(ast), 2) AS average_assists
FROM team_game_stats
WHERE team_name = '%husk%'
GROUP BY team_name;

#query to get distinct season type (for games page)
SELECT DISTINCT season_type
FROM games
ORDER BY season_type;

#query to return team search, display game table (for games page)
SELECT game_date, season_type, team_name_home, team_name_away, pts_home, pts_away, wl_home, wl_away
FROM games 
WHERE season_type LIKE '%pre%'
AND (team_name_home LIKE '%kni%' OR team_name_away LIKE '%sun%')
ORDER BY game_date DESC;

SELECT *
from team_game_stats;

#query to return the season drop down (for analytics page)
SELECT season_type
FROM team_game_stats
ORDER BY season_type;

#top teama by average points (for analytics page)
SELECT team_name, COUNT(*) AS games_played, AVG(pts) AS average_points
FROM team_game_stats
GROUP BY team_name
ORDER BY average_points DESC;

#home team vs away team average (for analytics pag)
SELECT is_home, AVG(pts) AS average_points, AVG(reb) AS average_rebounds, AVG(ast) AS average_assits
FROM team_game_stats
GROUP BY is_home;

#highest scoring games (for analytics page)
SELECT game_date, team_name_home, team_name_away, pts_home, pts_away, pts_home + pts_away AS total_points
FROM games
ORDER BY total_points DESC
LIMIT 20;


#for players dropdown (favorite player page)
SELECT player_id, player_name
FROM players
ORDER BY player_name;

#query for the saved favorites (fav player page)
SELECT favorite_player_id, p.player_name, notes, date_added
FROM favorite_player AS fp
JOIN players AS p
ON fp.player_id = p.player_id
ORDER BY date_added DESC;

#add favorite player (fav player page)
SELECT player_id, player_name
FROM players
WHERE player_name = 'Stephen Curry';
INSERT INTO favorite_player (player_id, notes)
VALUES(201939, "great 3 point shooter");

SELECT *
FROM favorite_player;

#update fav player
UPDATE favorite_player
SET notes = 'in warriors, great 3 point shooter, all star'
WHERE favorite_player_id = 201939;

#Delete fav player
DELETE FROM favorite_player
WHERE favorite_player_id = 201939;



    