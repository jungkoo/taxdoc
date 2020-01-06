# taxdoc

## TheBillCrawler

더빌 사이트에서 납입한 조합비 정보를 가져온다.

연말정산이기 때문에 단순히 search 메소드에서 year 값을 통해 필터링된다.

```python
from taxdoc.crawler import TheBillCrawler
craw = TheBillCrawler(user_id="더빌_아이디", user_pass="암호")
for row in craw.search(year=2019):
    print(row)

"""
{'user_name': '원더풀', 'phone_number': '010-1234-1231', 'pay_date': '2019-01-28~2019-11-26', 'pay_sum': 330000}
{'user_name': '손오공', 'phone_number': '010-4567-2355', 'pay_date': '2019-01-28~2019-11-26', 'pay_sum': 330000}
"""
```

```python
from taxdoc import format_pay_string
from taxdoc.crawler import TheBillCrawler

craw = TheBillCrawler(user_id="더빌_아이디", user_pass="암호")
fd = open("step1-the-bill-data.txt", "w")
# 2019년 데이터를 뽑는다면 다음과 같이 뽑음.
for row in craw.search(year=2019): 
    line = "{}\t{}\t{}\t{}".format(row["user_name"], row["phone_number"], format_pay_string(row["pay_date"]), row["pay_sum"])
    print(line)
    fd.write(line)
    fd.write("\n")
fd.close()

"""
## step1-the-bill-data.txt (2019년 데이터)
김길동	010-1212-1010	2019.01 ~ 2019.12	360000
한둘리	010-3434-2020	2019.01 ~ 2019.12	360000
고구미	010-5656-3030	2019.01 ~ 2019.12	360000
아스카	010-7878-4040	2019.01 ~ 2019.12	360000
김칠성	010-9090-5050	2019.01 ~ 2019.12	360000
"""
```

## TaxPdfCreator

연말정산서류를 pdf 로 만들어 준다.

```python
from taxdoc.document import TaxPdfCreator
tax = TaxPdfCreator(doc_id="2020-0001", user_name="둘리", user_id=None, price_date="2019.01~2019.12", price_all=35000)
tax.save("./output/asdf.pdf", "0101", True)
```


## EmailSender

이메일을 발송한다. 첨부파일을


```python
from taxdoc.sender import EmailSender
attach_file = "./output/a.pdf"
email = EmailSender(domain="smtp.dooray.com", port=465, email="admin@naverunion.dooray.com", password="암호")
email.send("1@koreausa.com", "제목", "본문입니다", attach_file)
email.close()
```