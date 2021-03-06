#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
FCMM模型的GIT命令行工具，提高版本管理执行效率
@module fcmm
@file fcmm.py
"""

import subprocess
import inspect
import json
import sys
import os
import copy
import traceback
from snakerlib.generic import FileTools, ExceptionTools, RunTools
from snakerlib.prompt_plus import PromptPlus
from fcmm_git_cmd import FCMMGitCmd
import git


__MOUDLE__ = 'fcmm'  # 模块名
__DESCRIPT__ = 'FCMM模型的GIT命令行工具'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.05'  # 发布日期


def prompt_comm_fun(message='', cmd='', cmd_para='', with_returncode=False):
    """
    通用的命令交互执行函数，调用fcmm_git_cmd的命令执行处理

    @param {string} message='' - 命令行提示信息
    @param {string} cmd='' - 要执行的命令
    @param {string} cmd_para='' - 命令参数
    @param {bool} with_returncode=False - 控制返回结果格式，是否带有returncode

    @returns {string / list} - 分两种情况返回：
        如果with_returncode是False，只返回显示结果字符串
        如果with_returncode是True， 返回数组[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
    """
    back_obj = [0, '']
    try:
        config_cmd_para = RunTools.get_global_var('config_cmd_para')
        if cmd in config_cmd_para.keys():
            # 执行FCMM命令
            back_obj = FCMMGitCmd.main_cmd_fun(cmd=cmd, cmd_para=cmd_para)
        else:
            # 执行其他命令
            res = subprocess.run(('%s %s' % (cmd, cmd_para)).rstrip(' '), shell=True)
            back_obj = [res.returncode, '']
    except Exception as e:
        back_obj[0] = -1
        back_obj[1] = 'execute "%s %s" error : \n%s' % (cmd, cmd_para, traceback.format_exc())

    # 处理返回
    if with_returncode:
        return back_obj
    else:
        return back_obj[1]


def load_fcmm_config():
    """
    装载fcmm的程序启动参数，返回参数JSON对象
    """
    config_file_path = FileTools.get_exefile_path() + '/fcmm.json'
    json_str = ''
    with open(config_file_path, 'r', encoding='utf-8') as f:
        json_str = f.read()
    return json.loads(json_str)


def cmd_para_init(config):
    """
    根据输入参数初始化命令交互参数(将一些非字符串对象初始化)

    @param {dict} config - 从配置文件获取到的json对象

    @returns {dict} - 初始化后命令参数
    """
    cmd_para = copy.deepcopy(config['cmd_para'])
    for _key in cmd_para.keys():
        for _para in cmd_para[_key].keys():
            if _para == 'deal_fun':
                cmd_para[_key][_para] = prompt_comm_fun
            elif cmd_para[_key][_para] == 'None':
                cmd_para[_key][_para] = None
            elif _para == 'long_para':
                for _sub_para in cmd_para[_key][_para].keys():
                    if cmd_para[_key][_para][_sub_para] == 'None':
                        cmd_para[_key][_para][_sub_para] = None

    return cmd_para


def fcmm_init():
    """
    初始化fcmm程序
    """
    # 获取启动参数
    config = load_fcmm_config()

    # 处理真实路径（在其他路径被调用的情况不会找错位置）
    fcmm_path = os.path.split(os.path.realpath(inspect.getfile(inspect.currentframe())))[0]
    temp_str = os.getcwd()
    os.chdir(fcmm_path)
    config['fcmm_path'] = fcmm_path
    config['temp_path'] = os.path.realpath(config['temp_path'])
    config['backup_path'] = os.path.realpath(config['backup_path'])
    os.chdir(temp_str)

    RunTools.set_global_var('config', config)  # 设置到全局变量中

    # 创建临时目录
    with ExceptionTools.ignored((FileExistsError)):
        FileTools.create_dir(config['temp_path'])
        RunTools.set_global_var('temp_path', config['temp_path'])

    # 创建备份目录
    if config['backup_before'] != 'false':
        with ExceptionTools.ignored((FileExistsError)):
            FileTools.create_dir(config['backup_path'])
            RunTools.set_global_var('backup_path', config['backup_path'])

    # 初始化命令行参数
    config_cmd_para = cmd_para_init(config)
    RunTools.set_global_var('config_cmd_para', config_cmd_para)


def fcmm_run():
    """
    启动fcmm4git
    """
    fcmm_init()

    config = RunTools.get_global_var('config')
    config_cmd_para = RunTools.get_global_var('config_cmd_para')

    # 处理命令行参数
    argv_count = len(sys.argv)
    if argv_count == 1:
        # 没有带任何参数，直接进入命令行方式
        _prompt = PromptPlus(
            message='FCMM>',
            default='',  # 默认输入值
            cmd_para=config_cmd_para,  # 命令定义参数
            default_dealfun=prompt_comm_fun  # 默认处理函数
        )
        # 执行命令行
        _prompt.start_prompt_service(
            tips=config['tips'],
            is_async=False
        )
    else:
        # 直接按参数执行
        cmd_para_str = ' '.join(sys.argv[2:])
        back_obj = prompt_comm_fun(
            message='', cmd=sys.argv[1], cmd_para=cmd_para_str, with_returncode=True)
        print(back_obj[1])
        exit(back_obj[0])


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 初始化命令行并启动
    # fcmm_run()

    # repo = git.Repo(r'C:/Users/hi.li/Desktop/opensource/fcmm4git')
    # repo = git.Repo(r'D:/dev/github/test')
    repo = git.Repo(r'C:\Users\hi.li\Desktop\opensource\fcmm4git')
    # repo = git.Repo(r'C:/Users/hi.li/Desktop/opensource/fcmm4git-unittest')
    print(repo.branches[0].name)
    print(repo.branches[0].commit.tree[1])

    """
    print(repo.is_dirty())
    print(repo.tags[0].name)
    print(type(repo.tags[0].commit))
    print(str(repo.tags[0].commit))
    print(repo.branches[0].name)
    print(repo.branches[0].commit)
    print(repo.remotes[0].name)
    print(repo.remotes[0].url)
    print(repo.active_branch.name)
    print(repo.config)
    """

    """
    res = subprocess.run('hahha', shell=True)
    print('returncode:%s\n%s\n%s' % (res.returncode, res.stdout, res.stderr))

    res = subprocess.run("hahha1", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('returncode:%s\nstdout: %s\nstderr: %s' %
          (res.returncode, res.stdout.decode(sys.getfilesystemencoding()),
           res.stderr.decode(encoding='GBK')))

    print(u'测试')
    """
