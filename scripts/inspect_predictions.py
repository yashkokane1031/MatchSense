"""Inspect real model predictions on key fixtures."""

from ml.models.dixon_coles import DixonColesModel


def main():
    model = DixonColesModel.load("data/models/dixon_coles_latest.pkl")

    matchups = [
        ("Manchester City", "Southampton"),
        ("Arsenal", "Luton"),
        ("Manchester City", "Luton"),
        ("Arsenal", "Tottenham"),
        ("Liverpool", "Everton"),
        ("Sheffield Utd", "Manchester City"),
    ]

    print("=== Real Match Predictions ===")
    for home, away in matchups:
        probs = model.predict_proba(home, away)
        h_score, a_score = model.predict_most_likely_score(home, away)
        ph = probs["prob_home"]
        pd_ = probs["prob_draw"]
        pa = probs["prob_away"]
        print(f"{home:18} vs {away:15} | H: {ph:5.1%} | D: {pd_:5.1%} | A: {pa:5.1%} | Score: {h_score}-{a_score}")

    print("\n=== Bottom 5 Defense Strengths (Highest Goals Conceded) ===")
    strengths = model.get_team_strengths()
    sorted_by_defense = sorted(strengths.items(), key=lambda x: x[1]["defense"], reverse=True)
    for team, s in sorted_by_defense[:5]:
        print(f"  {team:18}: defense={s['defense']:.3f}, attack={s['attack']:.3f}")

    print("\n=== Top 5 Defense Strengths (Lowest Goals Conceded) ===")
    sorted_by_defense_best = sorted(strengths.items(), key=lambda x: x[1]["defense"])
    for team, s in sorted_by_defense_best[:5]:
        print(f"  {team:18}: defense={s['defense']:.3f}, attack={s['attack']:.3f}")


if __name__ == "__main__":
    main()
