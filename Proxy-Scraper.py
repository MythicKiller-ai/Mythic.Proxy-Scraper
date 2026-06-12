#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from datetime import datetime, timezone
from colorama import Fore, Back, Style, init
import concurrent.futures
from queue import Queue
import socket
import socks
import httpx
from bs4 import BeautifulSoup

# Fix for old Python versions
try:
    from datetime import UTC
except ImportError:
    class UTC(timezone):
        def __init__(self):
            super().__init__(0)
        def utcoffset(self, dt):
            return timedelta(0)
        def tzname(self, dt):
            return "UTC"
        def dst(self, dt):
            return timedelta(0)
    UTC = UTC()

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

EMBED_WEBHOOK = "ENTER_YOUR_VALID_PROXIES_WEBHOOK_URL_HERE"
FILE_WEBHOOK = "ENTER_YOUR_VALID_PROXIES_FILE_UPLOAD_WEBHOOK_URL_HERE"

country_cache = {}
anonymity_cache = {}

def get_country_full(ip):
    if ip in country_cache:
        return country_cache[ip]
    apis = [
        f"https://ipinfo.io/{ip}/json",
        f"http://ip-api.com/json/{ip}?fields=country",
        f"https://freegeoip.app/json/{ip}"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=3)
            if r.status_code == 200:
                data = r.json()
                if 'ipinfo' in api:
                    country = data.get('country_name') or data.get('country')
                elif 'ip-api' in api:
                    country = data.get('country')
                else:
                    country = data.get('country_name') or data.get('country')
                if country and country != 'Unknown':
                    if len(country) == 2:
                        country = code_to_name(country)
                    country_cache[ip] = country
                    return country
        except:
            continue
    country_cache[ip] = 'Unknown'
    return 'Unknown'

