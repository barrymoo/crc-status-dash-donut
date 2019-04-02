import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pymongo
import os
import json


def cluster_plot_layout(name):
    return go.Layout(
        showlegend=False,
        margin={"l": 1, "r": 1, "t": 1, "b": 1},
        annotations=[
            {
                "visible": True,
                "text": name,
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 30},
            }
        ],
    )


def cluster_plot_traces(labels, vals):
    return [
        go.Pie(
            labels=labels,
            values=vals,
            marker={"colors": ["rgb(181, 160, 97)", "rgb(13, 75, 116)"]},
            textinfo="label",
            textposition="inside",
            textfont={"size": 24, "color": "#ffffff"},
            hole=0.65,
            hoverinfo="value+text+percent",
            sort=False,
        )
    ]


def generate_smp_figure(labels, data):
    d = json.loads(data)["smp"]
    return {
        "data": cluster_plot_traces(labels, d),
        "layout": cluster_plot_layout("SMP"),
    }


def generate_gpu_figure(labels, data):
    d = json.loads(data)["gpu"]
    return {
        "data": cluster_plot_traces(labels, d),
        "layout": cluster_plot_layout("GPU"),
    }


def generate_mpi_figure(labels, data):
    d = json.loads(data)["mpi"]
    return {
        "data": cluster_plot_traces(labels, d),
        "layout": cluster_plot_layout("MPI"),
    }


def generate_htc_figure(labels, data):
    d = json.loads(data)["htc"]
    return {
        "data": cluster_plot_traces(labels, d),
        "layout": cluster_plot_layout("HTC"),
    }


# The layout function, this allows for the page updates when navigating to the site
def generate_layout(labels, data):
    return html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id="smp-graph",
                        figure=generate_smp_figure(labels, data),
                        style={"display": "flex", "width": "130px"},
                    ),
                    dcc.Graph(
                        id="gpu-graph",
                        figure=generate_gpu_figure(labels, data),
                        style={"display": "flex", "width": "130px"},
                    ),
                ],
                style={"display": "flex", "width": "260px", "height": "122px"},
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="mpi-graph",
                        figure=generate_mpi_figure(labels, data),
                        style={"display": "flex", "width": "130px"},
                    ),
                    dcc.Graph(
                        id="htc-graph",
                        figure=generate_htc_figure(labels, data),
                        style={"display": "flex", "width": "130px"},
                    ),
                ],
                style={"display": "flex", "width": "260px", "height": "122px"},
            ),
            html.Div(id="data", style={"display": "none"}),
            dcc.Interval(
                id="interval-component", interval=300000, n_intervals=0  # 5 minutes
            ),
        ],
        style={"width": "260px", "height": "245px"},
    )


def query_most_recent_data():
    items = list(db["status"].find({}).sort("_id", pymongo.DESCENDING).limit(1))
    data = {}
    for item in items:
        for cluster in clusters:
            alloc = item[cluster]["alloc"]
            data[cluster] = [alloc, item[cluster]["total"] - alloc]
    return json.dumps(data)


# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/barrymoo/pen/rbaKVJ.css"],
)
server = app.server

# Ready the database
uri = os.environ["MONGO_URI"]
client = pymongo.MongoClient(uri)
db = client.get_database()

# Global variables which do not change
clusters = ["smp", "gpu", "mpi", "htc"]
labels = ["Used", "Free"]

# The app layout w/ wrapper for layout
# wrapper = generate_layout(labels)
# app.layout = wrapper
initial_data = query_most_recent_data()
app.layout = lambda: generate_layout(labels, initial_data)


@app.callback(
    Output("data", "children"),
    [Input("interval-component", "n_intervals")],
)
def query_most_recent_data_callback(_):
    return query_most_recent_data()


@app.callback(
    Output("smp-graph", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("data", "children"),
    ],
)
def update_smp_graph(_, data):
    return generate_smp_figure(labels, data)


@app.callback(
    Output("gpu-graph", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("data", "children"),
    ],
)
def update_gpu_graph(_, data):
    return generate_gpu_figure(labels, data)


@app.callback(
    Output("mpi-graph", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("data", "children"),
    ]
)
def update_mpi_graph(_, data):
    return generate_mpi_figure(labels, data)


@app.callback(
    Output("htc-graph", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("data", "children"),
    ],
)
def update_htc_graph(_, data):
    return generate_htc_figure(labels, data)


if __name__ == "__main__":
    app.run_server()
