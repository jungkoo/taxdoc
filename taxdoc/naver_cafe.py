#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from abc import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class NCafeAutoJoin(metaclass=ABCMeta):
    def __init__(self, driver_path, cafe_url="https://cafe.naver.com/nunion"):
        option = webdriver.ChromeOptions()
        # option.headless = True
        option.add_argument('--lang=ko-KR')
        option.add_argument('--user-agent="Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/37.0.2049.0 Safari/537.36"')
        option.add_argument("window-size=1024x768")
        d = webdriver.Chrome(driver_path, chrome_options=option)
        d.implicitly_wait(3)
        self._cafe_url = cafe_url
        self._driver = d
        self.club_id = 0

    def get_element(self, by, value, wait=False):
        print("get_elem,ent => {}, value={}, wait={}", by, value, wait)
        if not wait:
            if by == By.ID:
                return self._driver.find_element_by_id(value)
            if by == By.CSS_SELECTOR:
                return self._driver.find_element_by_css_selector(value)
            if by == By.CLASS_NAME:
                return self._driver.find_element_by_class_name(value)
            if by == By.LINK_TEXT:
                return self._driver.find_element_by_link_text(value)

        try:
            element = WebDriverWait(self._driver, 20).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            self._driver.quit()
        raise Exception("element error !")

    def login(self, user_name, user_password):
        self._driver.get("https://nid.naver.com/nidlogin.login?url=" + self._cafe_url)
        self._driver.execute_script("""
            document.querySelector("#id").value = "{}"; 
            document.querySelector("#pw").value = "{}";
        """.format(user_name, user_password))
        webdriver.ActionChains(self._driver).move_by_offset(712, 384).perform()
        self.get_element(By.ID, "log.login").click()
        self.club_id = self._extract_club_id()
        return self

    def _extract_club_id(self):
        self.get_element(By.CLASS_NAME, "ico_setting", True).click()
        url = self._driver.execute_script("return document.URL")
        code = "clubid="
        club_id = url[url.index(code)+len(code):].split("&")[0]
        return club_id

    @abstractmethod
    def user_check(self):
        pass


class Cafe(NCafeAutoJoin):

    def user_check(self):
        pass

