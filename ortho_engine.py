def ortho_recovery_score(
    severe_pain,
    swelling,
    fever,
    normal_mobility,
    infection_signs
):
    score = 100

    # Moderate risk factors
    if severe_pain.lower() == "y":
        score -= 20

    if swelling.lower() == "y":
        score -= 15

    # Critical risk factors
    if fever.lower() == "y":
        score -= 30

    if infection_signs.lower() == "y":
        score -= 30

    # Mobility check (inverse logic)
    if normal_mobility.lower() == "n":
        score -= 25

    return max(score, 0)

def ortho_risk_level(score):
    if score >= 70:
        return "STABLE 🟢"
    elif score >= 40:
        return "ATTENTION NEEDED 🟡"
    else:
        return "HIGH RISK 🔴"
    
def ortho_action(risk):
    if "STABLE" in risk:
        return "Continue routine monitoring"

    if "ATTENTION" in risk:
        return "Increase check-ins and monitor closely"

    return "Alert doctor immediately"
def ortho_next_check(risk):
    if "STABLE" in risk:
        return "Next check in 24 hours"

    if "ATTENTION" in risk:
        return "Next check in 6–8 hours"

    return "Immediate follow-up required"