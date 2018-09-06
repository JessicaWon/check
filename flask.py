#coding:utf-8
# 这个用于制作多张bar图表在一张图表的,ESIP这个地方实际上是部署的es服务器的地址
##密码等敏感信息是抹去的，请在对应的地方添加
from flask import Flask,render_template,url_for
from elasticsearch import Elasticsearch
import json, datetime, ConfigParser
from flask import request
import yaml, os, io

app = Flask(__name__, template_folder='templates',static_folder="",static_url_path="")


def QueryConn(project,time_from,time_to):

    query_name_contains = {
        "query":{"bool":{"must":[{"term":{"parsedJson.proj":project}},{"range":{"@timestamp":{"gt":time_from,"lt":time_to}}}],"must_not":[],"should":[]}},"size":500,"from":0,"sort":[],"aggs":{}
    }
    return query_name_contains

def CreateConn():
    '''
    es连接对象
    '''
    es = Elasticsearch('ESIP')
    return es

def SearchEs(project, index_name,time_from,time_to):
    '''
    es连接后的查询
    '''
    project = project
    index = index_name
    conn = CreateConn()
    query_clause = QueryConn(project,time_from,time_to)
    #searched = conn.search(index='checkdata-isntdocker-2018.08', doc_type='logs', body=query_clause)
    searched = conn.search(index, doc_type='logs', body=query_clause)
    return searched

def ByteIfy(input):
    '''
    转成utf-8格式的
    '''
    if isinstance(input, dict):
        return {ByteIfy(key): ByteIfy(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [ByteIfy(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


## php_service
#data_field = "query_service_version_gen"

all_services = []

def getData(searched, index_type, key_name):

    '''
    从es中获取对应的数据,并从配置文件中找出对应的键值对应的es中的字段
    '''
    current_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(current_path, "view.json")
    view_conf = io.open(json_path, encoding='utf-8')
    view_data = json.load(view_conf)

    if view_data[index_type].has_key(key_name):
        data_field = view_data[index_type][key_name]
    else:
        return {}
    ipv4_list = []
    formed_data = {}
    if searched:
        for data in searched["hits"]["hits"]:

            ipv4_list.append(data["_source"]["parsedJson"]["ipv4"])

            if data["_source"]["parsedJson"].has_key(data_field):
                if data["_source"]["parsedJson"][data_field]:
                    for _service in data["_source"]["parsedJson"][data_field]:
                        if _service in all_services:
                            pass
                        else:
                            all_services.append(_service.decode('utf-8'))
                        single_data = data["_source"]["parsedJson"][data_field]

                        if single_data[_service]:
                            if formed_data.has_key(_service):
                                if formed_data[_service].has_key("version") and single_data[_service] in formed_data[_service]["version"]:
                                    _index = formed_data[_service]["version"].index(single_data[_service]) #get version index to dump data to each data
                                    formed_data[_service]["data"][_index] = formed_data[_service]["data"][_index] + 1
                                else: #if not exist, append version and data to th tail of the array
                                    formed_data[_service]["version"].append(single_data[_service])
                                    formed_data[_service]["data"].append(1)
                            else:
                                formed_data[_service] = {}
                                formed_data[_service]["version"] = []
                                formed_data[_service]["version"].append(single_data[_service])
                                formed_data[_service]["data"] = [1]

                        else:
                            if formed_data.has_key(_service):
                                if formed_data[_service].has_key("version") and formed_data[_service]["version"]:
                                    if "unknown" in formed_data[_service]["version"]:
                                        _index = formed_data[_service]["version"].index("unknown")
                                        formed_data[_service]["data"][_index] = formed_data[_service]["data"][_index] + 1
                                    else:
                                        formed_data[_service]["version"].append("unknown")
                                        formed_data[_service]["data"].append(1)
                                else:
                                    formed_data[_service]["version"] = ["unknown"]
                                    formed_data[_service]["data"] = [1]
                            else:
                                formed_data[_service] = {}
                                formed_data[_service]["version"] = ["unknown"]
                                formed_data[_service]["data"] = [1]
                else:
                    pass
            else:
                data["_source"]["parsedJson"][data_field] = {}
    else:
        pass
    return formed_data


def transFormData(formed_data):
    '''
    将数据转换成echart所需要的
    通过获取的数据得到数组，用来做titile
    '''
    formed_array = []
    for _data in formed_data:
        formed_array.append(_data)
    return formed_array



@app.route('/pic/<project>')
def createEchart(project):
    '''
    处理数据为echart类型能识别的数据结构,其中ignored_keys就是需要手动摘除的键,因为这些键值在图表中展示不太好展示
    '''
    project_name = '{0}'.format(project)
    print project_name
    index_name = request.args.get("type")
    search_type = request.args.get("kind")
    today=datetime.date.today()
    index_time = today.strftime('%Y.%m')
    time_from = request.args.get("from")
    time_to = request.args.get("to")

    if index_name == unicode('非容器',"utf-8"):
        index = "checkdata-isntdocker-" + index_time
        index_type = "isntdocker"
    elif index_name == unicode('容器',"utf-8"):
        index = "checkdata-isdocker-" + index_time
        index_type = "docker"
    else:
        msg = {'error':"index not found"}
        return  msg

    searched = SearchEs(project_name, index, time_from, time_to)
    all_data = getData(searched, index_type, search_type)
    array = transFormData(all_data)
    count = len(array)

    ignored_keys = ["CPU_min_idle", "time_offset"]
    for _keys in ignored_keys:
        if _keys in array:
            del all_data[_keys]
            count = count - 1
            array.remove(_keys)

    result_json = ByteIfy(all_data)
    result_array = ByteIfy(array)
    print result_json

    if result_array:
        return render_template('multi-bar.html', result_json = json.dumps(result_json), result_array = json.dumps(result_array), array_len = count)
    else:
        return render_template('404.html')

@app.route('/jsondata/<project>')
def postDataToAjax(project):
     project_name = '{0}'.format(project)
     searched = SearchEs(project_name)
     all_data = getData(searched)
     array = transFormData(all_data)
     count = len(array)
     result_json = ByteIfy(all_data)
     result_array = ByteIfy(array)
     msg = {}
     msg_array = ','.join(result_array)
     msg["result_json"] = json.dumps(result_json)
     msg["result_array"] = json.dumps(msg_array)
     msg["array_len"] = count
     return json.dumps(msg)

@app.route('/page/<project>')
def myRoute(project):
    result = {}
    project_name = '{0}'.format(project)
    searched = SearchEs(project_name)
    all_data = getData(searched)
    result = transFormData(all_data)
    array = ByteIfy(all_services)
    return render_template('bar.html', result_json = json.dumps(result), result_array = array)

@app.route('/overview')
def overView():
    return render_template('overview.html')

if __name__ == '__main__':
    app.run('0.0.0.0')
