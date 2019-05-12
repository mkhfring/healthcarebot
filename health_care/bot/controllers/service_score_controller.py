import sys
import os
import re
import functools

from balebot.handlers import MessageHandler
from balebot.models.messages import TemplateMessage, TextMessage,\
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


class ServiceScoreController(RootController):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.handlers = [
            MessageHandler(
                TemplateResponseFilter(ButtonMessage.service_report_message),
                self.initiate_create_report
            )
        ]

    def __call__(self, *args, **kwargs):
        super().__call__()

    def initiate_create_report(self, bot, update):
        self.handlers.extend(self.dispatcher.message_handlers)
        user = update.get_effective_user()
        message = TemplateMessage(
            TextMessage(ConstantMessage.branch_selection_message),
            [
                TemplateMessageButton(ButtonMessage.all_branches),
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
                    keywords=[ButtonMessage.all_branches]
                ),
                self.handle_branch_code_input
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
                        self.handle_branch_code_input
                    )
                ]
        )

    def handle_branch_code_input(self, bot, update):
        user = update.get_effective_user()
        message = arabic_to_eng_number(update.get_effective_message().text)
        if not re.match(RegexPattern.branch_code_pattern, message) \
                and not message == ButtonMessage.all_branches:
            message = TextMessage(ConstantMessage.bad_format)
            self.send_message(
                bot,
                update,
                message,
                user,
                sys._getframe().f_code.co_name
            )
            return

        if message != ButtonMessage.all_branches:
            self.dispatcher.set_conversation_data(
                update=update,
                key='branch_code',
                value=message.zfill(4)
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
                    MessageHandler(
                        TextFilter(),
                        self.handle_report_begin_date
                    ),
                ]
            )

        else:
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
        jalali = khayyam.JalaliDatetime.now()
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
        branch_code = self.dispatcher.get_conversation_data(
                update=update,
                key='branch_code'
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

        if branch_code:
            single_branch_score = reporter.create_branch_score_data(
                branch_code=branch_code
            )
            final_result_path = os.path.join(
                RESULT_PATH,
                '{}-report.xlsx'.format(user.peer_id)
            )
            single_branch_writer = ResultWriter(final_result_path)
            single_branch_writer.write_to_excel(
                [
                    (
                        single_branch_score,
                        FieldTranslation.BRANCH_SCORE_TRANSLATION
                    )
                ],
                ['branches']
            )

            bot.send_document(
                user,
                doc_file=final_result_path,
                mime_type=MimeType.xlsx,
                file_type='file',
                name=str(jalali.year) + '-' + str(jalali.month) + \
                    '-' + str(jalali.day) + '-Report.xlsx',
                caption_text='report',
                success_callback=functools.partial(
                    self.show_menu,
                    bot,
                    update,
                ),
                failure_callback=self.failure_send_message,
                **kwargs
            )

        else:
            total_branch_score = reporter.create_branch_score_data()
            service_score = reporter.create_service_score_data()
            branch_request = reporter.create_branch_request_data()
            final_result_path = os.path.join(
                RESULT_PATH,
                '{}-report.xlsx'.format(user.peer_id)
            )
            result_writer = ResultWriter(final_result_path)
            result_writer.write_to_excel(
                [
                    (
                        service_score,
                        FieldTranslation.SERVICE_SCORE_TRANSLATION
                    ),
                    (
                        total_branch_score,
                        FieldTranslation.BRANCH_SCORE_TRANSLATION
                    ),
                    (
                        branch_request,
                        FieldTranslation.BRANCH_REQUEST_TRANSLATIOM
                    ),
                ],
                ['main', 'branches', 'request_count']
            )

            bot.send_document(
                user,
                doc_file=final_result_path,
                mime_type=MimeType.xlsx,
                file_type='file',
                name=str(jalali.year) + '-' + str(jalali.month) + \
                     '-' + str(jalali.day) + '-Report.xlsx',
                caption_text='report',
                success_callback=functools.partial(
                    self.show_menu,
                    bot,
                    update
                ),
                failure_callback=self.failure_send_message,
                **kwargs
            )
        self.dispatcher.add_handler(
            MessageHandler(
                TemplateResponseFilter(ButtonMessage.service_report_message)
                , self.initiate_create_report
            )
        )
