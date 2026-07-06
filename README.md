# 🏀 NBA Statistics Database Dashboard

An interactive NBA analytics dashboard built with **Python, MySQL, and Streamlit**. This project demonstrates relational database design, normalization, SQL querying, CRUD operations, and data visualization using over 75 years of publicly available NBA historical data.

---

## Features

- Browse current NBA teams
- Browse historical NBA franchises
- Search and filter games by team and season type
- Explore interactive analytics and visualizations
- Create, update, and delete a personal player watchlist (CRUD)
- Built on a normalized relational database with primary and foreign key relationships

---

## Technology Stack

- Python
- Streamlit
- MySQL
- MySQL Workbench
- Pandas
- Plotly

---

## Database Schema

The database consists of five primary entities:

- Teams
- Players
- Games
- Team Game Statistics
- Favorite Player

The schema follows relational database normalization principles and uses primary and foreign keys to maintain referential integrity.

---

## Data Source

This project uses the public NBA historical dataset provided by Wyatt Walsh on Kaggle.

Dataset:
https://www.kaggle.com/datasets/wyattowalsh/basketball

---

## Repository Note

GitHub's file size limitations prevent uploading the complete NBA dataset and generated database files.

The original dataset contains:

- Large CSV files
- SQLite database
- Play-by-play data (>2 GB)

These files are **not included** in this repository.

🗄️ Database Setup & Replication Due to GitHub's file size limitations

To replicate this database structure: Download the historical data from https://www.kaggle.com/datasets/wyattowalsh/basketball/data 

Run the clean_teams.ipynb notebook to process the raw datasets. 
Execute sql query file and app.py to launch streamlit.

---

## Reproducing the Database

### 1. Download the dataset

Download the Kaggle dataset:

https://www.kaggle.com/datasets/wyattowalsh/basketball

---

### 2. Clean the data

Run "kaggle_data_cleaning.ipynb" to:

- Standardize column names
- Remove duplicate records
- Convert data types
- Generate cleaned CSV files
- Normalize the game statistics table

---

### 3. Import into MySQL

Import the generated CSV files into MySQL:

- teams.csv
- players.csv
- games.csv
- team_game_stats.csv

Then:

- Create primary keys
- Create foreign keys
- Generate the EER diagram
(all included in nba_database_query.sql)

---

### 4. Run the application

Run the application:

```bash
streamlit run app.py
```

---

## Project Structure

```
.
├── app.py
├── clean_teams.ipynb
├── cleaned_csv/
├── README.md
├── requirements.txt
└── report/
```

---

## Learning Objectives

This project demonstrates:

- Relational database design
- Database normalization
- Primary and foreign key implementation
- SQL querying
- CRUD operations
- Interactive dashboard development
- Data cleaning and preprocessing

---

## Author

Vivian Wu

Applied Database Final Project

Indiana University
