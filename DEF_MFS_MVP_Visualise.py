from DEF_MFS_MVP_Storage import df_list
import pandas as pd
import plotly.express as px

class graphs:
    def open_vs_time(self, data):
        fig = px.line(data, x="Date", y="Open", title='Stock Open Prices')
        fig.show()

    def capitalism(self, data):
        # Market Capitalisation
        data['MarktCap'] = data['Open'] * data['Volume']
        fig = px.line(data, x="Date", y="MarktCap", title='Capitalism')
        fig.show()

    def volume_vs_time(self, data):
        fig = px.line(data, x="Date", y="Volume", title='Stock Volume')
        fig.show()

    def rolling_50(self, data):
        data['MA50'] = data['Open'].rolling(50).mean()
        fig = px.line(data, x="Date", y="MA50", title='Average of 50 days')
        fig.add_scatter(x=data['Date'], y=data['Open'])
        fig.show()

data = pd.concat(df_list)
graph = graphs()
graph.open_vs_time(data)
graph.volume_vs_time(data)
graph.capitalism(data)
graph.rolling_50(data)