import os
import sys
import time
import requests
import json

from jinja2 import __version__ as jinja2_version
from jinja2 import Environment
from jinja2 import FileSystemLoader

APP_NAME = 'pocket.widget'
APP_TITLE = 'Pocket Widget'
APP_URL = 'https://github.com/joedf/pocket.widget'

APP_USERNAME = 'joedf'

TEMPLATE_FILE = 'web/widget.j2'
TEMPLATE_OUT = 'web/output.html'

# REDIRECT_URI = 'pocketapp1234:authorizationFinished'
REDIRECT_URI = APP_URL
CONSUMER_KEY = ''
ACCESS_CODE = ''
ACCESS_TOKEN = ''

# https://getpocket.com/developer/docs/overview
API_URI = "https://getpocket.com/v3/"

ALLOW_SAVE_KEYS = False


def main():
    CONSUMER_KEY = tryGetKey('CONSUMER_KEY')
    ACCESS_CODE = tryGetKey('ACCESS_CODE')
    ACCESS_TOKEN = tryGetKey('ACCESS_TOKEN')

    # ----------------------------------------------------
    # Get consumer key as arg if provided
    if len(sys.argv) > 1:
        # check if provided as arg / param
        CONSUMER_KEY = sys.argv[1]

    # ----------------------------------------------------
    # Quick validate consumer key
    if not isValidKey(CONSUMER_KEY):
        print(f'ERROR: Invalid CONSUMER_KEY provided: {CONSUMER_KEY}')
        sys.exit()

    # ----------------------------------------------------
    # Request for authorization, if needed
    # https://getpocket.com/developer/docs/authentication
    if len(sys.argv) > 2:
        # check if provided as arg / param
        ACCESS_CODE = sys.argv[2]

    if not isValidKey(ACCESS_CODE):
        r = requests.get(API_URI + 'oauth/request', params={
            'consumer_key': CONSUMER_KEY,
            'redirect_uri': REDIRECT_URI,
        })

        if 'code=' not in r.text:
            print('ERROR: Failed to get access code.')
            sys.exit()

        access_code = r.text[5:]

        trySaveKey('ACCESS_CODE', access_code)
    else:
        access_code = ACCESS_CODE
    print("Access_code = " + access_code)

    # ----------------------------------------------------
    # Ask and Wait for user to authorize
    if len(sys.argv) > 3:
        # check if provided as arg / param
        ACCESS_TOKEN = sys.argv[3]

    if not isValidKey(ACCESS_TOKEN):
        url = f'https://getpocket.com/auth/authorize?request_token={access_code}^&redirect_uri={REDIRECT_URI}'
        AskUserToAuthorize(url)

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

        trySaveKey('ACCESS_TOKEN', access_token)
    else:
        access_token = ACCESS_TOKEN
        username = APP_USERNAME
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
    articles = []
    article_list = saves_data['list']
    for article_id in article_list:
        article = article_list[article_id]

        title = article['resolved_title']
        url = article['resolved_url']

        short_title = title[:27] + '...'

        print(f'\ntitle = {title}\nurl = {url}\nshortened title = {short_title}')

        articles.append({
            'title': title,
            'link': url,
            'image': article['top_image_url'],
            'excerpt': article['excerpt'],
            'time_to_read': article['time_to_read']
        })

    # ----------------------------------------------------
    # Generate widget HTML page
    print(f"\nGenerating html page with jinja2 v{jinja2_version} ...")
    renderSaveAs(TEMPLATE_FILE, TEMPLATE_OUT, {
        'app_name': APP_NAME,
        'app_title': APP_TITLE,
        'app_url': APP_URL,
        'username': APP_USERNAME,
        'articles': articles,
    })


def isValidKey(key):
    return ('-' in key) and (len(key) == 30)


def trySaveKey(keyFile, key):
    if ALLOW_SAVE_KEYS:
        try:
            with open(keyFile, 'w') as f:
                f.write(key)
        except:
            pass


def tryGetKey(keyFile):
    try:
        key = open(keyFile, 'r').readline()
        return key
    except:
        return ''


def AskUserToAuthorize(url):
    # import webbrowser
    # webbrowser.open('https://example.com')  # cross-platform
    os.system(f"start \"\" {url}")  # MS Windows only
    time.sleep(5)  # Sleep for n seconds.


def renderSaveAs(template_file, out_file, context):
    global JINJA2_ENV
    template = JINJA2_ENV.get_template(template_file)
    rendered_html = template.render(context)

    with open(out_file, "w", encoding='utf-8') as fp:
        fp.write(rendered_html)

    print('generated: '+out_file)


# This is the part that is executes first when the script is run by itself.
if __name__ == "__main__":
    global JINJA2_ENV
    JINJA2_ENV = Environment(loader=FileSystemLoader('.'))
    main()
