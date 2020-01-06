from taxdoc import format_pay_string
from taxdoc.crawler import TheBillCrawler

YEAR = 2019
USER_ID = "<더빌아이디>"
USER_PASSWORD = "<더빌암호>"

if __name__ == "__main__":
    craw = TheBillCrawler(user_id=USER_ID, user_pass=USER_PASSWORD)
    fd = open("./output/the_bill_data.txt", "w")
    # 2019년 데이터를 뽑는다면 다음과 같이 뽑음.
    for row in craw.search(year=YEAR):
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
