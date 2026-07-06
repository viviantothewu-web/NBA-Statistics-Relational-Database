🗄️ Database Setup & Replication
Due to GitHub's file size limitations, the raw 2.1 GB Play-by-Play dataset and generated 2.2 GB SQLite database are kept locally.
To replicate this database structure:

Download the historical data from https://www.kaggle.com/datasets/wyattowalsh/basketball/data

Run the clean_teams.ipynb notebook to process the raw datasets.

Execute untitled.py to initialize the local SQLite schemas and populate the tables.
