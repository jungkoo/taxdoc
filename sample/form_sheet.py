from datetime import datetime
from taxdoc.sheet import GoogleFormSheet
import re
if __name__ == "__main__":
    sheet = GoogleFormSheet("https://docs.google.com/spreadsheets/d/1u...cBqaJ6pI/edit#gid=1641959086")
    output = sheet.find_date(datetime(2018, 9, 18), datetime(2018, 10, 10, 23, 59, 59))
    for r in output:
        print(r)




