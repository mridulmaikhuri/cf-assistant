from fastapi import APIRouter, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
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
def get_submission_history(handle: str, days:int = 365):
    url = f"{BASE_CF_API}/user.status?handle={handle}"
    response = fetch_cf_api(url)
    
    submissions = response.get("result", [])
    daily_submission = defaultdict(int)
    one_year_ago = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(one_year_ago.timestamp())
    
    for submission in submissions:
        timestamp = submission["creationTimeSeconds"]
        if (timestamp < cutoff_timestamp):
            break
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        daily_submission[date] += 1
    
    dates = sorted(daily_submission.keys())
    counts = [daily_submission[date] for date in dates]
    if not counts:
        return {
            "heatmap": [],
            "stats": {
                "max_submission": 0,
                "avg_submission": 0,
                "max_streak": 0,
                "current_streak": 0
            }
        }
    
    max_submission = max(counts)
    avg_submission = round(sum(counts) / days, 2)
    
    max_streak = 0
    cur_streak = 0
    prev_date = None
    for date in dates:
        cur_date = datetime.strptime(date, "%Y-%m-%d")
        if prev_date and cur_date - prev_date == timedelta(days=1):
            cur_streak += 1
        else:
            cur_streak = 1
        max_streak = max(max_streak, cur_streak)
        prev_date = cur_date
    last_date = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    today = datetime.now().date()
    if (today - last_date).days > 1:
        cur_streak = 0
    
    return {
        "heatmap": [
            {"date": date, "count": count}
            for date, count in daily_submission.items()
        ],
        "stats": {
            "max_submission": max_submission,
            "avg_submission": avg_submission,
            "max_streak": max_streak,
            "current_streak": cur_streak
        }
    }
    
@router.get('/rating/{handle}')
def get_rating_history(handle: str):
    url = f"{BASE_CF_API}/user.rating?handle={handle}"
    response = fetch_cf_api(url)
    
    result = response.get("result", [])
    if not result:
        return {
            "rating_history": [],
            "max_delta": 0,
            "avg_delta": 0,
            "total_contest": 0
        }
    
    rating_history = []
    max_delta = -1e9
    avg_delta = 0
    total_contest = len(result)
    for res in result:
        delta = res["newRating"] - res["oldRating"]
        max_delta = max(max_delta, delta)
        avg_delta += delta
        rating_history.append({
            "contestId": res["contestId"],
            "contestName": res["contestName"],
            "rank": res["rank"],
            "oldRating": res["oldRating"],
            "newRating": res["newRating"]
        })
    avg_delta = round(avg_delta/len(result), 2)
    
    return {
        "rating_history": rating_history,
        "max_delta": max_delta,
        "avg_delta": avg_delta,
        "total_contest": total_contest
    }