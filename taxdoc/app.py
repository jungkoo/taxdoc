#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from taxdoc import LoginSession, default_config
import os
from taxdoc.document_builder import DocumentBuilder
from flask import Flask, request

from taxdoc.tax_api import TaxApi

_document_builder = None
_tax_api = None

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
    return str(r)


if __name__ == '__main__':
    os.environ["TAX_DOC_CONFIG"] = "/Users/tost/IdeaProjects/taxdoc/conf"
    config = default_config()
    _tax_api = TaxApi(LoginSession(user_id=config["LOGIN"]["user"], password=config["LOGIN"]["password"]))
    _document_builder = DocumentBuilder(config)
    app.run()
