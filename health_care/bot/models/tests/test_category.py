from sqlalchemy.orm import sessionmaker

from health_care.database.databasemanager import DatabaseManager
from health_care.bot.models import Category, CategoryEnum, Service
from health_care.config import BotConfig


class TestCategory:

    def test_category(self):
        with DatabaseManager(url=BotConfig.database_test_url) as dbmanager:
            dbmanager.drop_schema()
            dbmanager.setup_schema()
            engine = dbmanager.engine

        Session = sessionmaker(bind=engine)
        session = Session()
        service = Service(
            description='درخواست و بررسی وضعیت مادر و جنین'
        )
        pregnant = Category(
            category_type=CategoryEnum.PREGNANT,
            description='گروه سنی ۱ روز تا ۲ ماه',
            services=[service]

        )
        session.add(pregnant)
        session.commit()
        assert 1 == 1
