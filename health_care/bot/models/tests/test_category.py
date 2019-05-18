import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from health_care.database.databasemanager import DatabaseManager
from health_care.bot.models import Category, CategoryEnum


class TestCategory:

    def test_category(self):
        with DatabaseManager() as dbmanager:
            dbmanager.drop_schema()
            dbmanager.setup_schema()
            engine = dbmanager.engine

        Session = sessionmaker(bind=engine)
        session = Session()
        new_born = Category(
            category_type=CategoryEnum.NEWBORN,
            description='گروه سنی ۱ روز تا ۲ ماه',

        )
        session.add(new_born)
        session.commit()
        assert 1 == 1
