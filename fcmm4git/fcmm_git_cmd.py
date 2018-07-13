#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
FCMM针对Git的命令处理
@module fcmm_git_cmd
@file fcmm_git_cmd.py
"""

import os
import shutil
import tarfile
import json
import datetime
import logging
import traceback
import subprocess
from git import Repo
from snakerlib.generic import ExceptionTools, RunTools, FileTools, DebugTools


__MOUDLE__ = 'fcmm_git_cmd'  # 模块名
__DESCRIPT__ = 'FCMM针对Git的命令处理'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.05'  # 发布日期


class FcmmGitCmd(object):
    """
    FCMM针对Git的命令处理类
    """

    @staticmethod
    def main_cmd_fun(cmd='', cmd_para=''):
        """
        主含函数入口，所有命令都是走这个函数进行处理

        @decorators staticmethod

        @param {string} cmd='' - 命令
        @param {string} cmd_para='' - 参数字符串

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        back_obj = [0, '']
        # 通过switch字典实现switch的代码
        switch = {
            'cd': FcmmGitCmd.cmd_cd,
            'help': FcmmGitCmd.cmd_help,
            'init': FcmmGitCmd.cmd_init
        }
        try:
            dict_cmd_para = FcmmGitCmd.split_cmd_para(cmd_para)
            if 'h' in dict_cmd_para.keys() or 'help' in dict_cmd_para.keys():
                # 只是返回帮助文档
                back_obj = FcmmGitCmd.cmd_help({"cmd": ""})
            else:
                back_obj = switch[cmd](dict_cmd_para)
        except Exception as e:
            back_obj[0] = -1
            back_obj[1] = 'execute "%s %s" error : \n%s' % (cmd, cmd_para, traceback.format_exc())

        return back_obj

    #############################
    # 工具函数
    #############################

    @staticmethod
    def save_to_json_file(file_path, json_obj):
        """
        将dict对象写入json文件

        @decorators staticmethod

        @param {string} file_path - 要保存的文件路径（含文件名）
        @param {dict} json_obj - 要写入的对象
        """
        with open(file=file_path, mode='w', encoding='utf-8') as fp:
            fp.write(json.dumps(json_obj, indent=2))

    @staticmethod
    def split_cmd_para(cmd_para=''):
        """
        将命令参数字符串转换为key-value的字典格式

        @decorators staticmethod

        @param {string} cmd_para='' - 命令行参数

        @returns {dict} - 命令行参数字典，key为参数名(带-)，value为参数值
        """
        temp_array = cmd_para.split(' ')
        dict_cmd_para = dict()
        i = 0
        while i < len(temp_array):
            if temp_array[i] != '':
                if (temp_array[i].startswith('-') and i + 1 < len(temp_array) and
                        (not temp_array[i + 1].startswith('-'))):
                    dict_cmd_para[temp_array[i]] = temp_array[i + 1]
                    i = i + 2
                    continue
                else:
                    dict_cmd_para[temp_array[i]] = ''

            # 继续下一次寻找
            i = i + 1
            continue
        # 返回
        return dict_cmd_para

    @staticmethod
    def get_repo_info(work_dir):
        """
        从当前目录获取repo的信息

        @decorators staticmethod

        @param {string} work_dir - 工作目录

        @returns {dict} - 返回repo信息字典，格式为
            {
                'work_dir': '当前工作目录',
                'parent_dir': '工作目录的上一级目录',
                'repo': 'repo对象，获取不到为None'
            }
        """
        repo_info = dict()
        repo_info['work_dir'] = work_dir
        temp_dir = work_dir.rstrip('\\/')
        _index = temp_dir.replace('\\', '/').rfind('/')
        repo_info['parent_dir'] = temp_dir[0: _index]
        try:
            repo_info['repo'] = Repo(repo_info['work_dir'])
        except Exception as e:
            # 忽略异常，通过repo_info['repo']是否为None来进行后续处理
            repo_info['repo'] = None

        return repo_info

    @staticmethod
    def get_remote_repo_name(url):
        """
        根据url获取远程仓库的名字

        @decorators staticmethod

        @param {string} url - 远程仓库url

        @returns {string} - 仓库名字
        """
        remote_repo_name = url
        _index = url.rfind('/')
        if _index >= 0:
            remote_repo_name = remote_repo_name[_index + 1:]
        _index = remote_repo_name.rfind('.')
        if _index >= 0:
            remote_repo_name = remote_repo_name[0: _index]
        return remote_repo_name

    @staticmethod
    def backup_to_tar(src_path, save_path, save_name):
        """
        将指定目录打包成压缩包

        @decorators staticmethod

        @param {[type]} src_path - 要打包的目录路径
        @param {[type]} save_path - 保存路径
        @param {[type]} save_name - 保存文件名
        """
        with tarfile.open(save_path.rstrip('\\/') + '/' + save_name, "w:gz") as tar:
            tar.add(src_path, arcname=os.path.basename(src_path))

    @staticmethod
    def get_cmd_para_value(dict_cmd_para, short_para, long_para):
        """
        根据长短参数从命令中获取参数值

        @decorators staticmethod

        @param {dict} dict_cmd_para - 命令集
        @param {string} short_para - 短参数名
        @param {string} long_para - 长参数名

        @returns {string} - 获取到的参数值，如果获取不到返回None
        """
        value = dict_cmd_para.get(short_para)
        if value is None:
            value = dict_cmd_para.get(long_para)
        return value

    @staticmethod
    def get_must_has_para_tips(config, short_para, long_para):
        """
        获取必须包含参数的提示语句

        @decorators staticmethod

        @param {dict} config - 配置信息字典
        @param {string} short_para - 短参数
        @param {string} long_para - 长参数

        @returns {string} - 返回值
        """
        return (config['i18n_tips']['execute_fail'] + ': ' +
                config['i18n_tips']['must_has_para'] % (
                    ('%s/%s' % (long_para, short_para))) +
                '!')

    @staticmethod
    def run_sys_cmd(cmd_str):
        """
        执行操作系统命令（只判断成功与否，不处理返回信息）

        @decorators staticmethod

        @param {string} cmd_str - 要执行的命令

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        print('execute sys cmd: %s' % (cmd_str))
        complete_info = subprocess.run(cmd_str, shell=True)
        return [complete_info.returncode, '']

    #############################
    # Git相关操作原子函数
    #############################

    @staticmethod
    def get_fcmm_repo_config(work_dir=''):
        """
        获取本地fcmm4git节点信息

        @decorators staticmethod

        @param {string} work_dir - 要获取的工作目录

        @returns {dict} - 返回JSON配置信息对象，如果配置文件不存在，返回None
        """
        config_file_path = work_dir.rstrip('\\/') + '/.fcmm4git'
        json_str = ''
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
        except Exception as e:
            # 忽略异常，如果异常返回None
            return None

        return json.loads(json_str)

    @staticmethod
    def clone_remote_repo(url, path, rename=None, is_del_exit_dir=False):
        """
        克隆远程库到本地

        @decorators staticmethod

        @param {string} url - 远程库的地址
        @param {string} path - 本地主路径（不含repo目录）

        @param {string} rename=None - 本地目录重命名
        @param {bool} is_del_exit_dir=False - 如果本地目录已存在是否删除

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        repo_name = rename
        if repo_name is None:
            repo_name = FcmmGitCmd.get_remote_repo_name(url)
        full_path = os.path.realpath(path).rstrip('\\/') + '/'
        full_repo_path = full_path + repo_name

        # FIXME({$AUTHOR$}): DebugTool不显示
        DebugTools.debug_print(repo_name, full_path, full_repo_path)

        # 删除已存在的目录
        if os.path.exists(full_repo_path):
            if is_del_exit_dir:
                FileTools.remove_dir(full_repo_path)
            else:
                print('path is already exists: %s !' % (full_repo_path))
                return [1, '']
        # 克隆远程库
        os.chdir(full_path)  # 转到目录下
        return FcmmGitCmd.run_sys_cmd('git clone %s %s' % (url, repo_name))

    @staticmethod
    def check_tag_exists(repo, tag_name):
        """
        检查版本号是否已存在

        @decorators staticmethod

        @param {git.Repo} repo - 版本库
        @param {string} tag_name - 要检查的版本号

        @returns {bool} - 版本号是否已存在
        """
        is_exits = False
        for tag in repo.tags:
            if tag.name == tag_name:
                is_exits = True
                break
        return is_exits

    #############################
    # 具体命令处理函数
    #############################

    @staticmethod
    def cmd_cd(dict_cmd_para=None):
        """
        切换目录命令，为了适应cd命令无效的问题

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        if len(dict_cmd_para) > 0:
            # 带参数，修改路径
            os.chdir(sorted(dict_cmd_para.keys())[0])

        return FcmmGitCmd.run_sys_cmd('cd')

    @staticmethod
    def cmd_help(dict_cmd_para=None):
        """
        帮助命令，返回帮助显示信息

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 命令参数，取第一个显示帮助

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        config = RunTools.get_global_var('config')
        if len(dict_cmd_para) == 0:
            # 没有传入参数，返回全部命令的简要介绍
            return [0, config['help_text']['all']]
        else:
            # 返回指定命令的帮助信息
            return [0, config['help_text'][sorted(dict_cmd_para.keys())[0]]]

    @staticmethod
    def cmd_init(dict_cmd_para=None):
        """
        初始化FCMM版本库：根据指定的参数建立及初始化FCMM版本库

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 判断是否有帮助
        if '-h' in dict_cmd_para.keys() or '-help' in dict_cmd_para.keys():
            return FcmmGitCmd.cmd_help({'init': ''})

        # 需要获取的参数
        config = RunTools.get_global_var('config')

        # 最基础的参数校验
        url = FcmmGitCmd.get_cmd_para_value(dict_cmd_para, '-u', '-url')
        if url is None:
            return [1, FcmmGitCmd.get_must_has_para_tips(config, '-u', '-url')]

        base = FcmmGitCmd.get_cmd_para_value(dict_cmd_para, '-b', '-base')
        if base is None:
            return [1, FcmmGitCmd.get_must_has_para_tips(config, '-b', '-base')]

        ver = FcmmGitCmd.get_cmd_para_value(dict_cmd_para, '-v', '-version')
        if ver is not None and ver == '':
            return [1, config['i18n_tips']['version_no_value']]

        # 常用信息获取
        repo_info = FcmmGitCmd.get_repo_info(os.getcwd())  # 获取git库原生信息有建库
        repo_name = FileTools.get_dir_name(repo_info['work_dir'])
        # 获取fcmm4git配置信息
        fcmm_config = FcmmGitCmd.get_fcmm_repo_config(repo_info['work_dir'])
        remote_name = FcmmGitCmd.get_remote_repo_name(url)  # 远程仓库命名
        remote_repo_info = None
        remote_has_pkg = False
        remote_has_tag = False

        # 进行是否可处理的校验
        if base == 'local':
            if fcmm_config is not None:
                # 已经除初始化过fcmm4git，不允许重复处理exit_fcmm_file
                return [2, config['i18n_tips']['exit_fcmm_file']]
        else:
            # 检查本地目录是否为空
            if not ('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
                if os.listdir(repo_info['work_dir']):
                    return [3, config['i18n_tips']['local_not_bare']]

        # 需要将远程版本库下载下来比较处理
        fun_res = FcmmGitCmd.clone_remote_repo(url, config['temp_path'], None, True)
        if fun_res[0] != 0:
            return [fun_res[0], config['i18n_tips']['execute_fail']]
        remote_repo_info = FcmmGitCmd.get_repo_info(
            config['temp_path'].rstrip('\\/') + '/' + remote_name)
        # 尝试找远程的版本分支
        os.chdir(remote_repo_info['work_dir'])
        FcmmGitCmd.run_sys_cmd('git checkout --track origin/lb-pkg')
        for branch in remote_repo_info['repo'].branches:
            if branch.name == 'lb-pkg':
                remote_has_pkg = True
                break
        if ver is not None and FcmmGitCmd.check_tag_exists(remote_repo_info['repo'], ver):
            remote_has_tag = True

        if not ('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            # 没有强制标志，需要进行验证
            if base == 'local':
                if not remote_repo_info['repo'].bare:
                    return [3, config['i18n_tips']['remote_not_bare']]
            if remote_has_tag:
                # 检查版本号是否已存在
                return [3, config['i18n_tips']['remote_tag_exists']]

        # 检查通过或强制执行
        is_force_reset = False  # 标记是否强制更新服务器端版本
        if base == 'local':
            # 本地为准，打包备份到指备份目录中
            if not remote_repo_info['repo'].bare:
                FcmmGitCmd.backup_to_tar(
                    src_path=remote_repo_info['work_dir'],
                    save_path=config['backup_path'],
                    save_name='%s.bak.%s.tar' % (
                        remote_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
                )

            if '-r' in dict_cmd_para.keys() or '-reset' in dict_cmd_para.keys():
                # 强制替换服务器端的版本，以本地的版本库为准，直接强制替换
                # 如果不是git仓库，先初始化
                os.chdir(repo_info['work_dir'])
                if repo_info['repo'] is None:
                    fun_res = FcmmGitCmd.run_sys_cmd('git init')
                    if fun_res[0] != 0:
                        return [fun_res[0], config['i18n_tips']['execute_fail']]
                    repo_info = FcmmGitCmd.get_repo_info(repo_info['work_dir'])
                else:
                    # 如果原来有远程连接，解除连接
                    for remote_obj in repo_info['repo'].remotes:
                        fun_res = FcmmGitCmd.run_sys_cmd('git remote rm %s' % (remote_obj.name))
                        if fun_res[0] != 0:
                            return [fun_res[0], config['i18n_tips']['execute_fail']]

                # 绑定远程仓库
                fun_res = FcmmGitCmd.run_sys_cmd('git remote add origin %s' % (url))
                if fun_res[0] != 0:
                    return [fun_res[0], config['i18n_tips']['execute_fail']]

                # 指定强制更新服务器端
                is_force_reset = True
                remote_has_tag = False
            else:
                # 保留服务器端版本信息，用文件清除方式实现文件替换
                # 1：删除临时目录中远程分支的所有文件
                os.chdir(remote_repo_info['work_dir'])
                FcmmGitCmd.run_sys_cmd('git checkout master')
                fun_res = FcmmGitCmd.run_sys_cmd('git rm * -r')
                if fun_res[0] != 0:
                    return [fun_res[0], config['i18n_tips']['execute_fail']]
                # 2: 将本地目录中的文件复制到远程目录，删除本地目录，复制远程目录到本地目录
                FileTools.copy_all_with_path(
                    repo_info['work_dir'], remote_repo_info['work_dir'], '^(?!\\.git$)')
                FileTools.remove_all_with_path(repo_info['work_dir'])
                FileTools.copy_all_with_path(remote_repo_info['work_dir'], repo_info['work_dir'])
                os.chdir(repo_info['work_dir'])
        else:
            # 远程为准，打包备份到指备份目录中
            if os.listdir(repo_info['work_dir']):
                FcmmGitCmd.backup_to_tar(
                    src_path=repo_info['work_dir'],
                    save_path=config['backup_path'],
                    save_name='%s.%s.tar' % (
                        repo_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
                )
            # 复制远程目录到本地目录
            os.chdir(remote_repo_info['work_dir'])
            FileTools.remove_all_with_path(repo_info['work_dir'])
            FileTools.copy_all_with_path(remote_repo_info['work_dir'], repo_info['work_dir'])
            os.chdir(repo_info['work_dir'])

        # 完成本地版本库的建立和更新，统一进行配置参数处理和服务器的推送
        FcmmGitCmd.run_sys_cmd('git checkout master')
        fcmm_config_file = repo_info['work_dir'].rstrip('\\/') + '/.fcmm4git'
        if not os.path.exists(fcmm_config_file):
            fcmm_config = dict()
            fcmm_config['remote_url'] = url
            if '-n' in dict_cmd_para.keys() or '-nopkg' in dict_cmd_para.keys():
                fcmm_config['has_pkg'] = "False"
            else:
                fcmm_config['has_pkg'] = "True"
            FcmmGitCmd.save_to_json_file(fcmm_config_file, fcmm_config)
            # 提交修改
            FcmmGitCmd.run_sys_cmd('git add *')
            fun_res = FcmmGitCmd.run_sys_cmd('git commit -am "add .fcmm4git by fcmm4git"')
            if fun_res[0] != 0:
                return [fun_res[0], config['i18n_tips']['execute_fail']]
            # 设置版本信息
            ver = FcmmGitCmd.get_cmd_para_value(dict_cmd_para, '-v', '-version')
            if ver is not None:
                if remote_has_tag:
                    # 远程服务器已经有标签，应先删除标签，再新建
                    fun_res = FcmmGitCmd.run_sys_cmd(
                        'git tag -d %s' % (ver))
                    if fun_res[0] != 0:
                        return [fun_res[0], config['i18n_tips']['execute_fail']]

                fun_res = FcmmGitCmd.run_sys_cmd(
                    'git tag -a %s -m "add version by fcmm4git"' % (ver))
                if fun_res[0] != 0:
                    return [fun_res[0], config['i18n_tips']['execute_fail']]
        else:
            # 如果已经有.fcmm4git配置文件说明该目录已经初始化过，同步下来即可，不用再重新推送服务器
            return [0, config['i18n_tips']['just_clone_remote']]

        # 推送到服务器端
        push_force_tag = ''
        if is_force_reset:
            push_force_tag = '-f '
        fun_res = FcmmGitCmd.run_sys_cmd(
            'git push %s--follow-tags origin master' % (push_force_tag))
        if fun_res[0] != 0:
            return [fun_res[0], config['i18n_tips']['execute_fail']]
        # 添加版本分支
        if not ('-n' in dict_cmd_para.keys() or '-nopkg' in dict_cmd_para.keys()):
            if remote_has_pkg:
                # 远程仓库已有版本分支，要删除并强制推送
                fun_res = FcmmGitCmd.run_sys_cmd('git branch -d lb-pkg')
                if fun_res[0] != 0:
                    return [fun_res[0], config['i18n_tips']['execute_fail']]
                push_force_tag = '-f '  # 指定强制推送

            fun_res = FcmmGitCmd.run_sys_cmd('git checkout -b lb-pkg')
            if fun_res[0] != 0:
                return [fun_res[0], config['i18n_tips']['execute_fail']]
            fun_res = FcmmGitCmd.run_sys_cmd(
                'git push %s--follow-tags origin lb-pkg' % (push_force_tag))
            if fun_res[0] != 0:
                return [fun_res[0], config['i18n_tips']['execute_fail']]
            FcmmGitCmd.run_sys_cmd('git checkout master')

        # 返回执行成功
        return [0, config['i18n_tips']['execute_success']]


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
