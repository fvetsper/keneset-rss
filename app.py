import re
import requests
from datetime import datetime
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from flask import Flask, Response

app = Flask(__name__)

IL = ZoneInfo("Asia/Jerusalem")

ynet_cache = {
    'content': None,        # raw XML as fetched from ynet
    'last_fetch_hour': None
}

ITEM_RE = re.compile(rb'<item\b.*?</item>', re.DOTALL | re.IGNORECASE)
PUBDATE_RE = re.compile(rb'<pubDate>(.*?)</pubDate>', re.DOTALL | re.IGNORECASE)


def should_fetch_ynet():
    current_hour = datetime.now(IL).hour
    return ynet_cache['content'] is None or ynet_cache['last_fetch_hour'] != current_hour


def filter_before_current_hour(xml_bytes):
    # cutoff = top of the current Israel hour, e.g. 10:00:00
    cutoff = datetime.now(IL).replace(minute=0, second=0, microsecond=0)

    def keep(match):
        block = match.group(0)
        m = PUBDATE_RE.search(block)
        if not m:
            return block
        try:
            pub_dt = parsedate_to_datetime(m.group(1).strip().decode('utf-8', 'ignore'))
        except (TypeError, ValueError):
            return block
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=IL)
        return b'' if pub_dt >= cutoff else block  # drop items from this hour

    return ITEM_RE.sub(keep, xml_bytes)


@app.route('/health')
def health_check():
    return "OK", 200


@app.route('/ynet')
def get_ynet_rss():
    if should_fetch_ynet():
        url = 'https://www.ynet.co.il/Integration/StoryRss1854.xml'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                ynet_cache['content'] = response.content          # store RAW
                ynet_cache['last_fetch_hour'] = datetime.now(IL).hour
            elif ynet_cache['content'] is None:
                return f"Error: Status code {response.status_code}", 500
        except requests.RequestException as e:
            if ynet_cache['content'] is None:                     # serve stale on error
                return f"Error fetching RSS: {str(e)}", 500

    filtered = filter_before_current_hour(ynet_cache['content'])
    return Response(
        filtered,
        mimetype='application/rss+xml',
        headers={'Content-Type': 'application/rss+xml; charset=utf-8'}
    )


@app.route('/kneset')
def get_rss():
    url = 'https://main.knesset.gov.il/News/PressReleases/_layouts/15/listfeedKns.aspx'
    params = {
        'List': '0564d270-3847-4edf-a07e-9b8bd3c9f72d',
        'View': '6d8affa9-2f1c-48cb-a976-651985123519'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Cookie': 'waap_id=rR0E/Z0HgESk7wNxxh373RVIiyBuzuW0+ZE8Q1uVg1kGcF02En+bhNMHeGcbekj14Tn6phbuwzDN6JIiNCZY0d+GdTHZxESzEKvbIM61YuYMobDeT+U/wvZEggue0cVqrcHrtt1vKBs/oKtRqNGBhxL7tHTiIqjIBKONVx3veNDf/vF7qiwhFw0wBKX5xl3ac16Pp0nsKxmjPouzJnVN302grP8_'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            return Response(
                response.content,
                mimetype='application/rss+xml',
                headers={'Content-Type': 'application/rss+xml; charset=utf-8'}
            )
        else:
            return f"Error: Status code {response.status_code}", 500

    except requests.RequestException as e:
        return f"Error fetching RSS: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
