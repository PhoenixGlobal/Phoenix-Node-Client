#!/usr/bin/env python3

import requests
import json
import os
import time

import version
from log import log

TokenUrl = 'https://www.phoenix.global/sdk/computation/user/genToken'
NodeServerUrl = 'https://www.phoenix.global/prd/node/'


def GetToken(email,pwd):
    params = {'email':email,'passwd':pwd }
    x = requests.post(TokenUrl,data=json.dumps(params))
    dic = eval(x.text)
    if dic['code'] == 200:
        return dic['token']
    else:
        return ''

def GetKey(token):
    header = {'token': token}
    x = requests.get(NodeServerUrl+'genKey', headers=header)
    dic = eval(x.text)
    if dic['code'] == 200:
        return dic['data']['key']
    else:
        return ''

def RegisterNode(token,key,name,type,guid):
    header = {'token': token}
    params = {'key': key, 'name': name,'type':type,'guid':guid}
    x = requests.post(NodeServerUrl+'addNode', headers=header, data=json.dumps(params))
    print("response of RegisterNode is ", x.text)
    log(f'response of RegisterNode is {x.text}')
    dic = eval(x.text)
    if dic['code'] == 200:
        return 1
    else:
        return 0

def SubJobResult(job_id,key,name,type,files):
    file_name = files[8:]
    file = {
        "resultFile": (file_name,open(files, "rb"), "image/jpeg") #
    }
    datas = {'key': key, 'name': name,'computation_type':type,'job_id':job_id}
    x = requests.post(NodeServerUrl+'subJobResult', files=file, data=datas)
    print("response of subJobResult is ", x.text)
    log(f'response of subJobResult is {x.text}')
    dic = eval(x.text)
    if dic['code'] == 200:
        return 1
    else:
        print("SubJobResult fail")
        log("SubJobResult fail")
        return 0

def GetJobData(job_id,key,name):
    url_params = "job_id="+job_id+"&key="+key+"&name="+name
    url=NodeServerUrl+'generateData?'+url_params
    x = requests.get(url)
    print("response of generateData is ", x.text)
    log(f'response of generateData is {x.text}')
    dic = eval(x.text)
    ret_arr = []
    computation_type = ""
    if dic["code"] == 200:
        ret_arr.append(dic["data"]["x_train_url"])
        ret_arr.append(dic["data"]["y_train_url"])
        ret_arr.append(dic["data"]["x_test_url"])
        computation_type = dic["data"]["computation_type"]
    return ret_arr,computation_type

def HeartBeat(key,name):
    params = {'key': key, 'name': name}
    x = requests.post(NodeServerUrl+'heartbeat', data=json.dumps(params))
    dic = eval(x.text)
    print("response of HeartBeat is ", x.text)
    log(f'response of HeartBeat is {x.text}')
    if dic['code'] == 200:
        return 1
    else:
        print("HeartBeat fail")
        log("HeartBeat fail")
        return 0

# def CheckVersion(key,name):
#     v = version.VERSION
#     params = {'key': key, 'name': name,'version':v}
#     x = requests.post(NodeServerUrl+'checkVersion', data=json.dumps(params))
#     dic = eval(x.text)
#     print("response of CheckVersion is ", x.text)
#     log(f'response of CheckVersion is {x.text}')
#     if dic['code'] == 200:
#         return 1
#     else:
#         print("CheckVersion fail")
#         log("CheckVersion fail")
#         return 0

def CheckVersion():
    v = version.VERSION
    x = requests.get(NodeServerUrl+'getVersion')
    print("response of getVersion is ", x.text)
    log(f'response of getVersion is {x.text}')
    dic = eval(x.text)
    if dic['code'] == 200:
        serverVersion=dic["data"]["version"]
        if v == serverVersion:
            return 1
        else:
            return 0
    else:
        print("CheckVersion getVersion fail")
        log("CheckVersion getVersion fail")
        return 0

def CleanFiles():
    print("Begin start CleanFiles")
    log("Begin start CleanFiles")

    directory = "./files"
    exclude_file = "test.txt"
    now = time.time()

    three_days_ago = now - 12 * 60 * 60

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename != exclude_file:
            file_mod_time = os.path.getmtime(file_path)
            if file_mod_time < three_days_ago:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    print("End CleanFiles")
    log("End CleanFiles")