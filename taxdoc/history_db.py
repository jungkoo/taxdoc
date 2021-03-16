#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tinydb import Query, TinyDB
import time
import uuid


class HistoryDB:
    def __init__(self, head_doc_id="DOC", json_path="./tax_history.json"):
        self._doc_id_head = head_doc_id
        self._db = TinyDB(json_path)

    def insert(self, user_name, user_phone):
        query = Query()
        key = str(uuid.uuid4())
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        data = {"key": key, "doc_id": "", "user_name": str(user_name),
                "user_phone": user_phone, "date": now, "status": ""}
        seq = self._db.insert(data)
        doc_id = "{}-{}".format(self._doc_id_head, seq)
        self._db.update({"doc_id": doc_id}, query.key == key)
        return key

    def status(self, key, value):
        query = Query()
        self._db.update({"status": value}, query.key == key)

    def get(self, key):
        query = Query()
        value = self._db.search(query.key == key)
        if len(value) == 1:
            return value[0]
        else:
            return None

    def get_doc_id(self, key):
        value = self.get(key)
        if value:
            return value["doc_id"]
        return None

    def count(self):
        return len(self._db)

    def print(self, with_key=False):
        print("doc_id\tdate\tuser_name\tuser_phone\tstatus{}".format("\tkey" if with_key else ""))
        for item in self._db:
            row = "{doc_id}\t{date}\t{user_name}\t{user_phone}\t{status}".format(**item)
            row += "\t{}".format(item["key"]) if with_key else ""
            print(row)
