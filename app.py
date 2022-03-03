import flask
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

df_spores = pd.read_csv("./spores_data.csv", index_col=0)

server = flask.Flask(__name__)

app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    brand="Europe-wide energy system explorer",
    # brand_href="#",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(
            dbc.NavLink(
                [html.I(className="bi-box-arrow-right"), " See the paper"], href="#"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                [html.I(className="bi-download"), " Download the data"], href="#"
            )
        ),
    ],
)


def row_label(label, id):
    return dbc.Row(
        [
            dbc.Col(dbc.Label(label), md=3, class_name="slider-label"),
            dbc.Col(dcc.RangeSlider(0, 1, value=[0, 1], id=id), class_name="slider"),
        ],
        class_name="slider-group",
    )


controls = html.Div(
    [
        row_label(label="Transport electrification", id="slider-transport"),
        row_label(label="Curtailment", id="slider-curtailment"),
        row_label(label="Biofuel utilisation", id="slider-biofuel"),
        row_label(label="National import", id="slider-import"),
        row_label(label="Electricity gini", id="slider-elec-gini"),
        row_label(label="Fuel autarky", id="slider-fuel-gini"),
        row_label(label="EV as flexibility", id="slider-ev"),
    ]
)

results = (
    dbc.Tabs(
        [
            dbc.Tab(
                html.Img(id="overview-image"),
                label="Overview",
                tab_id="overview",
            ),
            dbc.Tab(
                html.Pre(id="spore-data"),
                label="Energy flows",
                tab_id="flows",
            ),
        ],
        id="tabs",
        active_tab="overview",
    ),
)

app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div([controls, dcc.Graph(id="spores-scatter")]),
                            md=4,
                        ),
                        dbc.Col(results, md=8, class_name="tabbedcontainer"),
                    ],
                    align="top",
                ),
            ],
            class_name="sporescontainer",
        ),
    ]
)


def spore_id_from_clickdata(clickData):
    try:
        return clickData["points"][0]["customdata"][0]
    except TypeError:
        return None


@app.callback(
    Output("overview-image", "src"),
    Input("spores-scatter", "clickData"),
)
def update_tabs(clickData):
    spore_id = spore_id_from_clickdata(clickData)
    if spore_id is None:
        return "assets/img/empty.jpg"
    else:
        return f"assets/img/{spore_id}.jpg"


@app.callback(
    Output("spore-data", "children"),
    Input("spores-scatter", "clickData"),
)
def update_flows(clickData):
    spore_id = spore_id_from_clickdata(clickData)
    if spore_id is None:
        return None
    else:
        return (f"SPORE id {spore_id}\n\n", df_spores.loc[spore_id, :].to_string())


@app.callback(
    Output("spores-scatter", "figure"),
    Input("slider-transport", "value"),
    Input("slider-curtailment", "value"),
    Input("slider-biofuel", "value"),
    Input("slider-import", "value"),
    Input("slider-elec-gini", "value"),
    Input("slider-fuel-gini", "value"),
    Input("slider-ev", "value"),
)
def update_figure(
    transport_range,
    curtailment_range,
    biofuel_range,
    import_range,
    elec_gini_rance,
    fuel_gini_range,
    ev_range,
):
    df_spores_filtered = df_spores[
        df_spores["Transport electrification"].between(
            transport_range[0], transport_range[1]
        )
        & df_spores["Curtailment"].between(curtailment_range[0], curtailment_range[1])
        & df_spores["Biofuel utilisation"].between(biofuel_range[0], biofuel_range[1])
        & df_spores["Average national import"].between(import_range[0], import_range[1])
        & df_spores["Electricity production Gini coefficient"].between(
            elec_gini_rance[0], elec_gini_rance[1]
        )
        & df_spores["Fuel autarky Gini coefficient"].between(
            fuel_gini_range[0], fuel_gini_range[1]
        )
        & df_spores["EV as flexibility"].between(ev_range[0], ev_range[1])
    ]

    fig = px.scatter(
        df_spores_filtered,
        x="Heat electrification",
        y="Storage discharge capacity",
        # size="",
        # color="",
        hover_name=df_spores_filtered.index,
        hover_data={c: False for c in df_spores_filtered.columns},
        custom_data=[df_spores_filtered.index],
        size_max=55,
        template="plotly_white",
        height=350,
        width=350,
        color_discrete_sequence=["#0d6efd"],
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        transition_duration=500,
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
