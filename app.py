from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route('/health')
def health_check():
    return "OK", 200

@app.route('/kneset')
def get_rss():
    url = 'https://main.knesset.gov.il/News/PressReleases/_layouts/15/listfeedKns.aspx'
    params = {
        'List': '0564d270-3847-4edf-a07e-9b8bd3c9f72d',
        'View': '6d8affa9-2f1c-48cb-a976-651985123519'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Cookie': 'rbzid=ZDSJhUp0+g8XLD6pDLz7cyioBy+ng7ckdrRdk/Sec3eMyPKQIKT+rYZiBTr4FOb/vtgxaeW6MI4MMELPvve108o+ctfVlykplOItMGY9PI/UXN6oqGnncOnWNgDqUd4F3BBK1Izj9CuP7CTIJJdpU14yGysh77riI8yUec4bPdsDl6x0WOHZ0Rpr/hf0OoFt; GCLB=CLjogLPPtqLtzAEQAw'
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
