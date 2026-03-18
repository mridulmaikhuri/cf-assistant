import requests
from fastapi import APIRouter, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
from cachetools import TTLCache

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
        problems = res["result"]["problems"]
        tags = set(tag for prob in problems for tag in prob.get("tags", []))
        
        problemset_cache["data"] = {
            "problems": problems,
            "tags": tags
        }
    
    return problemset_cache["data"]

def parse_submission(submissions):
    attempted_tags = defaultdict(int)
    solved_tags = defaultdict(int)
    solved_problems = set()
    attempted_problems = set()
    
    for sub in submissions:
        prob = sub.get("problem", {})
        contest_id = prob.get("contestId")
        index = prob.get("index")
        
        if contest_id is None or index is None:
            continue
        
        problem_key = (contest_id, index)
        attempted_problems.add(problem_key)
        
        tags = prob.get("tags", [])
        for tag in tags:
            attempted_tags[tag] += 1
        
        if sub.get("verdict") == "OK":
            solved_problems.add(problem_key)
            for tag in tags:
                solved_tags[tag] += 1
                
    return {
        "attempted_tags": attempted_tags,
        "solved_tags": solved_tags,
        "solved_problems": solved_problems,
        "attempted_problems": attempted_problems
    }

def get_tag_weakness(all_tags, attempted_tags, solved_tags):
    tag_weakness = {}
    
    for tag in all_tags:
        attempted = attempted_tags[tag]
        solved = solved_tags[tag]
        success_rate = solved / attempted if attempted > 0 else 0
        weakness = 1 - success_rate
        tag_weakness[tag] = weakness
    
    return tag_weakness

def get_candidates(rating, all_problems, solved_problems, tag_weakness, attempted_problems, ):
    min_rating = rating - 200
    max_rating = rating + 200
    min_rating = (min_rating // 100) * 100
    max_rating = ((max_rating + 99) // 100) * 100
    
    candidates = []
    for prob in all_problems:
        prob_rating = prob.get("rating")
        
        if (prob_rating is None):
            continue
        
        if not (min_rating <= prob_rating <= max_rating):
            continue
        
        contest_id = prob.get("contestId")
        index = prob.get("index")
        name = prob.get("name")
        tags = prob.get("tags", [])
        
        if (contest_id is None or index is None):
            continue
        
        problem_key = (contest_id, index)
        
        if problem_key in solved_problems:
            continue
        
        if not tags:
            continue
        
        avg_weakness = sum(tag_weakness.get(tag, 1) for tag in tags) / len(tags)
        unseen_bonus = 0.15 if problem_key not in attempted_problems else 0
        
        rating_bonus = 1 - abs(prob_rating - rating) / 200
        rating_bonus *= 0.1
        
        score = avg_weakness + unseen_bonus + rating_bonus
        
        candidates.append({
            "contestId": contest_id,
            "index": index,
            "name": name,
            "rating": prob_rating,
            "tags": tags,
            "score": round(score, 4),
            "link": f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        })
    
    candidates.sort(key=lambda x : (-x["score"], abs(x["rating"] - rating)))
    
    return candidates
    
recommendation_cache = TTLCache(maxsize=200, ttl=86400)
@router.get('/problems/{handle}')
def get_recommended_problems(handle: str):
    if handle in recommendation_cache:
        return recommendation_cache[handle]
    
    # Fetch necessary Info
    rating = get_user(handle).get("rating", 800)
    submissions = fetch_user_submissions(handle) 
    data = fetch_problemset_and_tags()
    all_problems = data["problems"]
    all_tags = data["tags"]
    
    # Logic
    
    # 1) get list of attempted tags, solved tags, solved problems and attempted problems from submissions list
    submission_data = parse_submission(submissions)
    attempted_tags = submission_data["attempted_tags"]
    solved_tags = submission_data["solved_tags"]
    solved_problems = submission_data["solved_problems"]
    attempted_problems = submission_data["attempted_problems"]
    
    # 2) get weakness score associated with each tag        
    tag_weakness = get_tag_weakness(all_tags, attempted_tags, solved_tags)
    
    # 3) Get list of unsolved problems sorted according to relevance
    candidates = get_candidates(rating, all_problems, solved_problems, tag_weakness, attempted_problems)
    
    recommendation_cache[handle] = {
        "recommendedProblems": candidates
    }
    
    return recommendation_cache[handle]