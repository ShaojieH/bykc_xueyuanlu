# coding=utf-8

import json
import time

from lxml import etree
from requests import session

login_vpn_url = "https://e.buaa.edu.cn/users/sign_in"
login_sso_url = "https://sso.e.buaa.edu.cn/login"
bykc_query_url = "https://bykc.e.buaa.edu.cn/sscv/querySelectableCourse"
token_url = "https://sso-443.e.buaa.edu.cn/login?TARGET=https%3A%2F%2Fbykc.e.buaa.edu.cn%2Fsscv%2FcasLogin"
session = session()
sleep_s = 10
username = input('username:')
password = input('password:')
auth_token = ""

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/77.0.3865.90 Safari/537.36",
    'Referer': 'http://bykc.e.buaa.edu.cn',
    'Host': 'bykc.e.buaa.edu.cn',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none'
}


def login_vpn():
    print("starting vpn log in ...")
    login_page = session.get(login_vpn_url)
    login_page.encoding = 'utf8'
    root = etree.HTML(login_page.content)
    if "青年北航" in login_page.text:
        print("vpn already logged in")
        return True
    authenticity_token = root.xpath('//input[@name="authenticity_token"]/@value')[0]
    login_result = session.post(login_vpn_url, data={
        'utf8': '✓',
        'user[login]': username,
        'user[password]': password,
        'user[dymatice_code]': 'unknown',
        'commit': '登录 Login',
        'authenticity_token': authenticity_token
    })
    result = " 青年北航" in login_result.text
    print("vpn log is done, result={0}".format(result))
    return result


def login_sso():
    print("starting sso log in ...")
    login_page = session.get(login_sso_url)
    print(login_page.text)
    login_page.encoding = 'utf8'
    root = etree.HTML(login_page.content)
    if "You have successfully logged in" in login_page.text or "退出登录" in login_page.text:
        print("sso already logged in")
        return True
    form = root.xpath('//div[@class="clearfix login_btncont"]')[0]
    lt = root.xpath('//input[@name="lt"]/@value')[0]
    execution = form.xpath(
        '//input[@name="execution"]/@value')[0]
    _eventId = form.xpath(
        '//input[@name="_eventId"]/@value')[0]
    login_result = session.post(login_sso_url, data={
        'submit': '登录',
        'username': username,
        'password': password,
        'code': '',
        'lt': lt,
        'execution': execution,
        "_eventId": _eventId
    })
    result = 'You have successfully logged in' in login_result.text
    print("sso log in done, result={0}".format(result))
    return result


def get_auth_token():
    global auth_token
    print("getting auth token...")
    redirect_1 = \
        session.get(token_url,
                    allow_redirects=False).headers['Location']
    print("redirecting to: {0}".format(redirect_1))
    redirect_2 = session.get(url=redirect_1, headers=default_headers, allow_redirects=False).headers['Location']
    print("redirecting to: {0}".format(redirect_2))
    redirect_3 = session.get(url=redirect_2, headers=default_headers, allow_redirects=False).headers['Location']
    print("redirecting to: {0}".format(redirect_3))
    auth_token = redirect_3.split('=')[1]
    print("token: {0}".format(auth_token))


def check_bykc_course():
    print("starting routine...")
    response = session.post(url=bykc_query_url, data={}, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/77.0.3865.120 Safari/537.36",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://bykc.e.buaa.edu.cn/system/course-mine",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://bykc.e.buaa.edu.cn",
        "Accept": "application/json",
        "auth_token": auth_token
    })
    # print("response : {0}".format(response.text))

    response_data = json.loads(response.text)
    for course in response_data['data']:
        if "学院路校区" in course['courseCampusList']:
            print(
                'name={0}, '
                'maxCount={1}, '
                'currentCount={2}, '
                'select start date={3}, '
                'select end date={4}, '
                'start date={5}, '
                'position={6}'.format(
                    course['courseName'],
                    course['courseMaxCount'],
                    course['courseCurrentCount'],
                    course['courseSelectStartDate'],
                    course['courseSelectEndDate'],
                    course['courseStartDate'],
                    course['coursePosition'])
            )
    print("routine done")


def main():
    while True:
        try:
            login_vpn()
            # login_sso()   # not needed
            get_auth_token()
            check_bykc_course()
        except Exception as e:
            print("error: {0}".format(str(e)))
        finally:
            time.sleep(sleep_s)


if __name__ == '__main__':
    main()
