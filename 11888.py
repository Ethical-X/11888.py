import secrets
import re
import requests
import argparse
from bs4 import BeautifulSoup as bsoup
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="victims last or full name.", type=str, required=True)
parser.add_argument("-o", "--outfile", help="writes results to results.txt")
parser.add_argument("-s", "--sleep", help="adds delay between every get request crawl to reduce noise/rate limiting", type=int)
args = parser.parse_args()

def outfile():
        pass


def main(headers):
        victims_info = set()
        page_num = 1
        print("\n")
        print("‐-----------------------------")
        print("| STARTING SEARCH  $^_^$     |")
        print("‐-----------------------------")
        while True:

                if args.sleep:
                        delay = args.sleep
                else:
                        delay = 1.2
                vic_name = args.name
                vic_name = vic_name.replace(" ", "%20")
                query = f"https://www.11888.gr/white-pages/?query={vic_name}&amp%3Bpage=3&page={page_num}"
                vic_urls = set()

                # selects a random User agent from headers
                ua = secrets.choice(range(1,11))
                header = {"User-Agent": f"{headers.get(ua)}"}

                # this request returns the search results of the victim name
                html_content = requests.get(query, headers=header)

                if html_content.status_code == 200:
                        html_content = html_content.text

                        #grabs all urls that lead to a victim
                        soup = bsoup(html_content, 'html.parser')
                        for link in soup.find_all('a'):
                                url = link.get('href')
                                if 'white' in url and 'location' not in url and url != '/white-pages/':
                                        vic_urls.add(url)
                                                                                                                                                                               # visits each victim url and grabs info
                        for vic_url in vic_urls:

                                ua = secrets.choice(range(1,11))
                                header = {"User-Agent": f"{headers.get(ua)}"}

                                vic_url = vic_url.lstrip("/")
                                victim_html = requests.get(f"https://www.11888.gr/{vic_url}", headers=header)

                                vic_soup = bsoup(victim_html.text, "html.parser")

                                name = vic_soup.title.string.strip("| 11888.gr")
                                addr = vic_soup.select_one("span.tw-text-gray-secondary.tw-text-left.tw-text-sm.tw-select-none")
                                tel = re.search("tel:", victim_html.text)
                                tel = victim_html.text[tel.start():tel.start() + 14]

                                if name:
                                        print(f"| Name: {name}")
                                else:
                                        name = None
                                if addr:
                                        print(f"| Address: {addr.get_text(strip=True)}")
                                else:
                                        addr = None
                                if tel:
                                        print(f"| Phone: {tel}")
                                else:
                                        tel = None
                                print("‐-----------------------------")

                                victims_info.add((name, addr, tel))
                                sleep(delay)

                        # page_num is incremented so recursion can happen.
                        page_num += 1
                        if vic_urls:
                                continue
                        else:
                                print("| Finished search")
                                print(f"| Gathered info on {len(victims_info)} people.")
                                print("‐-----------------------------")
                                return

                        vic_urls = set()

                else:
                        return print("| didnt get 200 OK")


agents = {1:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        2:"Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        3:"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        4:"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
        5:"Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:139.0) Gecko/20100101 Firefox/139.0",
        6:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/137.0.3296.52 Chrome/137.0.0.0 Safari/537.36",
        7:"Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        8:"Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
        9:"Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        10:"Mozilla/5.0 (Linux; Android 15; SM-S938B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/28.0 Chrome/137.0.0.0 Mobile Safari/537.36"}
main(agents)
