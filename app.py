from dash import Dash, html

app = Dash(__name__)
app.layout = html.Div("Hello Plotly Dash with Flask!")

if __name__ == '__main__':
    app.run_server(debug=True)

