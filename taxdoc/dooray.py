from selenium import webdriver
import os
# https://chromedriver.storage.googleapis.com/index.html?path=81.0.4044.69/


class Dooray:
    def __init__(self, user, passwd, domain="naverunion"):
        driver_path = os.path.abspath(__file__).replace("dooray.py", "chromedriver")
        self._driver = webdriver.Chrome(driver_path)
        self._driver.implicitly_wait(3)
        self._driver.get("https://{}.dooray.com".format(domain))
        self._driver.find_element_by_css_selector("input[title=\"아이디\"]").send_keys(user)
        self._driver.find_element_by_css_selector("input[title=\"비밀번호\"]").send_keys(passwd)
        self._driver.find_element_by_css_selector("button[type=\"submit\"]").click()

