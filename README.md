# taxdoc

더빌 사이트에서 납입한 조합비 정보를 PDF 로 다운로드 받을 수 있도록 제공한다.


```python
...
if __name__ == '__main__':
    os.environ["TAX_DOC_CONFIG"] = "/Users/tost/IdeaProjects/taxdoc/conf"  # config.ini , font.ttf, sign.png 경로  
    os.environ["TAX_DOC_YEAR"] = "2020" # 연말정산 귀속년도 
    os.environ["TAX_DOC_KEY"] = "123" # 일종의 매직키로 app.secret_key 값으로 사용된다.
    config = default_config()
    _tax_api = TaxApi(LoginSession(user_id=config["LOGIN"]["user"],
                                   password=config["LOGIN"]["password"]),
                      year=os.environ.get("TAX_DOC_YEAR"))
    _document_builder = DocumentBuilder(config)
    app.secret_key = os.environ.get("TAX_DOC_KEY")
    app.run(host='0.0.0.0', port='10080')
```