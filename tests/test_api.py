import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
import sqlalchemy
from stealth.app.main import app, init_app
from ..db.engine import get_db
from ..db.models import Channel, Message, User, UserRole, Role, Guild
from sqlalchemy.pool import StaticPool
from ..db.base import Base

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Override for the dependency that provides DB sessions
def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

test_config = {
    'dependency_overrides': {
        get_db: get_test_db
    }
}

init_app(app)
client = TestClient(app)
Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = get_test_db

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
    
def test_database_tables_created():
    meta = MetaData()
    meta.reflect(bind=engine)
    actual_tables = set(meta.tables.keys())
    expected_tables = {"channels", "guilds", "messages", "roles", "users", "user_roles"}
    missing_tables = set(expected_tables) - actual_tables
    assert not missing_tables, f"Missing tables: {missing_tables}"
    assert "messages" in actual_tables

def test_users_table_schema():
    meta = MetaData()
    meta.reflect(bind=engine)
    users_table = meta.tables['users']
    expected_columns = {'user_id', 'name'}
    actual_columns = set(users_table.columns.keys())
    missing_columns = expected_columns - actual_columns
    assert not missing_columns, f"Missing columns in users table: {missing_columns}"

def test_search_by_keyword():
    meta = MetaData()
    meta.reflect(bind=engine)
    messages_table = meta.tables['messages']
    assert messages_table is not None
    
    test_db = next(get_test_db())
    test_db.add_all([
        Message(message_id="1234356924875538492", content="How can I learn image prompting?"),
        Message(message_id="1234368546692403280", content="Use the /imagine command to create images by setting permissions for DMs to On in your Discord settings.\nThen DM the @Midjourney Bot <--right-click and click Message.\n    • Getting Started  <https://docs.midjourney.com/docs/quick-start>\n    • Direct Messages <https://docs.midjourney.com/docs/direct-messages>\n** Or you can set up a Discord server and invite the Bot so you can set up channels like folders to organize your images.**"),
    ])
    test_db.commit()
    test_db.close()
    
    keyword = "image"
    response = client.get(f"/keyword/{keyword}")
    
    data = response.json()
    assert response.status_code == 200
    assert "How can I learn image prompting?" in response.content
    assert isinstance(data, list)
    if data:
        assert isinstance(data[0], dict)

def test_search_by_invalid_keyword():
    keyword = "orangutbabanaan"
    response = client.get(f"/keyword/{keyword}")
    response_data = response.json()
    assert response_data == []

def test_search_by_date():
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    response = client.get(f"/date/{start_date}/{end_date}")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    if response_data:
        assert isinstance(response_data[0], dict)

def test_search_date_no_data_within_future_dates():
    start_date = "2024-05-01"
    end_date = "2024-12-31"
    response = client.get(f"/date/{start_date}/{end_date}")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0
    
def test_search_no_data_within_dates():
    start_date = "2024-01-01"
    end_date = "2024-01-10"
    response = client.get(f"/date/{start_date}/{end_date}")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0

def test_export_channel_invalid_channel():
    channel = "000000000000000000"
    token = "Njg2OTgzODExNTU2MzExMDc4.GY6jVB.H_AYAHHi5Iua1EG0oFBx7gl87RKnOOa6WHY0Cc"
    response = client.post(f"/export-channel/{channel}", headers={"user-token": token})
    assert response.status_code == 500

def test_export_channel_invalid_token():
    channel = "938713143759216720"
    token = "00000000invalidToken000000000"
    response = client.post(f"/export-channel/{channel}", headers={"user-token": token})
    assert response.status_code == 500

def test_export_channel_success():
    channel = "938713143759216720"
    token = "Njg2OTgzODExNTU2MzExMDc4.GY6jVB.H_AYAHHi5Iua1EG0oFBx7gl87RKnOOa6WHY0Cc"
    response = client.post(f"/export-channel/{channel}", headers={"user-token": token})
    assert response.status_code == 200