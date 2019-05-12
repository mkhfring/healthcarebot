import asyncio

from balebot.updater import Updater

from .config import BotConfig
from vip_admin.bot.controllers import RootController, OfficerScoreController, \
    ServiceScoreController, WeakScoreController, CustomerController, \
    OfficerSearchController


loop = asyncio.get_event_loop()
updater = Updater(token=BotConfig.token, loop=loop)
dispatcher = updater.dispatcher
RootController(dispatcher)()

if __name__ == '__main__':
    updater.run()

