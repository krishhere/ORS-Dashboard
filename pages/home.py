from dash import dcc, html
import dash

dash.register_page(__name__, path="/")

layout= html.Div([
    html.Div([
    html.H6("What is this dashboard about?"),
    html.Hr(),
    html.H6("Smoke",style={'text-decoration':'underline'}),
    html.Span(style={'color':'#dbdbdb'},
        children=[
        html.P(
          ["⦿ The daily execution status of all the smoke test cases are graphically represented in pie chart ",
            html.I(className='fa fa-pie-chart',style={'color':'#ff5200'}),"."]),
        html.P(["⦿ The test case status is set with green color of its left border ",
            html.Span("test case",style={'background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': 'green'}),
            ", If it is passed and red color ",
            html.Span("test case",style={'background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': 'red'}),
            ", If it is failed."]),
        html.P(["⦿ We can also see the detailed report ",
            html.I(className='fa fa-newspaper-o',style={'color':'#0400ff'})," of test caseses individually by clicking on it."])])
    ],className="row",style={'text-align':'center'}),
    html.Br(),
    html.Div([
    html.H6("Regression",style={'text-decoration':'underline'}),
    html.Span(style={'color':'#dbdbdb'},
        children=[
        html.P(
          ["⦿ The weekly execution status of all the regression test cases are graphically represented in pie chart ",
            html.I(className='fa fa-pie-chart',style={'color':'#00ffff'}),"."]),
        html.P(["⦿ The test case status is set with green color of its left border ",
            html.Span("test case",style={'background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': 'green'}),
            ", If it is passed and red color ",
            html.Span("test case",style={'background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': 'red'}),
            ", If it is failed."]),
        html.P(["⦿ We can also see the detailed report ",
            html.I(className='fa fa-newspaper-o',style={'color':'#ff5200'})," of test caseses individually by clicking on it."])])
    ],className="row",style={'text-align':'center'}),
    html.Br(),
    html.Div([
    html.H6("Functional",style={'text-decoration':'underline'}),
    html.Span(style={'color':'#dbdbdb'},
        children=[html.P(
          ["⦿ The functional test cases are categorized in order to release wise and graphically represented in bar graph ",
            html.I(className='fa fa-bar-chart',style={'color':'#ff006a'}),"."]),
        html.P(["⦿ We can see the individual test case detailed report ",
            html.I(className='fa fa-newspaper-o',style={'color':'#9dff00'})," by search with it's test case id."])])
    ],className="row",style={'text-align':'center'}),
],className="col-lg-12 mx-auto p-4")