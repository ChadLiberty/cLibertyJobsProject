import pytest
import main
import sqlite3

@pytest.fixture
def get_data():
    import main
    return main.get_github_jobs_data()

def test_jobs_dict(get_data):
    # first required test
    assert len(get_data) >=100
    assert type(get_data[1]) is dict

def test_jobs_data(get_data):
    # any real data should have both full time and Contract
    # jobs in the list, assert this
    data = get_data
    full_time_found = False
    contract_found = False
    for item in data:
        if item['type'] == 'Contract':
            contract_found = True
        elif item['type'] == 'Full Time':
            full_time_found = True
    assert  contract_found and full_time_found

def test_save_data():                               #changed to see if data is in database
    demo_data = {'id': 1234, 'type': "Testable"}
    list_data = []
    list_data.append(demo_data)
    main.make_jobs_table()
    #the save puts a newline at the end
    assert f"{str(demo_data)}\n" in main.make_jobs_table()

def table_exists():
    test_table =  f'''SELECT id, type, url, created_at, company, company_url, location, title, description
    FROM JOBS'''

def db_method_works():
    demo_data = {'id': 1234, 'type': "Testable"}
    #send to data table