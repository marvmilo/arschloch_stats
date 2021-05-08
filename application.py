import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import json
import datetime
import os
import base64
import time

timestamp_format = "%d-%m-%YT%H-%M-%S-%f"

########### Functions
def name_input(id, value):
    return dbc.Input(
        value = value,
        id = id, 
        bs_size="lg", 
        className="mb-3"
    )

def upload_button():
    return html.Div(
        dcc.Upload(
            dbc.Button(
                "Load Json",
                id = "upload-json-button",
                color = "primary",
                size = "lg",
                className = "mr-1"
            ),
            id = "upload-json"
        ),
        style = {"text-align": "center"}
    )
    
def points_table(table_dict):
    table_header = [
        html.Thead(
            html.Tr(
                children = [html.Th(key) for key in table_dict]
            )
        )
    ]
    
    table_rows = list()
    for i, rank in enumerate(table_dict["Ranks"]):
        row = [html.Th(rank)]
        for key in list(table_dict.keys())[1:]:
            if rank == "Points":
                row.append(html.Th(table_dict[key][i]))
            else:
                row.append(html.Td(table_dict[key][i]))
        table_rows.append(html.Tr(row))
    
    table_body = [
        html.Tbody(table_rows)
    ]
    
    return dbc.Table(table_header + table_body, bordered=True)

def modal(id,header,text):
    return dbc.Modal(
        children = [
            dbc.ModalHeader(header),
            dbc.ModalBody(text)
        ],
        id = id,
        centered = True
    )

def names_content(name_list = list()):
    content = list()
    content.append(dbc.Alert(html.H3("Create New Game 🎮"), color = "primary")),
    content.append(
        html.Div(
            dbc.Button(
                "Start Game",
                id = "start-game-button",
                color = "primary",
                size = "lg",
                className = "mr-1"
            ),
            style = {"text-align": "center"}
        )
    )
    content.append(html.Br())
    if not len(name_list):
        name_list = [None, None, None]
    for i, name in enumerate(name_list):
        content.append(name_input(f"input_{i}", name))
    content.append(
        dbc.Button(
            "👥 Add Player 👥",
            id = "add-player-button",
            color = "primary",
            block = True
        )
    )
    content.append(
        html.Div(
            children = [
                html.Br(),
                html.Div(
                    children = [
                        dbc.Checkbox(
                            id = "handout-mistakes-checkbox",
                            className = "custom-control-input",
                            checked = True
                        ),
                        dbc.Label(
                            "Count Handout Mistakes 🃏",
                            html_for  = "handout-mistakes-checkbox",
                            className = "custom-control-label"
                        )
                    ],
                    className = "custom-control custom-checkbox",   
                )
            ],
            style = {"text-align": "center"}
        )
    )
    content.append(
        html.Div(
            children = [
                html.Div(
                    children = [
                        dbc.Checkbox(
                            id = "beer-count-checkbox",
                            className = "custom-control-input",
                            checked = True
                        ),
                        dbc.Label(
                            "Count Beers 🍺",
                            html_for  = "beer-count-checkbox",
                            className = "custom-control-label"
                        )
                    ],
                    className = "custom-control custom-checkbox"    
                )
            ],
            style = {"text-align": "center"}
        )
    )
    content.append(
        html.Div(
            children = [
                html.Div(
                    children = [
                        dbc.Checkbox(
                            id = "goiß-count-checkbox",
                            className = "custom-control-input",
                            checked = True
                        ),
                        dbc.Label(
                            "Count Goiß Moß 🥴",
                            html_for  = "goiß-count-checkbox",
                            className = "custom-control-label"
                        )
                    ],
                    className = "custom-control custom-checkbox"    
                )
            ],
            style = {"text-align": "center"}
        )
    )
    content.append(html.Br()),
    content.append(html.Br()),
    content.append(dbc.Alert(html.H3("Load Game 📤"), color = "primary")),
    content.append(
        html.Div(
            upload_button(),
            id = "upload-button"
        )
    )
    content.append(
        dbc.Modal(
            children = [
                dbc.ModalHeader(
                    "📤 Continue the game of this file? 📤",
                ),
                dbc.ModalBody(
                    id = "file-name"
                ),
                dbc.ModalBody(
                    children = [
                        html.Div(
                            dbc.Spinner(
                                dbc.Button(
                                    "Start Game",
                                    id = "confirm-load-game",
                                    color = "primary",
                                    className = "mr-1",
                                    block = True,
                                    size = "lg"
                                )
                            ),
                            style = {"text-align": "center"}
                        ),
                        html.Div(
                            id = "json-content",
                            style = {"display": "none"}
                        )
                    ]
                )
            ],
            id = "confirm-upload-modal",
            centered = True
        )
    )
    content.append(
        html.Div(
            children = [
                dbc.Button(id = "add-results-button"),
                dbc.Button(id = "handout-mistake-button"),
                dbc.Button(id = "beer-count-button"),
                dbc.Button(id = "goiß-count-button"),
                dbc.Button(id = "save-game-button"),
                html.Div(
                    "{}",
                    id = "table-dict",
                    style = {"display": "none"}
                ),
                html.Div(
                    "{}",
                    id = "game-history",
                    style = {"display": "none"}
                ),
                html.Div(
                    "{}",
                    id = "points-development",
                    style = {"display": "none"}
                ),
                html.Div(
                    "{}",
                    id = "handout-mistakes",
                    style = {"display": "none"}
                ),
                html.Div(
                    "{}",
                    id = "beer-count",
                    style = {"display": "none"}
                ),
                html.Div(
                    "{}",
                    id = "goiß-count",
                    style = {"display": "none"}
                ),
            ],
            style = {"display": "None"}
        )
    )
    return content

