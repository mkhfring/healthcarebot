import argparse

from  sqlalchemy import create_engine

from ..bot.admin_bot import updater
from vip_admin.config import BotConfig


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "starter",
        help="Starting the bot"
    )
    args = parser.parse_args()
    if args.starter == 'start':
        updater.run()



