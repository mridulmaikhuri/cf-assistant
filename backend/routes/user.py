import requests
from fastapi import APIRouter, HTTPException
from collections import defaultdict
from cachetools import TTLCache
from math import sqrt

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

def get_user_rating(handle: str):
    url = f"{BASE_CF_API}/user.info?handles={handle}"
    response = fetch_cf_api(url)
    return response["result"][0].get("rating", 800)

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
    
    total_attempts = sum(attempted_tags.values())
    
    # For new users assign equal weakness to all tags
    if total_attempts == 0:
        return {tag: 0.5 for tag in all_tags}
    
    c = 10
    k = c / sqrt(total_attempts + 1)
    p = 0.5
    
    for tag in all_tags:
        attempted = attempted_tags[tag]
        solved = solved_tags[tag]
        
        success_rate = (solved + k * p) / (attempted + k)
        weakness = 1 - success_rate
        
        tag_weakness[tag] = weakness
    
    return tag_weakness

def get_candidates(rating, all_problems, solved_problems, tag_weakness, attempted_problems, ):
    min_rating = rating - 200
    max_rating = rating + 200
    min_rating = (min_rating // 100) * 100
    max_rating = ((max_rating + 99) // 100) * 100
    
    candidates = []
    for r in range(min_rating, max_rating + 1, 100):
        for prob in all_problems.get(r, []):
            prob_rating = prob.get("rating")
            
            if (prob_rating is None):
                continue
            
            if not (min_rating <= prob_rating <= max_rating):
                continue
            
            contest_id = prob.get("contestId")
            index = prob.get("index")
            name = prob.get("name")
            tags = prob.get("tags", [])
            
            if (contest_id is None or index is None or not tags):
                continue
            
            problem_key = (contest_id, index)
            
            if problem_key in solved_problems:
                continue
            
            weaknesses = [tag_weakness.get(tag, 1) for tag in tags]
            
            rating_range = max_rating - min_rating
            
            avg_weakness = sum(weaknesses) / len(weaknesses)
            rms_weakness = sqrt(sum(w*w for w in weaknesses) / len(weaknesses))
            unseen_bonus = 1 if problem_key not in attempted_problems else 0
            rating_bonus = (1 - abs(prob_rating - rating) / rating_range)
            tag_score = min(len(tags), 3) / 3
            
            # parameters which are used for score generation are as follows
            # 1. average weakness: to get average weakness of all tags in the problems and also to make sure that we get balanced training
            # 2. rms weakness: to make sure that very weak tags get slight nudge in the scoring
            # 3. len(tags): to make sure that more the no of tags the more weightage it gets basically to make sure that more diverse problems get more weightage
            # 4. unseen_bonus: to give bonus to unseen problems it ensures that never seen problems are recommended first
            # 5. rating_bonus: to make sure that problems closer to the rating ranger are preferred first
            score = 0.8 * avg_weakness + 0.2 * rms_weakness + 0.1 * tag_score + 0.1 * unseen_bonus + 0.1 * rating_bonus
            
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
    
    # Ensures diverse tags in recommendations
    # This makes sure that only problems of one tag don't get recommended
    tag_counter = defaultdict(int)

    for candidate in candidates:
        penalty = 0
        
        for tag in candidate["tags"]:
            penalty += (tag_counter[tag] ** 1.3) * 0.01 
        
        candidate["score"] -= penalty
        
        for tag in candidate["tags"]:
            tag_counter[tag] += 1
    
    candidates.sort(key=lambda x : (-x["score"], abs(x["rating"] - rating)))
    
    return candidates
    
recommendation_cache = TTLCache(maxsize=200, ttl=86400)
@router.get('/problems/{handle}')
def get_recommended_problems(handle: str):
    if handle in recommendation_cache:
        return recommendation_cache[handle]
    
    # Fetch necessary Info
    rating = get_user_rating(handle)
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