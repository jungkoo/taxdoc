#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import pdfencrypt
from reportlab.lib import colors

DEFAULT_PATH = os.path.dirname(os.path.realpath(__file__))


def font_path():
    return DEFAULT_PATH + "/default_font.ttf"


def sign_path():
    return DEFAULT_PATH + "/default_sign.png"


pdfmetrics.registerFont(TTFont("default_font", font_path()))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="default", fontName="default_font", alignment=1))
styles.add(ParagraphStyle(name="left", fontName="default_font", alignment=0, leftIndent=10))
styles.add(ParagraphStyle(name="right", fontName="default_font", alignment=2))
styles.add(ParagraphStyle(name="group_sign", fontName="default_font", fontSize=12, alignment=2, rightIndnt=20))
styles.add(ParagraphStyle(name="head_seq", fontName="default_font", fontSize=9, alignment=1))  # 일련번호
styles.add(ParagraphStyle(name="head_title", fontName="default_font", fontSize=20, alignment=1))  # 기부금영수증
styles.add(ParagraphStyle(name="sub_title", fontName="default_font", leftIndent=5))  # 기부금영수증

USER_DATE = "2020 년 1월 2일"
GROUP_DATE = "2020 년 1월 2일"


class TaxPdfCreator:
    def __init__(self, doc_id, user_name, user_id, price_date, price_all):
        """
        @doc_id : 문서번호
        @user_name : 조합원 이름
        @user_id : 조합원 주민번호
        @price_date : 조합비 납입일자 범위
        @price_all : 조합비 합계
        """
        if not isinstance(price_all, int):
            raise Exception("price_all is not integer")
        self._elements = []
        self.doc_id = doc_id
        self.user_name = user_name
        self.user_id = user_id
        self.user_address = ""
        self.corp_name = "전국화학섬유식품\n산업노동조합"
        self.corp_id = "107-82-63961"
        self.corp_address = "서울 동작구 장승배기로 98 장승빌딩 5층"
        self.price_type_name = "종료단체 외\n지정기부금"
        self.price_type_code = "40"
        self.price_type_contents = "노동조합비"
        self.price_date = price_date
        self.price_all = price_all
        self.user_contents = "<소득세법> 제34조, <조세특례제한법> 제73조, 제76조 및 제88조의4에 따른 기부금을 위와 같이 기부하였음을 증명하여 주시기 바랍니다."
        self.user_date = USER_DATE
        self.group_contents = "위와 같이 기부금(노동조합 조합비)를 기부 받았음을 증명합니다."
        self.group_date = GROUP_DATE
        self.group_name = "기부금 수령인 전국화학섬유식품산업노동조합"

    # 일련번호 : {{seq}} | 기부금 영수증 |
    @classmethod
    def head(cls, doc_id):
        text = Paragraph("일련번호", style=styles["head_seq"])
        seq = Paragraph(doc_id, style=styles["head_seq"])
        seq = Table([[text, seq]], colWidths=[18 * mm, 19 * mm], rowHeights=[11 * mm])
        seq.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        title = Paragraph("기부금 영수증", style=styles["head_title"])
        head = Table([[seq, title, '']], colWidths=[45 * mm, 58 * mm, 45 * mm], rowHeights=[11 * mm])
        head.setStyle(TableStyle([
            ('VALIGN', (0, 0), (2, 0), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        return head

    @classmethod
    def user_info(cls, user_name, user_id, user_address=""):
        """
        @user : 조합원 이름
        @user_id : 조합원 주민번호
        @user_address : 조합원 주소지
        """
        user = Table([
            [
                Paragraph("성 명", style=styles["default"]),
                Paragraph(user_name, style=styles["default"]),
                Paragraph("주민등록번호", style=styles["default"]),
                Paragraph(user_id if user_id else "", style=styles["default"])
            ],
            [
                Paragraph('주 소', style=styles["default"]),
                Paragraph(user_address, style=styles["default"]),
                '',
                ''
            ]
        ], colWidths=[35 * mm, 39 * mm, 35 * mm, 39 * mm], rowHeights=[10 * mm, 10 * mm])
        user.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.3, colors.black),
            ('SPAN', (1, 1), (3, 1)),
            ('VALIGN', (0, 0), (3, 1), 'MIDDLE'),
        ]))
        return user

    @classmethod
    def group_info(cls, corp_name, corp_id, corp_address):
        """
        @corp_name : 단체명
        @corp_id : 고유번호
        @corp_address : 소재지
        """
        group = Table([
            [
                Paragraph("단 체 명", style=styles["default"]),
                Paragraph(corp_name, style=styles["default"]),
                Paragraph("고유번호", style=styles["default"]),
                Paragraph(corp_id, style=styles["default"])
            ],
            [
                Paragraph('소 재 지', style=styles["default"]),
                Paragraph(corp_address, style=styles["default"]),
                '',
                ''
            ]
        ], colWidths=[35 * mm, 39 * mm, 35 * mm, 39 * mm], rowHeights=[15 * mm, 10 * mm])
        group.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.3, colors.black),
            ('SPAN', (1, 1), (3, 1)),
            ('VALIGN', (0, 0), (3, 1), 'MIDDLE'),
        ]))
        return group

    @classmethod
    def price_info(cls, price_type_name, price_type_code, price_date, price_type_contents, price_all):
        """
        @price_type_contents : 유형
        @price_type_code : 코드
        @price_date : 납부기간
        @price_type_contents : 내용
        @price_all : 금액
        """
        price = Table([
            [
                Paragraph("유 형", style=styles["default"]),
                Paragraph("코드", style=styles["default"]),
                Paragraph("납부기간", style=styles["default"]),
                Paragraph("내 용", style=styles["default"]),
                Paragraph("금액", style=styles["default"])
            ],
            [
                Paragraph(price_type_name, style=styles["default"]),
                Paragraph(price_type_code, style=styles["default"]),
                Paragraph(price_date, style=styles["default"]),
                Paragraph(price_type_contents, style=styles["default"]),
                Paragraph(format(price_all, ',d'), style=styles["default"]),
            ],
            [
                '',
                '',
                Paragraph('이 하 여 백', style=styles["default"]),
                '',
                '',
            ],
            [
                '',
                '',
                '',
                '',
                '',
            ],
            [
                '',
                '',
                '',
                '',
                '',
            ]
        ]
            , colWidths=[24 * mm, 11 * mm, 39 * mm, 44 * mm, 30 * mm]
            , rowHeights=[10 * mm, 14 * mm, 10 * mm, 10 * mm, 10 * mm])
        price.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.3, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return price

    @classmethod
    def user_check_info(cls, user_contents, user_date, user_name):
        """
        @contents : 사용자 체크 내용
        @date : 날짜
        @user_name : 조합원명
        """
        user_check = Table([
            [
                Paragraph(user_contents, style=styles["left"]),
            ],
            [
                Paragraph(user_date, style=styles["default"]),
            ],
            [
                Paragraph(user_name + ' (서명 또는 인)&nbsp;&nbsp;&nbsp;', style=styles["right"]),
            ],
        ]
            , colWidths=[148 * mm]
            , rowHeights=[20 * mm, 10 * mm, 10 * mm])
        user_check.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        return user_check

    @classmethod
    def group_check_info(cls, group_contents, group_date, group_name):
        """
        @group_contents : 조합용 내용
        @date : 날짜
        @group_name : 조합이름
        """
        im = Image(sign_path(), width=15 * mm, height=15 * mm)
        group_sign = Table([[Paragraph(group_name, style=styles["group_sign"]), im]], colWidths=[128 * mm, 20 * mm])
        group_sign.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        group_check = Table([
            [
                Paragraph(group_contents, style=styles["left"]),
            ],
            [
                Paragraph(group_date, style=styles["default"]),
            ],
            [
                group_sign,
            ],
        ]
            , colWidths=[148 * mm]
            , rowHeights=[10 * mm, 10 * mm, 10 * mm])
        group_check.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        return group_check

    def _create_elements(self):
        if not self.doc_id or len(self.doc_id) <= 0:
            raise Exception("empty 'doc_id")
        if not self.user_name or len(self.user_name) <= 0:
            raise Exception("empty 'user_name")
        if not self.price_date or len(self.price_date) <= 0:
            raise Exception("empty 'price_date")
        if self.price_all <= 0:
            raise Exception("price_all zero under value")

        layout_data = [[TaxPdfCreator.head(self.doc_id)],
                       [Paragraph("1. 기부자", style=styles["sub_title"])],
                       [TaxPdfCreator.user_info(self.user_name, self.user_id, self.user_address)],
                       [Paragraph("2. 기부자 단체", style=styles["sub_title"])],
                       [TaxPdfCreator.group_info(self.corp_name, self.corp_id, self.corp_address)],
                       [Paragraph("3. 기부내용", style=styles["sub_title"])],
                       [TaxPdfCreator.price_info(self.price_type_name, self.price_type_code, self.price_date,
                                                 self.price_type_contents, self.price_all)],
                       [TaxPdfCreator.user_check_info(self.user_contents, self.user_date, self.user_name)],
                       [TaxPdfCreator.group_check_info(self.group_contents, self.group_date, self.group_name)],
                       ]
        layout = Table(layout_data,
                       colWidths=[148 * mm],
                       rowHeights=[20 * mm, 10 * mm, 20 * mm, 10 * mm, 25 * mm, 10 * mm, 54 * mm, 40 * mm, 40 * mm])
        layout.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        self._elements.append(layout)

    def save(self, filename, password=None, overwrite=False):
        self._create_elements()
        if self._elements is None or len(self._elements) == 0:
            raise Exception("elements data is empty")
        if os.path.exists(filename) and overwrite is False:
            raise Exception("file exist. not overwrite : ", filename)
        enc = pdfencrypt.StandardEncryption(password, canPrint=0) if password else None
        doc = SimpleDocTemplate(filename, pagesize=A4, encrypt=enc, title="노동조합비 소득공제 자료 (공동성명)")
        doc.build(self._elements)