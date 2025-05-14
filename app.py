from flask import Flask, Response
import requests
from datetime import datetime

app = Flask(__name__)

ynet_cache = {
    'content': None,
    'last_fetch_hour': None
}

def should_fetch_ynet():
    current_hour = datetime.now().hour
    return ynet_cache['content'] is None or ynet_cache['last_fetch_hour'] != current_hour

@app.route('/health')
def health_check():
    return "OK", 200

@app.route('/ynet')
def get_ynet_rss():
    if should_fetch_ynet():
        url = 'https://www.ynet.co.il/Integration/StoryRss1854.xml'
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                ynet_cache['content'] = response.content
                ynet_cache['last_fetch_hour'] = datetime.now().hour
                return Response(
                    response.content,
                    mimetype='application/rss+xml',
                    headers={'Content-Type': 'application/rss+xml; charset=utf-8'}
                )
            else:
                return f"Error: Status code {response.status_code}", 500
                
        except requests.RequestException as e:
            return f"Error fetching RSS: {str(e)}", 500
    
    return Response(
        ynet_cache['content'],
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
        'Cookie': 'dLnSUL1UgeZ1Io1tcLAc2EnfIoQBVidSnh6/ax65Vmx9eCAQwrH8tl/JVTprte0auwaefcLDtjMfxRc67fcUw7OxprhjIvQQy+hmrutdV1NwYc60xAMTMJbct55yNbOAeTrsSbapRiAlkN/1TZTDZZO8hqmFkpkSrWeHEjNkMDGqctube9JswOGb8pJiOk2us6Zbw/92bih8UtE+69oC6TAOYP0_'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
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
