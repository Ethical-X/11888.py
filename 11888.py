import secrets
import re
import requests
import argparse

from bs4 import BeautifulSoup as bsoup
from time import sleep
from contextlib import redirect_stdout
from rich.console import Console

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="victims last or full name.", type=str, required=True)
parser.add_argument("-o", "--outfile", help="writes results to results.txt", action="store_true")
parser.add_argument("-s", "--sleep", help="adds delay between every get request crawl to reduce noise/rate limiting", type=float)
args = parser.parse_args()

def main(headers, rich_console):

        victims_info = set()
        page_num = 1

        print("\n")
        rich_console.print("[bright_blue]|-----------------------------[/bright_blue]")
        rich_console.print("[bright_blue]|[/bright_blue][bright_red]———STARTING SEARCH[/bright_red][green]  $^_^$[/green][bright_blue]   |[/bright_blue]")
        rich_console.print("[bright_blue]|-----------------------------[/bright_blue]")

        session = requests.Session()

        while True:

                try:

                        if args.sleep:
                                delay = args.sleep
                        else:
                                delay = 0
                        vic_name = args.name
                        vic_name = vic_name.replace(" ", "%20")
                        query = f"https://www.11888.gr/white-pages/?query={vic_name}&amp%3Bpage=3&page={page_num}"
                        vic_urls = set()

                        # selects a random User agent from headers
                        ua = secrets.choice(range(1,len(headers) + 1))
                        header = {"User-Agent": f"{headers.get(ua)}"}

                        # this request returns the search results of the victim name
                        html_content = session.get(query, headers=header)

                        if html_content.status_code == 200:
                                html_content = html_content.text

                                #grabs all urls that lead to a victim
                                soup = bsoup(html_content, 'html.parser')
                                for link in soup.find_all('a'):
                                        url = link.get('href')
                                        if url and 'white' in url and 'location' not in url and url != '/white-pages/':
                                                vic_urls.add(url)

                                # visits each victim url and grabs info
                                for vic_url in vic_urls:

                                        ua = secrets.choice(range(1,len(headers) + 1))
                                        header = {"User-Agent": f"{headers.get(ua)}"}

                                        vic_url = vic_url.lstrip("/")
                                        victim_html = session.get(f"https://www.11888.gr/{vic_url}", headers=header)

                                        vic_soup = bsoup(victim_html.text, "html.parser")

                                        name = vic_soup.title.string.replace("| 11888.gr", "")
                                        addr = vic_soup.select_one("span.tw-text-gray-secondary.tw-text-left.tw-text-sm.tw-select-none")
                                        tel = re.search("tel:", victim_html.text)

                                        if tel:
                                            tel = victim_html.text[tel.start():tel.start() + 14]
                                        else:
                                            tel = "tel:Not Found"

                                        if name:
                                                rich_console.print(f"[bright_blue]|[/bright_blue] Name: {name}")
                                        else:
                                                name = None
                                        if addr:
                                                rich_console.print(f"[bright_blue]|[/bright_blue] Address: {addr.get_text(strip=True)}")
                                        else:
                                                addr = None

                                        rich_console.print(f"[bright_blue]|[/bright_blue] Phone: {tel}")

                                        rich_console.print("[bright_blue]|-----------------------------[/bright_blue]")

                                        victims_info.add((name, addr, tel))
                                        sleep(delay)
                        else:
                            print("Didn't get 200 OK from site")

                except KeyboardInterrupt:
                        print("stopping..")
                        vic_urls = False

                # page_num is incremented so recursion can happen.
                page_num += 1
                if vic_urls:
                            continue

                else:
                            rich_console.print("[bright_blue]|[/bright_blue] Finished search")
                            rich_console.print(f"[bright_blue]|[/bright_blue] Gathered info on [bright_red]{len(victims_info)}[/bright_red] people.")
                            rich_console.print("[bright_blue]|-----------------------------[/bright_blue]")
                            return

                vic_urls = set()

# the user agents that will be randomly selected each request.
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


console = Console()

if args.outfile:
        console.print("[bright_blue]|-----------------------------[/bright_blue]")
        console.print("[bright_blue]|[bright_blue]      [bright_red]RUNNING SCRIPT[/bright_red]     [bright_blue]|[/bright_blue]")
        console.print("[bright_blue]|-----------------------------[/bright_blue]")
        console.print("[bright_blue]|[/bright_blue] Script will stop on end [bright_blue]|[/bright_blue]")
        with open("results.txt", "w") as f:
                with redirect_stdout(f):
                        main(agents, console)
        console.print("[bright_blue]|[/bright_blue] [bright_green]Finished search.[/bright_green]        [bright_blue]|[/bright_blue]")
        console.print("[bright_blue]|-----------------------------[/bright_blue]")
else:
        main(agents, console)
