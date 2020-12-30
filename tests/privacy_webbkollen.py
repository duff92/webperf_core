# -*- coding: utf-8 -*-
import sys
import socket
import ssl
import json
import requests
import urllib  # https://docs.python.org/3/library/urllib.parse.html
import uuid
import re
from bs4 import BeautifulSoup
import config
from tests.utils import *
import gettext
_ = gettext.gettext

# DEFAULTS
request_timeout = config.http_request_timeout
useragent = config.useragent


def run_test(langCode, url):
    import time
    points = 5.0
    review = ''
    return_dict = dict()

    language = gettext.translation(
        'privacy_webbkollen', localedir='locales', languages=[langCode])
    language.install()
    _ = language.gettext

    print(_('TEXT_RUNNING_TEST'))

    api_lang_code = 'en'
    if langCode == 'sv':
        api_lang_code = 'sv'
    elif langCode == 'de':
        api_lang_code = 'de'
    elif langCode == 'no':
        api_lang_code = 'no'

    url = 'https://webbkoll.dataskydd.net/{1}/check?url={0}'.format(
        url.replace('/', '%2F').replace(':', '%3A'), api_lang_code)
    headers = {
        'user-agent': 'Mozilla/5.0 (compatible; Webperf; +https://webperf.se)'}
    request = requests.get(url, allow_redirects=False,
                           headers=headers, timeout=request_timeout*2)

    time.sleep(20)

    # hämta det faktiska resultatet
    soup = BeautifulSoup(request.text, 'html.parser')
    final_url = None
    for link in soup.find_all('a'):
        final_url = 'https://webbkoll.dataskydd.net{0}'.format(
            link.get('href'))

    if final_url != None:
        request2 = requests.get(
            final_url, allow_redirects=True, headers=headers, timeout=request_timeout*2)
        soup2 = BeautifulSoup(request2.text, 'html.parser')
        summary = soup2.find_all("div", class_="summary")
        results = soup2.find_all(class_="result")

        for result in results:
            header = result.find("h3")
            # print(type(header.contents))
            #- alert
            points -= (len(header.find_all("i", class_="alert")) * 1.0)
            #- warning
            points -= (len(header.find_all("i", class_="warning")) * 0.5)

            divs = result.find_all("div")
            for div in divs:
                # print(type(h3a.contents))
                #-- alert
                points -= (len(div.find_all("i", class_="alert")) * 0.1)
                #-- warning
                points -= (len(div.find_all("i", class_="warning")) * 0.05)

        mess = ''

        for line in summary:
            mess += '* {0}'.format(re.sub(' +', ' ', line.text.strip()).replace(
                '\n', ' ').replace('    ', '\n* ').replace('Kolla upp', '').replace('Look up', '').replace('  ', ' '))

        if points == 5:
            review = ('TEXT_REVIEW_VERY_GOOD')
        elif points >= 4:
            review = _('TEXT_REVIEW_IS_GOOD')
        elif points >= 3:
            review = _('TEXT_REVIEW_IS_OK')
        elif points >= 2:
            review = _('TEXT_REVIEW_IS_BAD')
        else:
            review = _('TEXT_REVIEW_IS_VERY_BAD')
            points = 1.0

        review += mess

        return (points, review, return_dict)
