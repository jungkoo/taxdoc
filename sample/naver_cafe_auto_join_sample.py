#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.naver_cafe import NCafeAutoJoin, CafeUser

USER_ID = "<유저아이디>"
PASS_WORD = "<암호>"
DRIVER_PATH = "chromedriver"


if __name__ == "__main__":
    msg = ""
    cafe = NCafeAutoJoin(driver_path=DRIVER_PATH).login(USER_ID, PASS_WORD)
    wait_users = cafe.find_wait_users()
    for r in wait_users:
        # 예제: CafeUser(id='_gildong00', nick='hobu', age='20대 후반', gender='남', date='2020.05.11.', reply='가입처리테스트/홍길동/9998')
        # if is_member(r):
        #   가입처리테스트/홍길동/4321
        #   r.checked()
        #   msg += "\n"
        print(r)

    info = {"total": cafe.count(), "checked": cafe.count(True)}
    # cafe.save()
    msg = "## 총 {total} 명 신청 / {checked} 명 승인요청\n".format(**info) + msg
    print(msg)
