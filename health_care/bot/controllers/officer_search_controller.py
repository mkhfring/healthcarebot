import os
import re
import sys
import functools

import khayyam
from balebot.filters import TemplateResponseFilter, TextFilter
from balebot.handlers import MessageHandler
from balebot.models.messages import TemplateMessage, TextMessage, \
    TemplateMessageButton

from vip_admin.bot.constants import ButtonMessage, ConstantMessage, \
    RegexPattern, FieldTranslation
from vip_admin.config import BotConfig
from vip_admin.database.create_report_data import DatabaseReporter
from vip_admin.database.dbhandler import DB2Handler
from vip_admin.utils.mimetype import MimeType
from vip_admin.utils.result_writer import ResultWriter
from .customer_controller import CustomerController
from vip_admin import MAIN_DIRECTORY


RESULT_PATH = os.path.join(MAIN_DIRECTORY, 'data')


# TODO: Check if it is possible to use some common tasks like handling the branch code as mixin
class OfficerSearchController(CustomerController):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.handlers = [
            MessageHandler(
                TemplateResponseFilter(ButtonMessage.officer_search_message),
                self.initiate_search_officers
            )
        ]

    def __call__(self, *args, **kwargs):
        super().__call__()

    def initiate_search_officers(self, bot, update):
        self.handlers.extend(self.dispatcher.message_handlers)
        user = update.get_effective_user()
        message = TemplateMessage(
            TextMessage(ConstantMessage.officer_search_criterion),
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

    def create_and_send_final_report(self, update, bot):
        supervisor_search = None
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
                officer_search = reporter.create_officer_search_data(
                    social_number=officer_criterion
                )
            elif re.match(
                RegexPattern.phone_number_pattern,
                officer_criterion
            ):
                officer_search = reporter.create_officer_search_data(
                    phone_number=officer_criterion
                )
            elif re.match(
                RegexPattern.branch_code_pattern,
                officer_criterion
            ):
                officer_search = reporter.create_officer_search_data(
                    branch_code=officer_criterion
                )

            else:
                officer_search = reporter.create_officer_search_data(
                    personnel_id=officer_criterion
                )
        else:
            officer_search = reporter.create_officer_search_data()
            supervisor_search = reporter.create_supervisor_search_data()

        final_result_path = os.path.join(
            RESULT_PATH,
            '{}-report.xlsx'.format(user.peer_id)
        )
        officer_search_writer = ResultWriter(final_result_path)
        if supervisor_search:
            officer_search_writer.write_to_excel(
                [
                    (
                        officer_search,
                        FieldTranslation.OFFICER_SEARCH_TRANSLATION
                    ),
                    (
                        supervisor_search,
                        FieldTranslation.SUPERVISOR_SEARCH_TRANSLATION
                    )
                ],
                ['officers', 'supervisor']
            )

        else:

            officer_search_writer.write_to_excel(
                [
                    (
                        officer_search,
                        FieldTranslation.OFFICER_SEARCH_TRANSLATION
                    )
                ],
                ['officers']
            )

        bot.send_document(
            user,
            doc_file=final_result_path,
            mime_type=MimeType.xlsx,
            file_type='file',
            name=str(jalali_date.year) + '-' + str(jalali_date.month) + \
                 '-' + str(jalali_date.day) + '-Officer-Search-Report.xlsx',
            caption_text='officer search report',
            success_callback=functools.partial(
                self.show_menu,
                bot,
                update,
            ),
            failure_callback=self.failure_send_message,
            **kwargs
        )
