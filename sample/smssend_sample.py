#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc.sender import SendMessage

if __name__ == "__main__":
    sms = SendMessage("본문입니다. [*이름*] 문자발송 테스트중입니다. 길겔기리ㅑ얼미ㅏㄴ어랴ㅣㅁㅇ너리먼림ㅇ너ㅣ럼ㅇ니ㅏ럼니럼니ㅓㅇㅇㅇ리ㅏㅁ넝리ㅏㅁ너이ㅏ럼ㄴ아ㅣ럼나ㅣ어리ㅏㅁ넝리ㅏ먼아ㅣ럼나ㅣ얼마ㅣㅇ너라ㅣ먼리ㅏㅓㅁㄴ아ㅣ런ㅁ이라ㅓㅇㄴ미ㅏㄹㅁㄴ")
    sms.subject("제목입니다 [*이름*] 제목")
    sms.add_user("010-1234-5678", "홍길동")
    sms.add_user("099-3780-3940", "에러")
    sms.send()