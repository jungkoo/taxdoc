#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import os
import json
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import urllib.request
import ssl


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


_PPURIO_SEND_API_URL = "https://www.ppurio.com/api/send_utf8_json.php"
_PPURIO_CALLBACK_PHONE_NUMBER = "01097301804"
_PPURIO_USER_ID = "naverunion"
SMS_USER = collections.namedtuple("SMS_USER", 'name phone_number')


class SendMessage:
    """
    sms = SendMessage("본문입니다. 문자발송 테스트중입니다.")
    sms.add_user("01012345678", "이름")
    sms.add_user("099-3780-3940", "에러")
    sms.send()
    """
    def __init__(self, msg=""):
        self._data = {
            "userid": _PPURIO_USER_ID,
            "callback": _PPURIO_CALLBACK_PHONE_NUMBER,
            "phone": "",
            "msg": msg,
            "names": "",
            "appdate": "",
            "subject": ""
        }
        self._users = []
        self.message(msg)

    def count(self):
        return len(self._users)

    def add_user(self, phone_number, name=""):
        self._users.append(SMS_USER(name=name, phone_number=phone_number))
        return self

    def _names(self):
        return "|".join(map(lambda x: (x.name or "").replace("-", ""), self._users))

    def _phones(self):
        return "|".join(map(lambda x: (x.phone_number or "").replace("-", ""), self._users))

    def debug(self):
        msg = "=== DEBUG ===\n"
        msg += "userid   : " + self._data["userid"] + "\n"
        msg += "subject  : " + self._data["subject"] + "\n"
        msg += "callback : " + self._data["callback"] + "\n"
        msg += "names    : " + self._names() + "\n"
        msg += "phone    : " + self._phones() + "\n"
        msg += "appdate  : " + self._data["appdate"] + "\n"
        msg += "msg      : " + self._data["msg"]
        return msg

    def debug_print(self):
        print(self.debug())

    def send(self, subject=""):
        """
        subject 는 발송이력을 위한 타이틀이다.
        """
        if self._data["subject"] is None or self._data["msg"] is None:
            raise Exception("empty subject or msg")
        if len(self._users) <= 0:
            raise Exception("send user is empty (add user)")

        params = dict()
        params.update(self._data)
        params["phone"] = self._phones()
        params["names"] = self._names()
        params["subject"] = subject
        data = urllib.parse.urlencode(params)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        req = urllib.request.Request(_PPURIO_SEND_API_URL, data.encode("utf-8"))
        response = urllib.request.urlopen(req, context=ctx)
        result = response.read().decode("utf-8")
        if result:
            rsb = json.loads(result)
            ret_msg = rsb["result"]
            if ret_msg == "ok":
                return int(rsb["ok_cnt"])
            else:
                raise Exception("sms send error : " + ret_msg)
