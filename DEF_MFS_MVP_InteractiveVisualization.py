try:
    # pip install --upgrade google-api-python-client
    # pip install --upgrade google-cloud-storage
    from google.cloud import storage
    import os
    import sys
    import glob
    import pandas as pd
    import io
    from io import BytesIO
    import dash
    from dash import html
    from dash import dcc
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import plotly.graph_objects as go
    import urllib.request, json
    from dash.dependencies import Input, Output
    from datetime import date, timedelta
    import yfinance as yf
except Exception as e:
    print("Error : {} ".format(e))

storage_client = storage.Client.from_service_account_json(
    'C:\\Users\\surji\\Downloads\\College\\Sem-4\\Stock_Prediction\\DEF-MFS-MVP-Configuration.json')

bucket = storage_client.get_bucket('bucket_stock')

df_list = []

stylesheet = 'C:/Users/Raj/PycharmProjects/WIL/DEF-MFS-MVP/style.css'
external_stylesheets = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, external_stylesheets],
                assets_external_path=stylesheet)

app.config.suppress_callback_exceptions=True

start = date.today() - timedelta(days=31)
now = date.today()

symbols = ['TSLA', 'F']
stock=[]
for symbol in symbols:
    df_stock = yf.download(symbol, group_by="Ticker", start=start, end=now)
    df_stock['Ticker'] = symbol
    stock.append(pd.DataFrame(df_stock))

df=pd.concat(stock)
df_tesla=(df[df['Ticker'] == 'TSLA'])
df_tesla=df_tesla.reset_index()
df_ford=(df[df['Ticker'] == 'F'])
df_ford=df_ford.reset_index()