def get_ranks(names):
    ranks = list()
    half = int(len(names)/2)
    for i in range(len(names)):
        ranks.append("Bauer")
    for i in range(half):
        ranks[i] = f"{'Vize'*i} Arschloch"
        i_reverse = -(i + 1)
        ranks[i_reverse] = f"{'Vize'*i} König"
    ranks.reverse()
    return ranks

def game_content(table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count):
    ranking = list()
    names = list(table_dict.keys())[1:]
    names.reverse()
    for name in names:
        if not len(ranking):
            ranking.append(name)
        else:
            pos = 0
            for rank_name in ranking:
                if table_dict[name][-1] > table_dict[rank_name][-1]:
                    pos += 1
            ranking.insert(pos, name)
    ranking.reverse()
    
    html_headers = [html.H1, html.H2, html.H3, html.H4]
    html_ranking = list()
    for i, rank in enumerate(ranking):
        text = f"{i+1}. {rank}"
        try:
            html_ranking.append(html_headers[i](text))
        except IndexError:
            html_ranking.append(html.H5(text))
    
    game_history_data = list()
    game_tick_text = table_dict["Ranks"][:-1]
    game_tick_text.reverse()
    if len(game_history["x"]) > 6:
        game_x_range = [len(game_history["x"]) - 6, len(game_history["x"]) + 0.5]
    else:
        game_x_range = [0.5,6.5]
    for i, name in enumerate(list(game_history.keys())[1:]):
        game_history_data.append(go.Scatter(x = game_history["x"], y = game_history[name], name = name, mode = "lines"))
    game_history_fig = go.Figure(data = game_history_data)
    game_history_fig.update_layout(
        yaxis = dict(
            tickmode = "array",
            tickvals = list(range(len(table_dict["Ranks"][:-1]))),
            ticktext = game_tick_text
        ),
        xaxis = dict(
            title = "Game"
        ),
        xaxis_range = game_x_range
    )
    
    points_development_data = list()
    max_points = 0
    min_points = 0
    for i, name in enumerate(list(points_development.keys())[1:]):
        if max(points_development[name]) > max_points:
            max_points = max(points_development[name])
        if min(points_development[name]) < min_points:
            min_points = min(points_development[name])
        points_development_data.append(go.Scatter(x = points_development["x"], y = points_development[name], name = name))
    if len(points_development["x"]) >= 6:    
        points_x_range = None
    else:
        points_x_range = [-0.5,6.5]
    if max_points >= 6:
        points_y_range = None
    else:
        points_y_range = [min_points-0.5,6.5]
    points_development_fig = go.Figure(data = points_development_data)
    points_development_fig.update_layout(
        yaxis = dict(
            title = "Points"
        ),
        xaxis = dict(
            title = "Game"
        ),
        yaxis_range = points_y_range,
        xaxis_range = points_x_range
    )
    
    x_text = table_dict["Ranks"][:-1]
    x_vals = list(range(len(x_text)))
    rank_accumulation_data = list()
    max_ranks = 0
    for i, name in enumerate(list(table_dict.keys())[1:]):
        if max(table_dict[name][:-1]) > max_ranks:
            max_ranks = max(table_dict[name][:-1])
        rank_accumulation_data.append(go.Bar(x = x_vals, y = table_dict[name][:-1], name = name))
    rank_accumulation_fig = go.Figure(data = rank_accumulation_data)
    if max_ranks >= 5:
        ranks_y_range = None
    else:
        ranks_y_range = [-0.5,5]
    rank_accumulation_fig.update_layout(
        yaxis = dict(
            title = "Rank Amount"
        ),
        xaxis = dict(
            tickmode = "array",
            tickvals = x_vals,
            ticktext = x_text
        ),
        yaxis_range = ranks_y_range
    )
    
    
    if handout_mistakes:
        if max(handout_mistakes.values()) >= 5:
            handout_y_range = None
        else:
            handout_y_range = [-0.5,5]
        bar_widths = [0.35 for val in handout_mistakes.values()]
        handout_y = list(handout_mistakes.values())
        handout_mistake_data = [
            go.Bar(
                x = list(
                    handout_mistakes.keys()
                ), 
                y = handout_y, 
                width = bar_widths, 
                text = handout_y, 
                textposition="auto", 
                marker_color = "#007BFF",
                textfont = dict(color = "rgb(255, 255, 255)")
            )
        ]
        handout_mistake_fig = go.Figure(data = handout_mistake_data)
        handout_mistake_fig.update_layout(
            yaxis_range = handout_y_range
        )
        handout_mistakes_style = {}
    else:
        handout_mistakes_style = {"display": "none"}
        handout_mistake_fig = go.Figure()
        handout_mistakes = {}
        
    if beer_count:
        #print(max(beer_count.values()))
        if max(beer_count.values()) >= 5:
            beer_y_range = None
        else:
            beer_y_range = [-0.5,5]
        bar_widths = [0.35 for val in beer_count.values()]
        beer_y = list(beer_count.values())
        beer_count_data = [
            go.Bar(
                x = list(
                    beer_count.keys()
                ), 
                y = beer_y, 
                width = bar_widths, 
                text = beer_y, 
                textposition="auto", 
                marker_color = "#007BFF", 
                textfont = dict(color = "rgb(255, 255, 255)")
            )
        ]
        beer_count_fig = go.Figure(data = beer_count_data)
        beer_count_fig.update_layout(
            yaxis_range = beer_y_range
        )
        beer_count_style = {}
    else:
        beer_count_style = {"display": "none"}
        beer_count_fig = go.Figure()
        beer_count = {}
    
    if goiß_count:
        #print(max(beer_count.values()))
        if max(goiß_count.values()) >= 5:
            goiß_y_range = None
        else:
            goiß_y_range = [-0.5,5]
        bar_widths = [0.35 for val in goiß_count.values()]
        goiß_y = list(goiß_count.values())
        goiß_count_data = [
            go.Bar(
                x = list(
                    goiß_count.keys()
                ), 
                y = goiß_y, 
                width = bar_widths, 
                text = goiß_y, 
                textposition="auto", 
                marker_color = "#007BFF", 
                textfont = dict(color = "rgb(255, 255, 255)")
            )
        ]
        goiß_count_fig = go.Figure(data = goiß_count_data)
        goiß_count_fig.update_layout(
            yaxis_range = goiß_y_range
        )
        goiß_count_style = {}
    else:
        goiß_count_style = {"display": "none"}
        goiß_count_fig = go.Figure()
        goiß_count = {}
    
    return [
        dbc.Alert(html.H3("Overview 🔍"), color = "primary"),
        #html.Br(),
        html.Div(
            points_table(table_dict),
            style = {"overflow": "scroll"}
        ),
        html.Br(),
        html.Div(
            dbc.Button(
                "Add Game Results",
                id = "add-results-button",
                color = "primary",
                size = "lg",
                className = "mr-1"
            ),
            style = {"text-align": "center"}
        ),
        html.Br(),
        html.Div(
            dbc.Button(
                "Save Game",
                id = "save-game-button",
                color = "primary",
                size = "lg",
                className = "mr-1"
            ),
            style = {"text-align": "center"}
        ),
        
        html.Div(
            children = [
                dbc.Button(id = "start-game-button"),
                dbc.Button(id = "add-player-button"),
                dbc.Checkbox(id = "handout-mistakes-checkbox"),
                dbc.Checkbox(id = "beer-count-checkbox"),
                dbc.Checkbox(id = "goiß-count-checkbox")
            ],  
            style = {"display": "none"}
        ),
        html.Br(),
        html.Div(
            str(table_dict),
            id = "table-dict",
            style = {"display": "none"}
        ),
        html.Br(),
        dbc.Alert(html.H3("Ranking 🏆"), color = "primary"),
        html.Div(
            children = html_ranking,
            style = {
                "text-align": "center"
            }
        ),
        html.Br(),html.Br(),
        dbc.Alert(html.H3("Points Development 📈"), color = "primary"),
        dbc.Spinner(
            dcc.Graph(figure = points_development_fig)
        ),
        html.Div(
            str(points_development),
            id = "points-development",
            style = {"display": "none"}
        ),
        html.Br(),html.Br(),
        dbc.Alert(html.H3("Game History 🕑"), color = "primary"),
        dbc.Spinner(
            dcc.Graph(figure = game_history_fig)
        ),
        html.Div(
            str(game_history),
            id = "game-history",
            style = {"display": "none"}
        ),
        html.Br(),html.Br(),
        dbc.Alert(html.H3("Rank Accumulation 📊"), color = "primary"),
        dbc.Spinner(
            dcc.Graph(figure = rank_accumulation_fig)
        ),
        html.Br(),
        html.Div(
            children = [
                html.Br(),
                dbc.Alert(html.H3("Handout Mistakes 🃏"), color = "primary"),
                dbc.Spinner(
                    dcc.Graph(figure = handout_mistake_fig)
                ),
                html.Br(),
                html.Div(
                    dbc.Button(
                        "Add Handout Mistake",
                        id = "handout-mistake-button",
                        color = "primary",
                        size = "lg",
                        className = "mr-1"
                    ),
                    style = {"text-align": "center"}
                ),
            ],
            style = handout_mistakes_style
        ),
        html.Div(
            str(handout_mistakes),
            id = "handout-mistakes",
            style = {"display": "none"}
        ),
        html.Br(),
        html.Div(
            children = [
                html.Br(),
                dbc.Alert(html.H3("Beer Count 🍺"), color = "primary"),
                dbc.Spinner(
                    dcc.Graph(figure = beer_count_fig)
                ),
                html.Br(),
                html.Div(
                    dbc.Button(
                        "Add Beer",
                        id = "beer-count-button",
                        color = "primary",
                        size = "lg",
                        className = "mr-1"
                    ),
                    style = {"text-align": "center"}
                ),
            ],
            style = beer_count_style
        ),
        html.Div(
            str(beer_count),
            id = "beer-count",
            style = {"display": "none"}
        ),
        html.Br(),
        html.Div(
            children = [
                html.Br(),
                dbc.Alert(html.H3("Goiß Moß Count 🥴"), color = "primary"),
                dbc.Spinner(
                    dcc.Graph(figure = goiß_count_fig)
                ),
                html.Br(),
                html.Div(
                    dbc.Button(
                        "Add Goiß Moß",
                        id = "goiß-count-button",
                        color = "primary",
                        size = "lg",
                        className = "mr-1"
                    ),
                    style = {"text-align": "center"}
                ),
            ],
            style = goiß_count_style
        ),
        html.Div(
            str(goiß_count),
            id = "goiß-count",
            style = {"display": "none"}
        ),
        html.Div(
            children = [
                dbc.Button(id = "confirm-load-game"),
                html.Div(id = "json-content"),
                dcc.Upload(id = "upload-json"),
                dbc.Modal(id = "confirm-upload-modal"),
                html.Div(id = "file-name"),
                dbc.Button(id = "upload-button")
            ],
            style = {"display": "none"}
        )
    ]

