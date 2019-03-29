import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pymongo
import os


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


def query_most_recent_data():
    items = list(
        db["status"].find({}).sort("_id", pymongo.DESCENDING).limit(1)
    )
    data = {}
    for item in items:
        for cluster in clusters:
            alloc = item[cluster]["alloc"]
            data[cluster] = [alloc, item[cluster]["total"] - alloc]
    return data


def generate_smp_figure(labels):
    return {
        "data": cluster_plot_traces(labels, to_display["smp"]),
        "layout": cluster_plot_layout("SMP"),
    }


def generate_gpu_figure(labels):
    return {
        "data": cluster_plot_traces(labels, to_display["gpu"]),
        "layout": cluster_plot_layout("GPU"),
    }


def generate_mpi_figure(labels):
    return {
        "data": cluster_plot_traces(labels, to_display["mpi"]),
        "layout": cluster_plot_layout("MPI"),
    }


def generate_htc_figure(labels):
    return {
        "data": cluster_plot_traces(labels, to_display["htc"]),
        "layout": cluster_plot_layout("HTC"),
    }


# The layout function, this allows for the page updates when navigating to the site
def generate_layout(labels):
    return html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id="smp-graph",
                        figure=generate_smp_figure(labels),
                        style={"display": "flex", "width": "130px"},
                    ),
                    dcc.Graph(
                        id="gpu-graph",
                        figure=generate_gpu_figure(labels),
                        style={"display": "flex", "width": "130px"},
                    ),
                ],
                style={"display": "flex", "width": "260px", "height": "122px"},
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="mpi-graph",
                        figure=generate_mpi_figure(labels),
                        style={"display": "flex", "width": "130px"},
                    ),
                    dcc.Graph(
                        id="htc-graph",
                        figure=generate_htc_figure(labels),
                        style={"display": "flex", "width": "130px"},
                    ),
                ],
                style={"display": "flex", "width": "260px", "height": "122px"},
            ),
            dcc.Interval(
                id="interval-component",
                interval=300000, # 5 minutes
                n_intervals=0
            ),
        ],
        style={"width": "260px", "height": "245px"},
    )


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Ready the database
uri = os.environ["MONGO_URI"]
client = pymongo.MongoClient(uri)
db = client.get_database()

clusters = ["smp", "gpu", "mpi", "htc"]

to_display = query_most_recent_data()

# Useful variables
labels = ["Used", "Free"]

# The app layout w/ wrapper for layout
# wrapper = generate_layout(labels)
# app.layout = wrapper
app.layout = lambda: generate_layout(labels)


@app.callback(
    Output("smp-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_smp_graph(_):
    return generate_smp_figure(labels)


@app.callback(
    Output("gpu-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_gpu_graph(_):
    return generate_gpu_figure(labels)


@app.callback(
    Output("mpi-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_mpi_graph(_):
    return generate_mpi_figure(labels)


@app.callback(
    Output("htc-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_htc_graph(_):
    return generate_htc_figure(labels)


# Our main function
if __name__ == "__main__":
    app.run_server()
