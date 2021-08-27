import json
import sqlite3
from sqlite3 import Error


def read_json(file_path):
    with open(file_path, "r", encoding="utf8") as f:
        return json.load(f)


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


config = read_json("config.json")
db = create_connection(config["DATABASE"]["FILE"])

sql_create_options_table = """ CREATE TABLE IF NOT EXISTS options (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        value text
                                    ); """
sql_create_emotes_table = """CREATE TABLE IF NOT EXISTS emotes (
                                id integer PRIMARY KEY,
                                discord_id integer NOT NULL,
                                name text NOT NULL,
                                count integer
                            );"""
sql_create_groups_table = """CREATE TABLE IF NOT EXISTS groups (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                active integer DEFAULT 1
                            );"""
sql_create_group_members_table = """CREATE TABLE IF NOT EXISTS group_members (
                                id integer PRIMARY KEY,
                                group_id integer NOT NULL,
                                discord_id integer NOT NULL,
                                name text NOT NULL,
                                FOREIGN KEY (group_id) REFERENCES groups (id)
                            );"""

create_table(db, sql_create_options_table)
create_table(db, sql_create_emotes_table)
create_table(db, sql_create_groups_table)
create_table(db, sql_create_group_members_table)
