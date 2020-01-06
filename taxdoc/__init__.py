#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections

UnionMember = collections.namedtuple("UnionMember", 'doc_id user_name phone_number user_id password user_email pay_date pay_sum')


# 문서번호	이름	전화번호	주민번호	패스워드 이메일주소	납입기간	납입금액
def union_member_generator(file_path, first_line_skip=False):
    fd = open(file_path, "r")
    if first_line_skip:
        fd.readline()
    while True:
        line = fd.readline()
        if not line:
            break
        t = line.split("\t")
        yield UnionMember(doc_id=t[0], user_name=t[1], phone_number=t[2], user_id=t[3], password=t[4],
                          user_email=t[6] if t[5] in ("O", "True", "YES") else "", pay_date=t[7],
                          pay_sum=t[8].strip())
    fd.close()


def format_pay_string(text):
    # 2019-11-25~2019-12-26 => 2019.11 ~ 2019.12
    token = str(text).replace(" ", "").replace("-", "").split("~")
    if len(token) != 2:
        raise Exception("not found start_date, end_date")
    return "{}.{} ~ {}.{}".format(token[0][0:4], token[0][4:6], token[1][0:4], token[1][4:6])


def format_pay_sum(num):
    number = str(num).replace(" ", "").replace(",", "")
    number = int(number)
    return "{:,}".format(number)