#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.sheet import GoogleFormSheet, HistoryFormSheet
from datetime import datetime


def google_form_sheet_demo():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d//edit#gid=1641959086"
    sheet = GoogleFormSheet(spreadsheet_url)
    start_date = datetime(2018, 4, 4)
    end_date = datetime(2018, 4, 5)

    # 2018/04/04 00:00:00 이상 ~ 2018/04/05 00:00:00 이하 데이터 검색
    result = sheet.find_date(start_date, end_date)
    for row in result:
        print(row)


def history_form_sheet_demo():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/값/edit#gid=1641959086"
    history_results = HistoryFormSheet(GoogleFormSheet(spreadsheet_url))
    count = 0
    for row in history_results.more():
        print(row)
        count += 1
        if count >= 4:
            break


if __name__ == "__main__":
    google_form_sheet_demo()
    print("======")

    print("> more")
    history_form_sheet_demo()
    print("> more1")
    history_form_sheet_demo()
    print("> more2")
    history_form_sheet_demo()

