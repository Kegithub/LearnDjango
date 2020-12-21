from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from Myapp.models import *
import json
import requests


@login_required()
def welcome(request):
    print('欢迎')
    return render(request, 'welcome.html')


# 获取公共参数
def glodict(request):
    userimg = str(request.user.id)+".png"
    res = {"username": request.user.username, "userimg": userimg}
    return res


@login_required
def home(request, log_id=''):
    return render(request, 'welcome.html', {"whichHTML": "home.html", "oid": request.user.id, "ooid": log_id, **glodict(request)})


def login(request):
    return render(request, 'login.html')


def pei(request):
    tucao_text = request.GET["tucao_text"]
    DB_tucao.objects.create(user=request.user.username, text=tucao_text)
    return HttpResponse('')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


def login_action(request):
    u_name = request.GET['username']
    p_word = request.GET['password']
    user = auth.authenticate(username=u_name, password=p_word)
    if user is not None:
        auth.login(request, user)
        request.session['user'] = u_name
        # return HttpResponseRedirect('/home/')
        return HttpResponse('成功')
    else:
        return HttpResponse('失败')


def register_action(request):
    u_name = request.GET['username']
    p_word = request.GET['password']
    try:
        user = User.objects.create_user(username=u_name, password=p_word)
        user.save()
        return HttpResponse('注册成功')
    except:
        return HttpResponse('注册失败，用户名好像已存在')


def api_help(request):
    return render(request, 'welcome.html', {"whichHTML": "help.html", "oid": "", **glodict(request)})


# 返回子页面
def child(request, eid, oid, ooid):
    res = child_json(eid, oid, ooid)
    return render(request, eid, res)


# 控制不同页面返回不同的数据
def child_json(eid, oid='', ooid=''):
    res = {}
    if eid == 'home.html':
        data = DB_home_href.objects.all()
        home_log = DB_apis_log.objects.filter(user_id=oid)[::-1]
        hosts = DB_host.objects.all()
        if ooid == '':
            res = {"hrefs": data, "home_log": home_log, "hosts": hosts}
        else:
            log = DB_apis_log.objects.filter(id=ooid)[0]
            res = {"hrefs": data, "home_log": home_log, "log": log, "hosts": hosts}
    if eid == 'project_list.html':
        data = DB_project.objects.all()
        res = {"projects": data}
    if eid == 'P_apis.html':
        project = DB_project.objects.filter(id=oid)[0]
        apis = DB_apis.objects.filter(project_id=oid)
        for i in apis:
            try:
                i.short_url = i.api_url.split('?')[0][:50]
            except:
                i.short_url = ''
        project_header = DB_project_header.objects.filter(project_id=oid)
        hosts = DB_host.objects.all()
        project_host = DB_project_host.objects.filter(project_id=oid)
        res = {"project": project, 'apis': apis, 'project_header': project_header, "hosts": hosts, "project_host": project_host}
    if eid == 'P_cases.html':
        project = DB_project.objects.filter(id=oid)[0]
        cases = DB_cases.objects.filter(project_id=oid)
        apis = DB_apis.objects.filter(project_id=oid)
        project_header = DB_project_header.objects.filter(project_id=oid)
        hosts = DB_host.objects.all()
        project_host = DB_project_host.objects.filter(project_id=oid)
        res = {'cases': cases, 'project': project, "apis": apis, 'project_header': project_header, "hosts": hosts, "project_host": project_host}
    if eid == 'P_project_set.html':
        project = DB_project.objects.filter(id=oid)[0]
        res = {"project": project}
    return res


# 项目列表
def project_list(request):
    return render(request, 'welcome.html', {"whichHTML": "project_list.html", "oid": "", **glodict(request)})


# 删除项目
def delete_project(request):
    id = request.GET['id']
    DB_project.objects.filter(id=id).delete()
    DB_apis.objects.filter(project_id=id).delete()  # 删除其下接口
    all_case = DB_cases.objects.filter(project_id=id)  # 删除其下用例
    for i in all_case:
        DB_step.objects.filter(Case_id=i.id).delete()
        i.delete()
    return HttpResponse('')


