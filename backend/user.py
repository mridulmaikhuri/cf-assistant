from fastapi import APIRouter
from cachetools import TTLCache

from recommender import get_candidates, get_tag_weakness, parse_submission
from api import get_user, fetch_problemset_and_tags, fetch_user_submissions

router = APIRouter()
    
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