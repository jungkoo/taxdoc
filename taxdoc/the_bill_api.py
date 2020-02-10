#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

_base_url = "https://www.thebill.co.kr"
_authentication_url = "https://www.thebill.co.kr/webuser/loginProc.json"
_header = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

def filter_dict(data, *keys):
    if keys:
        m = dict()
        for k in keys:
            if k in data:
                m[k] = data[k]
        return m
    else:
        data


def bot_send(name, text, bot_hook_url):
    """
    두레이 봇으로 보내기
    """
    data = {"botName": name, "botIconImage": "https://static.dooray.com/static_images/dooray-bot.png",
            "text": text}
    requests.post(bot_hook_url, headers={"Content-Type": "application/json"}, data=json.dumps(data))


class TheBillAPI:
    """
    the bill 에서 납주 정보를 추출한다

    @user_id : the bill 아이디
    @user_pass : the bill 패스워드
    @error_fd : 에러 발생할때 이력을 저장할 open() 된 파일정보
    """
    def __init__(self, user_id, user_pass, error_fd=None):
        self.user_id = user_id
        self.user_pass = user_pass
        self.login_session = requests.session()
        self._authentication()
        self.error_fd = error_fd
        self.error_count = 0

    def _authentication(self):
        data = {'layoutCd': 'spa00',
                'loginid': self.user_id,
                'loginpw': self.user_pass
                }
        r = self.login_session.get(_base_url, headers=_header)
        r = self.login_session.post(_authentication_url, headers=_header, data=data)
        if r.json()['resultMsg'] != "":
            raise Exception("LOGIN ERROR")

    def _result_list(self, seed_url, **req_data):
        res = self.login_session.post(seed_url, headers=_header, data=req_data)
        res = res.json()
        for info in res['resultList']:
            yield info

    def get_unpaid(self, start_date, end_date):
        """
        미납자 리스트를 리턴한다
        ==================
        result:
        {memberName: 사람이름, serviceType: 카드/은행, lastResultMsg: 사유, sendDt: 원출금일, retryDt1: 1차출금}
        """
        seed_url = "https://www.thebill.co.kr/cms2/cmsInvList.json"
        req_data = {"sortGubn1": "01", "sortGubn2": "D", "setListPerPage": "100", "invoiceSt": "00",
                    "startDate": start_date, "endDate": end_date}
        for row in self._result_list(seed_url, **req_data):
            yield filter_dict(row, "memberName", "serviceType", "lastResultMsg", "sendDt", "retryDt1")

