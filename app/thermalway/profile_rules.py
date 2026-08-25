def edge_allowed_for_profile(edge,profile):
    return not (profile=="mobility_limited" and (edge.highway or "").lower()=="steps")
def profile_edge_penalty(edge,profile):
    if (edge.highway or "").lower()!="steps": return 1.0
    if profile=="older_adult": return 1.35
    if profile=="child": return 1.10
    return 1.0
