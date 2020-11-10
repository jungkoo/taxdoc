#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from hashlib import sha256
import os


def user_key(name, phone_number, magic_key="123"):
    """
    사용자 고유키
    :param name: 이름
    :param phone_number: 폰번호
    :param magic_key: 해쉬값 영향을 주는 매직키
    :return:
    """
    seed = "{}-{}-{}".format(name, normalized_phone_number(phone_number), magic_key)
    hash_result = sha256(seed.encode('utf-8')).hexdigest()
    return hash_result


def normalized_phone_number(src_text):
    """
    전화번호를 패턴에 맞게 리턴한다

    :param src_text: 1012345675 , 010-1234-5678, 010-123-4567, 0101234567
    :return: 010-xxxx-yyyy
    """
    phone_num = src_text.replace('-', '')
    if not phone_num.startswith("0"):
        phone_num = "0" + phone_num
    if len(phone_num) == 11:
        return "{}-{}-{}".format(phone_num[0:3], phone_num[3:7], phone_num[7:11])
    if len(phone_num) == 10:
        return "{}-{}-{}".format(phone_num[0:3], phone_num[3:6], phone_num[6:10])
    raise Exception("unknown phone number '{}'".format(src_text))


if __name__ == "__main__":
    domain = "http://0.0.0.0:10080"
    magic_key = os.environ.get("TAX_DOC_KEY") or "123"
    data_list = [("정민철", "01025746431", "123")]
    for data in data_list:
        k = user_key(data[0], data[1])
        print("{}\t{}\t{}?code={}".format(data[0], normalized_phone_number(data[1]), domain, k))