def code_to_name(code):
    # Complete mapping of all country codes to full names
    mapping = {
        'AF': 'Afghanistan', 'AX': 'Åland Islands', 'AL': 'Albania', 'DZ': 'Algeria',
        'AS': 'American Samoa', 'AD': 'Andorra', 'AO': 'Angola', 'AI': 'Anguilla',
        'AQ': 'Antarctica', 'AG': 'Antigua and Barbuda', 'AR': 'Argentina', 'AM': 'Armenia',
        'AW': 'Aruba', 'AU': 'Australia', 'AT': 'Austria', 'AZ': 'Azerbaijan',
        'BS': 'Bahamas', 'BH': 'Bahrain', 'BD': 'Bangladesh', 'BB': 'Barbados',
        'BY': 'Belarus', 'BE': 'Belgium', 'BZ': 'Belize', 'BJ': 'Benin', 'BM': 'Bermuda',
        'BT': 'Bhutan', 'BO': 'Bolivia', 'BA': 'Bosnia and Herzegovina', 'BW': 'Botswana',
        'BV': 'Bouvet Island', 'BR': 'Brazil', 'IO': 'British Indian Ocean Territory',
        'BN': 'Brunei Darussalam', 'BG': 'Bulgaria', 'BF': 'Burkina Faso', 'BI': 'Burundi',
        'KH': 'Cambodia', 'CM': 'Cameroon', 'CA': 'Canada', 'CV': 'Cape Verde',
        'KY': 'Cayman Islands', 'CF': 'Central African Republic', 'TD': 'Chad',
        'CL': 'Chile', 'CN': 'China', 'CX': 'Christmas Island', 'CC': 'Cocos (Keeling) Islands',
        'CO': 'Colombia', 'KM': 'Comoros', 'CG': 'Congo', 'CD': 'Congo, Democratic Republic',
        'CK': 'Cook Islands', 'CR': 'Costa Rica', 'CI': 'Côte d\'Ivoire', 'HR': 'Croatia',
        'CU': 'Cuba', 'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark',
        'DJ': 'Djibouti', 'DM': 'Dominica', 'DO': 'Dominican Republic', 'EC': 'Ecuador',
        'EG': 'Egypt', 'SV': 'El Salvador', 'GQ': 'Equatorial Guinea', 'ER': 'Eritrea',
        'EE': 'Estonia', 'ET': 'Ethiopia', 'FK': 'Falkland Islands', 'FO': 'Faroe Islands',
        'FJ': 'Fiji', 'FI': 'Finland', 'FR': 'France', 'GF': 'French Guiana',
        'PF': 'French Polynesia', 'TF': 'French Southern Territories', 'GA': 'Gabon',
        'GM': 'Gambia', 'GE': 'Georgia', 'DE': 'Germany', 'GH': 'Ghana', 'GI': 'Gibraltar',
        'GR': 'Greece', 'GL': 'Greenland', 'GD': 'Grenada', 'GP': 'Guadeloupe',
        'GU': 'Guam', 'GT': 'Guatemala', 'GG': 'Guernsey', 'GN': 'Guinea',
        'GW': 'Guinea-Bissau', 'GY': 'Guyana', 'HT': 'Haiti', 'HM': 'Heard Island and McDonald Islands',
        'VA': 'Holy See (Vatican City)', 'HN': 'Honduras', 'HK': 'Hong Kong',
        'HU': 'Hungary', 'IS': 'Iceland', 'IN': 'India', 'ID': 'Indonesia',
        'IR': 'Iran', 'IQ': 'Iraq', 'IE': 'Ireland', 'IM': 'Isle of Man',
        'IL': 'Israel', 'IT': 'Italy', 'JM': 'Jamaica', 'JP': 'Japan', 'JE': 'Jersey',
        'JO': 'Jordan', 'KZ': 'Kazakhstan', 'KE': 'Kenya', 'KI': 'Kiribati',
        'KP': 'North Korea', 'KR': 'South Korea', 'KW': 'Kuwait', 'KG': 'Kyrgyzstan',
        'LA': 'Laos', 'LV': 'Latvia', 'LB': 'Lebanon', 'LS': 'Lesotho', 'LR': 'Liberia',
        'LY': 'Libya', 'LI': 'Liechtenstein', 'LT': 'Lithuania', 'LU': 'Luxembourg',
        'MO': 'Macao', 'MG': 'Madagascar', 'MW': 'Malawi', 'MY': 'Malaysia',
        'MV': 'Maldives', 'ML': 'Mali', 'MT': 'Malta', 'MH': 'Marshall Islands',
        'MQ': 'Martinique', 'MR': 'Mauritania', 'MU': 'Mauritius', 'YT': 'Mayotte',
        'MX': 'Mexico', 'FM': 'Micronesia', 'MD': 'Moldova', 'MC': 'Monaco',
        'MN': 'Mongolia', 'ME': 'Montenegro', 'MS': 'Montserrat', 'MA': 'Morocco',
        'MZ': 'Mozambique', 'MM': 'Myanmar', 'NA': 'Namibia', 'NR': 'Nauru',
        'NP': 'Nepal', 'NL': 'Netherlands', 'NC': 'New Caledonia', 'NZ': 'New Zealand',
        'NI': 'Nicaragua', 'NE': 'Niger', 'NG': 'Nigeria', 'NU': 'Niue',
        'NF': 'Norfolk Island', 'MK': 'North Macedonia', 'MP': 'Northern Mariana Islands',
        'NO': 'Norway', 'OM': 'Oman', 'PK': 'Pakistan', 'PW': 'Palau', 'PS': 'Palestine',
        'PA': 'Panama', 'PG': 'Papua New Guinea', 'PY': 'Paraguay', 'PE': 'Peru',
        'PH': 'Philippines', 'PN': 'Pitcairn', 'PL': 'Poland', 'PT': 'Portugal',
        'PR': 'Puerto Rico', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Romania',
        'RU': 'Russian Federation', 'RW': 'Rwanda', 'BL': 'Saint Barthélemy',
        'SH': 'Saint Helena', 'KN': 'Saint Kitts and Nevis', 'LC': 'Saint Lucia',
        'MF': 'Saint Martin', 'PM': 'Saint Pierre and Miquelon', 'VC': 'Saint Vincent and the Grenadines',
        'WS': 'Samoa', 'SM': 'San Marino', 'ST': 'Sao Tome and Principe', 'SA': 'Saudi Arabia',
        'SN': 'Senegal', 'RS': 'Serbia', 'SC': 'Seychelles', 'SL': 'Sierra Leone',
        'SG': 'Singapore', 'SX': 'Sint Maarten', 'SK': 'Slovakia', 'SI': 'Slovenia',
        'SB': 'Solomon Islands', 'SO': 'Somalia', 'ZA': 'South Africa',
        'GS': 'South Georgia and the South Sandwich Islands', 'SS': 'South Sudan',
        'ES': 'Spain', 'LK': 'Sri Lanka', 'SD': 'Sudan', 'SR': 'Suriname',
        'SJ': 'Svalbard and Jan Mayen', 'SZ': 'Eswatini', 'SE': 'Sweden',
        'CH': 'Switzerland', 'SY': 'Syria', 'TW': 'Taiwan', 'TJ': 'Tajikistan',
        'TZ': 'Tanzania', 'TH': 'Thailand', 'TL': 'Timor-Leste', 'TG': 'Togo',
        'TK': 'Tokelau', 'TO': 'Tonga', 'TT': 'Trinidad and Tobago', 'TN': 'Tunisia',
        'TR': 'Turkey', 'TM': 'Turkmenistan', 'TC': 'Turks and Caicos Islands',
        'TV': 'Tuvalu', 'UG': 'Uganda', 'UA': 'Ukraine', 'AE': 'United Arab Emirates',
        'GB': 'United Kingdom', 'US': 'United States', 'UM': 'United States Minor Outlying Islands',
        'UY': 'Uruguay', 'UZ': 'Uzbekistan', 'VU': 'Vanuatu', 'VE': 'Venezuela',
        'VN': 'Vietnam', 'VG': 'Virgin Islands (British)', 'VI': 'Virgin Islands (U.S.)',
        'WF': 'Wallis and Futuna', 'EH': 'Western Sahara', 'YE': 'Yemen', 'ZM': 'Zambia', 'ZW': 'Zimbabwe'
    }
    return mapping.get(code, code)