class IntVisual:

    def read_data(self):
        # Getting all files from GCP bucket
        filename = [filename.name for filename in list(bucket.list_blobs(prefix=''))]

        # Reading a CSV file directly from GCP bucket
        for file in filename:
            df_list.append(pd.read_csv(
                io.BytesIO(
                    bucket.blob(blob_name=file).download_as_string()
                ),
                encoding='UTF-8',
                sep=',',
                index_col=None
            ))

    def dash_board(self):

        concatenated_df = pd.concat(df_list, ignore_index=True)

        # styling the sidebar
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            "box-shadow": "1px 5px 10px rgba(1, 1, 1, 1)",

        }

        # padding for the page content
        CONTENT_STYLE = {
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
            "color": "grey",
        }

        whole_page = {
            "background-color": "#192444"
        }

        sidebar = html.Div(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.CardImg(src="assets/stock_logo.png", style={"padding-left": "40px", 'width':'180px', 'height':'180px'})
                            )
                        ],

                    )
                ),
                html.Hr(style={"color": "grey"}),

                dbc.Nav(
                    [
                        # dbc.NavLink(" Dashboard", href="/", active="exact", className="fa fa-dashboard"),
                        dbc.NavLink(" Comparison", href="/comparison", active="exact", className="fa fa-exchange"),
                        html.Br(),
                        dbc.NavLink(" Forecast", href="/forecasting", active="exact", className="fa fa-line-chart"),
                        html.Br(),
                        dcc.Dropdown(id='demo-dropdown',
                                     options=[
                                         {'label': 'TESLA', 'value': 'Tesla'},
                                         {'label': 'FORD', 'value': 'Ford'},
                                     ],
                                     placeholder='Company',
                                     value='Tesla'
                        ),
                    ],
                    vertical=True,
                    pills=True,
                    className="mr-2"
                ),
            ],
            style=SIDEBAR_STYLE,
        )

        content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)


        app.layout = html.Div([
            dcc.Location(id="url"),
            sidebar,
            content,
            html.Div(id='dd-output-container1')
        ],
            style=whole_page
        )

    @app.callback(
        Output("page-content", "children"),
        Input("demo-dropdown", "value"),
        Input("url", "pathname")
    )
    def render_page_content(value, pathname):

        concatenated_df = pd.concat(df_list, ignore_index=True)

        if value == "Tesla":
            return [
                html.H4('Dashboard',
                        style={'textAlign': 'center'}),
                dbc.Container([
                    dbc.Row([
                        html.Div([
                            html.Div([
                                dbc.CardImg(src="assets/tesla.png", top=True, style={"width": "6rem"}),

                                html.H6(children=now.strftime(" %Y-%m-%d"),
                                        className="fa fa-calendar",
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        )], className='col s12 m6',
                                           style= {
                                                'border-radius': 5,
                                                'background-color': '#1f2c56',
                                                'margin': 15,
                                                'position': 'relative',
                                                'box-shadow': '2px 2px 2px #1f2c56',
                                                'textAlign': 'center',
                                                'padding': 5,
                                           }
                            ),

                            html.Div([
                                html.H6(children='Open',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_tesla['Open'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': 'orange',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_tesla['Open'].iloc[-1] - df_tesla['Open'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_tesla['Open'].iloc[-1] - df_tesla['Open'].iloc[-2]) /
                                                           df_tesla['Open'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': 'orange',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                            html.Div([
                                html.H6(children='Close',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_tesla['Close'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': '#e55467',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_tesla['Close'].iloc[-1] - df_tesla['Close'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_tesla['Close'].iloc[-1] - df_tesla['Close'].iloc[-2]) /
                                                           df_tesla['Close'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': '#e55467',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )],className='col s12 m6',
                                           style={
                                            'border-radius': 5,
                                            'background-color': '#1f2c56',
                                            'margin': 15,
                                            'padding': 5,
                                            'position': 'relative',
                                            'box-shadow': '2px 2px 2px #1f2c56',
                                           }
                            ),

                            html.Div([
                                html.H6(children='High',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_tesla['High'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': 'green',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_tesla['High'].iloc[-1] - df_tesla['High'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_tesla['High'].iloc[-1] - df_tesla['High'].iloc[-2]) /
                                                           df_tesla['High'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': 'green',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                            html.Div([
                                html.H6(children='Low',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_tesla['Low'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': 'red',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_tesla['Low'].iloc[-1] - df_tesla['Low'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_tesla['Low'].iloc[-1] - df_tesla['Low'].iloc[-2]) /
                                                           df_tesla['Low'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': 'red',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s8 m4',
                                           style={
                                                    'border-radius': 5,
                                                    'background-color': '#1f2c56',
                                                    'margin': 15,
                                                    'padding': 5,
                                                    'position': 'relative',
                                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                        ],className='row',
                       ),
                    ]),

                    dbc.Row([
                        html.Div([

                            html.Div([
                                    html.H6(children='Stocks Volume',
                                            style={
                                                'textAlign': 'center',
                                                'color': 'white'}
                                    ),

                                    html.Div([
                                        dcc.Graph(figure={
                                                      'data':[{ 'labels':['TESLA', 'FORD', 'APPLE', 'GOOGLE'],
                                                                'values': [df_tesla['Volume'].iloc[-1],
                                                                          df_ford['Volume'].iloc[-1]],
                                                               'type': 'pie',
                                                               'hole': .4,
                                                               'hoverinfo': "label+percent+name",
                                                               'rotation':45,
                                                               }],
                                                      'layout': {
                                                                  'plot_bgcolor': '#1f2c56',
                                                                  'paper_bgcolor': '#1f2c56',
                                                                  'font': {
                                                                          'color': 'white'
                                                                  },
                                                                }
                                                  },)
                                    ])

                            ],className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 5,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                },
                            ),

                            html.Div([
                                html.H6(children='Stocks Price One Month',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),

                                html.Div([
                                    dcc.Graph(
                                              figure={
                                                      'data':[{'x': df_tesla['Date'],
                                                               'y':df_tesla['Open'],
                                                               'type': 'bar',
                                                               'marker': dict(color='orange'),
                                                               }],
                                                      'layout': {
                                                                  'plot_bgcolor': '#1f2c56',
                                                                  'paper_bgcolor': '#1f2c56',
                                                                  'font': {
                                                                          'color': 'white'
                                                                  },

                                                                  'xaxis':dict(color='white',
                                                                               showline=True,
                                                                               showgrid=True,
                                                                               showticketlabels=True,
                                                                               linecolor='white',
                                                                               linewidth=2,
                                                                               ),

                                                                  'yaxis': dict(color='white',
                                                                                showline=True,
                                                                                showgrid=True,
                                                                                showticketlabels=True,
                                                                                linecolor='white',
                                                                                linewidth=2,
                                                                                )
                                                                }
                                                     }
                                              )
                                ]),

                            ],className='col s16 m12',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 0,
                                    'padding': 0,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                    'max-width': '70%',
                                }
                            ),

                        ],className='row',
                        )
                    ]),
                ])
            ]



        elif value == "Ford":
            return [
                html.H4('Dashboard',
                        style={'textAlign': 'center'}),
                dbc.Container([
                    dbc.Row([
                        html.Div([
                            html.Div([
                                dbc.CardImg(src="assets/ford.png", top=True, style={"width": "6rem"}),

                                html.H6(children=now.strftime(" %Y-%m-%d"),
                                        className="fa fa-calendar",
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        )], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                    'textAlign': 'center',
                                    'padding': 5,
                                }
                            ),

                            html.Div([
                                html.H6(children='Open',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_ford['Open'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': 'orange',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_ford['Open'].iloc[-1] - df_ford['Open'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_ford['Open'].iloc[-1] - df_ford['Open'].iloc[-2]) /
                                                           df_ford['Open'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': 'orange',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                            html.Div([
                                html.H6(children='Close',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_ford['Close'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': '#e55467',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_ford['Close'].iloc[-1] - df_ford['Close'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_ford['Close'].iloc[-1] - df_ford['Close'].iloc[-2]) /
                                                           df_ford['Close'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': '#e55467',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                            html.Div([
                                html.H6(children='High',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_ford['High'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': 'green',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_ford['High'].iloc[-1] - df_ford['High'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_ford['High'].iloc[-1] - df_ford['High'].iloc[-2]) /
                                                           df_ford['High'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': 'green',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                            html.Div([
                                html.H6(children='Low',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.P(f"{df_ford['Low'].iloc[-1]:,.2f}",
                                       style={
                                           'textAlign': 'center',
                                           'color': 'red',
                                           'fontsize': 40}
                                       ),
                                html.P('new: ' + f"{df_ford['Low'].iloc[-1] - df_ford['Low'].iloc[-2]:,.2f} "
                                       + ' (' + str(round(((df_ford['Low'].iloc[-1] - df_ford['Low'].iloc[-2]) /
                                                           df_ford['Low'].iloc[-1]) * 100, 2)) + '%)',
                                       style={
                                           'textAlign': 'center',
                                           'color': 'red',
                                           'fontsize': 15,
                                           'margin-top': '-18px'}
                                       )], className='col s8 m4',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 15,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                }
                            ),

                        ], className='row',
                        ),
                    ]),

                    dbc.Row([
                        html.Div([

                            html.Div([
                                html.H6(children='Stocks Volume',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),

                                html.Div([
                                    dcc.Graph(figure={
                                        'data': [{'labels': ['TESLA', 'FORD', 'APPLE', 'GOOGLE'],
                                                  'values': [df_tesla['Volume'].iloc[-1],
                                                             df_ford['Volume'].iloc[-1]],
                                                  'type': 'pie',
                                                  'hole': .4,
                                                  'hoverinfo': "label+percent+name",
                                                  'rotation': 45,
                                                  }],
                                        'layout': {
                                            'plot_bgcolor': '#1f2c56',
                                            'paper_bgcolor': '#1f2c56',
                                            'font': {
                                                'color': 'white'
                                            },
                                        }
                                    }, )
                                ])

                            ], className='col s12 m6',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 5,
                                    'padding': 5,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                },
                            ),

                            html.Div([
                                html.H6(children='Stocks Price One Month',
                                        style={
                                            'textAlign': 'center',
                                            'color': 'white'}
                                        ),
                                html.Div([
                                    dcc.Graph(
                                        figure={
                                            'data': [{'x': df_ford['Date'],
                                                      'y': df_ford['Open'],
                                                      'type': 'bar',
                                                      'marker': dict(color='orange'),
                                                      }],
                                            'layout': {
                                                'plot_bgcolor': '#1f2c56',
                                                'paper_bgcolor': '#1f2c56',
                                                'font': {
                                                    'color': 'white'
                                                },

                                                'xaxis': dict(color='white',
                                                              showline=True,
                                                              showgrid=True,
                                                              showticketlabels=True,
                                                              linecolor='white',
                                                              linewidth=2,
                                                              ),

                                                'yaxis': dict(color='white',
                                                              showline=True,
                                                              showgrid=True,
                                                              showticketlabels=True,
                                                              linecolor='white',
                                                              linewidth=2,
                                                              )
                                            }
                                        }
                                    )
                                ]),

                            ], className='col s16 m12',
                                style={
                                    'border-radius': 5,
                                    'background-color': '#1f2c56',
                                    'margin': 0,
                                    'padding': 0,
                                    'position': 'relative',
                                    'box-shadow': '2px 2px 2px #1f2c56',
                                    'max-width': '70%',
                                }
                            ),

                        ], className='row',
                        )
                    ]),
                ])
            ]

        elif pathname == "/forecasting":
            return [html.H4('Forecasted Data',
                        style={'textAlign': 'center'}),

                dbc.Container([
                    dbc.Row([
                        dcc.Dropdown(['TESLA', 'FORD'], 'TESLA', id='demo-dropdown1'),

                    ])
                ])
            ]

    @app.callback(
        Output('dd-output-container1', 'children'),
        Input('demo-dropdown1', 'value')
    )

    def update_output(value):

        if value=='TESLA':
            return [html.H4('Tesla Data',
                                style={'textAlign': 'center'})]

        elif value=='FORD':
            return [html.H4('Ford Data',
                                style={'textAlign': 'center'})]


Visual = IntVisual()
Visual.read_data()
Visual.dash_board()

if __name__ == "__main__":
    app.run_server(debug=True)
