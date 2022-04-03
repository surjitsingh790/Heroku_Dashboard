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
    # import dash_core_components as dcc
    # import dash_html_components as html
    from dash.dependencies import Input, Output

    import plotly.express as px
except Exception as e:
    print("Error : {} ".format(e))

storage_client = storage.Client.from_service_account_json(
             'C:\\Users\\Raj\\PycharmProjects\\Sensitive_Info\\DEF-MFS-MVP-Configuration.json')

bucket = storage_client.get_bucket('bucket_stock')
df_list = []


app = dash.Dash(__name__)

class IntVisual:

    def read_data(self):
        # Getting all files from GCP bucket
        filename = [filename.name for filename in list(bucket.list_blobs(prefix=''))]

        # Reading a CSV file directly from GCP bucket
        for file in filename:
            df_list.append(pd.read_csv(
                io.BytesIO(
                    bucket.blob(blob_name = file).download_as_string()
                    ),
                    encoding = 'UTF-8',
                    sep = ',',
                    index_col=None
                ))

    def dash_board(self):
        concatenated_df = pd.concat(df_list, ignore_index=True)
        concatenated_df["Date"] = pd.to_datetime(concatenated_df["Date"], format="%Y-%m-%d")

        # grouped = concatenated_df.groupby(concatenated_df.ticker)
        # df_new = grouped.get_group("F")
        # print(df_new)
        
        # ticker = list(set(concatenated_df.ticker.values))
        # for tick in ticker:
        #     tick = concatenated_df[concatenated_df.ticker.isin([tick])]

        
        fig =px.line(concatenated_df,
                     x="Date",
                     y="Volume",
                     title="Stock Prices between Jan-01-2021 to Dec-31-2021",
                     color_discrete_map={"Tesla":"red"}
                     )

        fig.update_layout(
            template="plotly_dark",
            font=dict(
                family="Verdana, sans-serif",
                size=18,
                color="white"
            )
        )

        app.layout = html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="header-area",
                    children=[
                        html.H1(
                            id="header-title",
                            children="Stocks Prices",

                        ),
                        html.P(
                            id="header-description",
                            children=("Stock Prices", html.Br(), "between 01-01-2021 and 12-31-2021"),
                        ),
                    ],
                ),
                html.Div(
                    id="menu-area",
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    className="menu-title",
                                    children="Stocks"
                                ),
                                dcc.Dropdown(
                                    id="ticker-filter",
                                    className="dropdown",
                                    options=[{"label": ticker, "value": ticker} for ticker in set(concatenated_df.ticker.values)],
                                    clearable=False,
                                    value= 'TSLA'
                                )
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    className="menu-title",
                                    children="Date Range"
                                ),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    min_date_allowed=concatenated_df.Date.min().date(),
                                    max_date_allowed=concatenated_df.Date.max().date(),
                                    start_date=concatenated_df.Date.min().date(),
                                    end_date=concatenated_df.Date.max().date()
                                  )
                            ]
                        )
                    ]
                ),
                html.Div(
                    id="graph-container",
                    children=dcc.Graph(
                        id="price-chart",
                        figure=fig,
                        config={"displayModeBar": False}
                    ),
                ),
            ]
        )



        @app.callback(
            Output("price-chart", "figure"),
            Input("ticker-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")
        )

        def update_chart(ticker, start_date, end_date):
            tick = concatenated_df[concatenated_df.ticker.isin([ticker])]
            filtered_data = tick.loc[(tick.Date >= start_date) & (tick.Date <= end_date)]
            # Create a plotly plot for use by dcc.Graph().
            fig = px.line(
                filtered_data,
                title="Stock Prices in 2021",
                x='Date',
                y="Open",
                color_discrete_map={
                    "TSLA": "#E5E4E2",
                    "GOOG": "gold",
                    "F": "silver",
                    "AAPL": "#CED0DD"
                }
            )

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Price (USD/oz)",
                font=dict(
                    family="Verdana, sans-serif",
                    size=18,
                    color="white"
                ),
            )

            return fig



Visual = IntVisual()
Visual.read_data()
Visual.dash_board()

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)

