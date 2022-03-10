from email.policy import default
from urllib.parse import urlencode, quote
import json

import flask
import dash
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import dash_dangerously_set_inner_html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from url_helpers import (
    apply_default_value,
    parse_state,
    param_string,
    myrepr,
)

df_spores = pd.read_csv("./spores_data.csv", index_col=0)
df_units = pd.read_csv("./units.csv", index_col=0)

COLS = {
    "storage": dict(
        label="Storage capacity",
        col="Storage discharge capacity",
    ),
    "curtailment": dict(
        label="Curtailment",
        col="Curtailment",
    ),
    "biofuel": dict(
        label="Biofuel utilisation",
        col="Biofuel utilisation",
    ),
    "import": dict(
        label="National import",
        col="Average national import",
    ),
    "elec-gini": dict(
        label="Electricity gini",
        col="Electricity production Gini coefficient",
    ),
    "fuel-gini": dict(
        label="Fuel autarky",
        col="Fuel autarky Gini coefficient",
    ),
    "ev": dict(
        label="EV as flexibility",
        col="EV as flexibility",
    ),
    "heat": dict(
        label="Heat electrification",
        col="Heat electrification",
    ),
    "transport": dict(
        label="Transport electrification",
        col="Transport electrification",
    ),
}

COL_NAMES = [v["col"] for k, v in COLS.items()]

SLIDER_DEFAULTS = {
    col: [df_spores[col].min(), df_spores[col].max()] for col in COL_NAMES
}

SLIDER_DEFAULTS_LIST = [v for k, v in SLIDER_DEFAULTS.items()]

server = flask.Flask(__name__)

app = Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    # This is needed because we construct the layout programmatically; at load time
    # of the app, many of the ids targeted by callbacks do not yet exist
    suppress_callback_exceptions=True,
)


url_bar_and_content_div = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-layout")]
)


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


def row_label_from_id(params, id_, default_marks=False):
    return row_label(
        params=params,
        label=COLS[id_]["label"],
        id=f"slider-{id_}",
        col=COLS[id_]["col"],
        default_marks=default_marks,
    )


def row_label(params, label, id, col, default_marks=False):
    if default_marks:
        kwargs = {}
    else:
        kwargs = {"marks": {0: "", 0.2: "", 0.4: "", 0.6: "", 0.8: "", 1: ""}}

    min_, max_ = df_spores[col].min(), df_spores[col].max()
    return dbc.Row(
        [
            dbc.Col(dbc.Label(label), md=3, class_name="slider-label"),
            dbc.Col(
                apply_default_value(params)(dcc.RangeSlider)(
                    min=0, max=1, value=[min_, max_], id=id, **kwargs
                ),
                class_name="slider",
            ),
        ],
        class_name="slider-group",
    )


def controls(params):
    return html.Div(
        [
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Button(
                            "Reset sliders",
                            color="primary",
                            id="reset-sliders",
                            outline=True,
                        ),
                        dbc.Button(
                            "Deselect SPORE",
                            color="primary",
                            id="reset-spore",
                            outline=True,
                        ),
                    ]
                ),
                class_name="buttons",
            ),
            row_label_from_id(params=params, id_="storage"),
            row_label_from_id(params=params, id_="curtailment"),
            row_label_from_id(params=params, id_="biofuel"),
            row_label_from_id(params=params, id_="import"),
            row_label_from_id(params=params, id_="elec-gini"),
            row_label_from_id(params=params, id_="fuel-gini"),
            row_label_from_id(params=params, id_="ev"),
            row_label_from_id(params=params, id_="heat"),
            row_label_from_id(params=params, id_="transport", default_marks=True),
        ]
    )


def page_layout(params=None):
    params = params or {}

    results = (
        dbc.Tabs(
            [
                dbc.Tab(
                    html.Img(id="overview-image"),
                    label="Overview",
                    tab_id="overview",
                ),
                dbc.Tab(
                    html.Div(id="summary-data"),
                    label="Summary data",
                    tab_id="summary",
                ),
            ],
            id="tabs",
            active_tab="overview",
        ),
    )

    layout = html.Div(
        [
            navbar,
            apply_default_value(params)(dcc.Store)(id="spore-id"),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        controls(params=params),
                                        dcc.Graph(id="spores-scatter"),
                                    ]
                                ),
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

    return layout


@app.callback(
    Output("overview-image", "src"),
    Input("spore-id", "data"),
)
def update_tabs(spore_id):
    if spore_id is None:
        return "assets/img/empty.jpg"
    else:
        return f"assets/img/{spore_id}.jpg"


