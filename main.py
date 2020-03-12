import requests
import time
from typing import Dict, List, Tuple, Any
import sqlite3
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QCheckBox
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSize
import plotly.graph_objects as go
import pandas as pd
from geopy.geocoders import Nominatim

def get_github_jobs_data() -> List[Dict]:
    """retrieve github jobs data in form of a list of dictionaries after json processing"""
    all_data = []
    page = 1
    more_data = True
    while more_data:
        url = f"https://jobs.github.com/positions.json?page={page}"
        raw_data = requests.get(url)
        if "GitHubber!" in raw_data.text:  # sometimes if I ask for pages too quickly I get an error; only happens in testing
            continue  # trying continue, but might want break
        if not raw_data.ok:  # if we didn't get a 200 response code, don't try to decode with .json
            continue
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


def hard_code_create_table(cursor: sqlite3.Cursor):
    create_statement = f"""CREATE TABLE IF NOT EXISTS hardcode_github_jobs(
    id TEXT PRIMARY KEY,
    type TEXT,
    url TEXT,
    created_at TEXT,
    company TEXT NOT NULL,
    company_url TEXT,
    location TEXT,
    title TEXT NOT NULL,
    description TEXT,
    how_to_apply TEXT,
    company_logo TEXT
    );
        """
    cursor.execute(create_statement)


def hard_code_save_to_db(cursor: sqlite3.Cursor, all_github_jobs: List[Dict[str, Any]]):
    # in the insert statement below we need one '?' for each column, then we will use a second param with each of the values
    # when we execute it. SQLITE3 will do the data sanitization to avoid little bobby tables style problems
    insert_statement = f"""INSERT or IGNORE INTO hardcode_github_jobs(
        id, type, url, created_at, company, company_url, location, title, description, how_to_apply, company_logo)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)"""
    for job_info in all_github_jobs:
        # first turn all the values from the jobs dict into a tuple
        data_to_enter = tuple(job_info.values())
        cursor.execute(insert_statement, data_to_enter)



def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()

#GUI (pyQT5) to filter through jobs
class ExampleWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(400,200))
        self.setWindowTitle("Filter Checkbox")

        self.b = QCheckBox("Job Technology", self)
        self.b.stateChanged.connect(self.clickBox)
        self.b.move(20,20)
        self.b.resize(320,40)

        self.b = QCheckBox("Age of Job Posting", self)
        self.b.stateChanged.connect(self.clickBox)
        self.b.move(20,40)
        self.b.resize(320,40)

        self.b = QCheckBox("Company", self)
        self.b.stateChanged.connect(self.clickBox)
        self.b.move(20, 60)
        self.b.resize(320, 40)

        self.b = QCheckBox("Experience Level", self)
        self.b.stateChanged.connect(self.clickBox)
        self.b.move(20, 80)
        self.b.resize(320, 40)

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            print("Checked")
        else:
            print("Unchecked")


def main():
    jobs_table_name = 'github_jobs_table'  # might be better as a constant in global space
    db_name = 'jobdemo.sqlite'
    connection, cursor = open_db(db_name)
    data = get_github_jobs_data()
    hard_code_create_table(cursor)
    hard_code_save_to_db(cursor, data)
    #desc = make_column_description_from_json_dict(data[0])  # assumes all records have the same fields so make table from first
    #create_table(cursor, desc, jobs_table_name)
    #save_to_db(data, cursor, jobs_table_name)
    close_db(connection)

    #Geolocator using GeoPy trying to extraxt latitude and longitude from database
    geolocator = Nominatim()
    location = geolocator.geocode()
    print(location)
    print((location.latitude, location.longitude))

    #map using plotly
    df = pd.read_json('https://jobs.github.com/positions.json?page={1}')
    df['text'] = df['job id'] + '' + df['type'] + ', ' + df['url'] + '' + 'Description: ' + df['cnt'].astype(str)

    fig = go.Figure(data=go.Scattergeo(
        lon = df['long'],
        lat = df['lat'],
        text = df['text'],
        mode = 'markers',
        marker_color = df['cnt'],))

    fig.update_layout(
        title = 'Most trafficked US airports<br>(Hover for airport names)',
        geo_scope = 'usa',
    )
    fig.show()





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec_())
    main()


#############################################################################################
# #the code below represents Professor Santore's original solution. NOT MINE
#############################################################################################


def save_to_db(data: List[Dict[str, str]], cursor: sqlite3.Cursor, table_name: str):

    for job_listing in data:  # loop through each dictionary in the list, use the keys as column names and values as
        row_values = []       # values to insert in the row for that column
        for key in job_listing:
            row_values.append(job_listing[key])
        # these next three lines from stackoverflow user abarnert answering https://stackoverflow.com/questions/14108162/
        columns = ', '.join(job_listing.keys())
        placeholders = ', '.join('?' * len(job_listing))

        insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        # end code used from stack overflow
        cursor.execute(insert_statement, tuple(job_listing.values()))


def create_table(cursor: sqlite3.Cursor, description: Dict[str, str], table_name: str):
    # build a create table statement, the column names are the keys in the dictionary
    # the column type and constraints are the values in the dictionary
    statement_start = f'''CREATE TABLE IF NOT EXISTS {table_name} ('''
    column_text = ""
    for column_name in description:
        if len(column_text) > 0:
            column_text = f"{column_text},"
        column_text = f"""{column_text}
{column_name} {description[column_name]}"""
    create_statement = f"{statement_start} {column_text});"
    cursor.execute(create_statement)
    return create_statement


def make_column_description_from_json_dict(json_rep: Dict[str, Any]) -> Dict[str, str]:
    """This is a first pass at what the Pragmatic programmer talks about in the DRY section
    In this case we don't want to represent the structure of the json data we download in our
    code if we can help it, so I'm building the description of the table columns by analyzing the
    dictionary"""
    descriptor = {}  # this is our output a mapping of column names to decriptions to build our table
    for key in json_rep:
        column_constraint = ''  # start with empty constraint then find the type of the data and choose the correct SQL type
        if type(json_rep[key]) is str:
            column_constraint = 'TEXT'
        elif type(json_rep[key]) is int:
            column_constraint = 'INTEGER'
        elif type(json_rep[key]) is float:
            column_constraint = 'REAL'
        else:
            column_constraint = 'BLOB'  # Blob data type is a generic byte by byte type
        if len(descriptor) == 0:  # we will assume that the first item in the JSON dict is the primary key
            column_constraint = f"{column_constraint} PRIMARY KEY"  # WARNING! this only works in python 3.6+
        descriptor[key] = column_constraint
    return descriptor












