#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import taxdoc
from taxdoc import union_member_generator
from taxdoc.document import TaxPdfCreator
from taxdoc.sender import EmailSender

taxdoc.document.USER_DATE = "2020 년 1월 2일"
taxdoc.document.GROUP_DATE = "2020 년 1월 9일"
INPUT_FILE_PATH = "./input/taxdoc_input_sample.txt"
SMTP_DOMAIN = "smtp.dooray.com"
SMTP_PORT = 465
SMTP_EMAIL = "admin@naverunion.dooray.com"
SMTP_PASSWORD = "<암호>"

TITLE = "[테스트] 2019년 귀속 연말정산용 기부금 영수증 발급 (test222 발송)"
CONTENTS = """
안녕하세요,
테스트 첨부발송 홍길동 사무장 입니다.

신청하신 2019년 귀속 연말정산용 기부금 영수증을 발급해 드립니다.
첨부파일 확인 부탁드리며, 이상이 있을 경우 카카오플러스친구 또는 홍길동 사무장에게 직접 연락 주세요.
개인정보를 위한 첨부파일 비밀번호는 생년월일 6자리 입니다. 
(만약, 주민번호 정보를 입력하지 않았다면 전화번호 뒤 6자리입니다)

함께 해 주셔서 늘 감사드립니다. :-)

Ps.
이 메일을 발송 전용 메일입니다. 
""".replace("\n", "<br/>")

if __name__ == "__main__":
    fd_offline = open("./output/offline/list.txt", "w")
    fd_email = open("./output/email/list.txt", "w")
    offline_count = 0
    email_count = 0
    email_sender = EmailSender(domain=SMTP_DOMAIN, port=SMTP_PORT, email=SMTP_EMAIL, password=SMTP_PASSWORD)
    for u in union_member_generator(INPUT_FILE_PATH, first_line_skip=True):
        tax = TaxPdfCreator(doc_id=u.doc_id, user_name=u.user_name,
                            user_id="" if u.user_id is None or len(u.user_id) == 0 else u.user_id,
                            price_date=u.pay_date, price_all=int(u.pay_sum))
        print(str(u))
        if len(u.user_email) == 0:
            offline_count += 1
            attach_file = "./output/offline/{}.pdf".format(u.doc_id)
            tax.save(attach_file, u.password, True)
            fd_offline.write(str(u))
            fd_offline.write("\n")
        else:
            email_count += 1
            attach_file = "./output/email/{}.pdf".format(u.doc_id)
            tax.save(attach_file, u.password, True)
            email_sender.send(u.user_email, TITLE, CONTENTS, attach_file)
            fd_email.write(str(u))
            fd_email.write("\n")

        # email session limit 100 send. (100 over reconnect)
        if email_count % 100 == 0 and email_count != 0:
            email_sender.close()
            email_sender = EmailSender(domain=SMTP_DOMAIN, port=SMTP_PORT, email=SMTP_EMAIL, password=SMTP_PASSWORD)

    fd_offline.close()
    fd_email.close()
    email_sender.close()
    print("[END] offline: {}, email: {}".format(offline_count, email_count))