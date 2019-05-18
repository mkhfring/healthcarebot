import argparse

from ..bot.admin_bot import updater
from ..bot.models.base_data import create_base_data


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "starter",
        help="Starting the bot"
    )
    args = parser.parse_args()
    if args.starter == 'start':
        updater.run()

    if args.starter == 'db':
        try:
            create_base_data()
        except Exception as e:
            print('Dublicate')

