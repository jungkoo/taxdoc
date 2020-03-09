#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import datetime
import json
from html_table_parser import HTMLTableParser
from datetime import datetime
import re

_base_url = "https://www.thebill.co.kr"
_authentication_url = "https://www.thebill.co.kr/webuser/loginProc.json"
_group_code_url = "https://www.thebill.co.kr/usergroup/userGroupList.json"
_pay_list_member = "https://www.thebill.co.kr/cms2/cmsPayListByMember.json"
_pay_info_url = "https://www.thebill.co.kr/cms2/popup/cmsPayListByMemberDet.tb?memberNo={}"
_register_url = "https://www.thebill.co.kr/real/cmsMemEntryAction.json"
_header = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}


def _pay_info_format(pay_info, year):
    begin = ""
    end = ""
    pay_sum = 0
    if len(pay_info) > 1:
        for pay_info in pay_info[:-1]:
            dt = datetime.strptime(pay_info[1], '%Y-%m-%d')
            if dt.year == year:
                won = int(re.search(r'\d+', pay_info[4].replace(",", "")).group())
                pay_sum += won
                if begin == "":
                    begin = pay_info[1]
                end = pay_info[1]
    return "{}~{}".format(begin, end), pay_sum


def _create_user_key(user):
    return "{}~{}".format(user["user_name"], user["phone_number"])


def _merge_data(data_generator):
    """
    (before)
    홍길동	010-0000-0001	2019.09 ~ 2019.12	120000
    홍길동	010-0000-9999	2019.01 ~ 2019.12	360000
    홍길동	010-0000-0001	2019.01 ~ 2019.08	240000

    (after)
    홍길동	010-0000-9999	2019.01 ~ 2019.12	360000
    홍길동	010-0000-0001	2019.01 ~ 2019.12	360000
    """
    if data_generator is None:
        return
    sam_name_mapper = {}

    def _phone_number_merge_reduce(_pre):
        """
        이름정렬 되어있는 경우, 전화번호 중복을 체크해 값을 합쳐준다.
        """
        if _pre is not None:
            if pre["phone_number"] in sam_name_mapper:
                sam_name_mapper[_pre["phone_number"]].append(_pre)
            else:
                yield _pre
        if len(sam_name_mapper) <= 0:
            return None
        for _k in sam_name_mapper:
            _merge = sam_name_mapper[_k][0]
            for _m in sam_name_mapper[_k][1:]:
                if _m["user_name"] == _merge["user_name"] and _m["phone_number"] == _merge["phone_number"]:
                    _merge["pay_sum"] += _m["pay_sum"]
                    _t1 = _merge["pay_date"].split("~")
                    _t2 = _m["pay_date"].split("~")
                    _merge["pay_date"] = "{} ~ {}".format(min(_t1[0].strip(), _t2[0].strip()),
                                                          max(_t1[1].strip(), _t2[1].strip()))
                else:
                    raise Exception("duplicate error")
            yield _merge
        sam_name_mapper.clear()

    pre = next(data_generator)

    for current in data_generator:
        if pre["user_name"] == current["user_name"]:
            if pre["phone_number"] not in sam_name_mapper:
                sam_name_mapper[pre["phone_number"]] = [pre, ]
            else:
                sam_name_mapper[pre["phone_number"]].append(pre)
        else:
            for _x in _phone_number_merge_reduce(pre):
                yield _x

        # 최근껀 이전값으로 유지
        pre = current
    # end
    for _x in _phone_number_merge_reduce(pre):
        yield _x


class TheBillCrawler:
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

    def search(self, year):
        for _r in _merge_data(self._search_for_data(year, status_cd=None, sort_cd1="02", sort_cd2="A")):
            yield _r

    def _search_for_data(self, year, status_cd="04", sort_cd1="01", sort_cd2="D"):
        r = self.login_session.post(_pay_list_member,
                                    headers=_header, data={"sortGubn1": sort_cd1, "sortGubn2": sort_cd2, "serviceType": "",
                                                           "memberName": "", "memberId": "", "srchCusGubn1": "",
                                                           "srchCusGubn2": "", "pageno": "1"})
        res = r.json()
        page_cnt = res['PageVO']['pageCnt']
        for page_num in range(1, int(page_cnt)+1):
            r = self.login_session.post(_pay_list_member,
                                        headers=_header,
                                        data={"sortGubn1": sort_cd1, "sortGubn2": sort_cd2, "serviceType": "", "memberName": "",
                                              "memberId": "", "srchCusGubn1": "", "srchCusGubn2": "",
                                              "pageno": str(page_num)})
            res = r.json()
            for member_info_list in res['resultList']:
                if((member_info_list['statusCd'] == status_cd or status_cd is None)
                   and member_info_list['paySeq'] is not None and member_info_list['lastSendDt'] is not None
                   and int(member_info_list['paySeq']) > 0):
                    result_html = self.login_session.get(_pay_info_url.format(member_info_list['memberNo'])).text
                    p = HTMLTableParser()
                    p.feed(result_html)
                    pay_info = p.tables[2][1:]
                    date_string, pay_sum = _pay_info_format(pay_info, year)
                    if pay_sum == 0:
                        continue

                    try:
                        yield dict(user_name=member_info_list['memberName'], phone_number=member_info_list['hpNo'],
                                   pay_date=date_string, pay_sum=pay_sum)
                    except Exception as e:
                        self.error_count += 1
                        if self.error_fd and isinstance(self.error_fd, open):
                            self.error_fd.write(json.dumps(member_info_list, ensure_ascii=False) + "\t==>" + str(e))
