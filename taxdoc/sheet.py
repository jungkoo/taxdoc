#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import os
import json
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import urllib.request
import ssl
from datetime import datetime
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]
_json_file_name = 'google_auth.json'


class GoogleFormSheet:
    def __init__(self, url, sheet_name="설문지 응답 시트1", auth_json_path=_json_file_name):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path, scope)
        gc = gspread.authorize(credentials)
        self._sheet = None
        self._count = 0
        self._doc = gc.open_by_url(url)
        self.change_worksheet(sheet_name)

    def change_worksheet(self, sheet_name):
        self._sheet = self._doc.worksheet(sheet_name)
        self._count = self._sheet.row_count

    def count(self):
        return self._count

    def get_row(self, row_seq):
        return self._sheet.row_values(row_seq)

    def find_date(self, start_date, end_date):
        seq = 2
        for row in self._sheet.get("A2:A"):
            # [2018, 3, 15, 2, 5, 45]
            date_num = [x_ for x_ in map(int, re.findall(r'(\d+)', row[0]))]
            dt = datetime(date_num[0], date_num[1], date_num[2], date_num[3], date_num[4], date_num[5])
            if start_date <= dt <= end_date:
                yield self._sheet.row_values(seq)
            seq += 1

