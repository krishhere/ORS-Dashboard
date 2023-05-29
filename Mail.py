import requests
import base64
from PIL import Image
import io
import plotly.io as pio
import orca

def sendEmail(to,type,graph):
    #img_bytes =pio.to_image(graph, format='png')
    img_bytes = graph.write_image(graph, engine='kaleido')

    url = 'https://email-ge4.ausvtc01.pcf.dell.com/email'
    data = {
        'To': f'{to}',
        'From': 'gopalakrishna_behara@dellteam.com',
        'Subject':f'{type} Dashboard',
        'CC':'gopalakrishna_behara@dellteam.com',
        'HTML':f'Hi Team<br/>{graph}'
    }
    response = requests.get(url, verify=False)
    #response = requests.post(url, json=data, verify=False)

    img_file = img_bytes
    payload = {
        "image": img_file
    }
    response = requests.post(url, json=data, verify=False, files=payload)

    if response.status_code == 200:
        try:
            result = response.json()
        except:
            pass
    else:
        pass