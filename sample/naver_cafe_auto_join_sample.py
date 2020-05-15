#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.naver_cafe import NCafeAutoJoin
from taxdoc.sheet import GoogleFormSheet
import re

USER_ID = "<유저아이디>"
PASS_WORD = "<암호>"
DRIVER_PATH = "chromedriver"
GOOGLE_SHEET_URL = "가입자시트정보"


def join_user_check(name, phone_last4):
    spreadsheet_url = GOOGLE_SHEET_URL
    sheet = GoogleFormSheet(url=spreadsheet_url, sheet_name="설문지 응답(CMS포함)")
    find_user = sheet.find_keyword_all(name, re.compile(r".*" + phone_last4 + "$"))
    if len(find_user) == 1 and len(find_user[0]) > 16:
        if find_user[0][12] != "완료":
            return "CMS 미등록자"
        if find_user[0][16].strip() in ("O", "o", "0"):
            return "기존가입자"
        return "미가입자"
    else:
        return "조합원 아님"


if __name__ == "__main__":
    msg = ""
    success_msg = "### 자동승인 대상\n"
    success_count = 0
    error_msg = "### 확인요망 대상\n"
    error_count = 0
    cafe = NCafeAutoJoin(driver_path=DRIVER_PATH).login(USER_ID, PASS_WORD)
    wait_users = cafe.find_wait_users()
    for row in wait_users:
        r = row.get()
        t = r.reply.split("/")
        find_msg = join_user_check(t[1].strip(), t[2].strip()) if len(t) == 3 else "잘못된 가입정보 {}".format(r.reply)
        user = {"id": r.id, "nick": r.nick, "date": r.date, "name": t[1][:1]+"**" if len(t) > 1 else "",
                "last_num": t[2] if len(t) > 2 else ""}
        if "미가입자" == find_msg:
            r.checked()
            success_count += 1
            success_msg += "[{id}/{nick}] {name}/{last_num} - 신청일: {date}".format(**user)
        else:
            error_count += 1
            user["error_msg"] = find_msg
            error_msg += "[{id}/{nick}] {name}/{last_num} - 신청일: {date} :: 실패이유: {error_msg}".format(**user)

    # cafe.save()
    msg = "## 자동승인 {}명 , 확인필요 {}명\n".format(success_count, error_count)
    if success_count > 0:
        msg += success_msg + "\n"
    if error_count > 0:
        msg += error_msg
    print(msg)
