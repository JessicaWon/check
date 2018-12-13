# coding:utf-8
import os, io, json
import csv
import sys
import logging
import datetime
import time
from elasticsearch import Elasticsearch
import collections  # 有序字典
from flask import Flask, Response
import random, subprocess
app = Flask(__name__)

reload(sys)
sys.setdefaultencoding('gbk')
logging.basicConfig()
es = Elasticsearch(["es:9200"])

def query_clause(time_from, time_to):

    """如果参数中的时间是有效时间的话，则为传入的时间参数，如果不是有效时间的话，则默认设置为今天的时间"""

    if time_from and time_to:
        pass
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days = 1)

        time_from = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d')))*1000
        time_to = int(round(time.time()*1000))
    print time_from,time_to

    # query_name_contains = {"query":{"bool":{"must":[{"range":{"@timestamp":{"gt":"1541448720000","lt":"1544148720461"}}}]}},"size":10000}
    """query_clause_detail = {
        "query": {"bool": {"must": [{"range": {"@timestamp": {"gt": time_from, "lt": time_to}}}], "must_not": [],
                           "should": []}}, "size": 5000, "from": 0, "sort": [], "aggs": {}
    }"""
    query_clause_detail = {
          "query": {
            "bool": {
                  "must": [
                    {
                      "range": {
                        "@timestamp": {
                          "gt": time_from,
                          "lt": time_to
                        }
                      }
                    }
                  ]
            }
          },
        "size": 5000,
        "sort": [
            {
                "parsedJson.proj": {
                    "order": "desc"
                }
            }
        ]
        }
    return query_clause_detail


def getMappingToExcelHeader(indexname):

    """打印excel头部到excel表中，这个地方使用的是循环，如果说后面的键值的层数变深的话就会出现问题"""
    """出现多层的结构并没有修改,通过调整headers的数组的顺序来对csv中的列的顺序进行修改"""

    headers = []
    es_mappings = es.indices.get_mapping(indexname)
    es_fields = es_mappings[indexname]["mappings"]["logs"]["properties"]["parsedJson"]
    for key, values in es_fields.items():
        for fields_key, fields_value in values.items():
            if fields_value.has_key("properties"):
                for sub_fields_key, sub_fields_value in fields_value["properties"].items():
                    headers.append(fields_key + '.' + sub_fields_key)
            else:
                headers.append(fields_key)
    reorderlist = ["ipv4", "proj"]
    for _header in reorderlist:
        headers.remove(_header)
        headers.insert(1, _header)
    print '---headers--',headers
    return headers



def getAllSourceData(origin_data, origin_key):

    """将查询出的单条数据经过这个函数递归变成csv需要的格式"""
    """判断键值是否为字典进行递归"""

    #all_source_data = {}
    if origin_data:
        for key in origin_data:
            if isinstance(origin_data[key],dict):
                if origin_key:
                    getAllSourceData(origin_data[key],origin_key + '.' + key)
                else:
                    getAllSourceData(origin_data[key], key)
            else:
                if origin_key:
                    if origin_data[key]:
                        all_source_data[origin_key + '.' + key] = origin_data[key]
                else:
                    if origin_data[key]:
                        all_source_data[key] = origin_data[key]
        #print '---', all_source_data
        return all_source_data
    else:
        return {}



def getEsToExcelData(indexname, time_from, time_to):

    """从mapping里面拿出来的数据先在csv头里面加上headers，然后再从es中拿出真正的数据然后再递归换成字典的数组，然后最后写入csv中
    如果是mapping中拿出的keys和数据中拿出的keys不一致的话就会出现问题"""
    """csv导入的数据都是要求外层是数组，里面是字典这种格式的"""
    """这个地方是先获取了mapping的结构来的"""

    my_query_clause = query_clause(time_from, time_to)
    #print my_query_clause
    searched = es.search(index=indexname,  doc_type='logs', body=my_query_clause)
    return searched



def writeToCSV(headers, data_rows,filename):

    """将读取的数据写入到excel中去"""

    if headers and data_rows:
            with open(filename, 'w') as f:
                f_csv = csv.DictWriter(f, headers)
                f_csv.writeheader()
                f_csv.writerows(data_rows)
    else:
        return {"error":"filename and data must be given"}


def delDataBySearch(indexname, query, doc_type):

    """删除es中的一些数据。通过query出来的数据来进行删除"""
    """并没有测试过"""

    searched_result = es.search(index=indexname, size=100, body={"query": query_name_contains}, search_type="scan",
                                scroll="60s")
    # print searched_result
    es.delete_by_query(index=indexname, body=query, doc_type=doc_type)

def searchValuesByAggs(index_name, key):

    """通过索引名称和键名称，聚合查询出所有的key对应的内容分类"""

    values = []

    _query_clause = {


    }

    return values

def getSelectedKeys(keys):

    """通过聚合得到一些键值的种类，其中在提供选择的时候使用"""
    pass
    #for key in keys:
    #    searchValuesByAggs(index_name='', key)


@app.route("/")
def hello():
    return '''
        <html><body>
        Hello. <a href="/getPlotCSV">点击下载巡检数据</a>
        </body></html>
        '''

@app.route("/getPlotCSV/")
def getPlotCSV():
    with open(file_dir + "JMdata.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=JMdata" + formatted_today +".csv"})

def getRandomString():

    """输入一些种子值，从中随机取出一些值作为随机值拼接成字符串"""

    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(4):
        sa.append(random.choice(seed))
    salt = "".join(sa)
    return salt



if __name__ == "__main__":


    today = datetime.date.today()
    formatted_today = today.strftime('%y-%m-%d')
    file_dir = "/tmp/"
    random_string = getRandomString()



    #index_name = "checkdata-isdocker-2018.12"
    index_name = ["isntdocker-2018.12", "isdocker-2018.12"]

    for _index in index_name:
        file_name = file_dir + "JMData_" + formatted_today + _index + "_" + random_string + '.csv'
        all_source_data = {}
        es_formed_data_array = []

        headers = getMappingToExcelHeader(_index)
        print headers

        rows = getEsToExcelData(_index, '','')
        rows_hits = rows["hits"]["hits"]


        for single_row_hits in rows_hits:
            single_row = single_row_hits["_source"]["parsedJson"]
            #print single_row["ipv4"], single_row["proj"]
            all_source_data = {}
            es_formed_data = getAllSourceData(single_row,"")
            #print '***',es_formed_data
            es_formed_data_array.append(es_formed_data)
            #es_formed_data = [{'php_service.Thrift': "v1"}]




        """写入操作"""
        """这个地方的数组是有问题的"""

        print "filename", file_name
        writeToCSV(headers, es_formed_data_array, file_name)
    _shell_command = "cat " + file_dir + "JMData_" + formatted_today + "*" + random_string + '.csv' + ">" + file_dir + "JMdata.csv"

    """这个地方的其实用shell直接得到两个csv的文件的合并，是个投机的做法"""
    subprocess.call(_shell_command, shell=True)


    app.run(
        host = '0.0.0.0',
        port = 6000,
        debug = True
    )
