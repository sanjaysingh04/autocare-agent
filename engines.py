# 🦴 ORTHOPEDIC ENGINE
def ortho_score(pain, swelling, fever, mobility, infection):
    score = 100

    if pain == "Y": score -= 20
    if swelling == "Y": score -= 10
    if fever == "Y": score -= 15
    if mobility == "N": score -= 30   # VERY critical
    if infection == "Y": score -= 25

    return score


# ❤️ CARDIAC ENGINE
def cardiac_score(chest_pain, breathing, dizziness, leg_swelling, missed_meds):
    score = 100

    if chest_pain == "Y": score -= 35   # VERY dangerous
    if breathing == "Y": score -= 30
    if dizziness == "Y": score -= 15
    if leg_swelling == "Y": score -= 10
    if missed_meds == "Y": score -= 20

    return score


# 🧠 Risk classifier (common)
def classify_risk(score):
    if score >= 70:
        return "LOW"
    elif score >= 40:
        return "MODERATE"
    else:
        return "HIGH"