from sqlalchemy.orm import sessionmaker

from health_care.bot.models import Category, CategoryEnum
from health_care.database.databasemanager import DatabaseManager


def create_base_data():

    with DatabaseManager() as dbmanager:
        dbmanager.setup_schema()
        engine = dbmanager.engine

    Session = sessionmaker(bind=engine)
    session = Session()
    new_born = Category(
        category_type=CategoryEnum.NEWBORN,
        description='گروه سنی ۱ روز تا ۲ ماه',

    )
    session.merge(new_born)
    elder = Category(
        category_type=CategoryEnum.ELDER,
        description='گروه سنی ۶۰ به بالا',
    )

    session.merge(elder)
    teen = Category(
        category_type=CategoryEnum.TEENAGER,
        description='گروه سنی ۶ تا ۱۸ سال'
    )
    session.merge(teen)
    middle_age = Category(
        category_type=CategoryEnum.MIDDLE_AGE,
        description='گروه سنی ۳۰ تا ۵۹ سال'
    )
    session.merge(middle_age)
    pregnant = Category(
        category_type=CategoryEnum.PREGNANT,
        description='مادران باردار'
    )
    session.merge(pregnant)
    pre_partuation = Category(
        category_type=CategoryEnum.PRE_PARTUATION,
        description='مراقبت پیش از بارداری'
    )
    session.merge(pre_partuation)
    lactating = Category(
        category_type=CategoryEnum.LACTATING,
        description='مادران شیرده'
    )
    session.merge(lactating)
    kid = Category(
        category_type=CategoryEnum.KID,
        description='کودکان دو ماه تا ۶ سال'
    )
    session.merge(kid)
    youth = Category(
        category_type=CategoryEnum.YOUTH,
        description='گروه سنی ۱۸ تا ۲۹ سال'
    )
    session.merge(youth)

    session.commit()
