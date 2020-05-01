#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.dooray import DooraySchedule
from taxdoc.the_bill_api import bot_send
from datetime import datetime

if __name__ == "__main__":
    dooray = DooraySchedule("아이디", "패스워드", "chromedriver경로")
    bot_hook_url = "https://hook.dooray.com/services/2185355349700794521/2731951412316204138/1i_-Cqr4TNeb83BCZAojsg"
    count = 0
    msg = "## {} 일정리스트업 ##\n".format(datetime.now().strftime("%Y-%m-%d"))

    for row in dooray.get_today_calendar():
        count += 1
        msg += "{} => {}\n".format(row.date, row.contents)
    for row in dooray.get_today_project():
        count += 1
        msg += "{} => {}\n".format(row.date, row.contents)
    if count > 0:
        bot_send("어텐션봇", text=msg, bot_hook_url=bot_hook_url)
    print(msg)