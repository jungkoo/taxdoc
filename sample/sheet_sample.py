#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.sheet import GoogleFormSheet
from datetime import datetime
if __name__ == "__main__":
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/문서번호/edit#gid=1641959086'
    sheet = GoogleFormSheet(spreadsheet_url)
    start_date = datetime(2018, 4, 4)
    end_date = datetime(2018, 4, 5)

    # 2018/04/04 00:00:00 이상 ~ 2018/04/05 00:00:00 이하 데이터 검색
    result = sheet.find_date(start_date)
    for row in result:
        print(row)
