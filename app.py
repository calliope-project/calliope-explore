import dash
import dash_bootstrap_components as dbc
import dash_dangerously_set_inner_html
import flask
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from dash.exceptions import PreventUpdate

import url_helpers


df_spores = pd.read_csv("./data/data.csv", index_col=0)
df_units = pd.read_csv("./data/units.csv", index_col=0)

COLS = {
    "storage": dict(
        label="Storage capacity",
        col="Storage discharge capacity",
        help_text="Total capacity of all storage technologies to discharge energy in any given hour,"
        " including low temperature heat,hydrogen and electricity. Scaled relative to its maximum value"
        "(range 0.08 – 11 TW)",
    ),
    "curtailment": dict(
        label="Curtailment",
        col="Curtailment",
        help_text="Percentage of maximum available renewable electricity production"
        " from wind and solar photovoltaic technologies that is curtailed"
        " Scaled relative to its maximum value (range 0.1 – 6 %)",
    ),
    "biofuel": dict(
        label="Biofuel utilisation",
        col="Biofuel utilisation",
        help_text="Percentage of available residual biofuels that are consumed",
    ),
    "import": dict(
        label="National import",
        col="Average national import",
        help_text="Average annual import of electricity across all countries in the study area."
        " Scaled relative to its maximum value (range 4 – 73 TWh)",
    ),
    "elec-gini": dict(
        label="Electricity gini",
        col="Electricity production Gini coefficient",
        help_text="Degree of inequality of spatial distribution of electricity across all model regions,"
        " measured by the Gini coefficient of regional electricity production."
        " Scaled relative to its maximum value (range 0.53 – 0.74)",
    ),
    "fuel-gini": dict(
        label="Fuel autarky",
        col="Fuel autarky Gini coefficient",
        help_text="Degree of inequality of spatial distribution of industry"
        " synthetic fuel production relative to industry fuel demand across all model regions,"
        " measured by the Gini coefficient of regional over-production."
        " Scaled relative to its maximum value (range 0.63 – 0.93)",
    ),
    "ev": dict(
        label="EV as flexibility",
        col="EV as flexibility",
        help_text="Pearson correlation between timeseries of electric vehicle"
        " charging against that of primary electricity supply."
        " Scaled relative to its maximum value (range 0.52 – 0.92)",
    ),
    "heat": dict(
        label="Heat electr.",
        col="Heat electrification",
        help_text="Percentage of heat demand met by electricity-consuming, heat-producing technologies",
    ),
    "transport": dict(
        label="Transport electr.",
        col="Transport electrification",
        help_text="Percentage of road passenger and freight transport demand met by electric vehicles",
    ),
}

COL_NAMES = [v["col"] for k, v in COLS.items()]

SLIDER_DEFAULTS = {
    col: [df_spores[col].min(), df_spores[col].max()] for col in COL_NAMES
}

SLIDER_DEFAULTS_LIST = [v for k, v in SLIDER_DEFAULTS.items()]

COMPONENT_IDS = {
    "spore-id": ["data"],
    "slider-storage": ["value"],
    "slider-curtailment": ["value"],
    "slider-biofuel": ["value"],
    "slider-import": ["value"],
    "slider-elec-gini": ["value"],
    "slider-fuel-gini": ["value"],
    "slider-ev": ["value"],
    "slider-heat": ["value"],
    "slider-transport": ["value"],
}

server = flask.Flask(__name__)

TITLE = "Carbon-neutral European energy systems"

app = Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    # This is needed because we construct the layout programmatically; at load time
    # of the app, many of the ids targeted by callbacks do not yet exist
    suppress_callback_exceptions=True,
    title=TITLE,
)


url_bar_and_content_div = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-layout")]
)


navbar = dbc.NavbarSimple(
    brand=TITLE,
    # brand_href="#",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(
            dbc.NavLink(
                [html.I(className="bi-box-arrow-right"), " See the paper"],
                href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4012180",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                [html.I(className="bi-download"), " Download the data"],
                href="https://zenodo.org/record/6368833",
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
        help_text=COLS[id_]["help_text"],
        default_marks=default_marks,
    )


def row_label(params, label, id, col, help_text, default_marks=False):
    if default_marks:
        kwargs = {}
    else:
        kwargs = {"marks": {0: "", 0.2: "", 0.4: "", 0.6: "", 0.8: "", 1: ""}}

    min_, max_ = df_spores[col].min(), df_spores[col].max()
    return dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label(
                        [f"{label} ", html.I(className="bi-question-circle")],
                        id=f"tgt-{id}",
                    ),
                    dbc.Popover(
                        dbc.PopoverBody(help_text),
                        target=f"tgt-{id}",
                        trigger="hover",
                    ),
                ],
                md=4,
                class_name="slider-label",
            ),
            dbc.Col(
                url_helpers.apply_default_value(params)(dcc.RangeSlider)(
                    min=0,
                    max=1,
                    value=[min_, max_],
                    id=id,
                    className="slider",
                    **kwargs,
                ),
                class_name="slider-col",
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
                            "Deselect result",
                            color="primary",
                            id="reset-spore",
                            outline=True,
                        ),
                        html.Span("Results: "),
                        html.Span(id="num-results"),
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


