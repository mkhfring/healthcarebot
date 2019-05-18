import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from health_care.database.databasemanager import DatabaseManager
from health_care.bot.models import Location, User
from health_care.config import BotConfig


class TestUser:

    def test_user(self):
        with DatabaseManager(url=BotConfig.database_test_url) as dbmanager:
            dbmanager.drop_schema()
            dbmanager.setup_schema()
            engine = dbmanager.engine

        Session = sessionmaker(bind=engine)
        session = Session()
        location = Location(langitude=12.3, latitude=134.5)

        user = User(
            peer_id='12334',
            access_hash='12345',
            locations=[location]
        )
        session.add(user)
        session.commit()
        assert 1 == 1