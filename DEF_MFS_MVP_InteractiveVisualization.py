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
    import base64
    from datetime import date, timedelta
    import yfinance as yf
except Exception as e:
    print("Error : {} ".format(e))

storage_client = storage.Client.from_service_account_json(
    'C:\\Users\\surji\\Downloads\\College\\Sem-4\\Stock_Prediction\\DEF-MFS-MVP-Configuration.json')

bucket = storage_client.get_bucket('bucket_stock')


df_list = []

stylesheet = 'C:\\Users\\surji\\Downloads\\College\\Sem-4\\Stock_Prediction\\week-10\\DEF-MFS-MVP-IntVisual\\style.css'
external_stylesheets = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, external_stylesheets],
                assets_external_path=stylesheet)
server = app.server


image_filename = 'stock_logo.png'  # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

image_filename1 = 'tesla.png'  # replace with your own image
encoded_image1 = base64.b64encode(open(image_filename1, 'rb').read())

image_filename2 = 'ford_logo.jpg'  # replace with your own image
encoded_image2 = base64.b64encode(open(image_filename2, 'rb').read())

start = date.today() - timedelta(days=1000)
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
                                html.Img(src='data:image/jpg;base64,{}'.format(encoded_image.decode()), height="140px",
                                         style={"padding-left": "35px"}))
                        ],

                    )
                ),
                html.Hr(style={"color": "grey"}),

                dbc.Nav(
                    [
                        dcc.Dropdown(id='demo-dropdown',
                                     options=[
                                         {'label': 'TSLA', 'value': 'Tesla'},
                                         {'label': 'F', 'value': 'ford'},
                                     ],
                        ),
                        # dbc.NavLink(" Dashboard", href="/", active="exact", className="fa fa-dashboard"),
                        dbc.NavLink(" Analytics", href="/analytics", active="exact", className="fa fa-line-chart"),
                        dbc.NavLink(" Comparison", href="/comparison", active="exact", className="fa fa-exchange"),
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
            content
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
                                dbc.CardImg(
                                    src='data:image/png;base64,{}'.format(encoded_image1.decode()),
                                    top=True,
                                    style={"width": "6rem"}
                                    ),
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



        elif value == "ford":
            return [
                html.H4('Dashboard',
                        style={'textAlign': 'center'}),
                dbc.Container([
                    dbc.Row([
                        html.Div([
                            html.Div([
                                dbc.CardImg(
                                    src='data:image/png;base64,{}'.format(encoded_image2.decode()),
                                    top=True,
                                    style={"width": "6rem"}
                                ),
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
                                            'data': [{'x': df_tesla['Date'],
                                                      'y': df_tesla['Open'],
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

        elif pathname == "/analytics":
            return [html.H4('Dashboard',
                        style={'textAlign': 'center'})]


    # Indicator Graph

    # @app.callback(
    #     Output("price-chart", "figure"),
    #     Input("ticker-filter", "value"),
    #     Input("date-range", "start_date"),
    #     Input("date-range", "end_date")
    # )
    # def update_chart(pathname,ticker, start_date, end_date):
    #     tick = df[df.Ticker.isin([ticker])]
    #     filtered_data = tick.loc[(tick.Date >= start_date) & (tick.Date <= end_date)]
    #
    #     # Create a plotly plot for use by dcc.Graph().
    #     fig = px.line(
    #         filtered_data,
    #         title="Stock Prices in 2021",
    #         x='Date',
    #         y="Open",
    #         color_discrete_map={
    #             "TSLA": "#E5E4E2",
    #             "GOOG": "gold",
    #             "F": "silver",
    #             "AAPL": "#CED0DD"
    #         }
    #     )
    #
    #     fig.update_layout(
    #         template="plotly_dark",
    #         xaxis_title="Date",
    #         yaxis_title="Price (USD/oz)",
    #         font=dict(
    #             family="Verdana, sans-serif",
    #             size=18,
    #             color="white"
    #         ),
    #     )
    #
    #     return fig

    # def update_graph(ticker-filter):

        # stock_data = df.groupby(['Date'])[['Open', 'Close', 'High', 'Low']].sum().reset_index()
        #
        # value_open = stock_data[stock_data['Open']== s_companies]['Open'].iloc[-1] - stock_data[stock_data['Open']== s_companies]['Open'].iloc[-2]
        # delta_open = stock_data[stock_data['Open']== s_companies]['Open'].iloc[-2] - stock_data[stock_data['Open']== s_companies]['Open'].iloc[-3]



Visual = IntVisual()
Visual.read_data()
Visual.dash_board()

if __name__ == "__main__":
    app.run_server(debug=True)
