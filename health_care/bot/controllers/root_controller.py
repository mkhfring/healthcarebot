import re
import sys
from datetime import datetime

from balebot.models.messages import TemplateMessageButton, TextMessage, \
    TemplateMessage
from balebot.handlers import CommandHandler
from balebot.handlers import MessageHandler
from balebot.filters import TextFilter, TemplateResponseFilter
from balebot.utils.util_functions import arabic_to_eng_number
import khayyam

from vip_admin.config import BotConfig
from vip_admin.utils import logger
from ..constants import RegexPattern, ConstantMessage, ButtonMessage

supported_users = BotConfig.supported_users


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

    def create_and_send_final_report(self, update, bot):
        raise NotImplementedError

    def send_message(self, bot, update, message, user,  step):
        kwargs = {
            'update': update,
            'user_id': user.peer_id,
            'step': step
        }

        bot.send_message(
            message,
            user,
            success_callback=self.success_sending_message,
            failure_callback=self.failure_send_message,
            **kwargs
        )

    def get_interval_begin_and_end(self, update):
        begin = self.dispatcher.get_conversation_data(
            update=update,
            key='start_time_delta'
        )
        end = self.dispatcher.get_conversation_data(
            update=update,
            key='end_time_delta'
        )
        return begin, end

    @staticmethod
    def get_time_delta(row_date):
        year = row_date.group(1)
        year = '13' + year if year[0] == '9' else '14' + year
        month = row_date.group(2)[0:2]
        day = row_date.group(2)[2:4]
        now = khayyam.JalaliDatetime.now()
        requested_day = khayyam.JalaliDate(year, month, day)
        time_delta = now - requested_day
        return time_delta.days

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
        message = TemplateMessage(
            TextMessage(ConstantMessage.menu_message),
            [
                TemplateMessageButton(ButtonMessage.service_report_message),
                TemplateMessageButton(ButtonMessage.officer_score_message),
                TemplateMessageButton(ButtonMessage.weak_score_report_message),
                TemplateMessageButton(ButtonMessage.customer_search_message),
                TemplateMessageButton(ButtonMessage.officer_search_message),
            ]
        )
        kwargs = {
            'update': update,
            'user_id': user_peer.peer_id,
            'step': sys._getframe().f_code.co_name
        }
        if user_peer.peer_id in supported_users:
            bot.send_message(
                message,
                user_peer, success_callback=self.success_sending_message,
                failure_callback=self.failure_send_message,
                **kwargs
            )
        else:
            bot.send_message(
                TextMessage(ConstantMessage.not_registered_message),
                user_peer,
                success_callback=self.success_sending_message,
                failure_callback=self.failure_send_message,
                **kwargs
            )

    def handle_report_begin_date(self, bot, update):
        user = update.get_effective_user()
        message = arabic_to_eng_number(update.get_effective_message().text)
        if re.match(RegexPattern.interval_pattern, message):
            split_message = message.split('-')
            self.dispatcher.set_conversation_data(
                update=update,
                key='start_time_delta',
                value=split_message[0]
            )
            self.dispatcher.set_conversation_data(
                update=update,
                key='end_time_delta',
                value=split_message[1]
            )
            self.create_and_send_final_report(update, bot)

        else:
            row_date = re.match(RegexPattern.jalali_input_pattern, message)
            if row_date:
                message = TemplateMessage(
                    TextMessage(ConstantMessage.service_report_end_date),
                    [TemplateMessageButton(ButtonMessage.main_menu_message)]
                )
                self.dispatcher.set_conversation_data(
                    update=update,
                    key='begin_date',
                    value=row_date
                )
                self.send_message(
                    bot,
                    update,
                    message,
                    user,
                    sys._getframe().f_code.co_name
                )
                self.dispatcher.register_conversation_next_step_handler(
                    update,
                    self.handlers +
                    [
                        MessageHandler(
                            TextFilter(),
                            self.handle_report_end_date
                        ),
                    ]
                )

            else:
                message = TextMessage(ConstantMessage.bad_format)
                self.send_message(
                    bot,
                    update,
                    message,
                    user,
                    sys._getframe().f_code.co_name
                )

    def handle_report_end_date(self, bot, update):
        user = update.get_effective_user()
        message = arabic_to_eng_number(update.get_effective_message().text)
        row_date = re.match(RegexPattern.jalali_input_pattern, message)
        if row_date:
            self.dispatcher.set_conversation_data(
                update=update,
                key='end_date',
                value=row_date
            )
            self.create_and_send_final_report(update, bot)

        else:
            message = TextMessage(ConstantMessage.bad_format)
            self.send_message(
                bot,
                update,
                message,
                user,
                sys._getframe().f_code.co_name
            )
