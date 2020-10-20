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
           "이름: <input name='name'/><br/>" \
           "전화번호: <input name='number'/><br/>" \
           "주민번호(인쇄시사용): <input name='jumin'/><br/>" \
           "다: <input name='key'>test</value><br/>" \
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
    print("member_id={}".format(member_id))
    r = _tax_api.get_pay_result(member_id)
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
            print("no file =>" , doc_id_file)
        return response
    return send_from_directory(directory='', filename=doc_id_file)


if __name__ == '__main__':
    os.environ["TAX_DOC_CONFIG"] = "/Users/tost/IdeaProjects/taxdoc/conf"
    config = default_config()
    _tax_api = TaxApi(LoginSession(user_id=config["LOGIN"]["user"], password=config["LOGIN"]["password"]))
    _document_builder = DocumentBuilder(config)
    app.run(host='0.0.0.0', port='42000', debug=True)
    # app.run()
