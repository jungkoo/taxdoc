#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import configparser
import os
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
import requests
import threading

_thread_local = threading.local()
_document_style = None
_config_path = None
_document_config = None

ResultRecord = collections.namedtuple("ResultRecord", 'doc_id user_name phone_number user_id password user_email pay_date pay_sum user_address')


def config_path():
    global _config_path
    if _config_path:
        return _config_path
    _config_path = os.environ["TAX_DOC_CONFIG"] if "TAX_DOC_CONFIG" in os.environ else ""
    return _config_path


def sign_path():
    return config_path() + "/sign.png"


def font_path():
    return config_path() + "/font.ttf"


def document_style():
    global _document_style
    if _document_style:
        return _document_style
    pdfmetrics.registerFont(TTFont("default_font", font_path()))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="default", fontName="default_font", alignment=1))
    styles.add(ParagraphStyle(name="left", fontName="default_font", alignment=0, leftIndent=10))
    styles.add(ParagraphStyle(name="right", fontName="default_font", alignment=2))
    styles.add(ParagraphStyle(name="group_sign", fontName="default_font", fontSize=12, alignment=2, rightIndnt=20))
    styles.add(ParagraphStyle(name="head_seq", fontName="default_font", fontSize=9, alignment=1))  # 일련번호
    styles.add(ParagraphStyle(name="head_title", fontName="default_font", fontSize=20, alignment=1))  # 기부금영수증
    styles.add(ParagraphStyle(name="sub_title", fontName="default_font", leftIndent=5))  # 기부금영수증
    _document_style = styles
    return _document_style


def document_config():
    global _document_config
    if _document_config:
        return _document_config
    path = os.path.abspath(config_path()) + "/config.ini"
    config = configparser.ConfigParser()
    config.read_file(open(path))
    _document_config = config
    return _document_config


class LoginSession:
    """
    request 를 이용한 데이터 조회
    """
    def __init__(self, user_id, password):
        self._user_id = user_id
        self._password = password
        self._login_session = requests.session()
        self._header = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        self._authentication()
        self._limit = 100000
        _thread_local.login_req = self

    def _authentication(self):
        data = {'layoutCd': 'spa00', 'loginid': self._user_id, 'loginpw': self._password}
        self._login_session.get("https://www.thebill.co.kr", headers=self._header)
        r = self._login_session.post("https://www.thebill.co.kr/webuser/loginProc.json", headers=self._header, data=data)
        if r.json()['resultMsg'] != "":
            raise Exception("LOGIN ERROR")

    def post(self, url, **data):
        return self._login_session.post(url, headers=self._header, data=data)

    def result_list_generator(self, url, **data):
        res = self.post(url, **data)
        json_res = res.json()
        page_cnt = json_res['PageVO']['pageCnt']
        page_param = dict()
        page_param.update(data)

        count = 0
        for page_num in range(1, int(page_cnt)+1):
            page_param['pageno'] = page_num
            if count >= self._limit:
                break
            res = self.post(url, **page_param)
            json_res = res.json()
            for row in json_res['resultList'] or []:
                if count >= self._limit:
                    break
                count += 1
                yield dict(filter(lambda elem: elem[1] is not None, row.items()))

    def session(self):
        return self._login_session

    @staticmethod
    def current():
        try:
            val = _thread_local.login_req
        except AttributeError:
            logging.debug("current login info not found")
        else:
            return val