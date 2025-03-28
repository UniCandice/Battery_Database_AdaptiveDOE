# app.py
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine, text

# Initialize app and database connection
app = Dash(__name__)
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/Battery_1')

app.layout = html.Div([
    html.H1("Battery Materials Interactive Dashboard"),
    
    # Data visualization section
    dcc.Graph(id='materials-plot'),
    
    # Parameter controls
    html.Div([
        html.Label("Select X-axis:"),
        dcc.Dropdown(
            id='x-axis',
            options=[{'label': col, 'value': col} 
                    for col in ['lfp_content', 'conductive_content', 'binder_content']],
            value='lfp_content'
        ),
        
        html.Label("Select Y-axis:"),
        dcc.Dropdown(
            id='y-axis',
            options=[{'label': col, 'value': col} 
                    for col in ['resistance_016_mpa', 'adhesion_force', 'viscosity_10s1']],
            value='resistance_016_mpa'
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    # Data editing section
    html.Div([
        html.H3("Edit Database Values"),
        html.Label("Select Formulation:"),
        dcc.Dropdown(id='formulation-dropdown'),
        
        html.Label("Parameter to Edit:"),
        dcc.Dropdown(id='parameter-dropdown'),
        
        html.Label("New Value:"),
        dcc.Input(id='new-value', type='number'),
        
        html.Button('Update Database', id='update-button'),
        html.Div(id='update-status')
    ], style={'margin-top': '50px'})
])

# Populate formulation dropdown
@app.callback(
    Output('formulation-dropdown', 'options'),
    Input('x-axis', 'value')
)
def update_formulation_dropdown(_):
    with engine.connect() as conn:
        formulations = pd.read_sql("SELECT formulation_name FROM Adaptive_DoE", conn)
    return [{'label': name, 'value': name} for name in formulations['formulation_name']]

# Update parameter dropdown based on selection
@app.callback(
    Output('parameter-dropdown', 'options'),
    Input('formulation-dropdown', 'value')
)
def update_parameter_dropdown(_):
    return [{'label': col, 'value': col} 
           for col in ['lfp_content', 'conductive_content', 'resistance_016_mpa']]

# Main plot update
@app.callback(
    Output('materials-plot', 'figure'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value')
)
def update_graph(x_col, y_col):
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM Adaptive_DoE", conn)
    return px.scatter(df, x=x_col, y=y_col, color='lfp_type', hover_name='formulation_name')

# Callback to update database
@app.callback(
    Output('update-status', 'children'),
    Input('update-button', 'n_clicks'),
    State('formulation-dropdown', 'value'),
    State('parameter-dropdown', 'value'),
    State('new-value', 'value'),
    prevent_initial_call=True
)
def update_database(n_clicks, formulation, parameter, new_value):
    if not all([formulation, parameter, new_value]):
        return "Please complete all fields before updating"
    
    try:
        with engine.begin() as conn:
            # Get current value for confirmation message
            current = pd.read_sql(
                f"SELECT {parameter} FROM Adaptive_DoE WHERE formulation_name = %s",
                conn, 
                params=(formulation,)
            ).iloc[0,0]
            
            # Execute update with parameterized query
            conn.execute(
                text(f"UPDATE Adaptive_DoE SET {parameter} = :val WHERE formulation_name = :form"),
                {"val": float(new_value), "form": formulation}
            )
            
        # Return success message with before/after values
        return f"Success! {formulation}: {parameter} changed from {current} to {new_value}"
    
    except ValueError:
        return "Error: Please enter a valid number"
    except Exception as e:
        return f"Database error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)