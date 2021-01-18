#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc import LoginSession
from datetime import timedelta
import datetime


class TaxApi:
    def __init__(self, login_session: LoginSession, year=(datetime.datetime.now() - timedelta(days=365)).year):
        self.session = login_session
        self.year = year

    def get_member_id(self, name, phone_number):
        s: LoginSession = self.session
        phone = phone_number.replace("-", "")
        rsb = s.result_list_generator("https://www.thebill.co.kr/cms2/cmsMemList.json", memberName=name)
        for r in rsb:
            if r["memberName"] == name and r["hpNo"].replace("-", "") == phone and '동의요청' not in r["statusNm"]:
                return r["memberId"]
        # 퇴사자 정보는 딴 API 에서 알아낸다.
        rsb = s.result_list_generator("https://www.thebill.co.kr/cms2/cmsPayListByMember.json", memberName=name)
        for r in rsb:
            print(r)
            if r["memberName"] == name and r["hpNo"].replace("-", "") == phone and "memberId" in r:
                return r["memberId"]
        return None

    def get_pay_result(self, member_id):
        """
        연말정산용 결과 리턴
        :param member_id: 더빌에서 사용하는 멤버 아이디
        :return: {name: 이름, pay_sum: 총납입금액, date_range: 납입범위워}
        """
        def format_pay_string(text):
            # 2019-11-25~2019-12-26 => 2019.11 ~ 2019.12
            token = str(text).replace(" ", "").replace("-", "").split("~")
            if len(token) != 2:
                raise Exception("not found start_date, end_date")
            return "{}.{} ~ {}.{}".format(token[0][0:4], token[0][4:6], token[1][0:4], token[1][4:6])
        s: LoginSession = self.session
        start_date = "{}-01-01".format(self.year)
        end_date = "{}-12-31".format(self.year)
        pay_sum = 0
        max_date = "000000"
        min_date = "999999"
        member_name = ""
        date_range = None
        url = "https://www.thebill.co.kr/cms2/cmsInvList.json"
        rsb = s.result_list_generator(url, invoiceSt="01", startDate=start_date,
                                      endDate=end_date, memberId=member_id, setListPerPage="30")
        for r in rsb:
            min_date = min(min_date, r['sendDt'][:6])
            max_date = max(max_date, r['sendDt'][:6])
            pay_sum += int(r['dealWon'])
            member_name = r['memberName']
            date_range = format_pay_string("{} ~ {}".format(min_date, max_date))

        if date_range is None:
            raise ValueError("가입이력은 있지만, 납부 이력이 없습니다")

        return dict(name=member_name, pay_sum=format(pay_sum, ',d'), date_range=date_range)

    def get_pay_detail_list(self, member_id):
        """
        납부 상세 내역리턴
        :param member_id: 더빌에서 사용하는 멤버 아이디
        :return:
        """
        s: LoginSession = self.session
        start_date = "{}-01-01".format(self.year)
        end_date = "{}-12-31".format(self.year)
        url = "https://www.thebill.co.kr/cms2/cmsInvList.json"
        rsb = s.result_list_generator(url, startDate=start_date,
                                      endDate=end_date, memberId=member_id, setListPerPage="30")
        output = []
        for r in rsb:
            date = r['sendDt'][:8]
            pay = format(int(r['dealWon']), ',d')
            output.append(dict(date="{}-{}-{}".format(date[:4], date[4:6], date[6:8]), pay=pay, msg=r['lastResultMsg']))
            # sorted(xx, key=itemgetter('')
        return sorted(output, key=lambda k: k['date'])
