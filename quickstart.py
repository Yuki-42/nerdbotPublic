"""
Quickstart script for setting up the project structure, logging, and database.
"""

# Standard Imports
from pathlib import Path
from sqlite3 import connect
from os import mkdir

# Create Logs Directory
mkdir("Logs")

# Create Database
with connect("BotData/database.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""create table users
(
    id            serial                              not null
        primary key,
    username      text                                not null,
    apply_filter  boolean   default false             not null,
    messages_sent int       default 0                 not null,
    banned        bool      default false             not null,
    created_at    timestamp default current_timestamp not null
);
""")
    cursor.execute("""create table banned_gifs
(
    id         integer                             not null
        constraint banned_gifs_pk
            primary key autoincrement,
    banned_by  serial                              not null
        references users,
    url        text                                not null,
    reason     text                                not null,
    created_at timestamp default current_timestamp not null
);
""")
    cursor.execute("""create table random_reactions
(
    id       integer                             not null
        primary key autoincrement,
    reaction text                                not null,
    added_by serial                              not null
        references users,
    added_at timestamp default CURRENT_TIMESTAMP not null
);
""")
    cursor.execute("""create table reactions
(
    id         integer                             not null
        primary key autoincrement,
    reaction   text                                not null,
    added_by   serial                              not null
        references users,
    applies_to serial                              not null
        references users,
    added_on   timestamp default current_timestamp not null
);
""")
    cursor.execute("""create table whitelist
(
    id         integer                             not null
        constraint whitelist_pk
            primary key autoincrement,
    url        text                                not null,
    added_by   serial                              not null
        references users,
    created_at timestamp default current_timestamp not null
);
""")
    conn.commit()

# Create Config File
with open("BotData/config.json", "w") as file:
    file.write("""{
    "status": "with the default config",
    "statusType": "playing",
    "filterEnabled": false,
    "owonerId": [
        discord ids of the bot owners here as a list
    ],
    "gifClassifiers": [
        "https://tenor.com/view/",
        "https://media.discordapp.net/attachments/"
    ],
    "loggingLevel": "INFO"
}""")
