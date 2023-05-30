import dash
import cx_Oracle
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import time
dash.register_page(__name__)
from dash import Dash, dcc, html, Input, Output, dash_table,State,callback
import dash_bootstrap_components as dbc
import plotly.express as px
import os
import threading
from Mail import sendEmail
#from app import app

host = 'udmnlorrrde3e01.amer.dell.com'
port = '1521'
service_name = 'EFDI.dit.emea.dell.com'

dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

username = 'UFD_ORS'
password = 'Di$closeNot'
databaseName = "DITAPJEMEA"
engine = cx_Oracle.connect(username, password, dsn)

#engine = sqlalchemy.create_engine("oracle+cx_oracle://UFD_ORS:Di$closeNot@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=udmnlorrrde3e01.amer.dell.com)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=EFDI.dit.emea.dell.com)))")
ge1 = 'GE1'
ge2= 'GE2'
ge4='GE4'
profiles = 'PROFILES'

def getData():
    orders_sql = "SELECT * FROM UFD_ORS.Automation_Status where TEST_TYPE='Smoke'"
    dfsmoke = pd.read_sql_query(orders_sql, engine)
    return dfsmoke

dfsmoke = getData()
totalSmokeCount = dfsmoke.shape[0]
lastRunDateGE1 = dfsmoke[ge1].iloc[0].split(",")[0] if dfsmoke[ge1].iloc[0] else 'NULL'
lastRunDateGE2 = dfsmoke[ge2].iloc[0].split(",")[0] if dfsmoke[ge2].iloc[0] else 'NULL'
lastRunDateGE4 = dfsmoke[ge4].iloc[0].split(",")[0] if dfsmoke[ge4].iloc[0] else 'NULL'
listLastRunDateEnv = [lastRunDateGE1,lastRunDateGE2,lastRunDateGE4]
RecentRunDate = str(max([i for i in listLastRunDateEnv if i is not 'NULL']))
index = listLastRunDateEnv.index(RecentRunDate)
RecentRunEnv = ""
if(index == 0):
    RecentRunEnv = ge1
elif(index == 1):
    RecentRunEnv = ge2
else:
    RecentRunEnv = ge4

def LatestRunDate(env):
    return dfsmoke[env].tolist()[0].split(',')[0]

def size(env):
    statusList = [i.split(',')[1] for i in dfsmoke[env].tolist()]
    my_dict = {i:statusList.count(i) for i in statusList}
    sizes = []
    for x, y in my_dict.items():
        sizes.append(y)
    return sizes

def label(env):
    statusList = [i.split(',')[1] for i in dfsmoke[env].tolist()]
    my_dict = {i:statusList.count(i) for i in statusList}
    labels = []
    for x, y in my_dict.items():
        labels.append(x)
    return labels

def removeFile(env):
    path = f"./assets/output/{env}/Smoke/"
    for files in os.listdir(path):
        file = path + files
        if os.path.isfile(file):
            os.remove(file)
    
def GetHtmlReport(profileName):
    filename = "./assets/output/{0}/Smoke/{1}.html".format(RecentRunEnv,profileName)
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()
    sql = "SELECT {0}_reports FROM UFD_ORS.Automation_Status where TEST_TYPE='Smoke' and profiles='{1}'".format(RecentRunEnv,profileName)
    cursor.execute(sql)
    row = cursor.fetchone()
    imageBlob = row[0]
    imageFile = open(filename,'wb')
    if imageBlob != None:
        imageFile.write(imageBlob.read())
        imageFile.close()
    cursor.close()
    connection.close()

dfProfileNames = list(dfsmoke[profiles].value_counts().keys())
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
for item in dfsmoke[profiles].tolist():
    if('DAO' in item):
        listDAO.append(item)
    elif('APJ' in item):
        listAPJ.append(item)
    else:
        listEMEA.append(item)

layout = html.Div([
    html.Div([
    html.Center(html.Span("Smoke - Dashboard",className="text-bg-primary btn-lg px-4",style={'padding':'5px','border-radius':'5px'})),
    html.Br(),
    html.Center(html.H6("Total smoke test cases - {0}".format(totalSmokeCount))),
    html.Hr(),
    html.Div([
                dcc.Dropdown(
                id="dropdown",
                options=['GE1','GE2','GE3','GE4'],
                value=RecentRunEnv.upper(),
                clearable=False,style={'color':'#000','width':'100px'}
            ),
            #html.Button('Send Email', id='send-email-button')
        ],className="col-lg-4"),
    html.Div([
        html.Div([
    dcc.Graph(id="pieSmokechart",config={"displaylogo": False,'modeBarButtonsToRemove':['pan2d','lasso2d']},style={'border-right':'1px solid','color':'#ffffff29','height':'400px'})
        ],className="col-sm-5"),
         html.Div(className="col-sm-2",children=[
            html.Span(['DAO:'],style={'padding':'4px'},className=".text-bg-primary"),
            html.Ul(id="daoProfiles", style={'list-style-type': 'none'})
        ]),
        html.Div(className="col-sm-2",children=[
            html.Span(['APJ:'],style={'padding':'4px'},className=".text-bg-primary"),
            html.Ul(id="apjProfiles", style={'list-style-type': 'none'}),
        ]),
        html.Div(className="col-sm-3",children=[
            html.Span(['EMEA:'],style={'padding':'4px'},className=".text-bg-primary"),
            html.Ul(id="emeaProfiles", style={'list-style-type': 'none'}),
        ])
    ],className="row"),
        html.Hr(),
        html.Div(html.H6("Last 5 days history:")),
        html.Div(id='smokeHistory',className="col-sm-12",style={'overflow':'scroll'})
    ],className="col-lg-12 mx-auto p-4")])

