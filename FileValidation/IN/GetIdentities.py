import requests

def getIdentities(token,url):

  print("URL:",url)

  payload = {}
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+token,
  }

  response = requests.request("GET", url, headers=headers, data=payload)
#   print("Identities ............................")
#   print(response.text)
  return(response)

def get_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': '99b81153f12a4daf99ae4caefffc4dec',
        'client_secret': 'aac59160fa745c08f6c8d32da8f478129660eac01cb18262639d10c8c0f770b1'
    }

    response = requests.post("https://partner101.api.identitynow.com/oauth/token", data=data)
    
    if response.status_code == 200:
        token = response.json()['access_token']
        return token
    else:
        print("Failed to retrieve token. Status code:", response.status_code)
        return None


# token = get_token()
# print("Token : "+token)

# getIdentities(token)

def triggerAggregation(token):

  url = 'https://partner101.api.identitynow.com/cc/api/source/loadAccounts/221636'

  print("URL:",url)

  payload = {}
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+token,
  }

  response = requests.request("POST", url, headers=headers, data=payload)
#   print("Identities ............................")
#   print(response.text)
  return(response)

