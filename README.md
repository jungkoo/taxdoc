# taxdoc

## TheBillCrawler

더빌 사이트에서 납입한 조합비 정보를 가져온다.

연말정산이기 때문에 단순히 search 메소드에서 year 값을 통해 필터링된다.

```python
craw = TheBillCrawler(user_id="아이디", user_pass="암호")
for row in craw.search(year=2019):
    print(row)

"""
{'user_name': '원더풀', 'phone_number': '010-1234-1231', 'pay_date': '2019-01-28~2019-11-26', 'pay_sum': 330000}
{'user_name': '손오공', 'phone_number': '010-4567-2355', 'pay_date': '2019-01-28~2019-11-26', 'pay_sum': 330000}
"""
```