@callback(Output("pieSmokechart", "figure"), Input("dropdown", "value"))
def update_bar_chart(env):
    val = size(env)
    name=label(env)
    latestRunDate=LatestRunDate(env)
    SmokeFig = px.pie(values=val, names=name, title='{0} Status on {1}'.format(env,latestRunDate),hole=.4,color_discrete_map={'PASSED':'cyan','FAILED':'darkorange','NotRan':'gold'})
    SmokeFig.update_layout({'plot_bgcolor':'rgba(0, 0, 0, 0)','paper_bgcolor':'rgba(0, 0, 0, 0)'},font_color='white')
    SmokeFig.update_traces(textinfo='label+percent+value')
    return SmokeFig

@callback(Output("daoProfiles", "children"), Input("dropdown", "value"))
def daoLinks(env):
    ProfileStatus = {k:v[-6:] for k, v in dfsmoke.set_index(profiles)[env].to_dict().items()}
    DAOlinks =[html.A(item, href=f'./assets/output/{env.upper()}/Smoke/{item}.html',target='_blank', style={'font-size':'14px','background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': '{0}'.format(getColor(ProfileStatus[item]))}) for item in listDAO]
    return [html.Li(DAOlink,style={'padding-top':'5px'}) for DAOlink in DAOlinks]

@callback(Output("apjProfiles", "children"), Input("dropdown", "value"))
def daoLinks(env):
    ProfileStatus = {k:v[-6:] for k, v in dfsmoke.set_index(profiles)[env].to_dict().items()}
    APJlinks =[html.A(item, href=f'./assets/output/{env.upper()}/Smoke/{item}.html',target='_blank', style={'font-size':'14px','background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': '{0}'.format(getColor(ProfileStatus[item]))}) for item in listAPJ]
    return [html.Li(APJlink,style={'padding-top':'5px'}) for APJlink in APJlinks]

@callback(Output("emeaProfiles", "children"), Input("dropdown", "value"))
def daoLinks(env):
    ProfileStatus = {k:v[-6:] for k, v in dfsmoke.set_index(profiles)[env].to_dict().items()}
    EMEAlinks =[html.A(item, href=f'./assets/output/{env.upper()}/Smoke/{item}.html',target='_blank', style={'font-size':'14px','background-color': '#3c3c3c','color':'white','padding':'0px 5px','text-align':'center','text-decoration':'none','display':'inline-block','border-style': 'solid','border-color': '#3c3c3c','border-left-color': '{0}'.format(getColor(ProfileStatus[item]))}) for item in listEMEA]
    return [html.Li(EMEAlink,style={'padding-top':'5px'}) for EMEAlink in EMEAlinks]

@callback(Output('smokeHistory', 'children'), Input("dropdown", "value"))
def display_data(env):
    orders_sql = f"select profiles,{env}_first,{env}_second,{env}_third,{env}_fourth,{env}_fifth from ufd_ors.automation_status where test_type='Smoke'"
    dfsmokeHistory = pd.read_sql_query(orders_sql, engine)
    dfsmokeHistory = dfsmokeHistory.fillna('Passed')
    dfsmokeHistory.insert(loc = 1,column = 'pass_count',value = "")
    j=0
    while(j<dfsmokeHistory.shape[0]):
        listCol =[]
        for column_name in dfsmokeHistory.columns:
            listCol.append(column_name)
        i = 2
        count = 0
        while(i <= 6):
            yn = dfsmokeHistory[listCol[i]].iloc[j]
            if(yn == 'Passed'):
                count = count + 1
            i=i+1
        dfsmokeHistory.at[j,'pass_count']=count
        j=j+1
    table = html.Table([
        html.Thead(
            html.Tr([html.Th(col,style={'width':'14.28%','border-width':'1px','text-align':'center','background-color':'cadetblue'}) for col in dfsmokeHistory.columns],style={'border-bottom-style':'solid','border-bottom-color':'#a9a9a9'})
        ),
        html.Tbody([
            html.Tr([
                html.Td(dfsmokeHistory.iloc[i][col],style={'width':'14.28%','border-width':'1px','text-align':'center'}) for col in dfsmokeHistory.columns
            ],style={'border-bottom-style':'solid','border-bottom-color':'#a9a9a9'}) for i in range(len(dfsmokeHistory))
        ])
    ])
    return table

# @callback(Output('send-email-button', 'disabled'),Input('send-email-button', 'n_clicks'),State('pieSmokechart', 'figure'))
# def send_email(n_clicks, figure):
#     if n_clicks is None or n_clicks <= 0:
#         return False
#     sendEmail('gopalakrishna_behara@dellteam.com','Smoke',figure)
#     return True