def detect_anonymity(proxy, protocol, timeout=5):
    """Improved anonymity detection - never returns Unknown."""
    cache_key = f"{proxy}_{protocol}"
    if cache_key in anonymity_cache:
        return anonymity_cache[cache_key]
    
    try:
        ip, port = proxy.split(':')
        test_url = 'http://httpbin.org/get'
        
        if protocol == 'http':
            proxies_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            r = requests.get(test_url, proxies=proxies_dict, timeout=timeout, verify=False)
            if r.status_code == 200:
                data = r.json()
                headers = data.get('headers', {})
                origin = data.get('origin', '')
                
                forwarded = headers.get('X-Forwarded-For', '')
                via = headers.get('Via', '')
                proxy_conn = headers.get('Proxy-Connection', '')
                
                if forwarded and origin in forwarded:
                    anonymity = 'Transparent'
                elif forwarded or via or proxy_conn:
                    anonymity = 'Anonymous'
                else:
                    anonymity = 'Elite'
                anonymity_cache[cache_key] = anonymity
                return anonymity
        elif protocol in ['socks4', 'socks5']:
            sock = socks.socksocket()
            if protocol == 'socks4':
                sock.set_proxy(socks.SOCKS4, ip, int(port))
            else:
                sock.set_proxy(socks.SOCKS5, ip, int(port))
            sock.settimeout(timeout)
            sock.connect(('httpbin.org', 80))
            request = f"GET /get HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            response = b''
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            sock.close()
            response_str = response.decode('utf-8', errors='ignore')
            
            if 'X-Forwarded-For' in response_str:
                anonymity = 'Transparent'
            elif 'Via' in response_str or 'Proxy-Connection' in response_str:
                anonymity = 'Anonymous'
            else:
                anonymity = 'Elite'
            anonymity_cache[cache_key] = anonymity
            return anonymity
    except Exception as e:
        pass
    
    anonymity_cache[cache_key] = 'Anonymous'
    return 'Anonymous'

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

BANNER = f"""
{C['header']}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███╗   ███╗██╗   ██╗████████╗██╗  ██╗██╗ ██████╗               ║
║   ████╗ ████║╚██╗ ██╔╝╚══██╔══╝██║  ██║██║██╔════╝               ║
║   ██╔████╔██║ ╚████╔╝    ██║   ███████║██║██║                    ║
║   ██║╚██╔╝██║  ╚██╔╝     ██║   ██╔══██║██║██║                    ║
║   ██║ ╚═╝ ██║   ██║      ██║   ██║  ██║██║╚██████╗               ║
║   ╚═╝     ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝               ║
║                                                                   ║
║              🔥 PROXY SCRAPER & TESTER 🔥                        ║
║                   BY: MR.MYTHIC_KILLER                           ║
║                        VERSION 6.0                                ║
║            📁 200+ SOURCES + COUNTRY DETECTION 📁                ║
╚═══════════════════════════════════════════════════════════════════╝
{C['reset']}
"""

