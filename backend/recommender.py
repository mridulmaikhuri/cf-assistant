from collections import defaultdict
from math import sqrt, exp, log
from random import betavariate

def parse_submission(submissions, user_rating):
    attempted_tags = defaultdict(int)
    solved_tags = defaultdict(int)
    solved_problems = set()
    attempted_problems = set()
    
    for sub in submissions:
        prob = sub.get("problem", {})
        contest_id = prob.get("contestId")
        index = prob.get("index")
        prob_rating = prob.get("rating", 800)
        
        if contest_id is None or index is None:
            continue
        
        problem_key = (contest_id, index)
        attempted_problems.add(problem_key)
        
        wt = exp((prob_rating - user_rating) / (user_rating - 300))
        
        tags = prob.get("tags", [])
        for tag in tags:
            attempted_tags[tag] += wt
        
        if sub.get("verdict") == "OK":
            solved_problems.add(problem_key)
            for tag in tags:
                solved_tags[tag] += wt
                
    return {
        "attempted_tags": attempted_tags,
        "solved_tags": solved_tags,
        "solved_problems": solved_problems,
        "attempted_problems": attempted_problems
    }

# still need to look into this function
def get_tag_weakness(all_tags, attempted_tags, solved_tags):
    tag_weakness = {}
    
    total_attempts = sum(attempted_tags.values())
    
    # For new users assign equal weakness to all tags
    if total_attempts == 0:
        return {tag: 0.5 for tag in all_tags} # TODO: change it to 1 / global_success_rate[tag]
    
    k = 20 / sqrt(total_attempts + 1)
    c = 0.1
    p = 0.5
    
    # Using Upper Confidence Bound (UCB) sampling for now
    for tag in all_tags:
        attempted = attempted_tags[tag]
        solved = solved_tags[tag]
        
        # Bayesian smoothing
        success = (solved + k * p) / (attempted + k)
        # Exploration like UCB for adding uncertainity to system
        exploration = c * sqrt(log(total_attempts + 1) / (attempted + 1))
        
        weakness = (1 - success) + exploration
        
        tag_weakness[tag] = weakness
    
    # Normalize
    max_w = max(tag_weakness.values())
    for tag in tag_weakness:
        tag_weakness[tag] /= max_w
    
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
            
            diff = prob_rating - rating
            
            # parameters which are used for score generation are as follows
            # 1. average weakness: to get average weakness of all tags in the problems and also to make sure that we get balanced training
            # 2. max weakness: to catch outliers so that tags which are extremely weak get some nudge
            # 3. len(tags): to make sure that more the no of tags the more weightage it gets basically to make sure that more diverse problems get more weightage
            # 4. unseen_bonus: to give bonus to unseen problems it ensures that never seen problems are recommended first
            # 5. rating_bonus: to make sure that problems closer to the rating ranger are preferred first
            
            avg_weakness = sum(weaknesses) / len(weaknesses)
            max_weakness = max(weaknesses)
            unseen_bonus = 1 if problem_key not in attempted_problems else 0 # TODO: change it to 1 - exp(-days_since_attempt)
            rating_bonus = exp(-(diff ** 2) / (2 * (300 ** 2)))
            tag_score = log(sqrt(len(tags)) + 1)
            
            if (diff < 0): rating_bonus *= 0.8
            
            score = 0.5 * avg_weakness + 0.2 * max_weakness + 0.1 * tag_score + 0.05 * unseen_bonus + 0.15 * rating_bonus
            
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
    candidates = candidates[:500]
    
    selected = []
    
    for i in range(min(200, len(candidates))):
        best_candidate = None
        best_score = -1e9
        
        for candidate in candidates:
            if "picked" in candidate:
                continue
            
            penalty = 0
            
            for sel in selected:
                common = len(set(candidate["tags"]) & set(sel["tags"]))
                penalty += log(1 + common)
                
            score = candidate["score"] - penalty * 0.02
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        best_candidate["score"] = best_score
        best_candidate["picked"] = True
        selected.append(best_candidate)
        
    return selected