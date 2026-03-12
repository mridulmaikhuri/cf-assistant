from fastapi import APIRouter, HTTPException
from collections import defaultdict
from datetime import datetime
import requests

BASE_CF_API = "https://codeforces.com/api"

router = APIRouter()

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

@router.get('/info/{handle}')
def get_user(handle: str):
    url = f"{BASE_CF_API}/user.info?handles={handle}"
    response = fetch_cf_api(url)
    user = response["result"][0]
    return {
        "handle": user["handle"],
        "profilePhoto": user["titlePhoto"],
        "rating": user["rating"],
        "rank": user["rank"],
        "maxRating": user["maxRating"],
        "maxRank": user["maxRank"],
    }

@router.get('/submission/{handle}')
def get_submission_history(handle: str):
    url = f"{BASE_CF_API}/user.status?handle={handle}"
    response = fetch_cf_api(url)
    submissions = response.get("result", [])
    daily_submission = defaultdict(int)
    for submission in submissions:
        timestamp = submission["creationTimeSeconds"]
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        daily_submission[date] += 1
    return [
        {"date": date, "count": count}
        for date, count in daily_submission.items()
    ]