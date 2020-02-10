from taxdoc.the_bill_api import TheBillAPI, bot_send
import datetime

_today = datetime.date.today().strftime("%Y-%m-%d")
_yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
_hook_url = "https://hook.dooray.com/serv..."

if __name__ == "__main__":
    api = TheBillAPI("아이디", "암호")
    count = 0
    msg = ""
    s = _yesterday
    e = _today
    for r in api.get_unpaid(s, e):
        count += 1
        msg += "{}) {} ({}/{}) - 원출금일: {}, 재출금일: {}\n".format(
            count, r["memberName"], r["serviceType"], r["lastResultMsg"] or "재출금중",
            r["sendDt"] or "-", r["retryDt1"] or "-"
        )
    msg = "===================\n[{} ~ {}] 미납자현황: 총 {}명\n===================\n{}".format(s, e, count, msg)
    print(msg)

    # 두레이 메신저로 보내기
    if count>0:
        bot_send("미납자관리봇", msg, _hook_url)
