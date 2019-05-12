import sys
import os
import re
import functools

from balebot.handlers import MessageHandler
from balebot.models.messages import TemplateMessage, TextMessage, \
    TemplateMessageButton
from balebot.filters import TemplateResponseFilter, TextFilter
from balebot.utils.util_functions import arabic_to_eng_number
import khayyam

from vip_admin.config import BotConfig
from vip_admin import MAIN_DIRECTORY
from vip_admin.bot.constants import ConstantMessage, RegexPattern
from vip_admin.bot.constants import ButtonMessage
from vip_admin.utils.result_writer import ResultWriter
from vip_admin.database.create_report_data import DatabaseReporter
from vip_admin.utils.mimetype import MimeType
from vip_admin.database.dbhandler import DB2Handler
from ..controllers import RootController
from ..constants import FieldTranslation

supported_users = BotConfig.supported_users
RESULT_PATH = os.path.join(MAIN_DIRECTORY, 'data')


class CustomerController(RootController):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.handlers = [
            MessageHandler(
                TemplateResponseFilter(ButtonMessage.customer_search_message),
                self.initiate_search_customer
            )
        ]

    def __call__(self, *args, **kwargs):
        super().__call__()

    @staticmethod
    def check_national_code(code):
        if code.replace("0", "") == "":
            return False

        if 8 <= len(code) <= 10:
            code = '00' + code
            code = code[len(code) - 10:]

            i = 2
            k = 0
            for c in code[-2::-1]:
                k += int(c) * i
                i += 1
            remain = k % 11
            if remain < 2:
                pass
            else:
                remain = 11 - remain

            if remain == int(code[-1]):
                return True
            else:
                return False

        else:
            return False

    def initiate_search_customer(self, bot, update):
        self.handlers.extend(self.dispatcher.message_handlers)
        user = update.get_effective_user()
        message = TemplateMessage(
            TextMessage(ConstantMessage.customer_search_criterion),
            [
                TemplateMessageButton(ButtonMessage.all_officers),
                TemplateMessageButton(ButtonMessage.main_menu_message)
            ]
        )
        self.send_message(
            bot,
            update,
            message,
            user,
            sys._getframe().f_code.co_name
        )
        self.handlers.extend([
            MessageHandler(
                TemplateResponseFilter(
                    keywords=[ButtonMessage.all_officers]
                ),
                self.handle_customer_criterion_input
            ),
            MessageHandler(
                TemplateResponseFilter(
                    keywords=[ButtonMessage.main_menu_message]
                ),
                self.show_menu
            ),
        ])

        # TODO: This seems odd to me to add two lists, find a better way if possible
        self.dispatcher.register_conversation_next_step_handler(
            update,
            self.handlers +
            [
                MessageHandler(
                    TextFilter(),
                    self.handle_customer_criterion_input
                )
            ]
        )

    # TODO: change to names to be more general in order to use in office search as well
    def handle_customer_criterion_input(self, bot, update):
        user = update.get_effective_user()
        message = arabic_to_eng_number(update.get_effective_message().text)
        if message != ButtonMessage.all_officers:
            self.dispatcher.set_conversation_data(
                update=update,
                key='officer_criterion',
                value=message
            )

        message = TemplateMessage(
            TextMessage(ConstantMessage.report_begin_date_message),
            [TemplateMessageButton(ButtonMessage.main_menu_message)]
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
                MessageHandler(TextFilter(), self.handle_report_begin_date),
            ]
        )

    def create_and_send_final_report(self, update, bot):
        interval = self.get_interval_begin_and_end(update)
        jalali_date = khayyam.JalaliDatetime.now()
        user = update.get_effective_user()
        kwargs = {
            'update': update,
            'user_id': user.peer_id,
            'step': sys._getframe().f_code.co_name
        }
        start_time_delta = self.get_time_delta(
            self.dispatcher.get_conversation_data(
                update=update,
                key='begin_date'
            )
        ) if not interval[0] else int(interval[0])

        end_time_delta = self.get_time_delta(
            self.dispatcher.get_conversation_data(
                update=update,
                key='end_date'
            )
        ) if not interval[1] else int(interval[1])

        if start_time_delta < end_time_delta:
            start_time_delta, end_time_delta = end_time_delta, start_time_delta

        officer_criterion = self.dispatcher.get_conversation_data(
            update=update,
            key='officer_criterion'
        )
        self.dispatcher.clear_conversation_data(update=update)
        handler = DB2Handler(
            host=BotConfig.db_hostname,
            port=BotConfig.db_port,
            database=BotConfig.db_name,
            username=BotConfig.db_username,
            password=BotConfig.db_password
        )
        reporter = DatabaseReporter(handler, start_time_delta, end_time_delta)
        if officer_criterion:
            if re.match(
                RegexPattern.national_id_pattern,
                officer_criterion
            ) and self.check_national_code(officer_criterion):
                customer_search = reporter.create_customer_search_data(
                    social_number=officer_criterion
                )
            elif re.match(
                RegexPattern.phone_number_pattern,
                officer_criterion
            ):
                customer_search = reporter.create_customer_search_data(
                    phone_number=officer_criterion
                )
            elif re.match(
                RegexPattern.branch_code_pattern,
                officer_criterion
            ):
                customer_search = reporter.create_customer_search_data(
                    branch_code=officer_criterion
                )

            else:
                customer_search = reporter.create_customer_search_data(
                    personnel_id=officer_criterion
                )
        else:
            customer_search = reporter.create_customer_search_data()

        final_result_path = os.path.join(
            RESULT_PATH,
            '{}-report.xlsx'.format(user.peer_id)
        )
        customer_search_writer = ResultWriter(final_result_path)
        customer_search_writer.write_to_excel(
            [
                (
                    customer_search,
                    FieldTranslation.CUSTOMER_SEARCH_TRANSLATION
                )
            ],
            ['customers']
        )

        bot.send_document(
            user,
            doc_file=final_result_path,
            mime_type=MimeType.xlsx,
            file_type='file',
            name=str(jalali_date.year) + '-' + str(jalali_date.month) + \
                 '-' + str(jalali_date.day) + '-Customer-Search-Report.xlsx',
            caption_text='customer search report',
            success_callback=functools.partial(
                self.show_menu,
                bot,
                update,
            ),
            failure_callback=self.failure_send_message,
            **kwargs
        )
