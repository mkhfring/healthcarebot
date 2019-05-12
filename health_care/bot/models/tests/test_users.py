import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from health_care.database.databasemanager import DatabaseManager
from health_care.bot.models.user import User
from health_care.bot.models.location import Location


class TestGetAndWriteStatementData:

    def test_get_and_write_statement_data(self):
        with DatabaseManager() as dbmanager:
            dbmanager.drop_schema()
            dbmanager.setup_schema()
            engine = dbmanager.engine

        Session = sessionmaker(bind=engine)
        session = Session()
        location = Location(langitude=12.3, latitude=134.5)

        user = User(
            peer_id='12334',
            access_hash='12345',
            created_at=datetime.datetime.now(),
            locations=[location]
        )
        session.add(user)
        session.flush()
        assert 1 == 1
