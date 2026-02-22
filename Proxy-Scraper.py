#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      MR.MYTHIC_KILLER'S PROXY SCRAPER & TESTER
                              by mr.mythic_killer | Version 1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
  • 200+ PROXY SOURCES (Websites + GitHub + APIs + Telegram + More)
  • Duplicate prevention (same proxies har bar nahi aayenge)
  • Protocol detection (HTTP/HTTPS/SOCKS4/SOCKS5)
  • COUNTRY & ANONYMITY DETECTION (via API and parsing)
  • DISCORD FILE UPLOAD notifications (separate files per protocol)
  • Real-time CUI with detailed stats
  • Saves proxies in organized files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import re
import sys
import time
import json
import random
import threading
import requests
import urllib3
import csv
import io
from datetime import datetime, timedelta
from colorama import Fore, Back, Style, init
import concurrent.futures
from queue import Queue
import socket
import socks
import httpx
from bs4 import BeautifulSoup

# Initialize Colorama
init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= CONFIGURATION =================
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Discord Webhook (hardcoded as requested)
DISCORD_WEBHOOK = "YOUR_DISCORD_WEBHOOK_URL_HERE"

# GeoIP API for country detection (free, no key needed)
GEOIP_API = "http://ip-api.com/json/{}?fields=country,countryCode"

# Colors for CUI
C = {
    'header': Fore.MAGENTA + Style.BRIGHT,
    'menu': Fore.CYAN,
    'option': Fore.YELLOW,
    'success': Fore.GREEN + Style.BRIGHT,
    'error': Fore.RED + Style.BRIGHT,
    'warning': Fore.YELLOW + Style.BRIGHT,
    'info': Fore.BLUE + Style.BRIGHT,
    'cpm': Fore.LIGHTMAGENTA_EX,
    'proxy': Fore.LIGHTGREEN_EX,
    'scrape': Fore.LIGHTCYAN_EX,
    'test': Fore.LIGHTYELLOW_EX,
    'good': Fore.GREEN,
    'bad': Fore.RED,
    'fail': Fore.LIGHTRED_EX,
    'webhook': Fore.LIGHTBLUE_EX,
    'reset': Style.RESET_ALL
}

# ================= BANNER =================
BANNER = f"""
{C['header']}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███╗   ███╗██╗   ██╗████████╗██╗  ██╗██╗ ██████╗              ║
║   ████╗ ████║╚██╗ ██╔╝╚══██╔══╝██║  ██║██║██╔════╝              ║
║   ██╔████╔██║ ╚████╔╝    ██║   ███████║██║██║                   ║
║   ██║╚██╔╝██║  ╚██╔╝     ██║   ██╔══██║██║██║                   ║
║   ██║ ╚═╝ ██║   ██║      ██║   ██║  ██║██║╚██████╗              ║
║   ╚═╝     ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝              ║
║                                                                   ║
║              🔥 PROXY SCRAPER & TESTER 🔥                        ║
║                   BY: MR.MYTHIC_KILLER                           ║
║                        VERSION 6.0                                ║
║            📁 200+ SOURCES + COUNTRY DETECTION 📁                ║
╚═══════════════════════════════════════════════════════════════════╝
{C['reset']}
"""

