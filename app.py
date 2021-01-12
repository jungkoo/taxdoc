#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta
from taxdoc import LoginSession, ResultRecord
import os
from taxdoc.document_builder import DocumentBuilder
from flask import Flask, request, send_from_directory, after_this_request, render_template, session, redirect, url_for

from taxdoc.history_db import HistoryDB
from taxdoc.tax_api import TaxApi
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from taxdoc.user_key import normalized_phone_number, user_key

_document_builder = None
_tax_api = None
_sub_name = os.environ.get("TAX_DOC_SUB_NAME") or "지회명"
_db = None

app = Flask(__name__, static_url_path='')


def code_check(user_name, phone_number, code):
    uk = user_key(user_name, phone_number, app.secret_key)
    if code != app.secret_key and code != uk:
        raise ValueError("CODE 값 입력이 잘못되었습니다")


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        code = request.form["code"]
        return render_template('login.html', code=code, sub_name=_sub_name)
    else:
        try:
            code = request.form["code"]
            user_name = request.form['user_name']
            user_phone = request.form['user_phone']
            code_check(user_name=user_name, phone_number=user_phone, code=code)
            member_id = _tax_api.get_member_id(user_name, user_phone)
            if member_id is not None:
                r = _tax_api.get_pay_result(member_id)
                rd = _tax_api.get_pay_detail_list(member_id)
                if not r:
                    return render_template('error.html', msg="소득공제 데이터가 존재하지 않습니다.")
                else:
                    session['member_id'] = member_id
                    session['result'] = r
                    session['detail'] = rd
                    session['user_name'] = user_name
                    session['user_phone'] = user_phone
                return redirect(url_for('index'))
            else:
                return render_template('error.html', msg="납부이력을 찾을 수 없습니다")
        except ValueError as e:
            return render_template('error.html', msg=str(e))


@app.route("/download", methods=["POST"])
def download():
    if not session.get("member_id"):
        return "다운로드 받을수 없습니다"
    r = session.get("result")
    user_name = session.get("user_name")
    user_phone = session.get("user_phone")
    user_id = request.form["user_uniq"] if request.method == 'POST' else ""
    user_address = request.form["user_address"] if request.method == 'POST' else ""
    key = _db.insert(user_name=user_name, user_phone=user_phone)
    doc_id = _db.get_doc_id(key)
    file_name = "{}/{}.pdf".format(os.path.dirname((os.path.abspath(__file__))), doc_id)
    result = ResultRecord(doc_id=doc_id, user_name=user_name, phone_number=normalized_phone_number(user_phone),
                          user_id=user_id, user_address=user_address, password=None, user_email="",
                          pay_date=r.get("date_range", "-"), pay_sum=r.get("pay_sum", "0"))
    doc_id_file = "{}.pdf".format(result.doc_id)
    _document_builder.save(result=result, file_name=file_name)
    _db.status(key=key, value="OK")
    print("[{}] name:{}, phone:{} ==> {}  ", doc_id, user_name, user_phone, result)

    @after_this_request
    def cleanup(response):
        if os.path.isfile(file_name):
            os.remove(file_name)
        return response
    return send_from_directory(directory='', filename=doc_id_file)


@app.route("/", methods=['GET', 'POST'])
def index():
    if not session.get("member_id"):
        code = request.args.get("code", "")
        return render_template("login.html", year=_tax_api.year, code=code, sub_name=_sub_name)
    else:
        user_name = session.get("user_name")
        detail = session.get('detail')
        return render_template("index.html", user_name=user_name, year=_tax_api.year, detail=detail)


if __name__ == '__main__':
    """
    # 독커 이미지 빌드
    docker build -t taxdoc .
    
    # 독커실행
    ``    
    SHELL_PATH=`pwd -P` ; docker run -p 10080:10080  
       -v ${SHELL_PATH}:/history 
       -e TAX_DOC_KEY=<시크릿키> 
       -e TAX_DOC_YEAR=<연말정산 귀속년도 yyyy>
       -e TAX_DOC_USER=<더빌 아이디:필수> 
       -e TAX_DOC_PASSWORD=<더빌 패스워드:필수>
       -e TAX_DOC_SUB_NAME=<지회이름>
       -e TAX_DOC_DB_POST=<문서번호 구분값: 여러대의 서버를 구분하기위한값>
       -e TAX_DOC_DB=<히스토리가 저장될 경로>
       -e TAX_DOC_SIGN=<사인이미지 변경시 사용>
       tost82/taxdoc:v2 
    """

    user = os.environ.get("TAX_DOC_USER")
    passwd = os.environ.get("TAX_DOC_PASSWORD")
    year = os.environ.get("TAX_DOC_YEAR") or "2019"
    key = os.environ.get("TAX_DOC_KEY") or "123"
    db_path = os.environ.get("TAX_DOC_DB") or "tax_doc_history.json"
    db_post = os.environ.get("TAX_DOC_DB_POST") or ""

    if not user or not passwd:
        raise Exception("[ERROR] THE BILL LOGIN : $TAX_DOC_USER , $TAX_DOC_PASSWORD")

    _db = HistoryDB(head_doc_id=year+db_post, json_path=db_path)
    _tax_api = TaxApi(LoginSession(user_id=user, password=passwd), year=int(year))
    _document_builder = DocumentBuilder()
    app.secret_key = key
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(10080)
    IOLoop.instance().start()
