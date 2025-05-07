# PyXLL-Dash

Plotly Dash Integration for Microsoft Excel.

See the [Plotly Dash Apps In Excel](https://www.pyxll.com/blog/plotly-dash-apps-in-excel).

# Installation

To install this package use:

    pip install pyxll-dash

The PyXLL Excel add-in must also be installed. See [PyXLL](https://www.pyxll.com).

# Usage

Once installed, the `pyxll.plot` function can be called with a dash app object.

Calling `pyxll.plot` with a dash app object from a PyXLL function will display the app in an embedded web control in Excel in the same way as other supported PyXLL plot types.

See [PyXLL Plotting](https://www.pyxll.com/docs/userguide/plotting/index.html) for details of
how to use the `pyxll.plot` function.

# Example

```python
from pyxll import xl_func, plot
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


@xl_func
def dash_app():

    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

    app = Dash()

    app.layout = [
        html.H1(children='Title of Dash App', style={'textAlign':'center'}),
        dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
        dcc.Graph(id='graph-content')
    ]

    @app.callback(
        Output('graph-content', 'figure'),
        Input('dropdown-selection', 'value')
    )
    def update_graph(value):
        dff = df[df.country==value]
        return px.line(dff, x='year', y='pop')

    # Show the dash app in Excel using PyXLL's plot function.
    # This requires the "pyxll-dash" package to be installed.
    plot(app)

    return app
```