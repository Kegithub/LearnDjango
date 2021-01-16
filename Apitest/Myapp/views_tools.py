from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from Myapp.models import *
import json
import requests
from allpairspy import AllPairs
import xlwt
from xlutils import copy
import os


# 获取公共参数
def glodict(request):
    userimg = str(request.user.id)+".png"
    res = {"username": request.user.username, "userimg": userimg}
    return res


# 进入正交工具页面
def zhengjiao(request):
    return render(request, 'welcome.html', {"whichHTML": "zhengjiao.html", "oid": request.user.id, **glodict(request)})


# 正交工具运行
def zhengjiao_play(request):
    end_values = request.GET['end_values'].split(',')
    new_values = [i.split('/') for i in end_values]
    res = []
    for i in AllPairs(new_values):
        res.append(i)
    d = {"res": res}
    return HttpResponse(json.dumps(d), content_type='application/json')


# 正交工具导出
def zhengjiao_excel(request):
    end_keys = request.GET['end_keys'].split(',')
    end_values = request.GET['end_values'].split(',')
    new_values = [i.split('/') for i in end_values]
    res = []
    for i in AllPairs(new_values):
        res.append(i)
    # 先创建
    zj_book = xlwt.Workbook(encoding='utf-8')  # 创建excel
    zj_sheet = zj_book.add_sheet("正交结果")  # 创建sheet页
    for i in range(len(res)):
        case_index = '用例：' + str(i+1)  # 用例序号
        hb = list(zip(end_keys, res[i]))  # 把key和values进行合并
        case = ','.join([':'.join(list(i)) for i in hb])  # 进行格式化
        zj_sheet.write(i, 0, case_index)  # 写入i为行，0为第一列
        zj_sheet.write(i, 1, case)  # 写入i为行，1为第二列

    zj_book.save('Myapp/static/tmp_zhengjiao.xls')  # 保存
    return HttpResponse('')