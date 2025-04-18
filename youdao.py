
    # name: "有道云签到"
    # cron: 20 0,8 * * *
    # 更新时间:2025-03-01
    # 变量YOUDAO_COOKIE=有道网页cookie

import os
import requests
import json

from dailycheckin import CheckIn

class YouDao(CheckIn):
    name = "有道云笔记"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def sign(cookies):
        ad_space = 0
        refresh_cookies_res = requests.get(
            "http://note.youdao.com/login/acc/pe/getsess?product=YNOTE", cookies=cookies
        )
        cookies = dict(refresh_cookies_res.cookies)
        url = "https://note.youdao.com/yws/api/daupromotion?method=sync"
        res = requests.post(url=url, cookies=cookies)
        if "error" not in res.text:
            checkin_response = requests.post(
                url="https://note.youdao.com/yws/mapi/user?method=checkin",
                cookies=cookies,
            )
            for i in range(3):
                ad_response = requests.post(
                    url="https://note.youdao.com/yws/mapi/user?method=adRandomPrompt",
                    cookies=cookies,
                )
                ad_space += ad_response.json().get("space", 0) // 1048576
            if "reward" in res.text:
                sync_space = res.json().get("rewardSpace", 0) // 1048576
                checkin_space = checkin_response.json().get("space", 0) // 1048576
                space = sync_space + checkin_space + ad_space
                youdao_message = f"+{space}M"
            else:
                youdao_message = "获取失败"
        else:
            youdao_message = "Cookie 可能过期"
        return youdao_message

    def main(self):
        # 从青龙的环境变量中直接获取 cookie
        youdao_cookie = os.environ.get("YOUDAO_COOKIE", "")
        if not youdao_cookie:
            print("未配置 YOUDAO_COOKIE 环境变量")
            return "未配置 YOUDAO_COOKIE 环境变量"
        
        # 将 cookie 字符串转换为字典
        youdao_cookie_dict = {
            item.split("=")[0]: item.split("=")[1]
            for item in youdao_cookie.split("; ")
        }
        
        try:
            ynote_pers = youdao_cookie_dict.get("YNOTE_PERS", "")
            uid = ynote_pers.split("||")[-2]
        except Exception as e:
            print(f"获取账号信息失败: {e}")
            uid = "未获取到账号信息"
        
        msg = self.sign(cookies=youdao_cookie_dict)
        msg = [
            {"name": "帐号信息", "value": uid},
            {"name": "获取空间", "value": msg},
        ]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    # 直接使用环境变量获取cookie
    _check_item = {"cookie": os.environ.get("YOUDAO_COOKIE", "")}
    
    # 如果没有配置cookie，直接返回
    if not _check_item["cookie"]:
        print("YOUDAO_COOKIE 环境变量为空，无法执行签到")
    else:
        print(YouDao(check_item=_check_item).main())
