import functools
import os
import sys

from balebot.handlers import MessageHandler
from balebot.filters import TemplateResponseFilter, TextFilter
from balebot.models.messages import TemplateMessage, TemplateMessageButton,\
    TextMessage
import khayyam

from vip_admin.utils.mimetype import MimeType
from vip_admin.utils.result_writer import ResultWriter
from .root_controller import RootController
from ..constants import ButtonMessage, ConstantMessage, FieldTranslation
from vip_admin.database.dbhandler import DB2Handler
from vip_admin.config import BotConfig
from vip_admin.database.create_report_data import DatabaseReporter
from vip_admin import MAIN_DIRECTORY


RESULT_PATH = os.path.join(MAIN_DIRECTORY, 'data')


class OfficerScoreController(RootController):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.handlers = [
            MessageHandler(
                TemplateResponseFilter(ButtonMessage.officer_score_message),
                self.officer_score_initial_state
            )
        ]

    def __call__(self, *args, **kwargs):
        super().__call__()

    def officer_score_initial_state(self, bot, update):
        self.handlers.extend(self.dispatcher.message_handlers)
        user = update.get_effective_user()
        message = TemplateMessage(
            TextMessage(ConstantMessage.report_begin_date_message),
            [
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
                    keywords=[ButtonMessage.main_menu_message]
                ),
                self.show_menu
            ),
        ])
        self.dispatcher.register_conversation_next_step_handler(
            update,
            self.handlers +
            [
                MessageHandler(
                    TextFilter(),
                    self.handle_report_begin_date
                )
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

        self.dispatcher.clear_conversation_data(update=update)
        handler = DB2Handler(
            host=BotConfig.db_hostname,
            port=BotConfig.db_port,
            database=BotConfig.db_name,
            username=BotConfig.db_username,
            password=BotConfig.db_password
        )
        reporter = DatabaseReporter(handler, start_time_delta, end_time_delta)
        officer_score = reporter.create_officer_score_data()
        collaborator_score = reporter.create_collaborator_score_data()
        supervisor_score = reporter.create_supervisor_score_data()

        final_result_path = os.path.join(
            RESULT_PATH,
            '{}-report.xlsx'.format(user.peer_id)
        )
        result_writer = ResultWriter(final_result_path)
        result_writer.write_to_excel(
            [
                (
                    officer_score,
                    FieldTranslation.OFFICER_SCORE_TRANSLATION
                ),
                (
                    collaborator_score,
                    FieldTranslation.OFFICER_SCORE_TRANSLATION
                ),
                (
                    supervisor_score,
                    FieldTranslation.OFFICER_SCORE_TRANSLATION
                ),
            ],
            ['officers', 'collaborators', 'supervisors']
        )

        bot.send_document(
            user,
            doc_file=final_result_path,
            mime_type=MimeType.xlsx,
            file_type='file',
            name=str(jalali.year) + '-' + str(jalali.month) + \
                 '-' + str(jalali.day) + '-OFFICER-SCORE-Report.xlsx',
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
                TemplateResponseFilter(ButtonMessage.officer_score_message)
                , self.officer_score_initial_state
            )
        )
