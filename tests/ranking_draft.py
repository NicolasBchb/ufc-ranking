# %%
import pandas as pd
from tqdm import tqdm
import dtale

"""
Critères attendus :
- Grosso modo
    1. Clair, simple, lisible, open source
    2. Que des critères sportifs
    3. Ne pas bloquer les catégories de poids
    4. Encourager l'activité
    5. Pas trop complexe

- Plus précisément
    - Classement uniquement lié aux performances à l'UFC
    - Pondérer les points des victoires en fonction de l'adversaire, mais pas trop non plus pour que les combattants acceptent les combats contre des adversaires moins bien classés
    - Dévaloriser les split decisions
    - Les title shots doivent rapporter plus de points



Critères implémentés :
- Type de victoire
    - Victoire par KO/TKO : 5 points
    - Victoire par soumission : 5 points
    - Victoire par décision unanime : 3 points
    - Victoire par décision majoritaire : 2 points
    - Victoire par décision partagée : 1 point
    - Victoire par disqualification : 1 point

- Age du combat
    - Si le combat a moins de 6 mois, alors coefficient = 1
    - Si le combat a plus de 4 ans, alors coefficient = 0
    - Si le combat a plus de 6 mois, alors le coefficient diminue de 0.55% par semaine, jusqu'à atteindre 0% à 4 ans

- Contexte du combat
    - Si c'est un title shot, alors coefficient = 3
    - Si c'est une performance of the night, alors coefficient = 1.5

- Nombre/écart de points de l'adversaire au moment du combat

- Un défaite = retrait de points ?
"""




# %%
df_fights = pd.read_csv('fights.csv', sep=";")

df_fights["eventDate"] = pd.to_datetime(df_fights["eventDate"])

df_fights['wins'] = 1

# dtale.show(df_fights)


# %%
df_win = df_fights[df_fights['result'] == 'win']

df_win = df_win[df_win["eventDate"] > "2019-11-29"]


# %%
coeffs = {
    'KO/TKO' : 5,
    'submission': 5,

    'unanimousDecision': 3,
    'majorityDecision': 2,
    'splitDecision': 1,

    'disqualification': 1
}

df_win['win_type_coeff'] = df_win['method'].map(coeffs)

# dtale.show()


# %%
def fight_peremption_coeff(row):
    today = pd.Timestamp.today()

    # Si le combat a moins de 6 mois, alors coefficient = 1
    if (today - row['eventDate']).days // 7 < 52/2:
        return 1
    
    # Si le combat a plus de 4 ans, alors coefficient = 0
    elif (today - row['eventDate']).days // 7 > 52*4:
        return 0

    # Si le combat a plus de 6 mois, alors le coefficient diminue de 0.00035 par jour
    else:
        # On a 182 semaines où on passe de 1 à 0, donc 1/182 = 0.0055
        return 1 - ((((today - row['eventDate']).days // 7) - 26) * 0.0055)

df_win['peremption'] = df_win.apply(fight_peremption_coeff, axis=1)


# %%
# A title shot is worth 3 times more points
df_win["belt_score"] = (df_win["belt"] * 2) + 1

# A performance of the night is worth 1.5 times more points
df_win["performance_of_the_night_score"] = (df_win["performanceOfTheNight"] *0.5) + 1

# %%
# On calcule le score de chaque combat
df_win["score"] = (
    df_win["win_type_coeff"] 
    * df_win["peremption"] 
    * df_win["belt_score"] 
    * df_win["performance_of_the_night_score"]
    )

dtale.show(df_win)


# %%
df_scores = df_win.groupby(['winnerHref', 'winnerFirstName', 'winnerLastName']).sum(numeric_only=True).sort_values(by='score', ascending=False).reset_index()

dtale.show(df_scores)

# %%
(df_scores[['winnerFirstName', 'winnerLastName', 'score']]
    .rename(
        columns={
            'winnerFirstName': 'firstName',
            'winnerLastName': 'lastName',
        }
    )
    .head(100)
    .to_csv('ranking.csv', sep=";", index=False)
    )
# %%
