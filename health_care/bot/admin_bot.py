import asyncio

from balebot.updater import Updater

from health_care.config import BotConfig
from health_care.bot.controllers import RootController
from health_care.database.databasemanager import DatabaseManager
from health_care.bot.models.base_data import create_base_data


loop = asyncio.get_event_loop()
updater = Updater(token=BotConfig.token, loop=loop)
dispatcher = updater.dispatcher
RootController(dispatcher)()

if __name__ == '__main__':
    updater.run()

