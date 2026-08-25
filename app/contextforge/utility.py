import json
def clamp01(v): return max(0.0,min(1.0,float(v)))
def context_utility(*,relevance,confidence,spatial_match,freshness,decision_impact):
    vals=[clamp01(relevance),clamp01(confidence),clamp01(spatial_match),clamp01(freshness),clamp01(decision_impact)]
    score=1.0
    for v in vals: score*=max(v,0.05)
    return score
def estimate_tokens(obj):
    text=json.dumps(obj,separators=(",",":"),ensure_ascii=False,default=str)
    return max(1,int(len(text)/3.5))
def trim_ranked(items,token_budget):
    ranked=sorted(items,key=lambda x:x.get("utility_score",0),reverse=True)
    kept=[]; used=0
    for item in ranked:
        cost=estimate_tokens(item)
        if used+cost<=token_budget:
            kept.append(item); used+=cost
    return kept,used
