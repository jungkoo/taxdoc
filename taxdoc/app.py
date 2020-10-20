#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc import LoginSession, default_config, ResultRecord
import os
from taxdoc.document_builder import DocumentBuilder
from flask import Flask, request, send_from_directory
from flask import send_file
from flask import make_response
from taxdoc.tax_api import TaxApi
import io
import hashlib

_document_builder = None
_tax_api = None
_cache = dict(doc_id=1)


def sequence():
    seq = _cache["doc_id"]
    _cache["doc_id"] = seq + 1
    return "{:04d}".format(seq)


app = Flask(__name__)


@app.route("/taxdoc")
def text_doc():
    name = request.args.get('name', "조합")
    number = request.args.get('number', "0000")
    print("name={}, number={}".format(name, number))
    member_id = _tax_api.get_member_id(name, number)
    print("member_id={}".format(member_id))
    r = _tax_api.get_pay_result(member_id)
    print("r==> {}".format(r))
    doc_id = "{}-{}".format(_tax_api.year, sequence())
    print("doc_id=> {}".format(doc_id))
    result = ResultRecord(doc_id=doc_id, user_name=name, phone_number=number, user_id="",
                          user_address="", password=None, user_email="", pay_date=r.get("date_range", "-"),
                          pay_sum=r.get("pay_sum", "0"))
    _document_builder.save(result=result)
    return send_from_directory(directory='', filename="{}.pdf".format(doc_id))


if __name__ == '__main__':
    os.environ["TAX_DOC_CONFIG"] = "/Users/tost/IdeaProjects/taxdoc/conf"
    config = default_config()
    _tax_api = TaxApi(LoginSession(user_id=config["LOGIN"]["user"], password=config["LOGIN"]["password"]))
    _document_builder = DocumentBuilder(config)

    app.run()
