import time
import requests
import random
import urllib3
import base64
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import socket
import sys
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup

"""
This script was used to perform the benchmark for this blog post: 
https://www.scrapingbee.com/blog/best-free-proxy-list-web-scraping/"

In order to run it you'll need:
Python3
pip install requests
pip install beautifulsoup4

A ScrapingBee API key you can get one for free with 1000 credits here: https://www.scrapingbee.com/ 
A proxy provider access, you need to put the proxy URL at line 42
"""


#choose between instagram, google and amazon, top1000
website_to_test = 'instagram'

most_common_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
]


def request_with_proxy(url):
    
    #replace with your mobile proxy provider URL 
    proxy = ""
    payload = {
        "proxies": {"http": proxy, "https": proxy},
        "url": url,
        "verify": False,
        "timeout": 60,
        "headers": {
            "User-Agent": random.choice(most_common_user_agents),
            "referrer": "https://www.google.com",
        },
    }
    
    try:
        start = time.time()
        resolved_url = ''
        response = requests.get(**payload)
        status_code = response.status_code
        resolved_url = response.url
        if 200 <= status_code <= 299 or status_code == 404:
            body = response.text
            #print(body)
        else:
            body = f"Server responded with {status_code}"
    except Exception as e:
        body, status_code = str(e), 500
        print("-------")
        print(time.time() - start, proxy, body, e)
        print("-------")
        return {"statusCode": 500, "body": body, "time": time.time() - start, "resolved_url": resolved_url}
    finally:
        return {"statusCode": status_code, "body": body, "time": time.time() - start,  "resolved_url": resolved_url}

total_requests = 1000

blocked = 0
concurrency = 20
error_status_code = 0
blocked_message = 0
success_requests = 0
banned_ips = {}
banned_ips = set()
pool = ThreadPool(concurrency)

lines = open(f'{website_to_test}.csv', "r").read().split("\n") * 1000
urls = lines[:total_requests]

results = pool.map(request_with_proxy, urls)
pool.close()
pool.join()
times = []
print(f"Results size: {len(results)}")

for i in results:
    if i["statusCode"] != 200 or "Server responded with 429" in i["body"] or "automated queries" in i["body"] or "Amazon CAPTCHA" in i["body"] or '/accounts/login/' in i["resolved_url"]:
        if i["statusCode"] != 200:
            error_status_code += 1
        if "Server responded with 429" in i["body"] or "automated queries" in i["body"] or "Amazon CAPTCHA" in i["body"] or '/accounts/login/' in i["resolved_url"]:
            blocked_message += 1
        blocked += 1
    else:
        success_requests += 1
        times.append(i["time"])


print(f"Concurrency:  {concurrency}")
print(f"Requests sent:  {total_requests}")
print(f"Successful requests: {success_requests}")
print(f"Error status_code: {error_status_code} / {total_requests}")
print(f"Blocked message : {blocked_message} / {total_requests}")
print(f"Average time per request: {sum(times) / len(times)}")