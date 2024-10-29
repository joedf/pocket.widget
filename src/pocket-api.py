import os
import sys
import time
import requests
import json

REDIRECT_URI = 'pocketapp1234:authorizationFinished'
CONSUMER_KEY = ''

# https://getpocket.com/developer/docs/overview
API_URI = "https://getpocket.com/v3/"


# ----------------------------------------------------
# Get consumer key
if len(sys.argv) > 1:
	# check if provided as arg / param
	CONSUMER_KEY = sys.argv[1]
else:
	# otherwise, attempt default file read
	CONSUMER_KEY = open('CONSUMER_KEY', 'r').readline()

# ----------------------------------------------------
# Quick validate consumer key
if '-' not in CONSUMER_KEY or len(CONSUMER_KEY) != 30:
	print(f'ERROR: Invalid CONSUMER_KEY provided: {CONSUMER_KEY}')
	sys.exit()

# ----------------------------------------------------
# Request for authorization
# https://getpocket.com/developer/docs/authentication
r = requests.get(API_URI + 'oauth/request', params={
	'consumer_key': CONSUMER_KEY,
	'redirect_uri': REDIRECT_URI,
})

if 'code=' not in r.text:
	print('ERROR: Failed to get access code.')
	sys.exit()

access_code = r.text[5:]
print("Access_code = " + access_code)


# ----------------------------------------------------
# Ask and Wait for user to authorize
url = f'https://getpocket.com/auth/authorize?request_token={access_code}^&redirect_uri={REDIRECT_URI}'
# import webbrowser
# webbrowser.open('https://example.com')  # cross-platform
os.system(f"start \"\" {url}")  # MS Windows only
time.sleep(5)  # Sleep for n seconds.


# ----------------------------------------------------
# Convert access_code to access token and get username
r = requests.get(API_URI + 'oauth/authorize', params={
	'consumer_key': CONSUMER_KEY,
	'code': access_code,
})

if 'username' not in r.text:
	print('ERROR: Failed to authorize.')
	sys.exit()

raw_access_data = r.text
# raw_access_data = 'access_token=1d08fda3-d25c-8ab0-6242-24b1c4&username=some_username_here'

access_data = raw_access_data.split('&')
access_token = access_data[0][len('access_token='):]
username = access_data[1][len('username='):]
print(f"\naccess_token = {access_token}\nusername = {username}")


# ----------------------------------------------------
# Get user's latest pocket saves
# https://getpocket.com/developer/docs/v3/retrieve
r = requests.get(API_URI + 'get', params={
	'consumer_key': CONSUMER_KEY,
	'access_token': access_token,
	'count': 3,
	'sort': 'newest',
	# 'detailType': 'complete',
	'detailType': 'simple',
})

try:
	saves_data = json.loads(r.text)
	# print(f'\nPocket saves:\n{json.dumps(saves_data, indent=2)}')  # useful for debug
except:
	print('ERROR: Failed to parse retrieved data as json.')
	sys.exit()


# ----------------------------------------------------
# Print out latest saved articles
articles = saves_data['list']
for article_id in articles:
	article = articles[article_id]

	title = article['given_title']
	url = article['resolved_url']

	short_title = title[:27] + '...'

	print(f'\ntitle = {title}\nurl = {url}\nshortened title = {short_title}')

