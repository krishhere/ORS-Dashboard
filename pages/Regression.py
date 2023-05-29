import dash
import cx_Oracle
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import time
dash.register_page(__name__)
from dash import Dash, dcc, html, Input, Output, State,callback
import dash_bootstrap_components as dbc
import plotly.express as px
import os
import threading

username = 'UFD_ORS'
password = 'Di$closeNot'
databaseName = "DITAPJEMEA"
try:
    engine = sqlalchemy.create_engine("oracle+cx_oracle://UFD_ORS:Di$closeNot@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=udmnlorrrde3e01.amer.dell.com)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=EFDI.dit.emea.dell.com)))")
    orders_sql = "SELECT * FROM UFD_ORS.Automation_Status where TEST_TYPE='Regression'"
    dfRegression = pd.read_sql_query(orders_sql, engine)
except Exception as ex:
    print('Failed to connect to %s\n', databaseName+ex)

totalSmokeCount = dfRegression.shape[0]
lastRunDateGE1 = dfRegression['ge1'].iloc[0].split(",")[0] if dfRegression['ge1'].iloc[0] else 'NULL'
lastRunDateGE2 = dfRegression['ge2'].iloc[0].split(",")[0] if dfRegression['ge2'].iloc[0] else 'NULL'
lastRunDateGE4 = dfRegression['ge4'].iloc[0].split(",")[0] if dfRegression['ge4'].iloc[0] else 'NULL'
listLastRunDateEnv = [lastRunDateGE1,lastRunDateGE2,lastRunDateGE4]
RecentRunDate = str(max([i for i in listLastRunDateEnv if i is not 'NULL']))
index = listLastRunDateEnv.index(RecentRunDate)
RecentRunEnv = ""
if(index == 0):
    RecentRunEnv = "ge1"
elif(index == 1):
    RecentRunEnv = "ge2"
else:
    RecentRunEnv = "ge4"

def LatestRunDate(env):
    return dfRegression[env].tolist()[0].split(',')[0]

def size(env):
    statusList = [i.split(',')[1] for i in dfRegression[env].tolist()]
    my_dict = {i:statusList.count(i) for i in statusList}
    sizes = []
    for x, y in my_dict.items():
        sizes.append(y)
    return sizes

def label(env):
    statusList = [i.split(',')[1] for i in dfRegression[env].tolist()]
    my_dict = {i:statusList.count(i) for i in statusList}
    labels = []
    for x, y in my_dict.items():
        labels.append(x)
    return labels

def removeFile(env):
    path = f"./assets/output/{env}/Regression/"
    for files in os.listdir(path):
        file = path + files
        if os.path.isfile(file):
            os.remove(file)
    
def GetHtmlReport(profileName):
    path = "./assets/output/{0}/Regression/{1}.html".format(RecentRunEnv,profileName)
    filename = "./assets/output/{0}/Regression/{1}.html".format(RecentRunEnv,profileName)
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()
    sql = "SELECT {0}_reports FROM UFD_ORS.Automation_Status where TEST_TYPE='Regression' and profiles='{1}'".format(RecentRunEnv,profileName)
    cursor.execute(sql)
    row = cursor.fetchone()
    imageBlob = row[0]
    imageFile = open(filename,'wb')
    if imageBlob != None:
        imageFile.write(imageBlob.read())
        imageFile.close()
    cursor.close()
    connection.close()

dfProfileNames = list(dfRegression["profiles"].value_counts().keys())
start_time = time.time()
thread_list = []
for profileName in dfProfileNames:
    thread = threading.Thread(target=GetHtmlReport, args=(profileName,))
    thread_list.append(thread)
for thread in thread_list:
    thread.start()
for thread in thread_list:
    thread.join()

def getColor(pro):
    if(pro.upper()=='FAILED'):
        return "#FF0000"
    elif(pro.upper()=='PASSED'):
        return "#006e00"
    else:
        return "#FDDA0D"

listDAO = []
listAPJ = []
listEMEA = []
for item in dfRegression['profiles'].tolist():
    if('DAO' in item):
        listDAO.append(item)
    elif('APJ' in item):
        listAPJ.append(item)
    else:
        listEMEA.append(item)

