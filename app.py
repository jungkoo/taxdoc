#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta

from taxdoc import LoginSession, default_config, ResultRecord
import os
from taxdoc.document_builder import DocumentBuilder
from flask import Flask, request, send_from_directory, after_this_request, render_template, session, redirect, url_for
from taxdoc.tax_api import TaxApi

_document_builder = None
_tax_api = None
counter = 1


def sequence():
    global counter
    counter += 1
    return "{:04d}".format(counter)


app = Flask(__name__, static_url_path='')


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            user_name = request.form['user_name']
            user_phone = request.form['user_phone']
            member_id = _tax_api.get_member_id(user_name, user_phone)
            if member_id is not None:
                doc_id = "{}-{}".format(_tax_api.year, sequence())
                r = _tax_api.get_pay_result(member_id)
                if not r:
                    return "소득공제 데이터가 존재하지 않습니다. 담당자에게 문의주세요"
                else:
                    session['member_id'] = member_id
                    session['result'] = r
                    session['doc_id'] = doc_id
                    session['user_name'] = user_name
                    session['user_phone'] = user_phone
                return redirect(url_for('index'))
            else:
                return "납부 이력을 찾을수 없습니다"
        except:
            return "에러가 발생했습니다"


@app.route("/download", methods=["POST"])
def download():
    if not session.get("member_id"):
        return "다운로드 받을수 없습니다"
    r = session.get("result")
    doc_id = session.get("doc_id")
    user_name = session.get("user_name")
    user_phone = session.get("user_phone")
    user_id = request.form["user_uniq"] if request.method == 'POST' else ""
    user_address = request.form["user_address"] if request.method == 'POST' else ""
    file_name = "{}/{}.pdf".format(os.path.dirname((os.path.abspath(__file__))), doc_id)
    result = ResultRecord(doc_id=doc_id, user_name=user_name, phone_number=user_phone, user_id=user_id,
                          user_address=user_address, password=None, user_email="", pay_date=r.get("date_range", "-"),
                          pay_sum=r.get("pay_sum", "0"))
    doc_id_file = "{}.pdf".format(result.doc_id)
    _document_builder.save(result=result, file_name=file_name)

    @after_this_request
    def cleanup(response):
        if os.path.isfile(file_name):
            os.remove(file_name)
        return response
    return send_from_directory(directory='', filename=doc_id_file)


@app.route("/", methods=['GET', 'POST'])
def index():
    if not session.get("member_id"):
        return render_template("login.html")
    else:
        user_name = session.get("user_name")
        return render_template("index.html", user_name=user_name)


if __name__ == '__main__':
    # os.environ["TAX_DOC_CONFIG"] = "/Users/tost/IdeaProjects/taxdoc/conf"
    # os.environ["TAX_DOC_YEAR"] = "2020"
    # os.environ["TAX_DOC_KEY"] = "123"
    config = default_config()
    _tax_api = TaxApi(LoginSession(user_id=config["LOGIN"]["user"],
                                   password=config["LOGIN"]["password"]),
                      year=os.environ.get("TAX_DOC_YEAR"))
    _document_builder = DocumentBuilder(config)
    app.secret_key = os.environ.get("TAX_DOC_KEY") or "123"
    app.run(host='0.0.0.0', port='10008')
