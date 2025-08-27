import requests

API_URL = "https://searchaccountbyname-aya.vercel.app/search"
KEY = "aya"

def search_player(nickname, region="vn"):
    url = f"{API_URL}?nickname={nickname}&key={KEY}&region={region}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # chỉ lấy players, bỏ DEV & channel
        return data.get("players", [])
    else:
        return None


players = search_player("conbobot")

if players:
    for p in players:
        print(f"{p['nickname']} (Level {p['level']}) - Last login: {p['lastLogin']}")
else:
    print("❌ Không tìm thấy tài khoản")