# ======================== UPDATED PROXY SOURCES (2025-2026) ========================
ALL_SOURCES = [
    # Existing sources (kept as is)
    {'name': 'Geonode', 'url': 'https://geonode.com/free-proxy-list', 'type': 'html', 'pages': 3},
    {'name': 'FreeProxy.World', 'url': 'https://www.freeproxy.world/', 'type': 'html', 'pages': 3},
    {'name': 'FreeProxy.World HTTP', 'url': 'https://www.freeproxy.world/?type=http', 'type': 'html', 'pages': 2},
    {'name': 'FreeProxy.World SOCKS4', 'url': 'https://www.freeproxy.world/?type=socks4', 'type': 'html', 'pages': 2},
    {'name': 'FreeProxy.World SOCKS5', 'url': 'https://www.freeproxy.world/?type=socks5', 'type': 'html', 'pages': 2},
    {'name': 'SSLProxies', 'url': 'https://www.sslproxies.org/', 'type': 'html', 'pages': 2},
    {'name': 'US-Proxy', 'url': 'https://www.us-proxy.org/', 'type': 'html', 'pages': 2},
    {'name': 'SocksProxy', 'url': 'https://www.socks-proxy.net/', 'type': 'html', 'pages': 2},
    {'name': 'Free-Proxy-List', 'url': 'https://free-proxy-list.net/', 'type': 'html', 'pages': 2},
    {'name': 'HideMy.name', 'url': 'https://hidemy.name/en/proxy-list/', 'type': 'html', 'pages': 3},
    {'name': 'ProxyNova', 'url': 'https://www.proxynova.com/proxy-server-list/', 'type': 'html', 'pages': 3},
    {'name': 'TheSpeedX HTTP', 'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'TheSpeedX SOCKS4', 'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'TheSpeedX SOCKS5', 'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'iplocate All', 'url': 'https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt', 'type': 'raw', 'pages': 1},
    {'name': 'iplocate HTTP', 'url': 'https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'iplocate SOCKS4', 'url': 'https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'iplocate SOCKS5', 'url': 'https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'triple666 All', 'url': 'https://raw.githubusercontent.com/trio666/proxy-checker/main/all.txt', 'type': 'raw', 'pages': 1},
    {'name': 'triple666 HTTP', 'url': 'https://raw.githubusercontent.com/trio666/proxy-checker/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'triple666 SOCKS4', 'url': 'https://raw.githubusercontent.com/trio666/proxy-checker/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'triple666 SOCKS5', 'url': 'https://raw.githubusercontent.com/trio666/proxy-checker/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'databay HTTP', 'url': 'https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'databay SOCKS4', 'url': 'https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'databay SOCKS5', 'url': 'https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'stormsia HTTP', 'url': 'https://raw.githubusercontent.com/stormsia/proxy-list/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'stormsia SOCKS4', 'url': 'https://raw.githubusercontent.com/stormsia/proxy-list/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'stormsia SOCKS5', 'url': 'https://raw.githubusercontent.com/stormsia/proxy-list/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyScrape API HTTP', 'url': 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=10000&country=all', 'type': 'api', 'pages': 1},
    {'name': 'ProxyScrape API SOCKS4', 'url': 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=10000&country=all', 'type': 'api', 'pages': 1},
    {'name': 'ProxyScrape API SOCKS5', 'url': 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=10000&country=all', 'type': 'api', 'pages': 1},
    {'name': 'Geonode API', 'url': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'type': 'api', 'pages': 1},
    {'name': 'OpenProxySpace HTTP', 'url': 'https://openproxy.space/list/http', 'type': 'html', 'pages': 2},
    {'name': 'OpenProxySpace SOCKS4', 'url': 'https://openproxy.space/list/socks4', 'type': 'html', 'pages': 2},
    {'name': 'OpenProxySpace SOCKS5', 'url': 'https://openproxy.space/list/socks5', 'type': 'html', 'pages': 2},
    
    # ======================== NEW PROXY SOURCES (2025-2026) ========================
    {'name': 'ProxyListDownload HTTP', 'url': 'https://www.proxy-list.download/api/v1/get?type=http', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyListDownload SOCKS4', 'url': 'https://www.proxy-list.download/api/v1/get?type=socks4', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyListDownload SOCKS5', 'url': 'https://www.proxy-list.download/api/v1/get?type=socks5', 'type': 'raw', 'pages': 1},
    {'name': 'OpenProxyList HTTP', 'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt', 'type': 'raw', 'pages': 1},
    {'name': 'OpenProxyList SOCKS4', 'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'type': 'raw', 'pages': 1},
    {'name': 'OpenProxyList SOCKS5', 'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'type': 'raw', 'pages': 1},
    {'name': 'MortenProxy HTTP', 'url': 'https://raw.githubusercontent.com/mortennas/ProxyLists/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'MortenProxy SOCKS4', 'url': 'https://raw.githubusercontent.com/mortennas/ProxyLists/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'MortenProxy SOCKS5', 'url': 'https://raw.githubusercontent.com/mortennas/ProxyLists/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ShiftyTR HTTP', 'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ShiftyTR SOCKS4', 'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ShiftyTR SOCKS5', 'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'Uptimer HTTP', 'url': 'https://raw.githubusercontent.com/Uptimer/Proxy-List/main/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'Uptimer SOCKS4', 'url': 'https://raw.githubusercontent.com/Uptimer/Proxy-List/main/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'Uptimer SOCKS5', 'url': 'https://raw.githubusercontent.com/Uptimer/Proxy-List/main/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyListPro HTTP', 'url': 'https://proxy-list.pro/list/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyListPro SOCKS4', 'url': 'https://proxy-list.pro/list/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyListPro SOCKS5', 'url': 'https://proxy-list.pro/list/socks5.txt', 'type': 'raw', 'pages': 1},
    {'name': 'PubProxy API', 'url': 'http://pubproxy.com/api/proxy?limit=20&format=txt', 'type': 'raw', 'pages': 1},
    {'name': 'ProxyRack API', 'url': 'https://www.proxyrack.com/api/freeproxies?protocol=http', 'type': 'raw', 'pages': 1},
    {'name': 'VPNBook', 'url': 'https://www.vpnbook.com/free-proxy-list', 'type': 'html', 'pages': 1},
    {'name': 'CoolProxy', 'url': 'https://www.cool-proxy.net/', 'type': 'html', 'pages': 1},
    {'name': 'ProxyElite', 'url': 'https://proxyelite.info/', 'type': 'html', 'pages': 1},
    {'name': 'SpysOne', 'url': 'https://spys.one/en/free-proxy-list/', 'type': 'html', 'pages': 1},
    {'name': 'Xseo', 'url': 'https://xseo.in/freeproxy', 'type': 'html', 'pages': 1},
    {'name': 'Proxydb', 'url': 'http://proxydb.net/', 'type': 'html', 'pages': 1},
    {'name': 'ProxyListOrg', 'url': 'https://www.proxy-list.org/', 'type': 'html', 'pages': 1},
    {'name': 'FreeProxyListsNet', 'url': 'https://www.freeproxylists.net/', 'type': 'html', 'pages': 1},
    {'name': 'ProxyHubMe', 'url': 'https://proxyhub.me/', 'type': 'html', 'pages': 1},
    {'name': 'MyProxy', 'url': 'https://www.my-proxy.com/free-proxy-list.html', 'type': 'html', 'pages': 1},
    {'name': 'FreeProxyListCC', 'url': 'https://www.freeproxylist.cc/', 'type': 'html', 'pages': 1},
]

DATABAY_SOURCES = [
    {'name': 'databay HTTP', 'url': 'https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/http.txt', 'type': 'raw', 'pages': 1},
    {'name': 'databay SOCKS4', 'url': 'https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks4.txt', 'type': 'raw', 'pages': 1},
    {'name': 'databay SOCKS5', 'url': 'https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks5.txt', 'type': 'raw', 'pages': 1},
]

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
seen_proxies = set()

def send_discord_embed(proxy, protocol, latency_ms, country, anonymity):
    ip, port = proxy.split(':')
    latency_s = latency_ms / 1000.0
    emoji_green_dot = "<a:Green_dot:1505951396409770035>"
    emoji_blue_lightning = "<a:Blue_lightening:1474817269635743975>"
    emoji_starry = "<a:Starry:1418231871279595561>"
    emoji_server_ping = "<:Server_Ping_5:1489894447213838336>"
    emoji_loading = "<a:loading:1492834560445120594>"
    emoji_world = "<:world:1492832312927191072>"
    emoji_user = "<:User:1489203845283451001>"
    embed = {
        "embeds": [{
            "title": f"{emoji_green_dot} Valid Proxy Found!",
            "color": 0x00ff00,
            "fields": [
                {"name": f"{emoji_blue_lightning} IP Address", "value": ip, "inline": True},
                {"name": "🔌 Port", "value": port, "inline": True},
                {"name": f"{emoji_starry} Combo", "value": proxy, "inline": False},
                {"name": "🛜 Type", "value": protocol.upper(), "inline": True},
                {"name": f"{emoji_server_ping} Latency", "value": f"{latency_ms:.2f} ms", "inline": True},
                {"name": f"{emoji_loading} Response", "value": f"{latency_s:.2f} s", "inline": True},
                {"name": f"{emoji_world} Country", "value": country, "inline": True},
                {"name": f"{emoji_user} Anonymity", "value": anonymity, "inline": True}
            ],
            "footer": {"text": "MR.MYTHIC_KILLER Proxy Tool"},
            "timestamp": datetime.now(UTC).isoformat()
        }]
    }
    try:
        r = requests.post(EMBED_WEBHOOK, json=embed, timeout=5)
        if r.status_code == 429:
            retry_after = r.json().get('retry_after', 1)
            time.sleep(retry_after)
            requests.post(EMBED_WEBHOOK, json=embed, timeout=5)
    except:
        pass

def get_ip_info(ip):
    country = get_country_full(ip)
    return country, ''

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
    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})', line)
    if match:
        proxy = f"{match.group(1)}:{match.group(2)}"
        with lock:
            if proxy not in seen_proxies:
                seen_proxies.add(proxy)
                return proxy
    return None

def parse_geonode_csv(csv_text):
    proxies = []
    try:
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader)
        ip_idx = port_idx = protocol_idx = country_idx = anonymity_idx = None
        for i, h in enumerate(headers):
            hl = h.lower()
            if 'ip' in hl: ip_idx = i
            elif 'port' in hl: port_idx = i
            elif 'protocol' in hl: protocol_idx = i
            elif 'country' in hl: country_idx = i
            elif 'anonymity' in hl or 'elite' in hl: anonymity_idx = i
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
                            protocol = row[protocol_idx].strip('"') if protocol_idx is not None else 'Unknown'
                            country = row[country_idx].strip('"') if country_idx is not None else 'Unknown'
                            anonymity = row[anonymity_idx].strip('"') if anonymity_idx is not None else 'Unknown'
                            with open(os.path.join(RESULTS_DIR, "proxy_details.txt"), 'a') as f:
                                f.write(f"{proxy} | {protocol} | {country} | {anonymity}\n")
    except:
        pass
    return proxies

def parse_api_json(json_text):
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
    except:
        pass
    return proxies

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def scrape_from_html(url):
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=(10,20), verify=False)
        if r.status_code == 200:
            if 'geonode.com' in url:
                soup = BeautifulSoup(r.text, 'html.parser')
                for tag in soup.find_all(['textarea', 'pre', 'script']):
                    if tag.string and ('IP' in tag.string or 'anonymityLevel' in tag.string):
                        csv_text = tag.string
                        geo_proxies = parse_geonode_csv(csv_text)
                        proxies.extend(geo_proxies)
            if not proxies:
                ip_ports = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})', r.text)
                for ip, port in ip_ports:
                    proxy = f"{ip}:{port}"
                    with lock:
                        if proxy not in seen_proxies:
                            seen_proxies.add(proxy)
                            proxies.append(proxy)
    except:
        pass
    return proxies

def scrape_from_raw(url):
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=(10,20), verify=False)
        if r.status_code == 200:
            for line in r.text.splitlines():
                proxy = parse_proxy_line(line.strip())
                if proxy:
                    proxies.append(proxy)
    except:
        pass
    return proxies

def scrape_from_api(url):
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=(10,20), verify=False)
        if r.status_code == 200:
            proxies = parse_api_json(r.text)
    except:
        pass
    return proxies

def scrape_proxies(max_limit=None):
    global scraped_proxies, seen_proxies
    scraped_proxies = []
    seen_proxies.clear()
    
    if max_limit is not None and max_limit < 500:
        sources = DATABAY_SOURCES
        source_type = "FAST (databay only)"
    else:
        sources = ALL_SOURCES
        source_type = "FULL (all sources)"
    
    if max_limit is None or max_limit <= 0:
        limit_text = "UNLIMITED (max possible)"
    else:
        limit_text = f"{max_limit}"
    
    print(f"\n{C['scrape']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['scrape']}║              SCRAPING PROXIES FROM WORKING SOURCES        ║")
    print(f"{C['scrape']}║              Mode: {source_type:<30}                    ║")
    print(f"{C['scrape']}║              Target: {limit_text:<30}                    ║")
    print(f"{C['scrape']}╚════════════════════════════════════════════════════════════╝\n")
    
    total_sources = sum(src.get('pages',1) for src in sources)
    current = 0
    
    for source in sources:
        if max_limit is not None and len(scraped_proxies) >= max_limit:
            print(f"\n{C['success']}  ✓ Reached target of {max_limit} proxies, stopping scrape.")
            break
        for page in range(1, source.get('pages',1)+1):
            if max_limit is not None and len(scraped_proxies) >= max_limit:
                break
            current += 1
            url = source['url']
            if page > 1:
                if 'page=' in url:
                    url = re.sub(r'page=\d+', f'page={page}', url)
                else:
                    url = url.rstrip('/') + f'?page={page}'
            
            if max_limit is None:
                print(f"{C['info']}Scraped Proxies: [{len(scraped_proxies):<6}] | Status: Scraping from {source['name']} (Page {page})...{C['reset']}", end='\r')
            else:
                print(f"{C['info']}Scraped Proxies: [{len(scraped_proxies)}/{max_limit}] | Status: Scraping from {source['name']} (Page {page})...{C['reset']}", end='\r')
            
            if source['type'] == 'html':
                proxies = scrape_from_html(url)
            elif source['type'] == 'api':
                proxies = scrape_from_api(url)
            else:
                proxies = scrape_from_raw(url)
            
            with lock:
                if max_limit is not None:
                    needed = max_limit - len(scraped_proxies)
                    if needed <= 0:
                        break
                    proxies = proxies[:needed]
                scraped_proxies.extend(proxies)
            
            if max_limit is None:
                print(f"{C['info']}Scraped Proxies: [{len(scraped_proxies):<6}] | Status: {source['name']} (Page {page}) -> +{len(proxies)}     {C['reset']}", end='\r')
            else:
                print(f"{C['info']}Scraped Proxies: [{len(scraped_proxies)}/{max_limit}] | Status: {source['name']} (Page {page}) -> +{len(proxies)}     {C['reset']}", end='\r')
            
            time.sleep(random.uniform(0.3,0.7))
    
    print(f"\n\n{C['success']}  ✓ Scraping finished! Total unique proxies scraped: {len(scraped_proxies)}")
    with open(os.path.join(RESULTS_DIR, "scraped_proxies.txt"), 'w') as f:
        for proxy in scraped_proxies:
            f.write(proxy + '\n')
    return scraped_proxies

def send_discord_file(protocol_type, proxies_list):
    if not proxies_list or FILE_WEBHOOK == "YOUR_FILE_WEBHOOK_URL_HERE":
        return
    try:
        filename = f"{protocol_type}_proxies.txt"
        filepath = os.path.join(RESULTS_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(f"# {len(proxies_list)} {protocol_type.upper()} Proxies\n")
            f.write(f"# Generated by MR.MYTHIC_KILLER Proxy Tool\n")
            f.write(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# format: ip:port\n")
            for proxy in proxies_list:
                f.write(proxy + '\n')
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            r = requests.post(FILE_WEBHOOK, files=files, timeout=10)
            if r.status_code == 429:
                retry_after = r.json().get('retry_after', 2)
                time.sleep(retry_after)
                requests.post(FILE_WEBHOOK, files=files, timeout=10)
    except:
        pass

def send_all_proxy_files():
    global valid_proxies
    if not valid_proxies:
        return
    http_proxies = [p[0] for p in valid_proxies if p[1] == 'http']
    socks4_proxies = [p[0] for p in valid_proxies if p[1] == 'socks4']
    socks5_proxies = [p[0] for p in valid_proxies if p[1] == 'socks5']
    if http_proxies:
        send_discord_file('http', http_proxies)
        time.sleep(1)
    if socks4_proxies:
        send_discord_file('socks4', socks4_proxies)
        time.sleep(1)
    if socks5_proxies:
        send_discord_file('socks5', socks5_proxies)
        time.sleep(1)
    all_proxies = [p[0] for p in valid_proxies]
    if all_proxies:
        send_discord_file('all_valid', all_proxies)

def test_proxy_http(proxy, timeout=5):
    try:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        start = time.time()
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=timeout, verify=False)
        if r.status_code == 200:
            return True, 'http', (time.time() - start) * 1000
    except:
        pass
    return False, None, 0

def test_proxy_socks4(proxy, timeout=5):
    try:
        ip, port = proxy.split(':')
        start = time.time()
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS4, ip, int(port))
        sock.settimeout(timeout)
        sock.connect(('httpbin.org', 80))
        sock.send(b"GET /ip HTTP/1.0\r\nHost: httpbin.org\r\n\r\n")
        sock.recv(1024)
        sock.close()
        return True, 'socks4', (time.time() - start) * 1000
    except:
        pass
    return False, None, 0

def test_proxy_socks5(proxy, timeout=5):
    try:
        ip, port = proxy.split(':')
        start = time.time()
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, ip, int(port))
        sock.settimeout(timeout)
        sock.connect(('httpbin.org', 80))
        sock.send(b"GET /ip HTTP/1.0\r\nHost: httpbin.org\r\n\r\n")
        sock.recv(1024)
        sock.close()
        return True, 'socks5', (time.time() - start) * 1000
    except:
        pass
    return False, None, 0

