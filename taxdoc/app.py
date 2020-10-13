#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc import LoginSession
from datetime import timedelta
import datetime
LoginSession(user_id='<더빌아이>', password='<더빌패스워드>')


def get_member_id(name, phone_number):
    s: LoginSession = LoginSession.current()
    phone = phone_number.replace("-", "")
    rsb = s.result_list_generator("https://www.thebill.co.kr/cms2/cmsMemList.json", memberName=name)
    for r in rsb:
        if r["memberName"] == name and r["hpNo"].replace("-", "") == phone:
            return r["memberId"]
    raise Exception("해당하는 멤버 아이디는 존재하지 않습니다.")


def get_pay_result(member_id, year=(datetime.datetime.now() - timedelta(days=365)).year):
    def format_pay_string(text):
        # 2019-11-25~2019-12-26 => 2019.11 ~ 2019.12
        token = str(text).replace(" ", "").replace("-", "").split("~")
        if len(token) != 2:
            raise Exception("not found start_date, end_date")
        return "{}.{} ~ {}.{}".format(token[0][0:4], token[0][4:6], token[1][0:4], token[1][4:6])
    s: LoginSession = LoginSession.current()
    start_date = "{}-01-01".format(year)
    end_date = "{}-12-31".format(year)
    pay_sum = 0
    max_date = "000000"
    min_date = "999999"
    member_name = ""
    rsb = s.result_list_generator("https://www.thebill.co.kr/cms2/cmsInvList.json", invoiceSt="01", startDate=start_date,
                            endDate=end_date, memberId=member_id, setListPerPage="30")
    for r in rsb:
        min_date = min(min_date, r['sendDt'][:6])
        max_date = max(max_date, r['sendDt'][:6])
        pay_sum += int(r['dealWon'])
        member_name = r['memberName']
        date_range = format_pay_string("{} ~ {}".format(min_date, max_date))

    return dict(name=member_name, pay_sum=format(pay_sum, ',d'), date_range=date_range)


# if __name__ == "__main__":
#     memberId = get_member_id("홍길", "010-1111-2222")
#     rsb = get_pay_result(memberId)
#     print(rsb)
#    {'name': '홍길', 'pay_sum': '360,000', 'date_range': '2019.01 ~ 2019.12'}