layout= html.Div([
    html.Center(html.Span("Regression - Dashboard",className="text-bg-primary btn-lg px-4",style={'padding':'5px','border-radius':'5px'})),
    html.Br(),
    html.Center(html.H6("Total Regression test cases - {0}".format(totalSmokeCount))),
    html.Hr(),
    html.Div([
                dcc.Dropdown(
                id="dropdownlist",
                options=['GE1','GE2','GE4'],
                value=RecentRunEnv.upper(),
                clearable=False,style={'color':'#000','width':'100px'}
            ),
        ],className="col-lg-12"),
    html.Div([
        html.Div([
    dcc.Graph(id="pieRegressionchart",config={"displaylogo": False,'modeBarButtonsToRemove':['pan2d','lasso2d']},style={'border-right':'1px solid','color':'#ffffff29','height':'400px'})
        ],className="col-sm-4"),
         html.Div(
        className="col-sm-3",
        children=[
            html.Span(['DAO:'],style={'padding':'4px'},className=".text-bg-primary"),
            html.Ul(id="daoRegressionProfiles", style={'list-style-type': 'none'})
        ]),
        html.Div(className="col-sm-2",children=[
            html.Span(['APJ:'],style={'padding':'4px'},className=".text-bg-primary"),
            html.Ul(id="apjRegressionProfiles", style={'list-style-type': 'none'}),
        ]),
        html.Div(className="col-sm-3",children=[
            html.Span(['EMEA:'],style={'padding':'4px'},className=".text-bg-primary"),
            html.Ul(id="emeaRegressionProfiles", style={'list-style-type': 'none'}),
        ])
    ],className="row")
],className="col-lg-12 mx-auto p-4")

@callback(Output("pieRegressionchart", "figure"), Input("dropdownlist", "value"))
def update_bar_chart(env):
    val = size(env.lower())
    name=label(env.lower())
    latestRunDate=LatestRunDate(env.lower())
    RegressionFig = px.pie(values=val, names=name, title='{0} Status on {1}'.format(env,latestRunDate),hole=.4,color_discrete_map={'NA':'gold','PASS':'cyan','FAIL':'darkorange'})
    RegressionFig.update_layout({'plot_bgcolor':'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'},font_color='white')
    RegressionFig.update_traces(textinfo='label+percent+value')
    return RegressionFig

@callback(Output("daoRegressionProfiles", "children"), Input("dropdownlist", "value"))
def daoLinks(env):
    env=env.lower()
    ProfileStatus = {k:v[-6:] for k, v in dfRegression.set_index('profiles')[env].to_dict().items()}
    DAOlinks =[html.A(item, href=f'./assets/output/{env.upper()}/Regression/{item}.html',target='_blank', style={'font-size':'14px','background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': '{0}'.format(getColor(ProfileStatus[item]))}) for item in listDAO]
    return [html.Li(DAOlink,style={'padding-top':'5px'}) for DAOlink in DAOlinks]

@callback(Output("apjRegressionProfiles", "children"), Input("dropdownlist", "value"))
def daoLinks(env):
    env=env.lower()
    ProfileStatus = {k:v[-6:] for k, v in dfRegression.set_index('profiles')[env].to_dict().items()}
    APJlinks =[html.A(item, href=f'./assets/output/{env.upper()}/Regression/{item}.html',target='_blank', style={'font-size':'14px','background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': '{0}'.format(getColor(ProfileStatus[item]))}) for item in listAPJ]
    return [html.Li(APJlink,style={'padding-top':'5px'}) for APJlink in APJlinks]

@callback(Output("emeaRegressionProfiles", "children"), Input("dropdownlist", "value"))
def daoLinks(env):
    env=env.lower()
    ProfileStatus = {k:v[-6:] for k, v in dfRegression.set_index('profiles')[env].to_dict().items()}
    EMEAlinks =[html.A(item, href=f'./assets/output/{env.upper()}/Regression/{item}.html',target='_blank', style={'font-size':'14px','background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': '{0}'.format(getColor(ProfileStatus[item]))}) for item in listEMEA]
    return [html.Li(EMEAlink,style={'padding-top':'5px'}) for EMEAlink in EMEAlinks]