########### Initiate the app
external_stylesheets = [dbc.themes.BOOTSTRAP]
meta_tags = [{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
server = flask.Flask(__name__)
app = dash.Dash(
    server = server, 
    external_stylesheets=external_stylesheets,
    meta_tags=meta_tags
)
application = app.server
app.title='Arschloch Stats'

@server.route("/download/<path:path>")
def download(path):
    return flask.send_from_directory(".", path, as_attachment=True)

########### Set up the layout
app.layout = html.Div(
    children = [
        #Navbar
        dbc.Navbar(
            children = [
                #navbar title
                dbc.Row(
                    children = [
                        dbc.Col(
                            " ".join(word.upper()),
                            style = {
                                "font-size": "20px",
                                "color": "white",
                                "white-space": "nowrap"
                            },
                            width = "auto"
                        )
                        for word in "Arschloch Stats".split(" ")
                    ],
                    style = {
                        "width": "300px",
                        "max-width": "50%"
                    }
                ),
        
                #navbar toggler
                dbc.NavbarToggler(id = "nav-toggler"),
                
                #navbar interactions
                dbc.Collapse(
                    dbc.Row(
                        children = [
                            dbc.Button(
                                "New Game",
                                id = "new-game-button",
                                color = "primary",
                                className = "mr-1"
                            ),
                            dbc.Button(
                                "Support Me",
                                id = "support-me-button",
                                color = "primary",
                                className = "mr-1"
                            )
                        ],
                        justify = "end",
                        no_gutters = True,
                        style = {"width": "100%"}
                    ),
                    navbar = True,
                    id = "nav-collapse"
                )
            ],
            color = "primary",
            dark = True,
            style = {"padding": "20px 40px"}
        ),
        
        # dbc.NavbarSimple(
        #     children = [
        #         html.Br(),
        #         dbc.Button(
        #             "New Game",
        #             id = "new-game-button",
        #             color = "primary",
        #             className = "mr-1"
        #         ),
        #         html.Br(),
        #         dbc.Button(
        #             "Support Me",
        #             id = "support-me-button",
        #             color = "primary",
        #             className = "mr-1"
        #         ),
        #         html.Br()
        #     ],
        #     brand = "Arschloch Stats",
        #     color = "primary",
        #     dark = True
        # ),
        html.Div(
            children = names_content(),
            id = "content",
            style = {"padding": "5%"}
        ),
        modal(
            "start-game-modal",
            "Please Notice!",
            "Game can only start with minimum 2 players and no equal names!"
        ),
        modal(
            "support-me-modal",
            "🍺 Support Me! 🍺",
            html.Div(
                children = [
                    "Donate a little bit to me, so that I can buy me some BEER! My fuel to program stuff like this.",
                    html.Br(), html.Br(),
                    html.A(
                        dbc.Button(
                            "💸 PayPal 💸",
                            id = "paypal-button",
                            color = "primary",
                            size = "lg",
                            className = "mr-1"
                        ),
                        href = "https://paypal.me/marvmilo",
                        target = "_blank"
                    )
                ],
                style = {"text-align": "center"}
            )
        ),
        modal(
            "confirm-selection-modal",
            "Your selection will be added to the statistical evaluation!",
            html.Div(
                dbc.Spinner(
                    children = [
                        dbc.Button(
                            "Ok",
                            id = "confirm-selection-button",
                            color = "primary",
                            size = "lg",
                            className = "mr-1"
                        ),
                        html.Div(
                            "{}",
                            id = "current-selection",
                            style = {"display": "none"}
                        )
                    ]
                ),
                style = {"text-align": "center"}
            )
        ),
        modal(
            "new-game-modal",
            "Are You sure?",
            dbc.Row(
                children = [
                    dbc.Col(
                        html.Div(
                            dbc.Button(
                                "✔️",
                                id = "confirm-new-game-button",
                                color = "primary",
                                className = "mr-1",
                                block = True,
                                size = "lg"
                            )
                        ),
                        width = 4
                    ),
                    dbc.Col(
                        html.Div(
                            dbc.Button(
                                "❌",
                                id = "delice-new-game-button",
                                color = "primary",
                                className = "mr-1",
                                block = True,
                                size = "lg"
                            )
                        ),
                        width = 4
                    )
                ],
                justify = "center"
            )
        ),
        dbc.Modal(
            children = [
                dbc.ModalHeader(
                    "name",
                    id = "points-modal-header"
                ),
                dbc.ModalBody(
                    html.Div(
                        dbc.RadioItems(
                            options = list(),
                            id = "select-points-radio",
                            value = 0
                        ),
                        style = {"padding": "10%"}
                    )
                ),
                dbc.ModalBody(
                    dbc.Row(
                        children = [
                            dbc.Col(
                                html.Div(
                                    dbc.Button(
                                        "Cancel",
                                        id = "cancel-points-radio",
                                        color = "primary",
                                        className = "mr-1",
                                        block = True,
                                        size = "lg"
                                    )
                                ),
                                width = 4
                            ),
                            dbc.Col(
                                html.Div(
                                    dbc.Button(
                                        "Next",
                                        id = "next-points-radio",
                                        color = "primary",
                                        className = "mr-1",
                                        block = True,
                                        size = "lg"
                                    )
                                ),
                                width = 4
                            )
                        ],
                        justify = "center"
                    )
                ),
                html.Div(
                    "{}",
                    id = "current-radio",
                    style = {"display": "none"}
                )
            ],
            id = "points-radio-modal",
            centered = True,
            backdrop = "static"
        ),
        dbc.Modal(
            children = [
                dbc.ModalHeader(
                    "Select Player who made the handout mistake:",
                ),
                dbc.ModalBody(
                    html.Div(
                        dbc.RadioItems(
                            options = list(),
                            id = "handout-mistake-radio",
                            value = 0
                        ),
                        style = {"padding": "10%"}
                    )
                ),
                dbc.ModalBody(
                    dbc.Spinner(
                        dbc.Row(
                            children = [
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Cancel",
                                            id = "cancel-handout-radio",
                                            color = "primary",
                                            className = "mr-1",
                                            block = True,
                                            size = "lg"
                                        )
                                    ),
                                    width = 4
                                ),
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Ok",
                                            id = "ok-handout-radio",
                                            color = "primary",
                                            className = "mr-1",
                                            block = True,
                                            size = "lg"
                                        )
                                    ),
                                    width = 4
                                )
                            ],
                            justify = "center"
                        )
                    )
                )
            ],
            id = "handout-mistake-radio-modal",
            centered = True,
            backdrop = "static"
        ),
        dbc.Modal(
            children = [
                dbc.ModalHeader(
                    "Select Player who finished the beer:",
                ),
                dbc.ModalBody(
                    html.Div(
                        dbc.RadioItems(
                            options = list(),
                            id = "beer-count-radio",
                            value = 0
                        ),
                        style = {"padding": "10%"}
                    )
                ),
                dbc.ModalBody(
                    dbc.Spinner(
                        dbc.Row(
                            children = [
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Cancel",
                                            id = "cancel-beer-radio",
                                            color = "primary",
                                            className = "mr-1",
                                            block = True,
                                            size = "lg"
                                        )
                                    ),
                                    width = 4
                                ),
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Ok",
                                            id = "ok-beer-radio",
                                            color = "primary",
                                            className = "mr-1",
                                            block = True,
                                            size = "lg"
                                        )
                                    ),
                                    width = 4
                                )
                            ],
                            justify = "center"
                        )
                    )
                )
            ],
            id = "beer-count-radio-modal",
            centered = True,
            backdrop = "static"
        ),
        dbc.Modal(
            children = [
                dbc.ModalHeader(
                    "Select Player who finished the Goiß Moß:",
                ),
                dbc.ModalBody(
                    html.Div(
                        dbc.RadioItems(
                            options = list(),
                            id = "goiß-count-radio",
                            value = 0
                        ),
                        style = {"padding": "10%"}
                    )
                ),
                dbc.ModalBody(
                    dbc.Spinner(
                        dbc.Row(
                            children = [
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Cancel",
                                            id = "cancel-goiß-radio",
                                            color = "primary",
                                            className = "mr-1",
                                            block = True,
                                            size = "lg"
                                        )
                                    ),
                                    width = 4
                                ),
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Ok",
                                            id = "ok-goiß-radio",
                                            color = "primary",
                                            className = "mr-1",
                                            block = True,
                                            size = "lg"
                                        )
                                    ),
                                    width = 4
                                )
                            ],
                            justify = "center"
                        )
                    )
                )
            ],
            id = "goiß-count-radio-modal",
            centered = True,
            backdrop = "static"
        ),
        dbc.Modal(
            children = [
                dbc.ModalHeader(
                    "📤 Download current Game Data 📥",
                ),
                dbc.ModalBody(
                    "Click here to downlad a json file of your current game data and continue your game the next time!"
                ),
                dbc.ModalBody(
                    html.Div(
                        dbc.Spinner(
                            html.A(
                                dbc.Button(
                                    "Download",
                                    id = "download-button",
                                    color = "primary",
                                    className = "mr-1",
                                    block = True,
                                    size = "lg"
                                ),
                                href = "/download/",
                                id = "download-href"
                            )
                        ),
                        style = {"text-align": "center"}
                    )
                )
            ],
            id = "download-modal",
            centered = True
        ),
        modal(
            "invalid-json-modal",
            "🙁 Invalid Game Data 🙁",
            html.Div(
                children = [
                    dbc.Button(
                        "Ok",
                        id = "confirm-invalid-json",
                        color = "primary",
                        size = "lg",
                        className = "mr-1"
                    )
                ],
                style = {"text-align": "center"}
            )
        ),
    ]
)

