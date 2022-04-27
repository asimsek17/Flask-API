import pytest
import requests
import requests
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from app import Teams, db, Tactics

api_url = 'http://127.0.0.1:5000'
teams_url = f'{api_url}/teams'
teams = ['liverpool FC', 'Manchester City', 'Manchester United']


@pytest.fixture
def client():

    engine = db.get_engine()
    meta = MetaData()
    meta.drop_all(engine)
    meta.create_all(engine)

    yield


def test_get_all_teams(client):
    r = requests.get(teams_url)
    assert r.status_code == 200
    all_teams = []
    teams = Teams.query.with_entities(Teams.id, Teams.team_name).all()
    all_teams = [dict(t) for t in teams]
    print(all_teams)
    assert r.json()['Teams'] == all_teams


def test_get_one_team(client):
    for i in teams:
        r = requests.get("{}/{}".format(teams_url, i))
        assert r.status_code == 200