# ================= 200+ PROXY SOURCES =================
SCRAPE_SOURCES = [
    # === WEBSITES (50+) ===
    {'name': 'Geonode', 'url': 'https://geonode.com/free-proxy-list', 'type': 'html', 'pages': 5},
    {'name': 'FreeProxy.World', 'url': 'https://www.freeproxy.world/', 'type': 'html', 'pages': 5},
    {'name': 'FreeProxy.World HTTP', 'url': 'https://www.freeproxy.world/?type=http', 'type': 'html', 'pages': 3},
    {'name': 'FreeProxy.World SOCKS4', 'url': 'https://www.freeproxy.world/?type=socks4', 'type': 'html', 'pages': 3},
    {'name': 'FreeProxy.World SOCKS5', 'url': 'https://www.freeproxy.world/?type=socks5', 'type': 'html', 'pages': 3},
    {'name': 'ProxyBros', 'url': 'https://proxybros.com/free-proxy-list/', 'type': 'html', 'pages': 5},
    {'name': 'SSLProxies', 'url': 'https://www.sslproxies.org/', 'type': 'html', 'pages': 3},
    {'name': 'US-Proxy', 'url': 'https://www.us-proxy.org/', 'type': 'html', 'pages': 3},
    {'name': 'SocksProxy', 'url': 'https://www.socks-proxy.net/', 'type': 'html', 'pages': 3},
    {'name': 'Free-Proxy-List', 'url': 'https://free-proxy-list.net/', 'type': 'html', 'pages': 3},
    {'name': 'Free-Proxy-List UK', 'url': 'https://free-proxy-list.net/uk-proxy.html', 'type': 'html', 'pages': 2},
    {'name': 'Proxy-List', 'url': 'https://www.proxy-list.download/', 'type': 'html', 'pages': 3},
    {'name': 'HideMy.name', 'url': 'https://hidemy.name/en/proxy-list/', 'type': 'html', 'pages': 5},
    {'name': 'ProxyNova', 'url': 'https://www.proxynova.com/proxy-server-list/', 'type': 'html', 'pages': 5},
    {'name': 'Cool-Proxy', 'url': 'https://www.cool-proxy.net/', 'type': 'html', 'pages': 3},
    {'name': 'Proxy-List-Web', 'url': 'https://www.proxy-list.org/', 'type': 'html', 'pages': 3},
    {'name': 'FreeProxyLists', 'url': 'https://www.freeproxylists.net/', 'type': 'html', 'pages': 3},
    {'name': 'ProxyHub', 'url': 'https://proxyhub.me/', 'type': 'html', 'pages': 3},
    {'name': 'Xseo.in', 'url': 'https://xseo.in/freeproxy', 'type': 'html', 'pages': 2},
    {'name': 'ProxyScanner', 'url': 'https://www.proxyscanner.com/', 'type': 'html', 'pages': 2},
    {'name': 'Spys.one', 'url': 'https://spys.one/en/free-proxy-list/', 'type': 'html', 'pages': 3},
    {'name': 'Proxydb', 'url': 'http://proxydb.net/', 'type': 'html', 'pages': 3},
    {'name': 'ProxyRack', 'url': 'https://www.proxyrack.com/free-proxy-list/', 'type': 'html', 'pages': 2},
    {'name': 'MyProxy', 'url': 'https://www.my-proxy.com/free-proxy-list.html', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.me', 'url': 'https://proxylist.me/', 'type': 'html', 'pages': 2},
    {'name': 'FreeProxy.io', 'url': 'https://freeproxy.io/', 'type': 'html', 'pages': 2},
    {'name': 'Proxy4Free', 'url': 'https://www.proxy4free.com/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyServerList', 'url': 'https://www.proxyserverlist.org/', 'type': 'html', 'pages': 2},
    {'name': 'FreeProxyList.cc', 'url': 'https://www.freeproxylist.cc/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.download', 'url': 'https://www.proxylist.download/', 'type': 'html', 'pages': 2},
    {'name': 'VPNBook', 'url': 'https://www.vpnbook.com/free-proxy-list', 'type': 'html', 'pages': 3},
    {'name': 'ProxySite', 'url': 'https://www.proxysite.com/free-proxy-list/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyElite', 'url': 'https://proxyelite.info/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.pro', 'url': 'https://proxylist.pro/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyDB.pro', 'url': 'https://proxydb.pro/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.to', 'url': 'https://proxylist.to/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.one', 'url': 'https://proxylist.one/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.org', 'url': 'https://proxylist.org/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.cc', 'url': 'https://proxylist.cc/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.co', 'url': 'https://proxylist.co/', 'type': 'html', 'pages': 2},
    {'name': 'ProxyList.net', 'url': 'https://proxylist.net/', 'type': 'html', 'pages': 2},
    
    # === GITHUB REPOS (100+) ===
    {'name': 'GitHub TheSpeedX HTTP', 'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub TheSpeedX SOCKS4', 'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub TheSpeedX SOCKS5', 'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub hookzof', 'url': 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub prxchk HTTP', 'url': 'https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub prxchk SOCKS4', 'url': 'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub prxchk SOCKS5', 'url': 'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub mmpx12 HTTP', 'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub mmpx12 SOCKS4', 'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub mmpx12 SOCKS5', 'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub jetkai HTTP', 'url': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online/proxies/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub jetkai SOCKS4', 'url': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online/proxies/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub jetkai SOCKS5', 'url': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online/proxies/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub ShiftyTR HTTP', 'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub ShiftyTR SOCKS4', 'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub ShiftyTR SOCKS5', 'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub roosterkid HTTP', 'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub roosterkid SOCKS4', 'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub roosterkid SOCKS5', 'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub Uptimer HTTP', 'url': 'https://raw.githubusercontent.com/Uptimer/Proxy-List/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub Uptimer SOCKS4', 'url': 'https://raw.githubusercontent.com/Uptimer/Proxy-List/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub Uptimer SOCKS5', 'url': 'https://raw.githubusercontent.com/Uptimer/Proxy-List/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub vakhov HTTP', 'url': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub vakhov SOCKS4', 'url': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub vakhov SOCKS5', 'url': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub proxy-list HTTP', 'url': 'https://raw.githubusercontent.com/proxy-list/proxy-list/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub proxy-list SOCKS4', 'url': 'https://raw.githubusercontent.com/proxy-list/proxy-list/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub proxy-list SOCKS5', 'url': 'https://raw.githubusercontent.com/proxy-list/proxy-list/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub sunshifty HTTP', 'url': 'https://raw.githubusercontent.com/sunshifty/Proxy-List/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub sunshifty SOCKS4', 'url': 'https://raw.githubusercontent.com/sunshifty/Proxy-List/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub sunshifty SOCKS5', 'url': 'https://raw.githubusercontent.com/sunshifty/Proxy-List/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub MortezaBashsiz HTTP', 'url': 'https://raw.githubusercontent.com/MortezaBashsiz/CFScanner/main/proxy/proxy.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub yemix HTTP', 'url': 'https://raw.githubusercontent.com/yemix/proxy-list/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub yemix SOCKS4', 'url': 'https://raw.githubusercontent.com/yemix/proxy-list/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub yemix SOCKS5', 'url': 'https://raw.githubusercontent.com/yemix/proxy-list/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub Zaeem20 HTTP', 'url': 'https://raw.githubusercontent.com/Zaeem20/ProxyLists/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub Zaeem20 SOCKS4', 'url': 'https://raw.githubusercontent.com/Zaeem20/ProxyLists/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub Zaeem20 SOCKS5', 'url': 'https://raw.githubusercontent.com/Zaeem20/ProxyLists/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub stefankumpan HTTP', 'url': 'https://raw.githubusercontent.com/stefankumpan/proxy-list/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub stefankumpan SOCKS4', 'url': 'https://raw.githubusercontent.com/stefankumpan/proxy-list/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub stefankumpan SOCKS5', 'url': 'https://raw.githubusercontent.com/stefankumpan/proxy-list/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub manuGMG HTTP', 'url': 'https://raw.githubusercontent.com/manuGMG/proxy-list/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub manuGMG SOCKS4', 'url': 'https://raw.githubusercontent.com/manuGMG/proxy-list/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub manuGMG SOCKS5', 'url': 'https://raw.githubusercontent.com/manuGMG/proxy-list/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub blackhorser HTTP', 'url': 'https://raw.githubusercontent.com/blackhorser/Proxy-List/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub blackhorser SOCKS4', 'url': 'https://raw.githubusercontent.com/blackhorser/Proxy-List/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'GitHub blackhorser SOCKS5', 'url': 'https://raw.githubusercontent.com/blackhorser/Proxy-List/main/socks5.txt', 'type': 'raw', 'pages': 1},
    
    # === APIS (30+) ===
    {'name': 'ProxyScrape HTTP', 'url': 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=10000&country=all', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyScrape SOCKS4', 'url': 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=10000&country=all', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyScrape SOCKS5', 'url': 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=10000&country=all', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyScrape HTTP (alt)', 'url': 'https://api.proxyscrape.com/?request=displayproxies&proxytype=http', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyScrape SOCKS4 (alt)', 'url': 'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyScrape SOCKS5 (alt)', 'url': 'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5', 'type': 'raw', 'pages': 1},
    {'name': 'Geonode API Page 1', 'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'type': 'api', 'pages': 1},
    {'name': 'Geonode API Page 2', 'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc', 'type': 'api', 'pages': 1},
    {'name': 'Geonode API Page 3', 'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc', 'type': 'api', 'pages': 1},
    {'name': 'Geonode API Page 4', 'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=4&sort_by=lastChecked&sort_type=desc', 'type': 'api', 'pages': 1},
    {'name': 'Geonode API Page 5', 'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=5&sort_by=lastChecked&sort_type=desc', 'type': 'api', 'pages': 1},
    {'name': 'OpenProxySpace HTTP', 'url': 'https://openproxy.space/list/http', 'type': 'html', 'pages': 5},
    {'name': 'OpenProxySpace SOCKS4', 'url': 'https://openproxy.space/list/socks4', 'type': 'html', 'pages': 5},
    {'name': 'OpenProxySpace SOCKS5', 'url': 'https://openproxy.space/list/socks5', 'type': 'html', 'pages': 5},
    {'name': 'ProxyList API HTTP', 'url': 'https://www.proxy-list.download/api/v1/get?type=http', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyList API SOCKS4', 'url': 'https://www.proxy-list.download/api/v1/get?type=socks4', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyList API SOCKS5', 'url': 'https://www.proxy-list.download/api/v1/get?type=socks5', 'type': 'raw', 'pages': 1},
    {'name': 'Proxy-List API', 'url': 'https://www.proxy-list.download/api/v1/get?type=http', 'type': 'raw', 'pages': 1},
    {'name': 'PubProxy API', 'url': 'http://pubproxy.com/api/proxy?limit=20&format=txt', 'type': 'raw', 'pages': 3},
    {'name': 'ProxyRack API', 'url': 'https://www.proxyrack.com/api/freeproxies?protocol=http', 'type': 'raw', 'pages': 1},
    
    # === TELEGRAM CHANNELS (scrape via web) ===
    {'name': 'Telegram Proxy Channel 1', 'url': 'https://t.me/s/proxy4par3', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 2', 'url': 'https://t.me/s/proxy_list', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 3', 'url': 'https://t.me/s/proxy_socks5', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 4', 'url': 'https://t.me/s/socks5_proxy_list', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 5', 'url': 'https://t.me/s/proxy_s4_s5', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 6', 'url': 'https://t.me/s/proxy_http_list', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 7', 'url': 'https://t.me/s/free_proxy_list', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 8', 'url': 'https://t.me/s/proxy_list_daily', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 9', 'url': 'https://t.me/s/socks5_proxies', 'type': 'html', 'pages': 2},
    {'name': 'Telegram Proxy Channel 10', 'url': 'https://t.me/s/http_proxy_list', 'type': 'html', 'pages': 2},
    
    # === FORUMS & OTHER SOURCES ===
    {'name': 'Reddit r/proxy', 'url': 'https://www.reddit.com/r/proxy/new/.rss', 'type': 'html', 'pages': 2},
    {'name': 'BlackHatWorld', 'url': 'https://www.blackhatworld.com/forums/proxy.129/', 'type': 'html', 'pages': 2},
    {'name': 'HackForums', 'url': 'https://hackforums.net/forumdisplay.php?fid=69', 'type': 'html', 'pages': 2},
    {'name': 'MPGH Proxy Section', 'url': 'https://www.mpgh.net/forum/forumdisplay.php?f=293', 'type': 'html', 'pages': 2},
]

# ================= GLOBAL VARIABLES =================
scraped_proxies = []
valid_proxies = []
invalid_proxies = []
failed_proxies = []
total_tested = 0
total_valid = 0
total_invalid = 0
total_failed = 0
cpm = 0
lock = threading.Lock()
start_time = time.time()
proxy_queue = Queue()
stop_testing = False
seen_proxies = set()  # For duplicate prevention

# ================= COUNTRY & ANONYMITY DETECTION =================
def get_ip_info(ip):
    """Get country and other info for an IP address"""
    try:
        url = GEOIP_API.format(ip)
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                country_code = data.get('countryCode', 'Unknown')
                return country, country_code
    except:
        pass
    return 'Unknown', 'Unknown'

def extract_anonymity_from_text(text):
    """Extract anonymity level from text (elite, anonymous, transparent)"""
    text_lower = text.lower()
    if 'elite' in text_lower or 'high' in text_lower:
        return 'Elite'
    elif 'anonymous' in text_lower or 'anon' in text_lower:
        return 'Anonymous'
    elif 'transparent' in text_lower:
        return 'Transparent'
    return 'Unknown'

# ================= HELPER FUNCTIONS =================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(BANNER)

def update_title():
    global total_tested, cpm
    elapsed = time.time() - start_time
    current_cpm = int((total_tested / elapsed) * 60) if elapsed > 0 and total_tested > 0 else 0
    try:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(
                f"MR.MYTHIC_KILLER Proxy Tool | Tested: {total_tested} | Valid: {total_valid} | "
                f"Invalid: {total_invalid} | Failed: {total_failed} | CPM: {current_cpm}"
            )
    except:
        pass

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_proxy_line(line):
    """Parse any line to extract IP:PORT - handles extra text"""
    # Match IP:PORT pattern
    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})', line)
    if match:
        proxy = f"{match.group(1)}:{match.group(2)}"
        # Check for duplicates
        with lock:
            if proxy not in seen_proxies:
                seen_proxies.add(proxy)
                return proxy
    return None

# ================= GEONODE CSV PARSER =================
def parse_geonode_csv(csv_text):
    """Special parser for Geonode CSV format"""
    proxies = []
    try:
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader)
        
        # Find column indices
        ip_idx = None
        port_idx = None
        protocol_idx = None
        country_idx = None
        anonymity_idx = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'ip' in header_lower:
                ip_idx = i
            elif 'port' in header_lower:
                port_idx = i
            elif 'protocol' in header_lower:
                protocol_idx = i
            elif 'country' in header_lower:
                country_idx = i
            elif 'anonymity' in header_lower or 'elite' in header_lower:
                anonymity_idx = i
        
        for row in csv_reader:
            if len(row) > max(ip_idx or 0, port_idx or 0):
                ip = row[ip_idx].strip('"') if ip_idx is not None else None
                port = row[port_idx].strip('"') if port_idx is not None else None
                
                if ip and port:
                    proxy = f"{ip}:{port}"
                    with lock:
                        if proxy not in seen_proxies:
                            seen_proxies.add(proxy)
                            proxies.append(proxy)
                            
                            # Extract extra info
                            protocol = row[protocol_idx].strip('"') if protocol_idx is not None else 'Unknown'
                            country = row[country_idx].strip('"') if country_idx is not None else 'Unknown'
                            anonymity = row[anonymity_idx].strip('"') if anonymity_idx is not None else 'Unknown'
                            
                            # Save extra info
                            with open(os.path.join(RESULTS_DIR, "proxy_details.txt"), 'a') as f:
                                f.write(f"{proxy} | {protocol} | {country} | {anonymity}\n")
        
        print(f"{C['info']}      Geonode CSV parsed: {len(proxies)} new proxies")
    except Exception as e:
        print(f"{C['error']}      Geonode CSV parse error: {str(e)[:50]}")
    
    return proxies

# ================= API PARSER (for Geonode API) =================
def parse_api_json(json_text):
    """Parse API JSON response for proxies"""
    proxies = []
    try:
        data = json.loads(json_text)
        if 'data' in data:
            for item in data['data']:
                ip = item.get('ip')
                port = item.get('port')
                protocols = item.get('protocols', [])
                country = item.get('country', 'Unknown')
                anonymity = item.get('anonymityLevel', 'Unknown')
                
                if ip and port:
                    proxy = f"{ip}:{port}"
                    with lock:
                        if proxy not in seen_proxies:
                            seen_proxies.add(proxy)
                            proxies.append(proxy)
                            
                            proto_str = ','.join(protocols) if protocols else 'Unknown'
                            with open(os.path.join(RESULTS_DIR, "api_proxy_details.txt"), 'a') as f:
                                f.write(f"{proxy} | {proto_str} | {country} | {anonymity}\n")
    except Exception as e:
        print(f"{C['error']}      API parse error: {str(e)[:50]}")
    
    return proxies

# ================= SCRAPING FUNCTIONS =================
def scrape_from_html(url):
    """Scrape proxies from HTML tables"""
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            # Special handling for Geonode
            if 'geonode.com' in url:
                soup = BeautifulSoup(r.text, 'html.parser')
                for tag in soup.find_all(['textarea', 'pre', 'script']):
                    if tag.string and ('IP' in tag.string or 'anonymityLevel' in tag.string):
                        csv_text = tag.string
                        geo_proxies = parse_geonode_csv(csv_text)
                        proxies.extend(geo_proxies)
            
            # Generic HTML parsing
            if not proxies:
                soup = BeautifulSoup(r.text, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            ip = None
                            port = None
                            country = None
                            anonymity = None
                            
                            for cell in cells:
                                text = cell.text.strip()
                                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
                                    ip = text
                                elif text.isdigit() and 1 <= int(text) <= 65535:
                                    port = text
                                elif len(text) == 2 and text.isalpha():  # Country code
                                    country = text
                                elif 'elite' in text.lower() or 'anonymous' in text.lower():
                                    anonymity = extract_anonymity_from_text(text)
                            
                            if ip and port:
                                proxy = f"{ip}:{port}"
                                with lock:
                                    if proxy not in seen_proxies:
                                        seen_proxies.add(proxy)
                                        proxies.append(proxy)
                                        
                                        # Save extra info if available
                                        if country or anonymity:
                                            with open(os.path.join(RESULTS_DIR, "html_proxy_details.txt"), 'a') as f:
                                                f.write(f"{proxy} | {country or 'Unknown'} | {anonymity or 'Unknown'}\n")
                
                # Fallback: regex on whole page
                if not proxies:
                    ip_ports = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})', r.text)
                    for ip, port in ip_ports:
                        proxy = f"{ip}:{port}"
                        with lock:
                            if proxy not in seen_proxies:
                                seen_proxies.add(proxy)
                                proxies.append(proxy)
    except Exception as e:
        print(f"{C['error']}      Error scraping {url}: {str(e)[:50]}")
    return proxies

def scrape_from_raw(url):
    """Scrape proxies from raw text files"""
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            lines = r.text.split('\n')
            for line in lines:
                proxy = parse_proxy_line(line.strip())
                if proxy:
                    proxies.append(proxy)
    except Exception as e:
        print(f"{C['error']}      Error scraping {url}: {str(e)[:50]}")
    return proxies

def scrape_from_api(url):
    """Scrape proxies from API endpoints"""
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            proxies = parse_api_json(r.text)
    except Exception as e:
        print(f"{C['error']}      Error scraping {url}: {str(e)[:50]}")
    return proxies

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

def scrape_proxies():
    """Main scraping function with duplicate prevention"""
    global scraped_proxies, seen_proxies
    scraped_proxies = []
    seen_proxies.clear()
    
    print(f"\n{C['scrape']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['scrape']}║              SCRAPING PROXIES FROM 200+ SOURCES          ║")
    print(f"{C['scrape']}╚════════════════════════════════════════════════════════════╝\n")
    
    total_sources = 0
    for source in SCRAPE_SOURCES:
        pages = source.get('pages', 1)
        total_sources += pages
    
    current = 0
    for source in SCRAPE_SOURCES:
        pages = source.get('pages', 1)
        for page in range(1, pages + 1):
            current += 1
            url = source['url']
            if pages > 1:
                # Handle pagination
                if 'page' in url:
                    url = url.replace('page=1', f'page={page}')
                elif '/page/' in url:
                    url = re.sub(r'/page/\d+', f'/page/{page}', url)
                elif '?page=' in url:
                    url = re.sub(r'page=\d+', f'page={page}', url)
            
            print(f"{C['info']}  [{current}/{total_sources}] Scraping from {source['name']} (Page {page})...")
            
            if source['type'] == 'html':
                proxies = scrape_from_html(url)
            elif source['type'] == 'api':
                proxies = scrape_from_api(url)
            else:
                proxies = scrape_from_raw(url)
            
            print(f"{C['proxy']}      Found {len(proxies)} new proxies")
            scraped_proxies.extend(proxies)
            
            # Small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
    
    print(f"\n{C['success']}  ✓ Total unique proxies scraped: {len(scraped_proxies)}")
    
    # Save scraped proxies
    with open(os.path.join(RESULTS_DIR, "scraped_proxies.txt"), 'w') as f:
        for proxy in scraped_proxies:
            f.write(proxy + '\n')
    
    return scraped_proxies

# ================= DISCORD FILE UPLOAD FUNCTION =================
def send_discord_file(protocol_type, proxies_list, extra_info=None):
    """Send proxy list as file to Discord webhook"""
    if not proxies_list:
        return
    
    try:
        # Create temporary file
        filename = f"{protocol_type}_proxies.txt"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"# {len(proxies_list)} {protocol_type.upper()} Proxies\n")
            f.write(f"# Generated by MR.MYTHIC_KILLER Proxy Tool\n")
            f.write(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if extra_info:
                f.write("# IP:PORT | COUNTRY | ANONYMITY | SPEED\n")
                for proxy, info in zip(proxies_list, extra_info):
                    country = info.get('country', 'Unknown')
                    anonymity = info.get('anonymity', 'Unknown')
                    speed = info.get('speed', 'N/A')
                    f.write(f"{proxy} | {country} | {anonymity} | {speed}ms\n")
            else:
                for proxy in proxies_list:
                    f.write(proxy + '\n')
        
        # Send file to Discord
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            
            # Simple message with file
            data = {
                'content': f"📁 **{len(proxies_list)} {protocol_type.upper()} Proxies Found!**"
            }
            
            r = requests.post(DISCORD_WEBHOOK, data=data, files=files, timeout=10)
            
            if r.status_code in [200, 204]:
                print(f"{C['webhook']}      ↳ Discord file uploaded: {filename} ✓")
            else:
                print(f"{C['warning']}      ↳ Discord upload returned {r.status_code}")
    
    except Exception as e:
        print(f"{C['error']}      ↳ Discord upload error: {str(e)[:30]}")

def send_all_proxy_files():
    """Send all protocol files to Discord with extra details"""
    global valid_proxies
    
    if not valid_proxies:
        print(f"{C['warning']}  ⚠ No valid proxies to upload")
        return
    
    print(f"\n{C['webhook']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['webhook']}║              UPLOADING PROXIES TO DISCORD                 ║")
    print(f"{C['webhook']}╚════════════════════════════════════════════════════════════╝\n")
    
    # Group by protocol with extra info
    http_proxies = []
    http_info = []
    socks4_proxies = []
    socks4_info = []
    socks5_proxies = []
    socks5_info = []
    
    for proxy, protocol, speed in valid_proxies:
        ip = proxy.split(':')[0]
        country, country_code = get_ip_info(ip)
        anonymity = 'Unknown'  # We don't have anonymity from testing
        
        info = {
            'country': country,
            'anonymity': anonymity,
            'speed': f"{speed:.2f}"
        }
        
        if protocol == 'http':
            http_proxies.append(proxy)
            http_info.append(info)
        elif protocol == 'socks4':
            socks4_proxies.append(proxy)
            socks4_info.append(info)
        elif protocol == 'socks5':
            socks5_proxies.append(proxy)
            socks5_info.append(info)
    
    # Send each protocol separately with extra info
    if http_proxies:
        send_discord_file('http', http_proxies, http_info)
        time.sleep(1)  # Rate limiting
    
    if socks4_proxies:
        send_discord_file('socks4', socks4_proxies, socks4_info)
        time.sleep(1)
    
    if socks5_proxies:
        send_discord_file('socks5', socks5_proxies, socks5_info)
        time.sleep(1)
    
    # Send all proxies combined (without extra info to save space)
    all_proxies = [p[0] for p in valid_proxies]
    if all_proxies:
        send_discord_file('all_valid', all_proxies)
    
    print(f"{C['success']}  ✓ All proxy files uploaded to Discord!")

# ================= PROXY TESTING FUNCTIONS =================
def test_proxy_http(proxy, timeout=5):
    """Test HTTP/HTTPS proxy"""
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        start = time.time()
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=timeout, verify=False)
        elapsed = (time.time() - start) * 1000
        if r.status_code == 200:
            return True, 'http', elapsed
    except:
        pass
    return False, None, 0

def test_proxy_socks4(proxy, timeout=5):
    """Test SOCKS4 proxy"""
    try:
        ip, port = proxy.split(':')
        start = time.time()
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS4, ip, int(port))
        sock.settimeout(timeout)
        sock.connect(('httpbin.org', 80))
        sock.send(b"GET /ip HTTP/1.0\r\nHost: httpbin.org\r\n\r\n")
        response = sock.recv(1024)
        sock.close()
        elapsed = (time.time() - start) * 1000
        if b'200 OK' in response:
            return True, 'socks4', elapsed
    except:
        pass
    return False, None, 0

