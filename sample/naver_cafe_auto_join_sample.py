#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.naver_cafe import NCafeAutoJoin, CafeUserCheckBox
from taxdoc.sheet import GoogleFormSheet
import re

USER_ID = "<아이디>"
PASS_WORD = "<패스워드>"
DRIVER_PATH = "chromedriver"
GOOGLE_SHEET_URL = "<구글주소>"
CAFE_IDX = GoogleFormSheet.column_code_to_index("Q")
CMS_IDX = GoogleFormSheet.column_code_to_index("M")

class CafeUserDocCheckBox:
    def __init__(self, checkbox_user: CafeUserCheckBox, google_sheet: GoogleFormSheet):
        self._user = checkbox_user
        self._sheet = google_sheet
        _t = checkbox_user.get().reply.split("/")
        self._name = _t[1].strip()
        self._phone_last4 = _t[2].strip()
        self._seq, self._level = self._load()

    def is_valid(self):
        return self._seq > 0

    def _load(self):
        _find_users = self._sheet.find_keyword_all_with_seq(self._name, re.compile(r".*" + self._phone_last4 + "$"))
        if len(_find_users) != 1:
            return -1, "비조합원"
        _seq, _user = _find_users[0]
        is_cms = _user[CMS_IDX] == "완료"
        is_cafe = _user[CAFE_IDX].strip() in ("O", "o", "0", "true")

        if is_cafe:
            if is_cms:
                return -1, "중복신청_일반조합원"
            else:
                return -1, "중복신청_준조합원"
        else:
            if is_cms:
                return _seq, "일반조합원"
            else:
                return _seq, "준조합원"

    def is_checked(self):
        return self._user.is_checked()

    def checked(self):
        try:
            self._sheet.update_value(self._seq, CAFE_IDX + 1, "o")
            self._user.checked()
        except (Exception, RuntimeError):
            self._sheet.update_value(self._seq, CAFE_IDX + 1, "x")

    def level(self):
        return self._level

    def level_up(self):
        if self._seq > 0:
            self._user.level(self._level)
            return "[SUCCESS] {} (등업: {})".format(self._user, self._level)
        else:
            return "[ERROR] {} (등업실패: {})".format(self._user, self._level)

    def user(self):
        return self._user

    def __str__(self):
        return "({}) {} - {}".format(self._seq, self._user().__str__(), self._level)

    def to_dict(self):
        r = self.user().get()
        return {"id": r.id, "nick": r.nick, "date": r.date,
                "name": self._name[:1] + "**" if len(self._name) > 1 else "",
                "last_num": self._phone_last4, "level": self._level}


if __name__ == "__main__":
    sheet = GoogleFormSheet(url=GOOGLE_SHEET_URL, sheet_name="설문지 응답(CMS포함)")
    cafe = NCafeAutoJoin(USER_ID, PASS_WORD, DRIVER_PATH, cafe_url="https://cafe.naver.com/nunion")
    success_msg = "### 자동처리 대상\n"
    error_msg = "### 수동처리 대상\n"
    success_cnt = 0
    error_cnt = 0
    for _u in cafe.find_wait_users():
        user = CafeUserDocCheckBox(_u, sheet)
        if user.is_valid():
            user.checked()
            user.level_up()
            success_cnt += 1
            success_msg += "[{id}/{nick}] {name}/{last_num} => {level} - 신청일: {date}\n".format(**user.to_dict())
        else:
            error_cnt += 1
            error_msg += "[{id}/{nick}] {name}/{last_num} => {level} - 신청일: {date}\n".format(**user.to_dict())

    msg = "## 처리현황 (자동처리: {}건, 확인요망: {}건)\n{}\n{}".format(success_cnt, error_cnt, success_msg, error_msg)
    cafe.close()
    print(msg)
