def lookup_url(url:str)->str:
    import requests
    response = requests.get(url)
    return response.text