@app.callback(
    Output("summary-data", "children"),
    Input("spore-id", "data"),
)
def update_summary(spore_id):
    if spore_id is None:
        return None
    else:
        df_ = pd.concat([df_spores.loc[spore_id, :], df_units], axis=1)
        df_.columns = ["Indicator", "Unit"]
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            df_.to_html(float_format=lambda x: "{:.2f}".format(x))
        )


@app.callback(
    Output("spore-id", "data"),
    Input("spores-scatter", "clickData"),
    Input("reset-spore", "n_clicks"),
    Input("spore-id", "data"),
)
def update_spore_id(scatter_clickdata, reset_n_clicks, old_spore_id):
    ctx = dash.callback_context

    if not ctx.triggered:
        _id = None
    else:
        _id = ctx.triggered[0]["prop_id"].split(".")[0]

    if _id == "spores-scatter":
        return scatter_clickdata["points"][0]["customdata"][0]
    elif _id == "reset-spore":
        return None
    elif _id is None:
        return old_spore_id

    # try:
    #     return scatter_clickdata["points"][0]["customdata"][0]
    # # If this was called without an actual valid click, resulting in no valid ClickData,
    # # we return the URL-persisted spore id
    # except TypeError:
    #     return old_spore_id


@app.callback(
    Output("spores-scatter", "figure"),
    Input("slider-storage", "value"),
    Input("slider-curtailment", "value"),
    Input("slider-biofuel", "value"),
    Input("slider-import", "value"),
    Input("slider-elec-gini", "value"),
    Input("slider-fuel-gini", "value"),
    Input("slider-ev", "value"),
    Input("slider-heat", "value"),
    Input("slider-transport", "value"),
)
def update_figure(
    storage_range,
    curtailment_range,
    biofuel_range,
    import_range,
    elec_gini_rance,
    fuel_gini_range,
    ev_range,
    heat_range,
    transport_range,
):
    df_spores_filtered = df_spores[
        df_spores["Transport electrification"].between(
            transport_range[0], transport_range[1]
        )
        & df_spores["Heat electrification"].between(heat_range[0], heat_range[1])
        & df_spores["Storage discharge capacity"].between(
            storage_range[0], storage_range[1]
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

    df_spores_filtered = pd.melt(
        df_spores_filtered.loc[:, COL_NAMES], ignore_index=False
    ).reset_index(drop=False)

    fig = px.strip(
        df_spores_filtered,
        x="variable",
        y="value",
        custom_data=["id"],
        hover_name="id",
        color="variable",
        hover_data={c: False for c in df_spores_filtered.columns},
        template="plotly_white",
        height=350,
        color_discrete_sequence=[
            "#0440fe",
            "#ff7c02",
            "#32ce4d",
            "#e9111c",
            "#933ae2",
            "#7f3901",
            "#f69adb",
            "#ffd85b",
            "#58e5fe",
        ],
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        transition_duration=500,
        xaxis=dict(showticklabels=False),
    )

    return fig


def app_layout():
    if flask.has_request_context():
        # When app actually runs
        return url_bar_and_content_div
    else:
        # For validation only
        return html.Div([url_bar_and_content_div, *page_layout()])


app.layout = app_layout


@app.callback(Output("page-layout", "children"), inputs=[Input("url", "href")])
def page_load(href):
    if not href:
        return []
    state = parse_state(href)
    return page_layout(state)


component_ids = {
    "spore-id": ["data"],
    "slider-transport": ["value"],
    "slider-curtailment": ["value"],
    "slider-biofuel": ["value"],
    "slider-import": ["value"],
    "slider-elec-gini": ["value"],
    "slider-fuel-gini": ["value"],
    "slider-ev": ["value"],
}


@app.callback(
    [
        Output("slider-storage", "value"),
        Output("slider-curtailment", "value"),
        Output("slider-biofuel", "value"),
        Output("slider-import", "value"),
        Output("slider-elec-gini", "value"),
        Output("slider-fuel-gini", "value"),
        Output("slider-ev", "value"),
        Output("slider-heat", "value"),
        Output("slider-transport", "value"),
    ],
    inputs=[Input("reset-sliders", "n_clicks")],
)
def reset_sliders(n_clicks):
    return SLIDER_DEFAULTS_LIST


@app.callback(
    Output("url", "search"),
    inputs=[Input(id, p) for id, param in component_ids.items() for p in param],
)
def update_url_state(*values):
    """Updates URL from component values."""

    keys = [param_string(id, p) for id, param in component_ids.items() for p in param]
    state = dict(zip(keys, map(myrepr, values)))
    params = urlencode(state, safe="%/:?~#+!$,;'@()*[]\"", quote_via=quote)
    return f"?{params}"


if __name__ == "__main__":
    app.run_server(debug=True)
