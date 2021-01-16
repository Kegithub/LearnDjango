"""Apitest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path
from Myapp.views import *
from Myapp.views_tools import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('welcome/', welcome),
    path('home/', home),
    path('login/', login),
    path('logout/', logout),
    path('pei/', pei),
    path('help/', api_help),
    path('login_action/', login_action),
    path('register_action/', register_action),
    path('accounts/login/', login),
    url(r"^child/(?P<eid>.+)/(?P<oid>.*)/(?P<ooid>.*)/$", child),
    path('project_list/', project_list),
    path('delete_project/', delete_project),
    path('add_project/', add_project),
    re_path(r'^apis/(?P<id>.*)/$', open_apis),  # 进入接口库
    re_path(r'^cases/(?P<id>.*)/$', open_cases),  # 进入用例管理
    re_path(r'^project_set/(?P<id>.*)/$', open_project_set),  # 进入项目设置
    re_path(r'^save_project_set/(?P<id>.*)/$', save_project_set),  # 保存项目设置
    re_path(r'^project_api_add/(?P<Pid>.*)/$', project_api_add),  # 新增接口
    re_path(r'^project_api_del/(?P<id>.*)/$', project_api_del),  # 删除接口
    path('save_bz/', save_bz),  # 添加接口备注
    path('get_bz/', get_bz),  # 获取接口备注
    path('Api_save/', Api_save),  # 保存接口
    path('get_api_data/', get_api_data),  # 获取接口数据
    path('Api_send/', Api_send),  # 调试层发送请求
    path('copy_api/', copy_api),  # 复制接口
    path('error_request/', error_request),  # 调用异常测试接口
    path('Api_send_home/', Api_send_home),  # 首页发送请求
    path('get_home_log/', get_home_log),  # 获取首页请求记录
    path('get_api_log_home/', get_api_log_home),
    re_path(r'^home_log/(?P<log_id>.*)/$', home),  # 再次进入首页，带着请求记录
    re_path(r'^add_case/(?P<eid>.*)/$', add_case),  # 增加用例
    re_path(r'^del_case/(?P<eid>.*)/(?P<oid>.*)/$', del_case),  # 删除用例
    re_path(r'^copy_case/(?P<eid>.*)/(?P<oid>.*)/$', copy_case),  # 复制用例
    path('get_small/', get_small),  # 获取小用例的列表数据
    path('user_upload/', user_upload),  # 上传头像
    path('add_new_step/', add_new_step),  # 新增小步骤接口
    re_path(r'^delete_step/(?P<eid>.*)/$', delete_step),  # 删除小步骤接口
    path('get_step/', get_step),  # 获取小步骤
    path('save_step/', save_step),  # 保存小步骤
    path('step_get_api/', step_get_api),  # 步骤详情页获取接口数据
    path('run_case/', run_case),  # 运行大用例
    re_path(r'^look_report/(?P<eid>.*)/$', look_report),  # 查看报告
    path('save_project_header/', save_project_header),  # 保存项目公共请求头
    path('save_case_name/', save_case_name),  # 保存用例名字
    path('save_project_host/', save_project_host),  # 保存项目全局域名
    path('project_get_login/', project_get_login),  # 获取项目登录态接口
    path('project_login_save/', project_login_save),  # 保存项目登录态接口
    path('project_login_send/', project_login_send),  # 调试登录态接口


    # -----小工具------ #
    path('tools_zhengjiao/', zhengjiao),  # 进入正交工具页面
    path('zhengjiao_play/', zhengjiao_play),  # 正交工具运行
    path('zhengjiao_excel/', zhengjiao_excel),  # 正交工具导出
]