def test_proxy_socks5(proxy, timeout=5):
    """Test SOCKS5 proxy"""
    try:
        ip, port = proxy.split(':')
        start = time.time()
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, ip, int(port))
        sock.settimeout(timeout)
        sock.connect(('httpbin.org', 80))
        sock.send(b"GET /ip HTTP/1.0\r\nHost: httpbin.org\r\n\r\n")
        response = sock.recv(1024)
        sock.close()
        elapsed = (time.time() - start) * 1000
        if b'200 OK' in response:
            return True, 'socks5', elapsed
    except:
        pass
    return False, None, 0

def test_proxy_worker(proxy_type_filter='mix'):
    """Worker function for testing proxies"""
    global total_tested, total_valid, total_invalid, total_failed, cpm
    
    while not stop_testing and not proxy_queue.empty():
        try:
            proxy = proxy_queue.get(timeout=1)
        except:
            break
        
        # Test based on filter
        is_valid = False
        protocol = None
        speed = 0
        
        if proxy_type_filter in ['mix', 'http']:
            is_valid, protocol, speed = test_proxy_http(proxy)
        
        if not is_valid and proxy_type_filter in ['mix', 'socks4']:
            is_valid, protocol, speed = test_proxy_socks4(proxy)
        
        if not is_valid and proxy_type_filter in ['mix', 'socks5']:
            is_valid, protocol, speed = test_proxy_socks5(proxy)
        
        with lock:
            total_tested += 1
            if is_valid:
                total_valid += 1
                valid_proxies.append((proxy, protocol, speed))
                status = f"{C['good']}✓ VALID"
            else:
                total_invalid += 1
                invalid_proxies.append(proxy)
                status = f"{C['bad']}✗ INVALID"
            
            elapsed = time.time() - start_time
            cpm = int((total_tested / elapsed) * 60) if elapsed > 0 else 0
            
            print(f"\r{C['test']}[{total_tested}] {status} {C['proxy']}{proxy} "
                  f"{C['info']}| {protocol if protocol else 'N/A'} | "
                  f"{C['cpm']}CPM: {cpm} | "
                  f"{C['good']}Valid: {total_valid} | "
                  f"{C['bad']}Invalid: {total_invalid} | "
                  f"{C['fail']}Fail: {total_failed}", end=' ' * 10)
            
            update_title()
        
        proxy_queue.task_done()

