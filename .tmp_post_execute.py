import requests, json
url = 'http://127.0.0.1:8000/api/command'
payload = {"prompt":"Skaffa 100 SEK i aktier, jurisdiktion SE","auto_run":True}
try:
    r = requests.post(url, json=payload, timeout=30)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(r.text)
except Exception as e:
    print('EXCEPTION', repr(e))