def test_proxy_worker(proxy_type_filter='mix'):
    global total_tested, total_valid, total_invalid, total_failed, cpm
    while not stop_testing and not proxy_queue.empty():
        try:
            proxy = proxy_queue.get(timeout=1)
        except:
            break
        is_valid = False
        protocol = None
        speed = 0
        if proxy_type_filter in ['mix','http']:
            is_valid, protocol, speed = test_proxy_http(proxy)
        if not is_valid and proxy_type_filter in ['mix','socks4']:
            is_valid, protocol, speed = test_proxy_socks4(proxy)
        if not is_valid and proxy_type_filter in ['mix','socks5']:
            is_valid, protocol, speed = test_proxy_socks5(proxy)
        with lock:
            total_tested += 1
            if is_valid:
                total_valid += 1
                country = get_country_full(proxy.split(':')[0])
                anonymity = detect_anonymity(proxy, protocol)
                valid_proxies.append((proxy, protocol, speed, anonymity))
                threading.Thread(target=send_discord_embed, args=(proxy, protocol, speed, country, anonymity), daemon=True).start()
            else:
                total_invalid += 1
            remaining = proxy_queue.qsize()
            elapsed = time.time() - start_time
            cpm = int((total_tested/elapsed)*60) if elapsed>0 else 0
            print(f"\r{C['test']}Working Proxies: {C['good']}{total_valid}{C['reset']} | Invalid: {C['bad']}{total_invalid}{C['reset']} | Remaining: {remaining} | CPM: {cpm}{C['reset']}", end='')
            update_title()
        proxy_queue.task_done()

