# %%
import plotly.express as px


def peremption_coeff(weeks):
    if weeks < 26:
        return 1
    elif weeks > 4*52:
        return 0
    else:
        return 1 - ((weeks - 26) * 0.0055)


# %%
weeks = list(range(0, 5*52))

coeffs = [peremption_coeff(week) for week in weeks]


# %%
fig = px.line(x=weeks, y=coeffs, template="plotly_dark")
# update y to percentage
fig.update_yaxes(tickformat=".0%")
# add line at 6 months, 1 year, 2 years, 3 years and 4 years
fig.add_vline(x=26, line_width=3, line_dash="dash", line_color="red")
fig.add_vline(x=52, line_width=3, line_dash="dash", line_color="red")
fig.add_vline(x=52*1.5, line_width=3, line_dash="dash", line_color="red")
fig.add_vline(x=52*2, line_width=3, line_dash="dash", line_color="red")
fig.add_vline(x=52*3, line_width=3, line_dash="dash", line_color="red")
fig.add_vline(x=52*4, line_width=3, line_dash="dash", line_color="red")

# add annotations
fig.add_annotation(
    x=26,
    y=1.1,
    text="6 months",
    showarrow=False
)
fig.add_annotation(
    x=52,
    y=1.1,
    text="1 year",
    showarrow=False
)
fig.add_annotation(
    x=52*1.5,
    y=1.1,
    text="18 months",
    showarrow=False
)
fig.add_annotation(
    x=52*2,
    y=1.1,
    text="2 years",
    showarrow=False
)
fig.add_annotation(
    x=52*3,
    y=1.1,
    text="3 years",
    showarrow=False
)
fig.add_annotation(
    x=52*4,
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