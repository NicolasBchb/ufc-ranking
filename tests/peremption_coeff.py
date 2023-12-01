# %%
import plotly.express as px

import pandas as pd


def peremption_coeff(weeks):
    if weeks < 26:
        return 1
    elif weeks < 52:
        return 0.95
    elif weeks < 52*1.25:
        return 0.9
    elif weeks < 52*1.5:
        return 0.85
    elif weeks > 52*4:
        return 0
    else:
        return 0.8 - ((weeks - 52*1.5) * 0.006)

def fight_peremption_coeff(event_date, today):
    # Si le combat a moins de 6 mois, alors coefficient = 1
    if (today - event_date).days // 7 < 52 / 2:
        return 1
    
    # Si le combat a moins de 1 an, alors coefficient = 0.95
    elif (today - event_date).days // 7 < 52:
        return 0.95
    
    # Si le combat a moins de 15 mois, alors coefficient = 0.9
    elif (today - event_date).days // 7 < 52 * 1.25:
        return 0.9
    
    # Si le combat a moins de 18 mois, alors coefficient = 0.85
    elif (today - event_date).days // 7 < 52 * 1.5:
        return 0.85

    # Si le combat a plus de 3 ans, alors coefficient = 0
    elif (today - event_date).days // 7 > 52 * 3:
        return 0

    # Si le combat a plus de 6 mois, alors le coefficient diminue de 0.00035 par jour
    else:
        # On a 130 semaines où on passe de 0.85 à 0, donc 0.8 / 130 ~= 0.006
        return 0.8 - ((((today - event_date).days // 7) - 52*1.5) * 0.01)

# %%
# list of dates between 2018 and today, every day
dates = [
    pd.to_datetime("2018-01-01") + pd.Timedelta(days=i) 
    for i in range(0, (pd.to_datetime("today") - pd.to_datetime("2018-01-01")).days)
]

coeffs = [fight_peremption_coeff(date, pd.to_datetime("today")) for date in dates]


# %%
fig = px.line(x=dates, y=coeffs, template="plotly_dark")
# update y to percentage
fig.update_yaxes(tickformat=".0%")
# add line at 6 months, 1 year, 2 years, 3 years and 4 years
fig.add_vline(
    x=pd.to_datetime("today") - pd.Timedelta(days=52/2*7),
    line_width=3, line_dash="dash", line_color="red")
fig.add_vline(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*7),
    line_width=3, line_dash="dash", line_color="red")
fig.add_vline(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*1.5*7),
    line_width=3, line_dash="dash", line_color="red")
fig.add_vline(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*2*7),
    line_width=3, line_dash="dash", line_color="red")
fig.add_vline(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*3*7),
    line_width=3, line_dash="dash", line_color="red")
fig.add_vline(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*4*7),
    line_width=3, line_dash="dash", line_color="red")

# add annotations
fig.add_annotation(
    x=pd.to_datetime("today") - pd.Timedelta(days=52/2*7),
    y=1.1,
    text="6 months",
    showarrow=False
)
fig.add_annotation(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*7),
    y=1.1,
    text="1 year",
    showarrow=False
)
fig.add_annotation(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*1.5*7),
    y=1.1,
    text="18 months",
    showarrow=False
)
fig.add_annotation(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*2*7),
    y=1.1,
    text="2 years",
    showarrow=False
)
fig.add_annotation(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*3*7),
    y=1.1,
    text="3 years",
    showarrow=False
)
fig.add_annotation(
    x=pd.to_datetime("today") - pd.Timedelta(days=52*4*7),
    y=1.1,
    text="4 years",
    showarrow=False
)

fig.update_layout(
    title="Peremption coefficient",
    xaxis_title="Weeks",
    yaxis_title="Coefficient",
)

fig.show()

# %%