import re
import sys
from datetime import datetime

from balebot.models.messages import TemplateMessageButton, TextMessage, \
    TemplateMessage
from balebot.handlers import CommandHandler
from balebot.handlers import MessageHandler
from balebot.filters import TextFilter, TemplateResponseFilter

from health_care.bot.models import User, Category
from health_care.utils import logger
from ..constants import RegexPattern, ConstantMessage, ButtonMessage
from health_care.database import session



class RootController:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.handlers = [
            CommandHandler(['start', 'menu'], self.show_menu),
            MessageHandler(
                TemplateResponseFilter(ButtonMessage.main_menu_message),
                self.show_menu
            )
        ]

    def __call__(self, *args, **kwargs):
        self.handlers.extend(self.dispatcher.message_handlers)
        self.dispatcher.add_handlers(self.handlers)


    @staticmethod
    def success_sending_message(response, user_data):
        step = user_data['step'] if 'step' in user_data.keys() \
            else user_data['kwargs']['step']
        user_id = user_data['user_id'] if 'user_id' in user_data.keys() \
            else user_data['kwargs']['user_id']

        logger.info(
            'Message was sent from {} was successful'.format(step),
            extra={'user_id': user_id, 'step': step, 'time0': datetime.now()}
        )

    @staticmethod
    def failure_send_message(response, user_data):
        step = user_data['step'] if 'step' in user_data.keys() \
            else user_data['kwargs']['step']
        user_id = user_data['user_id'] if 'user_id' in user_data.keys() \
            else user_data['kwargs']['user_id']

        logger.info(
            'Message from {} was failed'.format(step),
            extra={'user_id': user_id, 'step': step, 'time0': datetime.now()}
        )

    def show_menu(self, bot, update, response=None, user_data=None):
        self.dispatcher.clear_conversation_data(update=update)

        user_peer = update.get_effective_user()
        if not User.exists(user_peer.peer_id):
            session.add(
                User(
                    peer_id=user_peer.peer_id,
                    access_hash=user_peer.access_hash
                )
            )
            session.commit()

        categories = session.query(Category).all()
        category_list = [TemplateMessageButton(category.description) for category in categories]
        message = TemplateMessage(
            TextMessage(ConstantMessage.menu_message),
            category_list
        )
        kwargs = {
            'update': update,
            'user_id': user_peer.peer_id,
            'step': sys._getframe().f_code.co_name
        }
        bot.send_message(
            message,
            user_peer, success_callback=self.success_sending_message,
            failure_callback=self.failure_send_message,
            **kwargs
        )
