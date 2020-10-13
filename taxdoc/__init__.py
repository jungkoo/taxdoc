#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import configparser
import os
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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




#
#
#
#
# UnionMember = collections.namedtuple("UnionMember", 'doc_id user_name phone_number user_id password user_email pay_date pay_sum')
#
#
# # 문서번호	이름	전화번호	주민번호	패스워드 이메일주소	납입기간	납입금액
# def union_member_generator(file_path, first_line_skip=False):
#     fd = open(file_path, "r")
#     if first_line_skip:
#         fd.readline()
#     while True:
#         line = fd.readline()
#         if not line:
#             break
#         t = line.split("\t")
#         yield UnionMember(doc_id=t[0], user_name=t[1], phone_number=t[2], user_id=t[3], password=t[4],
#                           user_email=t[6] if t[5] in ("O", "True", "YES") else "", pay_date=t[7],
#                           pay_sum=t[8].strip())
#     fd.close()
#
#
# def format_pay_string(text):
#     # 2019-11-25~2019-12-26 => 2019.11 ~ 2019.12
#     token = str(text).replace(" ", "").replace("-", "").split("~")
#     if len(token) != 2:
#         raise Exception("not found start_date, end_date")
#     return "{}.{} ~ {}.{}".format(token[0][0:4], token[0][4:6], token[1][0:4], token[1][4:6])
#
#
# def format_pay_sum(num):
#     number = str(num).replace(" ", "").replace(",", "")
#     number = int(number)
#     return "{:,}".format(number)