HELP_TEXT = [
    html.P(
        "The Europe-wide energy system explorer allows you to navigate hundreds of alternative energy system configurations (SPORES)"
        " to reach carbon-neutrality across the entire European energy system in 2050. All such end-point configurations are equally feasible"
        " from a technical perspective and comparable in their total annualised system cost. If you want to know more about how we"
        " generate SPORES, click on 'See the paper' in the top-right corner."
    ),
    html.P("How to explore?"),
    html.Ol(
        [
            html.Li(
                "Use the sliders on the left to filter the SPORES based on practically-relevant indicators."
                " All indicators are scaled to their maximum values to range between 0 and 1. You can hover on the 'info' icon next to"
                " each indicator for a more extended definition and the actual value range."
            ),
            html.Li(
                "The slider ranges act on the plot in the bottom-left"
                " corner of the interface, which shows those SPORES that match the selected ranges. For default slider ranges, you will see all the SPORES across each indicator."
            ),
            html.Li(
                " Click on each of the SPORES in the plot to see it visualised on maps in the 'Overview' panel."
                " You can also click on the 'Summary data' panel for quantitative metrics. For further details on the map contents, you can refer to the paper."
            ),
            html.Li(
                [
                    "Different parts of the user interface use the ",
                    html.I(className="bi-question-circle"),
                    " icon to indicate that you can hover for further help.",
                ],
            ),
        ]
    ),
    html.P("Note: This application is still under development"),
    html.A(
        "Feedback and suggestions are welcome!",
        href="https://github.com/calliope-project/calliope-explore/issues",
    ),
]


OVERVIEW_HELP_1 = "Spatial distribution of onshore wind, offshore wind, and PV supply (right) and total primary energy supply across all regions (left). Capacities are shown for 29 zones which are aggregated from the 98 model regions to give comparable land area. Zonal supply is only shown when the sum of supply in that zone is greater than 6% of maximum supply from one technology in any region, making it visually easier to see the major supply hubs. Cyprus is not shown, but its data is included in the same zone as Greece in the maps. Biofuels, waste, hydro, and nuclear electricity supply are not shown on the maps."

OVERVIEW_HELP_2 = "Annual regional net electricity import and high synthetic fuel producing regions. Data is shown at the resolution of the 98 model regions. For each region, annual net electricity import is the sum of all electricity imported from connected regions over the year minus electricity exported to connected regions over the year. A positive net import indicates a region imports more electricity than it exports, while a negative net imports indicates more exports than imports. High synthetic fuel-producing regions are those producing above 5% of European total hydrogen. Since hydrogen cannot be transported between regions in our models, nor can it be directly consumed to meet service demands, high hydrogen production is equivalent to high synthetic fuel production."

OVERVIEW_HELP_3 = "Electricity grid transmission expansion beyond existing or planned capacities between regions. The title states the total line capacity added across Europe above the baseline capacities. Light grey lines depict regions connected by transmission lines that are not expanded. Where transmission expansion occurs, lines are shown in blue, with increasing thickness indicating increasing transmission expansion. Two values in the legend mapping expansion to line thickness refer to the mean and maximum expansion of any one line of all those that are expanded."

overview_help_div_content = [
    html.I(className="bi-question-circle overview-help", id="overview-help-1"),
    dbc.Popover(
        dbc.PopoverBody(OVERVIEW_HELP_1),
        target="overview-help-1",
        trigger="hover",
    ),
    html.I(className="bi-question-circle overview-help", id="overview-help-2"),
    dbc.Popover(
        dbc.PopoverBody(OVERVIEW_HELP_2),
        target="overview-help-2",
        trigger="hover",
    ),
    html.I(className="bi-question-circle overview-help", id="overview-help-3"),
    dbc.Popover(
        dbc.PopoverBody(OVERVIEW_HELP_3),
        target="overview-help-3",
        trigger="hover",
    ),
]


def page_layout(params=None):
    params = params or {}

    results = (
        html.Details(
            [
                html.Summary("Click here to show help"),
            ]
            + HELP_TEXT,
            id="help",
        ),
        dbc.Tabs(
            [
                dbc.Tab(
                    html.Div(
                        [
                            html.Img(id="overview-image"),
                            html.Div(id="overview-help-div"),
                        ],
                        className="relcontainer",
                    ),
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
            url_helpers.apply_default_value(params)(dcc.Store)(id="spore-id"),
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
            html.Div(
                dbc.Container(
                    dbc.Row(
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.A(
                                            "Built with Plotly Dash",
                                            href="https://dash.plotly.com/",
                                        ),
                                        " - ",
                                        html.A(
                                            "Source code on GitHub",
                                            href="https://github.com/calliope-project/calliope-explore",
                                        ),
                                    ],
                                    id="footer-content",
                                )
                            ]
                        )
                    ),
                ),
                id="footer-container",
                className="container-fluid",
            ),
        ]
    )

    return layout


@app.callback(
    Output("overview-image", "src"),
    Input("spore-id", "data"),
)
def update_overview_image(spore_id):
    if spore_id is None:
        return "assets/img/empty.jpg"
    else:
        return f"assets/img/{spore_id}.jpg"


@app.callback(
    Output("overview-help-div", "children"),
    Input("spore-id", "data"),
)
def update_overview_help_div(spore_id):
    if spore_id is None:
        return ""
    else:
        return overview_help_div_content


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
    Output("num-results", "children"),
    Input("spores-scatter", "figure"),
)
def update_num_results(figure):
    return len(figure["data"][0]["y"])


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
        y="variable",
        x="value",
        custom_data=["id"],
        hover_name="id",
        color="variable",
        hover_data={c: False for c in df_spores_filtered.columns},
        template="plotly_white",
        orientation="h",
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
        yaxis=dict(showticklabels=False, title=None),
        xaxis=dict(title=None),
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
    state = url_helpers.parse_state(href)
    return page_layout(state)


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
    inputs=[Input(id, p) for id, param in COMPONENT_IDS.items() for p in param],
)
def update_url(*values):
    return url_helpers.update_url_state(COMPONENT_IDS, values)


if __name__ == "__main__":
    app.run_server(debug=True)