def test_proxies(proxies_to_test, proxy_type_filter='mix', threads=500):
    global stop_testing, total_tested, total_valid, total_invalid, valid_proxies, start_time
    stop_testing = False
    total_tested = 0
    total_valid = 0
    total_invalid = 0
    valid_proxies = []
    start_time = time.time()
    for p in proxies_to_test:
        proxy_queue.put(p)
    print(f"\n{C['test']}Finished Scraping now Testing...{C['reset']}\n")
    print(f"{C['test']}Testing {len(proxies_to_test)} proxies with {threads} threads...\n")
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
    if valid_proxies:
        valid_proxies.sort(key=lambda x: x[2])
        http_proxies = [p[0] for p in valid_proxies if p[1]=='http']
        socks4_proxies = [p[0] for p in valid_proxies if p[1]=='socks4']
        socks5_proxies = [p[0] for p in valid_proxies if p[1]=='socks5']
        with open(os.path.join(RESULTS_DIR, "http_proxies.txt"), 'w') as f:
            f.write('\n'.join(http_proxies))
        with open(os.path.join(RESULTS_DIR, "socks4_proxies.txt"), 'w') as f:
            f.write('\n'.join(socks4_proxies))
        with open(os.path.join(RESULTS_DIR, "socks5_proxies.txt"), 'w') as f:
            f.write('\n'.join(socks5_proxies))
        with open(os.path.join(RESULTS_DIR, "all_valid_proxies.txt"), 'w') as f:
            for proxy, protocol, resp_time, anonymity in valid_proxies:
                f.write(f"{proxy} | {protocol} | {resp_time:.2f}ms | {anonymity}\n")
        print(f"{C['success']}  ✓ Saved valid proxies to {RESULTS_DIR}/")
        send_all_proxy_files()
    return valid_proxies

