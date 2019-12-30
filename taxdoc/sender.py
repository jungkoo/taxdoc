#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    """
    SMTP 를 이용하여 메일을 발송한다

    (현재 메일발송 실패는 인지하지 못한다. (예: dsfasf@xxxeffadsf.com)
    """

    def __init__(self, domain="smtp.dooray.com", port=465, email="test@naverunion.dooray.com", password=None):
        """
        @domain : smtp 도메인주소
        @port : smtp 포트
        @email : 발송이메일주소 (로그인용)
        @password : 발송이메일 패스워드
        """
        self._from_mail = email
        self._mail = smtplib.SMTP_SSL(domain, port)
        self._mail.login(email, password)

    def send(self, to_mail, subject, contents, attach_file=None):
        EmailSender.mail_check(to_mail)
        msg = MIMEMultipart("alternative")
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self._from_mail
        msg['To'] = to_mail
        msg.attach(MIMEText(contents, 'html', 'utf-8'))

        # 파일추가
        if attach_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attach_file, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach_file))
            msg.attach(part)

        self._mail.sendmail(self._from_mail, to_mail, msg.as_string())

    @classmethod
    def mail_check(cls, mail_address):
        if mail_address is None or len(mail_address) == 0:
            raise Exception("[EMAIL] email address is empty", mail_address)
        if mail_address.index("@") <= 0:
            raise Exception("[EMAIL] email address '@' not found.", mail_address)
        if mail_address.index(".") <= 0:
            raise Exception("[EMAIL] email address '.' not found.", mail_address)

    def close(self):
        self._mail.close()
