#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from taxdoc import document_style, sign_path, ResultRecord
from reportlab.lib.pagesizes import A4, mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import pdfencrypt
from reportlab.lib import colors
from datetime import datetime


class DocumentBuilder:
    def __init__(self):
        self.corp_name = "전국화학섬유식품\n산업노동조합"
        self.corp_code = "107-82-63961"
        self.corp_address = "서울 동작구 장승배기로 98 장승빌딩 5층"
        self.bill_title = "종교단체 외\n지정기부금"
        self.price_type_name = "종교단체 외\n지정기부금"
        self.price_type_code = "40"
        self.price_type_contents = "노동조합비"
        self.user_contents = "<소득세법> 제34조, <조세특례제한법> 제73조, 제76조 및 제88조의4에 따른 기부금을 위와 같이 기부하였음을 증명하여 주시기 바랍니다."
        self.group_contents = "위와 같이 기부금(노동조합 조합비)를 기부 받았음을 증명합니다."
        self.group_name = "기부금 수령인 전국화학섬유식품산업노동조합"
        self.doc_title = "노동조합비 소득공제 자료"

    @staticmethod
    def _head(doc_id="", title="기부금 영수증"):
        styles = document_style()
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
        title_paragraph = Paragraph(title, style=styles["head_title"])
        head = Table([[seq, title_paragraph, '']], colWidths=[45 * mm, 58 * mm, 45 * mm], rowHeights=[11 * mm])
        head.setStyle(TableStyle([
            ('VALIGN', (0, 0), (2, 0), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        return head

    @staticmethod
    def _user_info(user_name="홍길동", user_id="790102-1111111", user_address=""):
        """
        @user : 조합원 이름
        @user_id : 조합원 주민번호
        @user_address : 조합원 주소지
        """
        styles = document_style()
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

    @staticmethod
    def _group_info(corp_name="회사이름", corp_id="123-444-55", corp_address="서울시 행복구 사랑동 123-33"):
        """
        @corp_name : 단체명
        @corp_id : 고유번호
        @corp_address : 소재지
        """
        styles = document_style()
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

    @staticmethod
    def _price_info(price_type_name="종교단체 외\n지정기부금", price_type_code="40", price_date="시작날짜 ~ 종료날짜",
                    price_type_contents="노동조합비", price_all="0"):
        """
        @price_type_contents : 유형
        @price_type_code : 코드
        @price_date : 납부기간
        @price_type_contents : 내용
        @price_all : 금액
        """
        styles = document_style()
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
                # Paragraph(format(price_all, ',d'), style=styles["default"]),
                Paragraph(price_all, style=styles["default"]),
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

    @staticmethod
    def _user_check_info(user_contents, user_date="날짜", user_name="이름"):
        """
        @contents : 사용자 체크 내용
        @date : 날짜
        @user_name : 조합원명
        """
        styles = document_style()
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

    @staticmethod
    def _group_check_info(group_contents, group_date, group_name):
        """
        @group_contents : 조합용 내용
        @date : 날짜
        @group_name : 조합이름
        """
        styles = document_style()
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

    def __call__(self, result: ResultRecord):
        styles = document_style()
        if not result.doc_id or len(result.doc_id) <= 0:
            raise Exception("empty 'doc_id")
        if not result.user_name or len(result.user_name) <= 0:
            raise Exception("empty 'user_name")
        if not result.pay_date or len(result.pay_date) <= 0:
            raise Exception("empty 'price_date")
        if len(result.pay_sum) <= 0:
            raise Exception("price_all zero under value")
        to_day = datetime.now().strftime("%Y-%m-%d")
        layout_data = [[DocumentBuilder._head(result.doc_id)],
                       [Paragraph("1. 기부자", style=styles["sub_title"])],
                       [DocumentBuilder._user_info(result.user_name, result.user_id, result.user_address)],
                       [Paragraph("2. 기부자 단체", style=styles["sub_title"])],
                       [DocumentBuilder._group_info(self.corp_name, self.corp_code, self.corp_address)],
                       [Paragraph("3. 기부내용", style=styles["sub_title"])],
                       [DocumentBuilder._price_info(self.price_type_name, self.price_type_code, result.pay_date,
                                                 self.price_type_contents, result.pay_sum)],
                       [DocumentBuilder._user_check_info(self.user_contents, to_day, result.user_name)],
                       [DocumentBuilder._group_check_info(self.group_contents, to_day, self.group_name)],
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
        return layout

    def save(self, result: ResultRecord, file_name="", overwrite=True):
        layout = self(result)
        filename = file_name if file_name else result.doc_id + ".pdf"
        if os.path.exists(filename) and overwrite is False:
            raise Exception("file exist. not overwrite : ", filename)
        enc = pdfencrypt.StandardEncryption(result.password, canPrint=0) if result.password else None
        doc = SimpleDocTemplate(filename, pagesize=A4, encrypt=enc, title=self.doc_title)
        doc.build([layout, ])