def main():
    global scraped_proxies, start_time
    print_banner()
    print(f"\n{C['menu']}╔════════════════════════════════════════════════════════════╗")
    print(f"{C['menu']}║                    SELECT MODE                             ║")
    print(f"{C['menu']}╠════════════════════════════════════════════════════════════╣")
    print(f"{C['menu']}║  {C['option']}[1] {C['menu']}Auto Scraping Only                         ║")
    print(f"{C['menu']}║  {C['option']}[2] {C['menu']}Proxy Test Only                            ║")
    print(f"{C['menu']}║  {C['option']}[3] {C['menu']}Both (Scrape + Test)                       ║")
    print(f"{C['menu']}╚════════════════════════════════════════════════════════════╝")
    choice = input(f"\n{C['option']}  [?] Enter your choice (1/2/3): {C['reset']}").strip()
    
    proxy_type_filter = 'mix'
    if choice in ['2','3']:
        print(f"\n{C['menu']}╔════════════════════════════════════════════════════════════╗")
        print(f"{C['menu']}║                SELECT PROXY TYPE TO TEST                   ║")
        print(f"{C['menu']}╠════════════════════════════════════════════════════════════╣")
        print(f"{C['menu']}║  {C['option']}[1] {C['menu']}HTTP/HTTPS Only                           ║")
        print(f"{C['menu']}║  {C['option']}[2] {C['menu']}SOCKS4 Only                               ║")
        print(f"{C['menu']}║  {C['option']}[3] {C['menu']}SOCKS5 Only                               ║")
        print(f"{C['menu']}║  {C['option']}[4] {C['menu']}MIX (Auto-detect)                         ║")
        print(f"{C['menu']}╚════════════════════════════════════════════════════════════╝")
        type_choice = input(f"\n{C['option']}  [?] Enter your choice (1/2/3/4): {C['reset']}").strip()
        type_map = {'1':'http','2':'socks4','3':'socks5','4':'mix'}
        proxy_type_filter = type_map.get(type_choice, 'mix')
    
    max_limit = None
    if choice in ['1','3']:
        limit_input = input(f"\n{C['option']}  [?] Maximum proxies to scrape (0 or Enter for unlimited): {C['reset']}").strip()
        if limit_input == "" or limit_input == "0":
            max_limit = None
        else:
            try:
                max_limit = int(limit_input)
                if max_limit <= 0:
                    max_limit = None
            except:
                max_limit = None
    
    threads = 500
    if choice in ['2','3']:
        try:
            threads_input = input(f"\n{C['option']}  [?] Testing threads (10-500, default 500): {C['reset']}") or "500"
            threads = int(threads_input)
            threads = max(10, min(500, threads))
        except:
            threads = 500
    
    start_time = time.time()
    
    if choice == '1':
        proxies = scrape_proxies(max_limit)
        print(f"\n{C['success']}  ✓ Scraping complete! {len(proxies)} proxies saved to {RESULTS_DIR}/scraped_proxies.txt")
    elif choice == '2':
        file_path = input(f"\n{C['option']}  [?] Enter path to proxy file: {C['reset']}").strip()
        if not os.path.exists(file_path):
            print(f"{C['error']}  ✗ File not found!")
            return
        with open(file_path, 'r') as f:
            proxies_to_test = [parse_proxy_line(line) for line in f if parse_proxy_line(line)]
        print(f"{C['info']}  → Loaded {len(proxies_to_test)} proxies")
        test_proxies(proxies_to_test, proxy_type_filter, threads)
    elif choice == '3':
        proxies = scrape_proxies(max_limit)
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
