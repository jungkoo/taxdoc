#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
from tinydb import TinyDB, Query, where

_scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
_json_file_name = 'google_auth.json'
_TIMESTAMP_COLUMN_LIST = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split()
_TIMESTAMP_COLUMN_MAP = {_TIMESTAMP_COLUMN_LIST[i]: i for i in range(0, len(_TIMESTAMP_COLUMN_LIST))}


class GoogleFormSheet:
    def __init__(self, url, sheet_name="설문지 응답 시트1", auth_json_path=_json_file_name, timestamp_column_name="A"):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path, _scope)
        gc = gspread.authorize(credentials)
        self._sheet = None
        self._count = 0
        self.url = url
        self.sheet_name = sheet_name
        self._doc = gc.open_by_url(url)
        self._timestamp_column_name = timestamp_column_name
        self._timestamp_column_index = _TIMESTAMP_COLUMN_MAP[timestamp_column_name]
        self.change_worksheet(sheet_name)

    def change_worksheet(self, sheet_name):
        self.sheet_name = sheet_name
        self._sheet = self._doc.worksheet(sheet_name)
        self._count = self._sheet.row_count

    def count(self):
        return self._count

    def get_row(self, row_seq):
        return self._sheet.row_values(row_seq)

    @staticmethod
    def convert_date(date_value):
        if date_value:
            date_num = [x_ for x_ in map(int, re.findall(r'(\d+)', date_value))]
            dt = datetime(date_num[0], date_num[1], date_num[2], date_num[3], date_num[4], date_num[5])
            return dt
        else:
            return None

    def find_date(self, start_date, end_date=datetime.today(), start_seq=2):
        seq, value = self.find_date_with_seq(start_date, end_date, start_seq)
        return value

    def find_date_with_seq(self, start_date, end_date=datetime.today(), start_seq=2):
        if self._count < start_seq:
            raise Exception("row_values(sequence) : sequence over number !!!")
        seq = start_seq
        for row in self._sheet.get("{timestamp_column_name}{start_seq}:{timestamp_column_name}".format(
                **{"start_seq": start_seq, "timestamp_column_name": self._timestamp_column_name})):
            # [2018, 3, 15, 2, 5, 45]
            dt = GoogleFormSheet.convert_date(row[0])  # 0 은 고정
            if start_date <= dt <= end_date:
                yield seq, self._sheet.row_values(seq)
            seq += 1

    def find_keyword_all(self, *keywords):
        seed_set = None
        for keyword in keywords:
            cell_set = set()
            cell_set.update([x.row for x in self._sheet.findall(keyword)])
            if seed_set is None:
                seed_set = cell_set
                continue
            seed_set = seed_set & cell_set
        return [self._sheet.row_values(seq) for seq in seed_set or []]


def str_to_date(sdt):
    return datetime.strptime(sdt, "%Y-%m-%d %H:%M:%S")


def date_to_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class HistoryFormSheet:
    """
    마지막으로 읽어들인 날짜와 seq 값을 저장했다가, 그 이후부터 읽어내는 구
    """
    def __init__(self, google_form_sheet, db_path="./history.json", seed_next_seq=2, seed_date=datetime(2018, 1, 1)):
        self._next_seq = seed_next_seq
        self._date = seed_date
        self._db = TinyDB(db_path)
        self._sheet = google_form_sheet
        self._timestamp_column_index = _TIMESTAMP_COLUMN_MAP[google_form_sheet._timestamp_column_name]
        self.load_history_item()

    def init_history(self):
        self._next_seq = 2
        self._date = datetime(2018, 1, 1)

    def more(self):
        cnt = 0
        try:
            for seq, row in self._sheet.find_date_with_seq(start_date=self._date, start_seq=self._next_seq):
                self._date = GoogleFormSheet.convert_date(row[self._timestamp_column_index])
                self._next_seq = seq + 1
                cnt += 1
                yield row
        finally:
            if cnt > 0:
                self.save_history_item()
            else:
                print("# empty value !!!  (next sequence: {})".format(self._next_seq))

    def get_history_item(self):
        return self._db.search(where('url') == self._sheet.url and where('sheet_name') == self._sheet.sheet_name)

    def load_history_item(self):
        data = self.get_history_item()
        if len(data) > 0:
            self._next_seq = data[0]["next_seq"]
            self._date = str_to_date(data[0]["date"])
            return True
        else:
            return False

    def save_history_item(self):
        data = self.get_history_item()
        if len(data) == 1:
            self._db.update({'date': date_to_str(self._date), 'next_seq': self._next_seq},
                            where('url') == self._sheet.url and where('sheet_name') == self._sheet.sheet_name)
        else:
            self._db.insert({'url': self._sheet.url, 'sheet_name': self._sheet.sheet_name,
                             'date': date_to_str(self._date), 'next_seq': self._next_seq})