# 创建项目
def add_project(request):
    project_name = request.GET['project_name']
    DB_project.objects.create(name=project_name, remark='', user=request.user.username, other_user='')
    return HttpResponse('添加成功')


# 进入接口库
def open_apis(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_apis.html", "oid": project_id, **glodict(request)})


# 用例管理
def open_cases(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_cases.html", "oid": project_id, **glodict(request)})


# 项目设置
def open_project_set(request, id):
    project_id = id
    return render(request, 'welcome.html', {"whichHTML": "P_project_set.html", "oid": project_id, **glodict(request)})


# 保存项目设置
def save_project_set(request, id):
    project_id = id
    name = request.GET['name']
    print(name)
    remark = request.GET['remark']
    other_user = request.GET['other_user']
    DB_project.objects.filter(id=project_id).update(name=name, remark=remark, other_user=other_user)
    return HttpResponse('保存成功')


# 新增接口
def project_api_add(request, Pid):
    project_id = Pid
    DB_apis.objects.create(project_id=project_id, api_method='none', api_url='')
    return HttpResponseRedirect('/apis/%s/' % project_id)


# 删除接口
def project_api_del(request, id):
    project_id = DB_apis.objects.filter(id=id)[0].project_id
    DB_apis.objects.filter(id=id).delete()
    return HttpResponseRedirect('/apis/%s/' % project_id)


# 保存接口备注信息
def save_bz(request):
    api_id = request.GET['api_id']
    bz_value = request.GET['bz_value']
    DB_apis.objects.filter(id=api_id).update(desc=bz_value)
    return HttpResponse('添加备注成功')


# 获取接口备注
def get_bz(request):
    api_id = request.GET['api_id']
    bz_value = DB_apis.objects.filter(id=api_id)[0].desc
    return HttpResponse(bz_value)


# 保存接口
def Api_save(request):
    # 提取所有数据
    api_id = request.GET['api_id']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    api_name = request.GET['api_name']
    ts_project_headers = request.GET['ts_project_headers']
    if ts_body_method == '返回体':
        api = DB_apis.objects.filter(id=api_id)[0]
        ts_body_method = api.last_body_method
        ts_api_body = api.last_api_body
    else:
        ts_api_body = request.GET['ts_api_body']
    # 保存数据
    DB_apis.objects.filter(id=api_id).update(
        api_method=ts_method,
        api_url=ts_url,
        api_header=ts_header,
        api_host=ts_host,
        body_method=ts_body_method,
        api_body=ts_api_body,
        name=api_name,
        public_header=ts_project_headers,
    )
    # 返回
    return HttpResponse('success')


# 获取接口数据
def get_api_data(request):
    api_id = request.GET['api_id']
    api = DB_apis.objects.filter(id=api_id).values()[0]
    return HttpResponse(json.dumps(api), content_type='application/json')


# 调试层发送请求
def Api_send(request):
    # 提取所有数据
    api_id = request.GET['api_id']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    api_name = request.GET['api_name']
    ts_project_headers = request.GET['ts_project_headers'].split(',')

    # 出来域名host
    if ts_host[0:4] == '全局域名':
        project_host_id = ts_host.split('-')[1]
        ts_host = DB_project_host.objects.filter(id=project_host_id)[0].host

    if ts_body_method == '返回体':
        api = DB_apis.objects.filter(id=api_id)[0]
        ts_body_method = api.last_body_method
        ts_api_body = api.last_api_body
        if ts_body_method in ['', None]:
            return HttpResponse('请先选择请求体编码格式和请求体，再进行send操作')
    else:
        ts_api_body = request.GET['ts_api_body']
        api = DB_apis.objects.filter(id=api_id)
        api.update(last_body_method=ts_body_method, last_api_body=ts_api_body)
    # 发送请求获取返回值
    try:
        header = json.loads(ts_header)
    except:
        return HttpResponse('请求头不符合json格式')

    for i in ts_project_headers:
        project_header = DB_project_header.objects.filter(id=i)[0]
        header[project_header.key] = project_header.value
    print(header)

    # 拼接网站url
    if ts_host[-1] == '/' and ts_url[0] == '/':
        url = ts_host[:-1] + ts_url
    elif ts_host[-1] != '/' and ts_url[0] != '/':
        url = ts_host + '/' + ts_url
    else:
        url = ts_host + ts_url
    try:
        if ts_body_method == 'none':
            response = requests.request(ts_method.upper(), url, headers=header, data={})
        elif ts_body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(ts_api_body):
                payload[i[0]] = i[1]
            response = requests.request(ts_method.upper(), url, headers=header, data=payload, files=files)
        elif ts_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(ts_api_body):
                payload[i[0]] = i[1]
            response = requests.request(ts_method.upper(), url, headers=header, data=payload)
        else:
            if ts_body_method == 'Text':
                header['Content-Type'] = 'text/plain'
            if ts_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'
            if ts_body_method == 'Json':
                header['Content-Type'] = 'text/plain'
            if ts_body_method == 'Html':
                header['Content-Type'] = 'text/plain'
            if ts_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            response = requests.request(ts_method.upper(), url, headers=header, data=ts_api_body.encode('utf-8'))

        # 把返回值传给前端
        response.encoding = 'utf-8'
        DB_host.objects.update_or_create(host=ts_host)
        return HttpResponse(response.text)
    except Exception as e:
        return HttpResponse(str(e))


# 复制接口
def copy_api(request):
    api_id = request.GET['api_id']
    # 开始复制接口
    old_api = DB_apis.objects.filter(id=api_id)[0]

    DB_apis.objects.create(project_id=old_api.project_id,
                           name=old_api.name+'_副本',
                           api_method=old_api.api_method,
                           api_url=old_api.api_url,
                           api_header=old_api.api_header,
                           api_login=old_api.api_login,
                           api_host=old_api.api_host,
                           desc=old_api.desc,
                           body_method=old_api.body_method,
                           api_body=old_api.api_body,
                           result=old_api.result,
                           sign=old_api.sign,
                           file_key=old_api.file_key,
                           file_name=old_api.file_name,
                           public_header=old_api.public_header,
                           last_body_method=old_api.last_body_method,
                           last_api_body=old_api.last_api_body
                           )
    # 返回
    return HttpResponse('')


# 异常测试请求
def error_request(request):
    api_id = request.GET['api_id']
    new_body = request.GET['new_body']
    span_text = requests.GET['span_text']
    print(new_body)
    api = DB_apis.objects.filter(id=api_id)[0]
    method = api.api_method
    url = api.api_url
    host = api.api_host
    header = api.api_header
    body_method = api.body_method
    try:
        header = json.loads(header)
    except:
        return HttpResponse('请求头不符合json格式')
    if host[-1] == '/' and url[0] == '/':  # 都有/
        url = host[:-1] + url
    elif host[-1] != '/' and url[0] != '/':  # 都没有/
        url = host + '/' + url
    else:  # 肯定有一个有/
        url = host + url
    try:
        if body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(new_body):
                payload[i[0]] = i[1]
            response = requests.request(method.upper(), url, headers=header, data=payload, files=files)
        elif body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(new_body):
                payload[i[0]] = i[1]
            response = requests.request(method.upper(), url, headers=header, data=payload)
        elif body_method == 'Json':
            header['Content-Type'] = 'text/plain'
            response = requests.request(method.upper(), url, headers=header, data=new_body.encode('utf-8'))
        else:
            return HttpResponse('非法的请求体类型')
        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        res_json = {"response": "接口未通", "span_text": span_text}
        return HttpResponse(json.dumps(res_json), content_type='application/json')
    except:
        res_json = {"response": "接口未通", "span_text": span_text}
        return HttpResponse(json.dumps(res_json), content_type='application/json')


# 首页发送请求
def Api_send_home(request):
    # 提取所有数据
    print('qwe')
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_api_body = request.GET['ts_api_body']
    # 发送请求获取返回值
    try:
        header = json.loads(ts_header) #处理header
    except:
        return HttpResponse('请求头不符合json格式！')
    # 写入表中
    DB_apis_log.objects.create(user_id=request.user.id,
                               api_method=ts_method,
                               api_url=ts_url,
                               api_header=ts_header,
                               api_host=ts_host,
                               body_method=ts_body_method,
                               api_body=ts_api_body)
    # 拼接完整url
    if ts_host[-1] == '/' and ts_url[0] == '/':  # 都有/
        url = ts_host[:-1] + ts_url
    elif ts_host[-1] != '/' and ts_url[0] != '/':  # 都没有/
        url = ts_host+ '/' + ts_url
    else: #肯定有一个有/
        url = ts_host + ts_url
    try:
        if ts_body_method == 'none':
            response = requests.request(ts_method.upper(), url, headers=header, data={} )

        elif ts_body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(ts_api_body):
                payload[i[0]] = i[1]
            response = requests.request(ts_method.upper(), url, headers=header, data=payload, files=files )

        elif ts_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(ts_api_body):
                payload[i[0]] = i[1]
            response = requests.request(ts_method.upper(), url, headers=header, data=payload )

        else: #这时肯定是raw的五个子选项：
            if ts_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Json':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            response = requests.request(ts_method.upper(), url, headers=header, data=ts_api_body.encode('utf-8'))

        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        DB_host.objects.update_or_create(host=ts_host)
        return HttpResponse(response.text)
    except Exception as e:
        return HttpResponse(str(e))


# 首页获取请求记录
def get_home_log(request):
    user_id = request.user.id
    all_logs = DB_apis_log.objects.filter(user_id=user_id)
    ret = {"all_logs": list(all_logs.values("id", "api_method", "api_host", "api_url"))[::-1]}
    return HttpResponse(json.dumps(ret), content_type='application/json')


# 获取完整的单一请求记录数据
def get_api_log_home(request):
    log_id = request.GET['log_id']
    log = DB_apis_log.objects.filter(id=log_id)
    ret = {"log": list(log.values())[0]}
    return HttpResponse(json.dumps(ret), content_type='application/json')


# 增加用例
def add_case(request, eid):
    DB_cases.objects.create(project_id=eid, name='')
    return HttpResponseRedirect('/cases/%s/' % eid)


# 删除用例
def del_case(request, eid, oid):
    DB_cases.objects.filter(id=oid).delete()
    return HttpResponseRedirect('/cases/%s/' % eid)


# 复制用例
def copy_case(request, eid, oid):
    old_case = DB_cases.objects.filter(id=oid)[0]
    DB_cases.objects.create(project_id=old_case.project_id, name=old_case.name+'_副本')
    return HttpResponseRedirect('/cases/%s/' % eid)


# 保存用例名字
def save_case_name(request):
    id = request.GET['id']
    name = request.GET['name']
    DB_cases.objects.filter(id=id).update(name=name)
    return HttpResponse('')


# 获取小用例的数据
def get_small(request):
    case_id = request.GET['case_id']
    steps = DB_step.objects.filter(Case_id=case_id).order_by('index')
    ret = {"all_steps": list(steps.values("index", "id", "name"))}
    return HttpResponse(json.dumps(ret), content_type='application/json')


# 上传头像
def user_upload(request):
    file = request.FILES.get('fileUpload', None)
    if not file:
        return HttpResponseRedirect('/home/')

    new_name = str(request.user.id) + '.png'
    destination = open("Myapp/static/user_img/"+new_name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    return HttpResponseRedirect('/home/')


# 新增小步骤
def add_new_step(request):
    Case_id = request.GET['Case_id']
    all_len = len(DB_step.objects.filter(Case_id=Case_id))
    DB_step.objects.create(Case_id=Case_id, name='新增小步骤', index=all_len+1)
    return HttpResponse('')


# 删除小用例接口
def delete_step(request, eid):
    step = DB_step.objects.filter(id=eid)[0]
    index = step.index
    Case_id = step.Case_id
    step.delete()
    for i in DB_step.objects.filter(Case_id=Case_id).filter(index__gt=index):
        i.index -= 1
        i.save()
    return HttpResponse('')


# 获取小步骤
def get_step(request):
    step_id = request.GET['step_id']
    step = DB_step.objects.filter(id=step_id)
    steplist = list(step.values())[0]
    return HttpResponse(json.dumps(steplist), content_type='application/json')


# 保存小步骤
def save_step(request):
    step_id = request.GET['step_id']
    name = request.GET['name']
    index = request.GET['index']
    step_method = request.GET['step_method']
    step_url = request.GET['step_url']
    step_host = request.GET['step_host']
    step_header = request.GET['step_header']
    ts_project_headers = request.GET['ts_project_headers']
    mock_res = request.GET['mock_res']
    step_body_method = request.GET['step_body_method']
    step_api_body = request.GET['step_api_body']
    get_path = request.GET['get_path']
    get_zz = request.GET['get_zz']
    assert_zz = request.GET['assert_zz']
    assert_qz = request.GET['assert_qz']
    assert_path = request.GET['assert_path']

    DB_step.objects.filter(id=step_id).update(name=name,
                                              index=index,
                                              api_method=step_method,
                                              api_url=step_url,
                                              api_host=step_host,
                                              api_header=step_header,
                                              public_header=ts_project_headers,
                                              mock_res=mock_res,
                                              api_body_method=step_body_method,
                                              api_body=step_api_body,
                                              get_path=get_path,
                                              get_zz=get_zz,
                                              assert_zz=assert_zz,
                                              assert_qz=assert_qz,
                                              assert_path=assert_path,
                                              )
    return HttpResponse('')


# 步骤详情页获取接口数据
def step_get_api(request):
    api_id = request.GET['api_id']
    api = DB_apis.objects.filter(id=api_id).values()[0]
    return HttpResponse(json.dumps(api), content_type='application/json')


# 运行大用例
def run_case(request):
    case_id = request.GET['case_id']
    case = DB_cases.objects.filter(id=case_id)[0]
    steps = DB_step.objects.filter(Case_id=case_id)

    from Myapp.run_case import run
    run(case_id, case.name, steps)
    return HttpResponse('')


# 查看报告
def look_report(request, eid):
    case_id = eid

    return render(request, 'reports/%s.html' % case_id)


# 保存项目公共请求头
def save_project_header(request):
    project_id = request.GET['project_id']
    req_names = request.GET['req_names']
    req_keys = request.GET['req_keys']
    req_values = request.GET['req_values']
    req_ids = request.GET['req_ids']
    names = req_names.split(',')
    keys = req_keys.split(',')
    values = req_values.split(',')
    ids = req_ids.split(',')

    for i in range(len(ids)):
        if names[i] != '':
            if ids[i] == 'new':
                DB_project_header.objects.create(project_id=project_id, name=names[i], key=keys[i], value=values[i])
            else:
                DB_project_header.objects.filter(id=ids[i]).update(name=names[i], key=keys[i], value=values[i])
        else:
            try:
                DB_project_header.objects.filter(id=ids[i]).delete()
            except:
                pass
    return HttpResponse('')


# 保存项目公共域名
def save_project_host(request):
    project_id = request.GET['project_id']
    req_names = request.GET['req_names']
    req_hosts = request.GET['req_hosts']
    req_ids = request.GET['req_ids']
    names = req_names.split(',')
    hosts = req_hosts.split(',')
    ids = req_ids.split(',')
    for i in range(len(ids)):
        if names[i] != '':
            if ids[i] == 'new':
                DB_project_host.objects.create(project_id=project_id,name=names[i],host=hosts[i])
            else:
                DB_project_host.objects.filter(id=ids[i]).update(name=names[i],host=hosts[i])
        else:
            try:
                DB_project_host.objects.filter(id=ids[i]).delete()
            except:
                pass
    return HttpResponse('')











































