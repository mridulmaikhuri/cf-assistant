import requests
from fastapi import HTTPException
from cachetools import TTLCache
from collections import defaultdict

BASE_CF_API = "https://codeforces.com/api"

def fetch_cf_api(url: str):
    try:
        res = requests.get(url, timeout=10)
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Failed to connect to CF API")
    
    try:
        data = res.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid response from CF API")
    
    if data.get("status") != "OK":
        raise HTTPException(status_code=404, detail=data.get("comment", "Codeforces API error"))
    return data


def get_user(handle: str):
    url = f"{BASE_CF_API}/user.info?handles={handle}"
    response = fetch_cf_api(url)
    return response["result"][0]

submission_cache = TTLCache(maxsize=200, ttl=3599) # cache user submission for 1 hr
def fetch_user_submissions(handle: str):
    if handle not in submission_cache:
        url = f'{BASE_CF_API}/user.status?handle={handle}'
        res = fetch_cf_api(url)
        submission_cache[handle] = res["result"]
    return submission_cache[handle]

problemset_cache = TTLCache(maxsize=1, ttl=2*86399) # cache problemset data for 2 days
def fetch_problemset_and_tags():
    if "data" not in problemset_cache:
        url = f'{BASE_CF_API}/problemset.problems'
        res = fetch_cf_api(url)
        data = res["result"]["problems"]
        
        tags = set(tag for prob in data for tag in prob.get("tags", []))
        problems = defaultdict(list)
        
        for prob in data:
            if "rating" in prob:
                problems[prob["rating"]].append(prob)
        
        problemset_cache["data"] = {
            "problems": problems,
            "tags": tags
        }
    
    return problemset_cache["data"]