import requests
import time
from typing import Dict, List
import sqlite3
from typing import Tuple

def get_github_jobs_data() -> List[Dict]:
    """retrieve github jobs data in form of a list of dictionaries after json processing"""
    all_data = []
    page = 1
    more_data = True
    while more_data:
        url = f"https://jobs.github.com/positions.json?page={page}"
        raw_data = requests.get(url)
        if "GitHubber!" in raw_data:  # sometimes if I ask for pages too quickly I get an error; only happens in testing
            continue  # trying continue, but might want break
        partial_jobs_list = raw_data.json()
        all_data.extend(partial_jobs_list)
        if len(partial_jobs_list) < 50:
            more_data = False
        time.sleep(.1)  # short sleep between requests so I dont wear out my welcome.
        page += 1
    return all_data

def save_data(data, filename='data.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            print(item, file=file)

def open_db(filename:str)->Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)
    cursor = db_connection.cursor()
    return db_connection, cursor

def close_db(connection:sqlite3.Connection):
    connection.commit()
    connection.close()

def save_to_db(data):
    """:keyword data is a list of dictionaries. Each dictionary is a JSON object with a bit of jobs data"""
    pass

def setup_db(cursor:sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs(
    job_id INTEGER PRIMARY KEY, 
    type TEXT NOT NULL, 
    url TEXT NOT NULL, 
    created_at TEXT NOT NULL, 
    company TEXT NOT NULL, 
    company_url TEXT NOT NULL, 
    location TEXT NOT NULL, 
    title TEXT NOT NULL, 
    description TEXT DEFAULT 0);''')

#def make_jobs_table(cursor:sqlite3.Cursor):
#   for x in title:     #for loop goes through data.txt
#       cursor.execute(f'''INSERT INTO JOBS(job_id, type, url, created_at, company, company_url, location, title, description)''')

def main():
    data = get_github_jobs_data()
    save_data(data)
    conn, cursor = open_db("demo_db.sqlite")
    print(type(conn))
    close_db(conn)


if __name__ == '__main__':
    main()