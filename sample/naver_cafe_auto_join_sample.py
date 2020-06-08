#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.naver_cafe import NCafeLogin, NCafeAutoJoin, CafeUser
from taxdoc.sheet import GoogleFormSheet
import re

USER_ID = "<관리자아이디>"
PASS_WORD = "<관리자패스워드>"
DRIVER_PATH = "chromedriver"
GOOGLE_SHEET_URL = "https://docs...01"
CAFE_IDX = GoogleFormSheet.column_code_to_index("Q")
CMS_IDX = GoogleFormSheet.column_code_to_index("M")


class CafeUserConform:
    def __init__(self, google_sheet: GoogleFormSheet, cafeAutoJoin: NCafeAutoJoin):
        self._sheet = google_sheet
        self._join_cafe = cafeAutoJoin

    @staticmethod
    def name_phone4(cafe_user: CafeUser):
        _t = cafe_user.reply.split("/")
        _name = _t[1].strip()
        _phone_last4 = _t[2].strip()
        return _name, _phone_last4

    def check_user(self, cafe_user: CafeUser):
        _name, _phone_last4 = CafeUserConform.name_phone4(cafe_user)
        _find_users = self._sheet.find_keyword_all_with_seq(_name, re.compile(r".*" + _phone_last4 + "$"))
        _seq, _user = _find_users[0]
        is_cms = _user[CMS_IDX] == "완료"
        is_cafe = _user[CAFE_IDX].strip() in ("O", "o", "0", "true")
        if is_cafe:
            return -1, "중복가입"
        else:
            if is_cms:
                return _seq, "일반 조합원"
            else:
                return _seq, "준조합원"

    def conform(self, cafe_user: CafeUser):
        seq, visible_text = self.check_user(cafe_user)
        if seq < 0:
            return visible_text
        try:
            self._sheet.update_value(seq, CAFE_IDX + 1, "o")
            self._join_cafe._conform_wait_users(user_id_list=[cafe_user.id, ])
            self._join_cafe._conform_level_users(user_id_list=[cafe_user.id, ], visible_text=visible_text)
            self._sheet.update_value(seq, CAFE_IDX + 1, "O")
        except (Exception, RuntimeError) as e:
            self._sheet.update_value(seq, CAFE_IDX + 1, "x")
            raise RuntimeError("Unknown ERROR! (msg={})".format(str(e)))
        return visible_text


if __name__ == "__main__":
    success_msg = "### 자동처리 대상\n"
    fail_msg = "### 수동처리 대상\n"
    error_msg = "### 에러메시지\n"
    success_cnt = 0
    fail_cnt = 0
    error_cnt = 0

    sheet = GoogleFormSheet(url=GOOGLE_SHEET_URL, sheet_name="설문지 응답(CMS포함)")
    cafe = NCafeAutoJoin(NCafeLogin(DRIVER_PATH).login(USER_ID, PASS_WORD))
    conform = CafeUserConform(sheet, cafe)
    for cafe_user in cafe.get_wait_users():
        try:
            _name, _phone_last4 = CafeUserConform.name_phone4(cafe_user)
            seq, level_name = conform.check_user(cafe_user)
            param = dict(id=cafe_user.id, nick=cafe_user.nick, name=_name, last_num=_phone_last4, date=cafe_user.date,
                         level=level_name)
            if seq > 0:
                conform.conform(cafe_user)
                success_cnt += 1
                success_msg += "[{id}/{nick}] {name}/{last_num} => {level} 승인처리 - 신청일: {date}\n".format(**param)
            else:
                fail_cnt += 1
                fail_msg += "[{id}/{nick}] {name}/{last_num} => 조합원 아님 수동체크 필요 - 신청일: {date}\n".format(**param)
        except (Exception, RuntimeError) as e:
            error_msg = "{}/{} 에러 {}".format(_name, _phone_last4, str(e))
            error_cnt += 1
    msg = "## 처리현황 (자동승인: {}건, 확인요망: {}건, 에러: {}건)\n".format(success_cnt, fail_cnt, error_cnt)
    if success_cnt > 0:
        msg += success_msg
    if fail_cnt > 0:
        msg += fail_msg
    if error_cnt > 0:
        msg += error_msg
    print(msg)