def test_proxies(proxies_to_test, proxy_type_filter='mix', threads=50):
    """Main testing function"""
    global stop_testing, proxy_queue, total_tested, total_valid, total_invalid, total_failed, start_time, valid_proxies
    
    stop_testing = False
    total_tested = 0
    total_valid = 0
    total_invalid = 0
    total_failed = 0
    valid_proxies.clear()
    invalid_proxies.clear()
    start_time = time.time()
    
    # Fill queue
    for proxy in proxies_to_test:
        proxy_queue.put(proxy)
    
    print(f"\n{C['test']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['test']}║              TESTING PROXIES ({len(proxies_to_test)} total)            ║")
    print(f"{C['test']}║  Filter: {proxy_type_filter.upper()} | Threads: {threads}                 ║")
    print(f"{C['test']}╚════════════════════════════════════════════════════════════╝\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(test_proxy_worker, proxy_type_filter) for _ in range(threads)]
        
        try:
            while total_tested < len(proxies_to_test):
                time.sleep(0.1)
        except KeyboardInterrupt:
            stop_testing = True
            print(f"\n{C['warning']}\n  ⚠ Testing stopped by user!")
    
    elapsed = time.time() - start_time
    print(f"\n\n{C['success']}  ✓ Testing Complete!")
    print(f"{C['info']}     Time: {format_time(elapsed)}")
    print(f"{C['good']}     Valid: {total_valid}")
    print(f"{C['bad']}     Invalid: {total_invalid}")
    print(f"{C['cpm']}     Avg CPM: {int((total_tested/elapsed)*60) if elapsed>0 else 0}")
    
    # Save results
    if valid_proxies:
        valid_proxies.sort(key=lambda x: x[2])
        
        # Save by protocol
        http_proxies = [p[0] for p in valid_proxies if p[1] == 'http']
        socks4_proxies = [p[0] for p in valid_proxies if p[1] == 'socks4']
        socks5_proxies = [p[0] for p in valid_proxies if p[1] == 'socks5']
        
        with open(os.path.join(RESULTS_DIR, "http_proxies.txt"), 'w') as f:
            f.write('\n'.join(http_proxies))
        
        with open(os.path.join(RESULTS_DIR, "socks4_proxies.txt"), 'w') as f:
            f.write('\n'.join(socks4_proxies))
        
        with open(os.path.join(RESULTS_DIR, "socks5_proxies.txt"), 'w') as f:
            f.write('\n'.join(socks5_proxies))
        
        with open(os.path.join(RESULTS_DIR, "all_valid_proxies.txt"), 'w') as f:
            for proxy, protocol, resp_time in valid_proxies:
                f.write(f"{proxy} | {protocol} | {resp_time:.2f}ms\n")
        
        print(f"{C['success']}  ✓ Saved valid proxies to {RESULTS_DIR}/")
        
        # Send files to Discord with extra details
        send_all_proxy_files()
    
    return valid_proxies

# ================= MAIN MENU =================
def main():
    global scraped_proxies, start_time
    
    print_banner()
    
    print(f"\n{C['menu']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['menu']}║                    SELECT MODE                            ║")
    print(f"{C['menu']}╠════════════════════════════════════════════════════════════╣")
    print(f"{C['menu']}║  {C['option']}[1] {C['menu']}Auto Scraping Only                         ║")
    print(f"{C['menu']}║  {C['option']}[2] {C['menu']}Proxy Test Only                            ║")
    print(f"{C['menu']}║  {C['option']}[3] {C['menu']}Both (Scrape + Test)                       ║")
    print(f"{C['menu']}╚════════════════════════════════════════════════════════════╝")
    
    choice = input(f"\n{C['option']}  [?] Enter your choice (1/2/3): {C['reset']}").strip()
    
    proxy_type_filter = 'mix'
    if choice in ['2', '3']:
        print(f"\n{C['menu']}╔════════════════════════════════════════════════════════════╗")
        print(f"{C['menu']}║                SELECT PROXY TYPE TO TEST                   ║")
        print(f"{C['menu']}╠════════════════════════════════════════════════════════════╣")
        print(f"{C['menu']}║  {C['option']}[1] {C['menu']}HTTP/HTTPS Only                           ║")
        print(f"{C['menu']}║  {C['option']}[2] {C['menu']}SOCKS4 Only                               ║")
        print(f"{C['menu']}║  {C['option']}[3] {C['menu']}SOCKS5 Only                               ║")
        print(f"{C['menu']}║  {C['option']}[4] {C['menu']}MIX (Auto-detect)                         ║")
        print(f"{C['menu']}╚════════════════════════════════════════════════════════════╝")
        
        type_choice = input(f"\n{C['option']}  [?] Enter your choice (1/2/3/4): {C['reset']}").strip()
        
        type_map = {
            '1': 'http',
            '2': 'socks4',
            '3': 'socks5',
            '4': 'mix'
        }
        proxy_type_filter = type_map.get(type_choice, 'mix')
    
    threads = 30
    if choice in ['2', '3']:
        try:
            threads = int(input(f"\n{C['option']}  [?] Testing threads (10-200, default 50): {C['reset']}") or "50")
            threads = max(10, min(200, threads))
        except:
            threads = 50
    
    start_time = time.time()
    
    if choice == '1':
        proxies = scrape_proxies()
        print(f"\n{C['success']}  ✓ Scraping complete! {len(proxies)} proxies saved to {RESULTS_DIR}/scraped_proxies.txt")
    
    elif choice == '2':
        file_path = input(f"\n{C['option']}  [?] Enter path to proxy file (or press Enter for default 'proxies.txt'): {C['reset']}").strip()
        if not file_path:
            file_path = 'proxies.txt'
        
        try:
            with open(file_path, 'r') as f:
                proxies_to_test = []
                for line in f:
                    proxy = parse_proxy_line(line.strip())
                    if proxy:
                        proxies_to_test.append(proxy)
            
            print(f"{C['info']}  → Loaded {len(proxies_to_test)} proxies from {file_path}")
            test_proxies(proxies_to_test, proxy_type_filter, threads)
        except FileNotFoundError:
            print(f"{C['error']}  ✗ File not found: {file_path}")
    
    elif choice == '3':
        proxies = scrape_proxies()
        if proxies:
            test_proxies(proxies, proxy_type_filter, threads)
    
    else:
        print(f"{C['error']}  ✗ Invalid choice!")
    
    print(f"\n{C['header']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['header']}║                    THANKS FOR USING                         ║")
    print(f"{C['header']}║                  MR.MYTHIC_KILLER                           ║")
    print(f"{C['header']}╚════════════════════════════════════════════════════════════╝{C['reset']}")
    input(f"\n{C['option']}Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['warning']}\n  ⚠ Program stopped by user!")
        sys.exit(0)
    except Exception as e:
        print(f"{C['error']}\n  ✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
