#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc import LoginSession
from datetime import timedelta
import datetime


class TaxApi:
    def __init__(self, login_session: LoginSession, year=(datetime.datetime.now() - timedelta(days=365)).year):
        self.session = login_session
        self.year = year

    def get_member_id_list(self, name, phone_number):
        """
        납부정보 변경자들의 경우 member_id 가 N개인 문제가 존재한다.

        :param name:
        :param phone_number:
        :return:
        """
        member_id_set = set()
        s: LoginSession = self.session
        phone = phone_number.replace("-", "")
        # 모든 가입자 정보들
        rsb = s.result_list_generator("https://www.thebill.co.kr/cms2/cmsPayListByMember.json", memberName=name)
        for r in rsb:
            if r["memberName"] == name and r["hpNo"].replace("-", "") == phone and r.get("resultMsg", "") == "정상처리":
                member_id_set.add(r["memberId"])
        return [x for x in member_id_set]

    def extract_pay_result(self, member_id_list):
        """
        납부 상세 이력정보를 의미한다.

        :param member_id_list: 회원코드 정보
        :return: {date: 날짜, name: 회원이름, pay: 금액, msg: 상태명, invoice: 상태코}
        """
        if len(member_id_list) == 0:
            raise ValueError("가입정보를 찾을 수 없습니다")
        s: LoginSession = self.session
        start_date = "{}-01-01".format(self.year)
        end_date = "{}-12-31".format(self.year)
        url = "https://www.thebill.co.kr/cms2/cmsInvList.json"

        rsb = []
        for member_id in member_id_list:
            r = s.result_list_generator(url, startDate=start_date, endDate=end_date, memberId=member_id, setListPerPage="30")
            rsb.extend(r)
        output = []
        for r in rsb:
            date = r['sendDt'][:8]
            name = r['memberName']
            pay = int(r['dealWon'])
            output.append(dict(name=name, date="{}-{}-{}".format(date[:4], date[4:6], date[6:8]), pay=pay,
                               msg=r['lastResultMsg'], invoice=r["invoiceSt"]))
        return sorted(output, key=lambda k: k['date'])

    @staticmethod
    def convert_pay_result(pay_result):
        """
        연말정산용 결과 리턴
        :param pay_result: extract_pay_result 의 결과
        :return: {name: 이름, pay_sum: 총납입금액, date_range: 납입범위}
        """
        def format_pay_string(text):
            # 2019-11-25~2019-12-26 => 2019.11 ~ 2019.12
            token = str(text).replace(" ", "").replace("-", "").split("~")
            if len(token) != 2:
                raise ValueError("시작과 종료날짜 지정불가 (관리자 확인이 필요합니다)")
            return "{}.{} ~ {}.{}".format(token[0][0:4], token[0][4:6], token[1][0:4], token[1][4:6])
        pay_sum = 0
        max_date = "000000"
        min_date = "999999"
        member_name = ""
        date_range = None
        for r in pay_result:
            if r["invoice"] != "01":
                continue  # 정상납부 아니면 스킵
            min_date = min(min_date, r['date'])
            max_date = max(max_date, r['date'])
            pay_sum += r['pay']
            member_name = r['name']
            date_range = format_pay_string("{} ~ {}".format(min_date, max_date))
        if date_range is None:
            raise ValueError("가입이력은 있지만, 납부 이력이 없습니다")
        return dict(name=member_name, pay_sum=format(pay_sum, ',d'), date_range=date_range)

    @staticmethod
    def convert_pay_detail_list(pay_result):
        """
        납부 상세 내역리턴
        :param pay_result: extract_pay_result 의 결과
        :return:
        """
        output = []
        for r in pay_result:
            date = r["date"]
            pay = format(int(r['pay']), ',d')
            output.append(dict(date=date, pay=pay, msg=r['msg']))
        return sorted(output, key=lambda k: k['date'])