import requests
import time
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = "bottoken"
CHAT_ID = "chatid"
USERNAME = 'username'
PASSWORD = 'passwd'

# CHANGE APPOINMENT ID AND APPLICANTS AT REQ3 BEFORE USING !!!

# Function to send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# Initialize a list to store dates
saved_dates = []

# Function to run the visa checker and send message if new dates are found
def check_visa_dates():
    # Step 1: Perform the first request to get CSRF token
    req1_url = 'https://ais.usvisa-info.com/tr-tr/niv/users/sign_in'

    req1_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response1 = requests.get(req1_url, headers=req1_headers)
    soup = BeautifulSoup(response1.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    # Step 2: Perform the login request
    login_url = 'https://ais.usvisa-info.com/tr-tr/niv/users/sign_in'
    login_data = {
        'user[email]': USERNAME,
        'user[password]': PASSWORD,
        'policy_confirmed': '1',
        'commit': 'Oturum+Aç'
    }

    login_headers = {
        'Accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://ais.usvisa-info.com',
        'Referer': 'https://ais.usvisa-info.com/tr-tr/niv/users/sign_in',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'X-CSRF-Token': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response2 = requests.post(login_url, headers=login_headers, cookies=response1.cookies, data=login_data)

    cookies_dict = requests.utils.dict_from_cookiejar(response2.cookies)

    # Step 3: Use cookies from the second request to perform the third request
    req3_url = 'https://ais.usvisa-info.com/tr-tr/niv/schedule/56348665/appointment?applicants%5B%5D=66235009&applicants%5B%5D=66235046&applicants%5B%5D=66235111&confirmed_limit_message=1&commit=Devam+Et'
    response3 = requests.get(req3_url, cookies=response2.cookies)

    # Step 4: Use cookies from the second request and CSRF token from the first request to perform the fourth request
    req4_url = 'https://ais.usvisa-info.com/tr-tr/niv/schedule/56348665/appointment/days/125.json?appointments[expedite]=false'
    req4_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': req3_url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'X-CSRF-Token': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response4 = requests.get(req4_url, headers=req4_headers, cookies=response2.cookies)

    # Extract dates from the response
    dates = [item['date'] for item in response4.json()]

    # Check for new dates
    new_dates = []
    for date in dates:
        if date not in saved_dates:
            new_dates.append(date)
            saved_dates.append(date)

    # If new dates are found, send a message to Telegram
    if new_dates:
        message = f"New visa appointment dates available: {', '.join(new_dates)}"
        send_telegram_message(message)

    # Print all available dates
    print("Available dates:")
    for date in dates:
        print(date)


# Run the function every 5 minutes
while True:
    check_visa_dates()
    time.sleep(300)  # Sleep for 5 minutes (300 seconds)
