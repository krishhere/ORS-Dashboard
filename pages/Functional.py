import dash
import cx_Oracle
import pandas as pd
dash.register_page(__name__)
from dash import Dash, dcc, html, Input, Output,State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import os
from app import app

host = 'udmnlorrrde3e01.amer.dell.com'
port = '1521'
service_name = 'EFDI.dit.emea.dell.com'

dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

username = 'UFD_ORS'
password = 'Di$closeNot'
databaseName = "DITAPJEMEA"
engine = cx_Oracle.connect(username, password, dsn)
# engine = sqlalchemy.create_engine("oracle+cx_oracle://UFD_ORS:Di$closeNot@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=udmnlorrrde3e01.amer.dell.com)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=EFDI.dit.emea.dell.com)))")

ge1 = 'GE1'
ge2= 'GE2'
ge4='GE4'
profiles = 'PROFILES'
release_target = 'RELEASE_TARGET'
testcase_id = 'TESTCASE_ID'

orders_sql = "SELECT * FROM UFD_ORS.Automation_Status where TEST_TYPE='Functional'"
dfFunctional = pd.read_sql_query(orders_sql, engine)

totalFunctionalCount = dfFunctional.shape[0]
dfProfileNames = list(dfFunctional[profiles].value_counts().keys())
Releases = sorted(dfFunctional.RELEASE_TARGET.unique(),reverse=True)
ReleaseLists =[{"label": x, "value": x} for x in Releases]
release = Releases[0]

path = f"./assets/Functional/"
for files in os.listdir(path):
    file = path + files
    if os.path.isfile(file):
        os.remove(file)
    
def GetHtmlReport(TCid,env):
    filename = f"./assets/Functional/{TCid}.html"
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()
    sql = "SELECT {0}_reports FROM UFD_ORS.Automation_Status where TEST_TYPE='Functional' and TESTCASE_ID='{1}'".format(env,TCid)
    cursor.execute(sql)
    row = cursor.fetchone()
    imageBlob = row[0]
    imageFile = open(filename,'wb')
    if imageBlob != None:
        imageFile.write(imageBlob.read())
        imageFile.close()
    cursor.close()
    connection.close()

def selectEnv(TCid):
    dfTemp = dfFunctional.loc[dfFunctional[testcase_id]==TCid]
    for strEnv in [ge1,ge2,ge4]:
        if(dfTemp[strEnv].to_string().find('None')==-1):
            return strEnv
   
layout = html.Div([
    html.Center(html.Span("Functional - Dashboard",className="text-bg-primary btn-lg px-4",style={'padding':'5px','border-radius':'5px'})),
    html.Hr(),
    html.Div([
        html.Div(style={'width':'200px'},children=[
            dcc.Dropdown(id="dropdown",options=ReleaseLists, value=release, clearable=False,style={'color':'#000'}),
        ],className="col-lg-4"),
        html.Div(html.Center(id='output'),className="col-lg-8")
    ],className="row"),
    html.Div([
        dcc.Graph(id="bar-chart",config={"displaylogo": False,'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d','lasso2d', 'zoomIn2d', 'zoomOut2d','autoScale2d']}),
        html.Hr()],className="col-lg-12"),
    html.Div([
    html.Div([
    dcc.Dropdown(style={'color':'#000','float':'left','width':'300px'},
        id='searchInput',options=sorted(dfFunctional['TESTCASE_ID'].to_list(),key=int,reverse=True),
        searchable=True,
        placeholder="Enter test case id"),
    html.Button('Search', id='searchButton',className="text-bg-primary btn-lg px-4",style={"border-color":"transparent",'border-radius':'4px','height':'36px'})
    ],className="col-lg-5"),
    html.Div([
        html.Span(id="testcaseStatus"),
        html.Span(id='searchOutput')
    ],className="col-lg-7")],className="row")
],className="col-lg-12 mx-auto p-4")

@callback(Output('searchOutput', 'children'),[Input('searchButton', 'n_clicks')],[State('searchInput', 'value')])
def search(n_clicks, search_term):
    if n_clicks is not None:
        if len(search_term)>5:
            ranEnv = selectEnv(search_term)
            GetHtmlReport(search_term,ranEnv)
            return [html.A('Report('+search_term+')', href=f'./assets/Functional/{search_term}.html',target='_blank', style={'font-size':'14px','color':'#11adf7','padding':'10px','font-weight':'bold'})]
        else:
            return 'No testcase exists'

@callback(Output('testcaseStatus', 'children'),[Input('searchButton', 'n_clicks')],[State('searchInput', 'value')])
def search(n_clicks, search_term):
    if n_clicks is not None:
        if len(search_term)>5:
            ranEnv = selectEnv(search_term)
            TCstatus = list(dfFunctional.loc[dfFunctional[testcase_id]==search_term][ranEnv].value_counts().keys())[0]
            return f'Test case({search_term}) status - {TCstatus}'
        else:
            return ''

@callback(Output("bar-chart", "figure"),[Input("dropdown", "value")])
def update_bar_chart(release):
    releaseValues = dfFunctional[release_target] == release
    value_counts = dfFunctional[releaseValues][profiles].value_counts().reset_index()
    value_counts.columns = ['Profiles', 'Testcase_Count']
    fig = px.bar(value_counts, x='Profiles', y='Testcase_Count',labels={'x': 'Profiles', 'y': 'Test case Count'}, text='Testcase_Count', title='Release wise programs status')
    # fig.update_traces(textposition='outside')
    fig.update_layout({'plot_bgcolor':'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'},font_color='white',xaxis_showgrid=False, yaxis_showgrid=False)
    return fig

@callback(Output('output', 'children'),[Input('dropdown', 'value')])
def update_output(release):
    releaseTestCaseCount = (dfFunctional[release_target] == release).sum()
    return f'Total {releaseTestCaseCount} test cases are automated in {release}.'