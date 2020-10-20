#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc import LoginSession, default_config, ResultRecord
import os
from taxdoc.document_builder import DocumentBuilder
from flask import Flask, request, send_from_directory, after_this_request
from taxdoc.tax_api import TaxApi

_document_builder = None
_tax_api = None
_cache = dict(doc_id=1)


def sequence():
    seq = _cache["doc_id"]
    _cache["doc_id"] = seq + 1
    return "{:04d}".format(seq)


app = Flask(__name__)


@app.route("/")
def index():
    return "{} 연말정산<br/><form action='/taxdoc'>" \
           "# 필수입력 -- <br/>" \
           "이름: <input name='name'/><br/>" \
           "전화번호: <input name='number'/><br/>" \
           "<br/># 나중에 문자로 개인 코드를 넣어야할거 같음<br/>개인코드: <input name='key' value='test' readonly='true'/><br/>" \
           "<br/><br/># 선택사항(입력안해도 동작함) -- <br/>" \
           "주민번호(인쇄할때 단순 출력하는용도 입력한그대로...): <input name='jumin'/><br/>" \
           "<button type='submit'>ok</button><form>".format(_tax_api.year)


@app.route("/taxdoc")
def text_doc():
    name = request.args.get('name', "조합")
    number = request.args.get('number', "0000")
    jumin = request.args.get('jumin', "")
    key = request.args.get('key', "")
    if key != "test":
        return "시크릿 코드 잘못됨"
    print("name={}, number={}".format(name, number))
    member_id = _tax_api.get_member_id(name, number)
    if not member_id:
        return "해당 유저 정보 없음 (이름: {}, 전화번호: {} 확인요망 (전화번호 모두 적어주셔야합니다 010-1234-5678)".format(name, number)
    print("member_id={}".format(member_id))
    r = _tax_api.get_pay_result(member_id)
    if not r:
        return "소득공제 데이터가 존재하지 않습니다. 메일로 문의주세요"
    print("r==> {}".format(r))
    doc_id = "{}-{}".format(_tax_api.year, sequence())
    doc_id_file = "{}.pdf".format(doc_id)
    print("doc_id=> {}".format(doc_id))
    result = ResultRecord(doc_id=doc_id, user_name=name, phone_number=number, user_id=jumin,
                          user_address="", password=None, user_email="", pay_date=r.get("date_range", "-"),
                          pay_sum=r.get("pay_sum", "0"))
    _document_builder.save(result=result)

    @after_this_request
    def cleanup(response):
        if os.path.isfile(doc_id_file):
            print("delete => ", doc_id_file)
            os.remove(doc_id_file)
        else:
            print("no file =>", doc_id_file)
        return response
    return send_from_directory(directory='', filename=doc_id_file)


if __name__ == '__main__':
    os.environ["TAX_DOC_CONFIG"] = "/Users/tost/IdeaProjects/taxdoc/conf"
    config = default_config()
    _tax_api = TaxApi(LoginSession(user_id=config["LOGIN"]["user"], password=config["LOGIN"]["password"]), year=2020)
    _document_builder = DocumentBuilder(config)
    app.run(host='0.0.0.0', port='42000', debug=True)
    # app.run()