########### Callbacks
@app.callback(
    [Output("content", "children"),
    Output("start-game-modal", "is_open"),
    Output("new-game-modal", "is_open"),
    Output("handout-mistake-radio-modal", "is_open"),
    Output("handout-mistake-radio", "options"),
    Output("beer-count-radio-modal", "is_open"),
    Output("beer-count-radio", "options"),
    Output("goiß-count-radio-modal", "is_open"),
    Output("goiß-count-radio", "options"),
    Output("add-player-button", "n_clicks"),
    Output("start-game-button", "n_clicks"),
    Output("new-game-button", "n_clicks"),
    Output("confirm-new-game-button", "n_clicks"),
    Output("delice-new-game-button", "n_clicks"),
    Output("confirm-selection-button", "n_clicks"),
    Output("handout-mistake-button", "n_clicks"),
    Output("cancel-handout-radio", "n_clicks"),
    Output("ok-handout-radio", "n_clicks"),
    Output("beer-count-button", "n_clicks"),
    Output("cancel-beer-radio", "n_clicks"),
    Output("ok-beer-radio", "n_clicks"),
    Output("goiß-count-button", "n_clicks"),
    Output("cancel-goiß-radio", "n_clicks"),
    Output("ok-goiß-radio", "n_clicks"),
    Output("confirm-load-game", "n_clicks")],
    [Input("add-player-button", "n_clicks"),
    Input("start-game-button", "n_clicks"),
    Input("new-game-button", "n_clicks"),
    Input("confirm-new-game-button", "n_clicks"),
    Input("delice-new-game-button", "n_clicks"),
    Input("confirm-selection-button", "n_clicks"),
    Input("handout-mistake-button", "n_clicks"),
    Input("cancel-handout-radio", "n_clicks"),
    Input("ok-handout-radio", "n_clicks"),
    Input("handout-mistakes-checkbox", "checked"),
    Input("beer-count-button", "n_clicks"),
    Input("cancel-beer-radio", "n_clicks"),
    Input("ok-beer-radio", "n_clicks"),
    Input("beer-count-checkbox", "checked"),
    Input("goiß-count-button", "n_clicks"),
    Input("cancel-goiß-radio", "n_clicks"),
    Input("ok-goiß-radio", "n_clicks"),
    Input("goiß-count-checkbox", "checked"),
    Input("confirm-load-game", "n_clicks")],
    [State("content", "children"),
    State("current-selection", "children"),
    State("table-dict", "children"),
    State("game-history", "children"),
    State("points-development", "children"),
    State("handout-mistake-radio", "value"),
    State("handout-mistakes", "children"),
    State("beer-count-radio", "value"),
    State("beer-count", "children"),
    State("goiß-count-radio", "value"),
    State("goiß-count", "children"),
    State("json-content", "children")]
)
def update_content(
    n_add_player, 
    n_start_game, 
    n_new_game, 
    n_confirm_new_game, 
    n_delice_new_game, 
    n_confirm_selection, 
    n_handout_mistake, 
    n_cancel_handout_mistake, 
    n_ok_handout_mistake,
    handout_mistakes_check,
    n_beer_count, 
    n_cancel_beer_count,
    n_ok_beer_count,
    beer_count_check,
    n_goiß_count, 
    n_cancel_goiß_count, 
    n_ok_goiß_count,
    goiß_count_check,
    n_load_game,
    content, 
    selection, 
    table_dict, 
    game_history, 
    points_development, 
    handout_mistake_selection, 
    handout_mistakes,
    beer_count_selection, 
    beer_count,
    goiß_count_selection, 
    goiß_count,
    upload_json_content
):
    def return_list(
        content, 
        start_game_modal = False, 
        new_game_modal = False, 
        handout_mistake_modal = False, 
        handout_mistake_options = [], 
        beer_count_modal = False, 
        beer_count_options = [],
        goiß_count_modal = False, 
        goiß_count_options = []
    ):
        return [
            content, 
            start_game_modal, 
            new_game_modal, 
            handout_mistake_modal, 
            handout_mistake_options, 
            beer_count_modal, 
            beer_count_options,
            goiß_count_modal, 
            goiß_count_options,  
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
    
    selection = json.loads(selection.replace("'", "\""))
    table_dict = json.loads(table_dict.replace("'", "\""))
    game_history = json.loads(game_history.replace("'", "\""))
    points_development = json.loads(points_development.replace("'", "\""))
    handout_mistakes = json.loads(handout_mistakes.replace("'", "\""))
    beer_count = json.loads(beer_count.replace("'", "\""))
    goiß_count = json.loads(goiß_count.replace("'", "\""))
    
    names = list()
    for element in content:
        try:
            if element["type"] == "Input":
                names.append(element["props"]["value"])
        except TypeError:
            pass
            
    if n_add_player:
        names.append(None)
        return return_list(names_content(names))
        
    if n_start_game:
        names = [n for n in names if n]
        if len(names) >= 2 and len(names) == len(list(set(names))):
            ranks = get_ranks(names)
    
            table_dict = {"Ranks": [*ranks, "Points"]}
            for name in names:
                table_dict[name] = [0 for i in range(len(ranks)+1)]
            
            game_history = {"x": list()}
            for name in names:
                game_history[name] = list()
                
            points_development = {"x": [0]}
            for name in names:
                points_development[name] = [0]
            
            if handout_mistakes_check:
                handout_mistakes = {}
                for name in names:
                    handout_mistakes[name] = 0
            else:
                handout_mistakes = None

            if beer_count_check:
                beer_count = {}
                for name in names:
                    beer_count[name] = 0
            else:
                beer_count = None
            
            if goiß_count_check:
                goiß_count = {}
                for name in names:
                    goiß_count[name] = 0
            else:
                goiß_count = None
            
            return return_list(game_content(table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count))
        else:
            return return_list(content, start_game_modal = True)
    
    if n_load_game:
        upload_json_content = json.loads(upload_json_content.replace("'", "\""))
        return return_list(
            game_content(
                upload_json_content["table-dict"],
                upload_json_content["game-history"],
                upload_json_content["points-development"],
                upload_json_content["handout-mistakes"],
                upload_json_content["beer-count"],
                upload_json_content["goiß-count"]
            )
        )
    
    if n_new_game:
        return return_list(content, new_game_modal = True)
    
    if n_confirm_new_game:
        names = [None, None, None]
        return return_list(names_content(names))
    
    if n_confirm_selection:
        for name in selection:
            table_dict[name][selection[name]] += 1
            points = 0
            points_list = table_dict[name][:-1]
            for i, p in enumerate(points_list):
                points += p * (len(points_list)-i-1)
            try:
                points -= handout_mistakes[name]
                points += beer_count[name]
                points += 3*goiß_count[name]
            except KeyError:
                pass
            table_dict[name][-1] = points
            
            game_history[name].append(len(points_list) - selection[name] - 1)
            points_development[name].append(points)
        game_history["x"].append(len(game_history["x"])+1)
        points_development["x"].append(len(points_development["x"]))
        return return_list(game_content(table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count))
    
    if n_handout_mistake:
        handout_mistake_options = []
        for i, name in enumerate(list(table_dict.keys())[1:]):
            handout_mistake_options.append({"label": name, "value": i})
        return return_list(content, handout_mistake_modal = True, handout_mistake_options = handout_mistake_options)
    
    if n_ok_handout_mistake:
        for i, name in enumerate(handout_mistakes):
            if i == handout_mistake_selection:
                handout_mistakes[name] += 1
                table_dict[name][-1] -= 1
                points_development[name][-1] -= 1
        return return_list(game_content(table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count))

    if n_beer_count:
        beer_count_options = []
        for i, name in enumerate(list(table_dict.keys())[1:]):
            beer_count_options.append({"label": name, "value": i})
        return return_list(content, beer_count_modal = True, beer_count_options = beer_count_options)
    
    if n_ok_beer_count:
        for i, name in enumerate(beer_count):
            if i == beer_count_selection:
                beer_count[name] += 1
                table_dict[name][-1] += 1
                points_development[name][-1] += 1
        return return_list(game_content(table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count))
    
    if n_goiß_count:
        goiß_count_options = []
        for i, name in enumerate(list(table_dict.keys())[1:]):
            goiß_count_options.append({"label": name, "value": i})
        return return_list(content, goiß_count_modal = True, goiß_count_options = goiß_count_options)
    
    if n_ok_goiß_count:
        for i, name in enumerate(goiß_count):
            if i == goiß_count_selection:
                goiß_count[name] += 1
                table_dict[name][-1] += 3
                points_development[name][-1] += 3
        return return_list(game_content(table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count))
        
    return return_list(content)
    
@app.callback(
    [Output("points-radio-modal", "is_open"),
    Output("select-points-radio", "options"),
    Output("points-modal-header", "children"),
    Output("current-radio", "children"),
    Output("select-points-radio", "value"),
    Output("confirm-selection-modal", "is_open"),
    Output("current-selection", "children"),
    Output("add-results-button", "n_clicks"),
    Output("cancel-points-radio", "n_clicks"),
    Output("next-points-radio", "n_clicks")],
    [Input("add-results-button", "n_clicks"),
    Input("cancel-points-radio", "n_clicks"),
    Input("next-points-radio", "n_clicks")],
    [State("table-dict", "children"),
    State("select-points-radio", "value"),
    State("current-radio", "children"),
    State("points-modal-header", "children")]
)
def add_results(n_add_results, n_cancel_radio, n_next_radio, table_dict, radio_values, current, name):
    def return_list(points_modal = False, radio_points = [], name = "name", current = "{}", value = 0, confirm_modal = False, selection = "{}"):
        return [points_modal, radio_points, name, current, value, confirm_modal, selection, 0, 0, 0]
    
    try:
        table_dict = json.loads(table_dict.replace("'","\""))
        options = list()
        for i, rank in enumerate(table_dict["Ranks"][:-1]):
            options.append({"label": rank, "value": i})
            names = list(table_dict.keys())[1:]
    except (KeyError, AttributeError):
        table_dict = dict()
        names = [""]
    
    #print(json.dumps(table_dict, indent = 4))
    #print(radio_values)
    #print(current)
    #print(name)
    
    current = json.loads(current.replace("'","\""))
    value = 0
    all_selected = False
    
    try:
        new_name = names[names.index(name)+1]
    except ValueError:
        new_name = names[0]
    except IndexError:
        current[name] = radio_values
        all_selected = True
    
        
    if n_add_results:
        return return_list(points_modal = True, radio_points = options, name = new_name)
    
    if n_cancel_radio:
        return return_list()
    
    if n_next_radio:
        if all_selected:
            return return_list(confirm_modal = True, selection = str(current))
        else:
            current[name] = radio_values
            for val in current.values():
                options[val]["disabled"] = True
            while True:
                if value in current.values():
                    value += 1
                else:
                    break
            return return_list(points_modal = True, radio_points = options, name = new_name, current = str(current), value = value)
        
    return return_list()
    
@app.callback(
    [Output("support-me-modal", "is_open"),
    Output("support-me-button", "n_clicks"),
    Output("paypal-button", "n_clicks")],
    [Input("support-me-button", "n_clicks"),
    Input("paypal-button", "n_clicks")]
)
def open_support_me_modal(n_support_me, n_paypal):
    def return_list(modal = False):
        return [modal, 0, 0]
    
    if n_support_me:
        return return_list(modal = True)
     
    return return_list()

@app.callback(
    [Output("download-modal", "is_open"),
     Output("download-href", "href"),
     Output("save-game-button", "n_clicks"),
     Output("download-button", "n_clicks")],
    [Input("save-game-button", "n_clicks"),
     Input("download-button", "n_clicks")],
    [State("table-dict", "children"),
    State("game-history", "children"),
    State("points-development", "children"),
    State("handout-mistakes", "children"),
    State("beer-count", "children"),
    State("goiß-count", "children")]
)
def open_download_modal(n_save_game, n_download, table_dict, game_history, points_development, handout_mistakes, beer_count, goiß_count):
    def return_list(modal = False, href = "/download/"):
        return[modal, href, 0, 0]
    
    if n_save_game:
        download_json = {
            "table-dict": table_dict,
            "game-history": game_history,
            "points-development": points_development,
            "handout-mistakes": handout_mistakes,
            "beer-count": beer_count,
            "goiß-count": goiß_count
        }
        timestamp = datetime.datetime.now().strftime(timestamp_format)
        file = f"{timestamp}_game_data.json"

        for key in download_json:
            download_json[key] = json.loads(download_json[key].replace("'", "\""))

        with open(f"./{file}", "w") as wd:
            wd.write(json.dumps(download_json, indent = 4))
        return return_list(modal = True, href = f"/download/{file}")

    if n_download:
        time.sleep(1)
        for file in os.listdir():
            if file.endswith("_game_data.json"):
                try:
                    os.remove(file)
                except PermissionError:
                    pass
        return return_list()
    
    return return_list()

@app.callback(
    [Output("confirm-upload-modal", "is_open"),
     Output("invalid-json-modal", "is_open"),
     Output("file-name", "children"),
     Output("json-content", "children"),
     Output("confirm-invalid-json", "n_clicks"),
     Output("upload-button", "children")],
    [Input("upload-json", "filename"),
     Input("confirm-invalid-json", "n_clicks")],
    [State("upload-json", "contents")]
)
def upload_game(filename, n_confirm_invalid, content):
    def return_list(start_game_modal = False, invalid_json_modal = False, filename = None, json_content = dict()):
        return [start_game_modal, invalid_json_modal, filename, json_content, 0, upload_button()]
    
    if n_confirm_invalid:
        return return_list()
    
    if filename:
        try:
            content_type, content_string = content.split(",")
            content_string = base64.b64decode(content_string).decode("utf-8")
            content_dict = json.loads(content_string)
            game_content(
                content_dict["table-dict"],
                content_dict["game-history"],
                content_dict["points-development"],
                content_dict["handout-mistakes"],
                content_dict["beer-count"],
                content_dict["goiß-count"]
            )
            return return_list(start_game_modal = True, filename= filename, json_content = content_string)
        
        except Exception as e:
            return return_list(invalid_json_modal = True)
    
    raise PreventUpdate

#navbar collapse callback
@app.callback(
    [Output("nav-collapse", "is_open")],
    [Input("nav-toggler", "n_clicks")],
    [State("nav-collapse", "is_open")]
)
def toggle_navbar_collapse(n_clicks, is_open):
    if n_clicks:
        return [not is_open]
    return [is_open]

########### Run the app
if __name__ == '__main__':
    #application.run(debug=True)
    app.run_server(debug = True, host = "0.0.0.0", port = 8050)