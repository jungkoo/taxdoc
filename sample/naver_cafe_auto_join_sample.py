#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.naver_cafe import NCafeAutoJoin, CafeUser

USER_ID = "<아이디>"
PASS_WORD = "<패스워드>"
DRIVER_PATH = "<크롬드라이브 경로>"


if __name__ == "__main__":
    cafe = NCafeAutoJoin(driver_path=DRIVER_PATH).login(USER_ID, PASS_WORD)
    wait_users = cafe.find_wait_users()

    # CafeUser = namedtuple('CafeUser', 'id nick age gender date reply')
    def member_check(data: CafeUser):
        """

        """
        pass

    wait_users.filter(member_check).checked().save()

