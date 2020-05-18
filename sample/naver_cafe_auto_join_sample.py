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


class CafeUserDocCheckBox(CafeUserCheckBox):
    def __init__(self, init_user: CafeUserCheckBox, google_sheet: GoogleFormSheet):
        super().__init__(init_user._value, init_user._parent)
        self._sheet = google_sheet
        _t = self.get().reply.split("/")
        self._name = _t[1].strip()
        self._phone_last4 = _t[2].strip()
        self._seq, self._msg = self._load()

    def is_valid(self):
        return self._seq > 0

    def _load(self):
        _find_users = self._sheet.find_keyword_all_with_seq(self._name, re.compile(r".*" + self._phone_last4 + "$"))
        if len(_find_users) != 1:
            return -1, "[ERROR] 조합원 아님"

        _seq, _user = _find_users[0]
        if _user[CMS_IDX] != "완료":
            return -1, "[ERROR] CMS 미등록자"
        if _user[CAFE_IDX].strip() in ("O", "o", "0", "true"):
            return -1, "[ERROR] 기존가입자"
        return _seq, "가입대기자"

    def is_checked(self):
        return super().is_checked()

    def checked(self):
        self._sheet.update_value(self._seq, CAFE_IDX + 1, "true")
        super().checked()

    def unchecked(self):
        self._sheet.update_value(self._seq, CAFE_IDX + 1, "X")
        # super().unchecked()

    def __str__(self):
        return "({}) {} - {}".format(self._seq, super().__str__(), self._msg)

    def to_dict(self):
        r = self.get()
        return {"id": r.id, "nick": r.nick, "date": r.date,
                "name": self._name[:1] + "**" if len(self._name) > 1 else "",
                "last_num": self._phone_last4, "error_msg": self._msg}


if __name__ == "__main__":
    msg = ""
    total_count = 0
    success_msg = "### 자동승인 대상\n"
    success_count = 0
    error_msg = "### 확인요망 대상\n"
    error_count = 0
    sheet = GoogleFormSheet(url=GOOGLE_SHEET_URL, sheet_name="설문지 응답(CMS포함)")
    cafe = NCafeAutoJoin(driver_path=DRIVER_PATH).login(USER_ID, PASS_WORD)
    rollback = []
    for row in cafe.find_wait_users():
        total_count += 1
        cafe_user = CafeUserDocCheckBox(row, sheet)
        try:
            if cafe_user.is_valid():
                cafe_user.checked()
                success_count += 1
                rollback.append(cafe_user)
                success_msg += "[{id}/{nick}] {name}/{last_num} - 신청일: {date}\n".format(**cafe_user.to_dict())
            else:
                error_count += 1
                error_msg += "[{id}/{nick}] {name}/{last_num} - 신청일: {date} : 실패이유: {error_msg}\n" \
                    .format(**cafe_user.to_dict())
        except (Exception, RuntimeError):
            error_count += 1
            error_msg += "[Exception] {}".format(row)

    is_cafe_save = False
    try:
        is_cafe_save = cafe.save()
        cafe.close()
    except (Exception, RuntimeError):
        is_cafe_save = False
    finally:
        if success_count > 0 and not is_cafe_save and len(rollback) > 0:
            for r in rollback:
                if r.is_valid():
                    r.unchecked()
        msg = "## 자동승인 {}명 , 확인필요 {}명 (총: {}명, 저장: {})\n".format(success_count, error_count,
                                                                 total_count, "O" if is_cafe_save else "X")
        if success_count > 0 and is_cafe_save:
            msg += success_msg + "\n"
        if success_count > 0 and not is_cafe_save:
            msg += "### 저장실패 " + success_msg + "\n"
        if error_count > 0:
            msg += error_msg
        print(msg)
