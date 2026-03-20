from collections import defaultdict
from math import sqrt

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
    
    return candidates[:200]