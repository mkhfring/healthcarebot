import os
import sys
from datetime import datetime
from collections import OrderedDict

import pandas as pd

from vip_admin.utils import logger


DATA_INDEX = 0
TRANSLATION_INDEX = 1


class ResultWriter:

    def __init__(self, exel_file_path):
        self.path = exel_file_path

    @staticmethod
    def convert_score_to_float(data):
        for key, value in data.items():
            if key == 'SCORE':
                data[key] = float(value)

        return data

    def _create_data_frame(self, data_tuple):
        result = OrderedDict()
        for data in data_tuple[DATA_INDEX]:
            data = self.convert_score_to_float(data)
            for key, value in data.items():
                result.setdefault(key, []).append(value) if len(data_tuple) == 1 \
                    else result.setdefault(
                    data_tuple[TRANSLATION_INDEX][key], []
                ).append(value)

        return result

    def write_to_excel(self, data_list, sheet_name_list):
        data_frame_list = []
        if os.path.exists(self.path):
            os.remove(self.path)

        if len(data_list) != len(sheet_name_list):
            logger.error(
                'Data tuple and sheet list are not equal',
                extra={
                    'step': sys._getframe().f_code.co_name,
                    'time': datetime.now()
                }
            )
            raise RuntimeError('Data tuple and sheet list are not equal')

        for data_tuple in data_list:
            data_frame_list.append(self._create_data_frame(data_tuple))

        writer = pd.ExcelWriter(self.path)
        for index, data in enumerate(data_frame_list):
            try:
                pandas_dataframe = pd.DataFrame(OrderedDict(data))
            except ValueError as e:
                logger.error(
                    'Data Is Malform',
                    extra={
                        'step':sys._getframe().f_code.co_name,
                        'time': datetime.now()
                    }
                )
                raise RuntimeError('Data Is Malform')
            pandas_dataframe.to_excel(writer, sheet_name_list[index])

        writer.save()

