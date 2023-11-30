# %%
import pandas as pd
from tqdm import tqdm
import dtale

from numpy import nan


# %%
df_fights = pd.read_csv("fights.csv", sep=";")

df_fights = df_fights[df_fights["result"] == "win"]

df_fights["eventDate"] = pd.to_datetime(df_fights["eventDate"])

df_fights.sort_values(by=["eventDate"], inplace=True)


# %%
def fight_peremption_coeff(event_date, today):
    # Si le combat a moins de 6 mois, alors coefficient = 1
    if (today - event_date).days // 7 < 52 / 2:
        return 1

    # Si le combat a plus de 4 ans, alors coefficient = 0
    elif (today - event_date).days // 7 > 52 * 4:
        return 0

    # Si le combat a plus de 6 mois, alors le coefficient diminue de 0.00035 par jour
    else:
        # On a 182 semaines où on passe de 1 à 0, donc 1/182 = 0.0055
        return 1 - ((((today - event_date).days // 7) - 26) * 0.0055)


win_type_scores = {
    "KO/TKO": 5,
    "submission": 5,
    "unanimousDecision": 3,
    "majorityDecision": 2,
    "splitDecision": 1,
    "disqualification": 1,
}

df_fights["win_type_scores"] = df_fights["method"].map(win_type_scores)

# A title shot is worth 3 times more points
df_fights["belt_score"] = (df_fights["belt"] * 2) + 1

# A performance of the night is worth 1.5 times more points
df_fights["performance_of_the_night_score"] = (
    df_fights["performanceOfTheNight"] * 0.5
) + 1

df_fights["base_score"] = (
    df_fights["win_type_scores"]
    * df_fights["belt_score"]
    * df_fights["performance_of_the_night_score"]
)

# %%
df_fights["opponent_bonus"] = nan

df_fights["score"] = nan

for i, fight in tqdm(
    df_fights.iterrows(), desc="Iterate over fights", total=len(df_fights)
):
    previous_fights = df_fights[df_fights["eventDate"] < fight["eventDate"]].copy()

    if fight["loserHref"] not in previous_fights["winnerHref"].values:
        loser_score = 0
    else:
        loser_wins = previous_fights[
            previous_fights["winnerHref"] == fight["loserHref"]
        ].copy()
        loser_wins["peremption_coeff"] = loser_wins["eventDate"].map(
            lambda event_date: fight_peremption_coeff(event_date, fight["eventDate"])
        )
        loser_wins["score_perempted"] = (
            loser_wins["score"] * loser_wins["peremption_coeff"]
        )
        loser_score = loser_wins["score_perempted"].sum()

    opponent_bonus = loser_score / 2

    df_fights.loc[i, "opponent_bonus"] = opponent_bonus

    df_fights.loc[i, "score"] = fight["base_score"] + opponent_bonus


# dtale.show(df_fights[['eventDate', 'winnerFirstName', 'winnerLastName', 'loserFirstName', 'loserLastName', 'base_score', 'opponent_bonus', 'score']])

# %%
df_score = df_fights.copy()

df_score["peremption_coeff"] = df_score["eventDate"].map(
    lambda event_date: fight_peremption_coeff(event_date, pd.Timestamp.today())
)

df_score["score_perempted"] = df_score["score"] * df_score["peremption_coeff"]

df_ranking = (
    df_score.groupby(["winnerHref", "winnerFirstName", "winnerLastName"])
    .sum(numeric_only=True)
    .sort_values(by="score_perempted", ascending=False)
    .reset_index()
)

df_ranking["rank_score"] = df_ranking.index + 1

df_ranking.rename(
    columns={
        "winnerHref": "href",
        "winnerFirstName": "firstName",
        "winnerLastName": "lastName",
        "score_perempted": "rank_score",
    },
    inplace=True,
)

df_ranking["rank_score"] = df_ranking["rank_score"].round(2)

df_ranking[["href", "firstName", "lastName", "rank_score"]].to_csv(
    "ranking/rank_P4P.csv", sep=";", index=False
)

# dtale.show(df_ranking[['winnerHref', 'winnerFirstName', 'winnerLastName', 'score_perempted']])
# %%
for weight_class in df_score["weightClass"].unique():
    df_weight_class = df_score[df_score["weightClass"] == weight_class].copy()

    df_weight_class_ranking = (
        df_weight_class.groupby(["winnerHref", "winnerFirstName", "winnerLastName"])
        .sum(numeric_only=True)
        .sort_values(by="score_perempted", ascending=False)
        .reset_index()
    )

    df_weight_class_ranking.rename(
        columns={
            "winnerHref": "href",
            "winnerFirstName": "firstName",
            "winnerLastName": "lastName",
            "score_perempted": "rank_score_" + weight_class,
        },
        inplace=True,
    )

    df_weight_class_ranking["rank_score_" + weight_class] = df_weight_class_ranking[
        "rank_score_" + weight_class
    ].round(2)

    df_weight_class_ranking["rank_" + weight_class] = df_weight_class_ranking.index + 1

    df_weight_class_ranking[
        [
            "href",
            "firstName",
            "lastName",
            "rank_score_" + weight_class,
            "rank_" + weight_class,
        ]
    ].to_csv("ranking/rank_" + weight_class + ".csv", sep=";", index=False)
# %%
