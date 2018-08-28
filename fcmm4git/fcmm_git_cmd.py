#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
FCMM针对Git的命令处理
@module fcmm_git_cmd
@file fcmm_git_cmd.py
"""

import os
import datetime
import traceback
from snakerlib.generic import RunTools, FileTools
from fcmm_tools import FCMMTools
from fcmm_git_tools import FCMMGitTools


__MOUDLE__ = 'fcmm_git_cmd'  # 模块名
__DESCRIPT__ = 'FCMM针对Git的命令处理'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.05'  # 发布日期


class FCMMGitCmd(object):
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
            'cd': FCMMGitCmd.cmd_cd,
            'help': FCMMGitCmd.cmd_help,
            'init': FCMMGitCmd.cmd_init,
            'add-pkg': FCMMGitCmd.cmd_add_pkg,
            'add-dev': FCMMGitCmd.cmd_add_dev,
            'add-temp': FCMMGitCmd.cmd_add_temp,
            'rollback': FCMMGitCmd.cmd_rollback,
            'check': FCMMGitCmd.cmd_check
        }
        try:
            dict_cmd_para = FCMMTools.split_cmd_para(cmd_para)
            if 'h' in dict_cmd_para.keys() or 'help' in dict_cmd_para.keys():
                # 只是返回帮助文档
                back_obj = FCMMGitCmd.cmd_help({"cmd": ""})
            else:
                back_obj = switch[cmd](dict_cmd_para)
        except Exception as e:
            back_obj[0] = -1
            back_obj[1] = 'execute "%s %s" error : \n%s' % (cmd, cmd_para, traceback.format_exc())

        return back_obj

    #############################
    # 通用逻辑集合处理
    #############################

    @staticmethod
    def cmd_common_init(cmd_str='', dict_cmd_para=None):
        """
        通用命令前期通用处理
        具体处理的内容包括：
            1、判断是否帮助
            2、基础参数校验
            3、检查当前环境是否未提交，如果未提交不允许继续处理
            4、检查本地配置文件及仓库信息是否准确
            5、更新master分支和lb-pkg分支的最新本地版本

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {tuple} - 返回多个值的数组，按顺序如下
            is_exit {bool} - 标识是否应直接，不进行后续的处理
            return_obj {list} - 直接退出的执行结果[returncode, msgstring]
                returncode - 0代表成功，其他代表失败
                msgstring - 要返回显示的内容
            config {dict} - 获取到的全局参数config
            fcmm_config {dict} - 获取到的.fcmm4git配置信息
            repo_info {dict} - 获取到的本地仓库信息
            current_branch {string} - 当前本地工作分支

        """
        # 判断是否有帮助
        if '-h' in dict_cmd_para.keys() or '-help' in dict_cmd_para.keys():
            return (True, FCMMGitCmd.cmd_help({cmd_str: ''}), None, None, None, None)

        # 最基础的参数校验
        res = FCMMTools.vailidate_cmd_para(dict_cmd_para, cmd_str)
        if res[0] != 0:
            return (True, res, None, None, None, None)

        # 本地仓库信息检查
        config = RunTools.get_global_var('config')
        repo_info = FCMMGitTools.get_repo_info(os.getcwd())
        fcmm_config = FCMMTools.get_fcmm_config(repo_info['work_dir'])
        if repo_info['repo'] is None or fcmm_config is None:
            return (True, [2, FCMMTools.get_i18n_tips(config, 'local_git_error')], None, None, None, None)

        # 检查当前分支是否存在未提交信息
        if FCMMGitTools.is_dirty(repo_info):
            return (True, [2, FCMMTools.get_i18n_tips(config, 'current_branch_is_dirty')], None, None, None, None)

        # 下载最新的master分支
        current_branch = FCMMGitTools.get_active_branch(repo_info)
        try:
            res = FCMMTools.run_sys_cmd_list([
                'git checkout master',
                'git pull origin master'
            ])
            if res[0] != 0:
                return (True, [res[0], FCMMTools.get_i18n_tips(config, 'execute_fail')], None, None, None, None)
            fcmm_config = FCMMTools.get_fcmm_config(repo_info['work_dir'])
            if fcmm_config is None:
                return (True, [2, FCMMTools.get_i18n_tips(config, 'local_git_error')], None, None, None, None)

            # 判断是否有版本分支
            if fcmm_config['has_pkg'] == "true":
                # 要下载版本分支，绑定与本地版本分支的关系
                res = FCMMGitTools.get_remote_branch(repo_info, 'lb-pkg')

                # 处理结果
                if res[0] != 0:
                    return (True, [res[0], FCMMTools.get_i18n_tips(config, 'execute_fail')], None, None, None, None)

        finally:
            # 最后尝试跳转回工作分支
            FCMMTools.run_sys_cmd('git checkout %s' % (current_branch))

        # 最后返回
        return (False, [0, ''], config, fcmm_config, repo_info, current_branch)

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

        return FCMMTools.run_sys_cmd('cd')

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
        # 最基础的参数校验
        res = FCMMTools.vailidate_cmd_para(dict_cmd_para, 'help')
        if res[0] != 0:
            return res

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
            return FCMMGitCmd.cmd_help({'init': ''})

        # 需要获取的参数
        config = RunTools.get_global_var('config')

        # 最基础的参数校验
        res = FCMMTools.vailidate_cmd_para(dict_cmd_para, 'init')
        if res[0] != 0:
            return res

        # 要处理的参数
        url = FCMMTools.get_cmd_para_value(dict_cmd_para, '-u', '-url')
        base = FCMMTools.get_cmd_para_value(dict_cmd_para, '-b', '-base')
        ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')

        # 常用信息获取
        repo_info = FCMMGitTools.get_repo_info(os.getcwd())  # 获取git库原生信息有建库
        repo_name = FileTools.get_dir_name(repo_info['work_dir'])
        # 获取fcmm4git配置信息
        fcmm_config = FCMMTools.get_fcmm_config(repo_info['work_dir'])
        remote_name = FCMMGitTools.get_remote_repo_name(url)  # 远程仓库命名
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
        fun_res = FCMMGitTools.clone_remote_repo(url, config['temp_path'], None, True)
        if fun_res[0] != 0:
            return [fun_res[0], config['i18n_tips']['execute_fail']]
        remote_repo_info = FCMMGitTools.get_repo_info(
            config['temp_path'].rstrip('\\/') + '/' + remote_name)
        # 尝试找远程的版本分支
        os.chdir(remote_repo_info['work_dir'])
        FCMMTools.run_sys_cmd('git checkout --track origin/lb-pkg')
        remote_has_pkg = FCMMGitTools.check_branch_exists(remote_repo_info, 'lb-pkg')
        if ver is not None and FCMMGitTools.check_tag_exists(remote_repo_info['repo'], ver):
            remote_has_tag = True

        if not ('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            # 没有强制标志，需要进行验证
            if base == 'local':
                if not FCMMGitTools.is_bare(remote_repo_info):
                    return [3, config['i18n_tips']['remote_not_bare']]
            if remote_has_tag:
                # 检查版本号是否已存在
                return [3, config['i18n_tips']['remote_tag_exists']]

        # 检查通过或强制执行
        is_force_reset = False  # 标记是否强制更新服务器端版本
        if base == 'local':
            # 本地为准，打包备份到指备份目录中
            if not FCMMGitTools.is_bare(remote_repo_info):
                FCMMTools.backup_to_tar(
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
                    fun_res = FCMMTools.run_sys_cmd('git init')
                    if fun_res[0] != 0:
                        return [fun_res[0], config['i18n_tips']['execute_fail']]
                    repo_info = FCMMGitTools.get_repo_info(repo_info['work_dir'])
                else:
                    # 如果原来有远程连接，解除连接
                    for remote_obj in repo_info['repo'].remotes:
                        fun_res = FCMMTools.run_sys_cmd('git remote rm %s' % (remote_obj.name))
                        if fun_res[0] != 0:
                            return [fun_res[0], config['i18n_tips']['execute_fail']]

                # 绑定远程仓库
                fun_res = FCMMTools.run_sys_cmd('git remote add origin %s' % (url))
                if fun_res[0] != 0:
                    return [fun_res[0], config['i18n_tips']['execute_fail']]

                # 指定强制更新服务器端
                is_force_reset = True
                remote_has_tag = False
            else:
                # 保留服务器端版本信息，用文件清除方式实现文件替换
                # 1：删除临时目录中远程分支的所有文件
                os.chdir(remote_repo_info['work_dir'])
                FCMMTools.run_sys_cmd('git checkout master')
                FCMMTools.run_sys_cmd('git rm * -r')

                # 2: 将本地目录中的文件复制到远程目录，删除本地目录，复制远程目录到本地目录
                FileTools.copy_all_with_path(
                    repo_info['work_dir'], remote_repo_info['work_dir'], '^(?!\\.git$)')
                FileTools.remove_all_with_path(repo_info['work_dir'])
                FileTools.copy_all_with_path(remote_repo_info['work_dir'], repo_info['work_dir'])
                os.chdir(repo_info['work_dir'])
        else:
            # 远程为准，打包备份到指备份目录中
            if os.listdir(repo_info['work_dir']):
                FCMMTools.backup_to_tar(
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
        FCMMTools.run_sys_cmd('git checkout master')
        fcmm_config_file = repo_info['work_dir'].rstrip('\\/') + '/.fcmm4git'
        if not os.path.exists(fcmm_config_file):
            fcmm_config = dict()
            fcmm_config['remote_url'] = url
            if '-n' in dict_cmd_para.keys() or '-nopkg' in dict_cmd_para.keys():
                fcmm_config['has_pkg'] = "false"
            else:
                fcmm_config['has_pkg'] = "true"
            FCMMTools.save_to_json_file(fcmm_config_file, fcmm_config)
            # 提交修改
            FCMMTools.run_sys_cmd('git add *')
            fun_res = FCMMTools.run_sys_cmd('git commit -am "add .fcmm4git by fcmm4git"')
            if fun_res[0] != 0:
                return [fun_res[0], config['i18n_tips']['execute_fail']]
            # 设置版本信息
            ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')
            if ver is not None:
                if remote_has_tag:
                    # 远程服务器已经有标签，应先删除标签，再新建
                    fun_res = FCMMTools.run_sys_cmd(
                        'git tag -d %s' % (ver))
                    if fun_res[0] != 0:
                        return [fun_res[0], config['i18n_tips']['execute_fail']]

                fun_res = FCMMTools.run_sys_cmd(
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
        fun_res = FCMMTools.run_sys_cmd(
            'git push %s--follow-tags origin master' % (push_force_tag))
        if fun_res[0] != 0:
            return [fun_res[0], config['i18n_tips']['execute_fail']]
        # 添加版本分支
        if not ('-n' in dict_cmd_para.keys() or '-nopkg' in dict_cmd_para.keys()):
            if remote_has_pkg:
                # 远程仓库已有版本分支，要删除并强制推送
                fun_res = FCMMTools.run_sys_cmd('git branch -d lb-pkg')
                if fun_res[0] != 0:
                    return [fun_res[0], config['i18n_tips']['execute_fail']]
                push_force_tag = '-f '  # 指定强制推送

            fun_res = FCMMTools.run_sys_cmd('git checkout -b lb-pkg')
            if fun_res[0] != 0:
                return [fun_res[0], config['i18n_tips']['execute_fail']]
            fun_res = FCMMTools.run_sys_cmd(
                'git push %s--follow-tags origin lb-pkg' % (push_force_tag))
            if fun_res[0] != 0:
                return [fun_res[0], config['i18n_tips']['execute_fail']]
            FCMMTools.run_sys_cmd('git checkout master')

        # 返回执行成功
        return [0, config['i18n_tips']['execute_success']]

    @staticmethod
    def cmd_add_pkg(dict_cmd_para=None):
        """
        新增FCMM的pkg分支，如果原分支存在，可以重置分支

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'add-pkg', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')
        has_pkg = FCMMGitTools.check_branch_exists(repo_info, 'lb-pkg')
        if not('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            if has_pkg:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_has_exists', 'lb-pkg')]
            # 检查版本
            if ver is not None and not FCMMGitTools.check_tag_exists(repo_info, ver):
                return [1, FCMMTools.get_i18n_tips(config, 'tag_not_exists', ver)]

        # 开始进行处理
        if has_pkg:
            # 分支已存在，覆盖分支
            if config['backup_before'] == 'true':
                res = FCMMGitTools.backup_branch(
                    repo_info,
                    'lb-pkg',
                    FCMMGitTools.get_git_config_user_name(repo_info, config['consle_encode'])
                )
            if res[0] == 0:
                res = FCMMGitTools.overwrite_branch(repo_info, 'lb-pkg', 'master', ver)
        else:
            # 分支不存在，创建分支并推送到远端
            res = FCMMTools.run_sys_cmd('git checkout master')
            if res[0] == 0:
                fcmm_config['has_pkg'] = "true"
                FCMMTools.save_to_json_file(repo_info['work_dir'], fcmm_config)
                res = FCMMTools.run_sys_cmd_list([
                    'git add *',
                    'git commit -m "change .fcmm4gig by tools"',
                    'git push origin master'
                ])
                if res[0] == 0:
                    res = FCMMGitTools.add_branch(repo_info, 'lb-pkg', 'master', ver)

        # 返回值
        FCMMTools.run_sys_cmd('git checkout %s' % (current_branch))
        if res[0] != 0:
            res[1] = FCMMTools.get_i18n_tips(config, 'execute_fail')
        return res

    @staticmethod
    def cmd_add_cfg(dict_cmd_para=None):
        """
        新增FCMM的cfg分支，如果原分支存在，可以重置分支

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'add-cfg', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        cfg_branch_name = 'lb-cfg-' + FCMMTools.get_cmd_para_value(dict_cmd_para, '-n', '-name')
        res = FCMMGitTools.get_remote_branch(repo_info, cfg_branch_name)
        has_cfg_branch = False
        if res[0] == 0:
            has_cfg_branch = True
        elif not res[2]:
            # 远程节点存在但处理失败
            res[1] = FCMMTools.get_i18n_tips(config, 'execute_fail')
            return res

        if not('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            if has_cfg_branch:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_has_exists', cfg_branch_name)]

        para_clone = FCMMTools.get_cmd_para_value(dict_cmd_para, '-c', '-clone')
        para_bare = FCMMTools.get_cmd_para_value(dict_cmd_para, '-b', '-bare')
        if para_bare is None and para_clone is None:
            return [1, FCMMTools.get_i18n_tips(config, 'must_has_para', '-bare / -b 或 -clone / -c')]

        clone_branch_name = ''
        if para_bare is None:
            clone_branch_name = 'lb-cfg-' + para_clone
            res = FCMMGitTools.get_remote_branch(repo_info, clone_branch_name)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', clone_branch_name)]

        # 进行实际的处理
        if has_cfg_branch:
            # 先备份
            if config['backup_before'] == 'true':
                res = FCMMGitTools.backup_branch(
                    repo_info,
                    cfg_branch_name,
                    FCMMGitTools.get_git_config_user_name(repo_info, config['consle_encode'])
                )
            if res[0] == 0:
                if clone_branch_name != '':
                    res = FCMMGitTools.overwrite_branch(
                        repo_info, cfg_branch_name, src_branch=clone_branch_name)
                else:
                    res = FCMMGitTools.overwrite_branch(repo_info, cfg_branch_name, is_bare=True)
        else:
            if clone_branch_name != '':
                res = FCMMGitTools.add_branch(
                    repo_info, cfg_branch_name, src_branch=clone_branch_name)
            else:
                res = FCMMGitTools.add_branch(repo_info, cfg_branch_name, is_bare=True)

        return res

    @staticmethod
    def cmd_add_dev(dict_cmd_para=None):
        """
        新增FCMM的dev分支，如果原分支存在，可以重置分支

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'add-dev', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        branch_name = 'tb-%s-%s' % (
            FCMMTools.get_cmd_para_value(dict_cmd_para, '-t', '-type '),
            FCMMTools.get_cmd_para_value(dict_cmd_para, '-n', '-name')
        )
        res = FCMMGitTools.get_remote_branch(repo_info, branch_name)
        has_branch = False
        if res[0] == 0:
            has_branch = True
        elif not res[2]:
            # 远程节点存在但处理失败
            res[1] = FCMMTools.get_i18n_tips(config, 'execute_fail')
            return res
        if not('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            if has_branch:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_has_exists', has_branch)]

        clone_branch_name = ''
        para_clone = FCMMTools.get_cmd_para_value(dict_cmd_para, '-c', '-clone')
        ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')
        if ver is not None and not FCMMGitTools.check_tag_exists(repo_info, ver):
            return [1, FCMMTools.get_i18n_tips(config, 'tag_not_exists', ver)]

        if para_clone is None or ver is not None:
            if fcmm_config['has_pkg'] == "true":
                clone_branch_name = 'lb-pkg'
            else:
                clone_branch_name = 'master'
        else:
            clone_branch_name = 'tb-' + para_clone
            res = FCMMGitTools.get_remote_branch(repo_info, clone_branch_name)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', clone_branch_name)]
        tag = FCMMTools.get_cmd_para_value(dict_cmd_para, '-tag', '-tag')

        # 进行实际的处理
        if has_branch:
            # 先备份
            if config['backup_before'] == 'true':
                res = FCMMGitTools.backup_branch(
                    repo_info,
                    branch_name,
                    FCMMGitTools.get_git_config_user_name(repo_info, config['consle_encode'])
                )
            if res[0] == 0:
                res = FCMMGitTools.overwrite_branch(
                    repo_info, branch_name, src_branch=clone_branch_name, tag=ver, commit=tag)
        else:
            res = FCMMGitTools.add_branch(repo_info, branch_name,
                                          src_branch=clone_branch_name, tag=ver, commit=tag)

        return res

    @staticmethod
    def cmd_add_temp(dict_cmd_para=None):
        """
        新增FCMM的开发者临时分支，如果原分支存在，可以重置分支

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'add-temp', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        branch_name = 'tb-dev-%s' % (
            FCMMTools.get_cmd_para_value(dict_cmd_para, '-n', '-name')
        )
        clone_branch_name = FCMMGitTools.get_active_branch(repo_info)
        res = FCMMGitTools.get_remote_branch(repo_info, branch_name)
        has_branch = False
        if res[0] == 0:
            has_branch = True
        elif not res[2]:
            # 远程节点存在但处理失败
            res[1] = FCMMTools.get_i18n_tips(config, 'execute_fail')
            return res
        if not('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            if has_branch:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_has_exists', branch_name)]

        # 进行处理
        para_bare = FCMMTools.get_cmd_para_value(dict_cmd_para, '-b', '-bare')
        if has_branch:
            if para_bare:
                res = FCMMGitTools.overwrite_branch(
                    repo_info, branch_name, is_bare=True)
            else:
                res = FCMMGitTools.overwrite_branch(
                    repo_info, branch_name, src_branch=clone_branch_name)
        else:
            if para_bare:
                res = FCMMGitTools.add_branch(
                    repo_info, branch_name, is_bare=True)
            else:
                res = FCMMGitTools.add_branch(
                    repo_info, branch_name, src_branch=clone_branch_name)

        return res

    @staticmethod
    def cmd_rollback(dict_cmd_para=None):
        """
        将指定分支回退到指定版本

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'rollback', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        branch_name = FCMMTools.get_cmd_para_value(dict_cmd_para, '-n', '-name')
        if branch_name is None:
            # 获取当前工作分支
            branch_name = FCMMGitTools.get_active_branch(repo_info)
        else:
            # 检查分支是否存在
            res = FCMMGitTools.get_remote_branch(repo_info, branch_name)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', branch_name)]

        # master和lb-pkg分支不允许回退
        if not('-f' in dict_cmd_para.keys() or '-force' in dict_cmd_para.keys()):
            if branch_name == 'master' or branch_name == 'lb-pkg':
                return [1, FCMMTools.get_i18n_tips(config, 'master_pkg_no_rollback')]

        ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')
        tag = FCMMTools.get_cmd_para_value(dict_cmd_para, '-t', '-tag')
        if ver is None and tag is None:
            return [1, FCMMTools.get_i18n_tips(config, 'must_has_para', 'version / tag')]

        # 进行处理
        # 先进行备份
        if config['backup_before'] == 'true':
            res = FCMMGitTools.backup_branch(
                repo_info,
                branch_name,
                FCMMGitTools.get_git_config_user_name(repo_info, config['consle_encode'])
            )
        if res[0] == 0:
            # 处理回滚
            if branch_name == 'master' or branch_name == 'lb-pkg':
                # 采取回滚方式处理
                if ver is not None:
                    res = FCMMGitTools.rollback_to_tag(repo_info, branch_name, ver)
                else:
                    res = FCMMGitTools.rollback_to_commit(repo_info, branch_name, tag)
            else:
                # 采取覆盖方式处理
                src_branch = 'master'
                if fcmm_config['has_pkg'] == 'true':
                    src_branch = 'lb-pkg'
                res = FCMMGitTools.overwrite_branch(
                    repo_info, branch_name, src_branch, tag=ver, commit=tag)

        # 返回结果
        return res

    @staticmethod
    def cmd_check(dict_cmd_para=None):
        """
        检查分支的基础版本与指定分支是否一致（比较版本在检查分支的历史节点里）

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'check', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        branch_name = FCMMTools.get_cmd_para_value(dict_cmd_para, '-n', '-name')
        if branch_name is None:
            # 获取当前工作分支
            branch_name = FCMMGitTools.get_active_branch(repo_info)
        else:
            # 检查分支是否存在
            res = FCMMGitTools.get_remote_branch(repo_info, branch_name)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', branch_name)]
        source_branch = FCMMTools.get_cmd_para_value(dict_cmd_para, '-s', '-source')
        if source_branch is None:
            if fcmm_config['has_pkg'] == 'true':
                source_branch = 'lb-pkg'
            else:
                source_branch = 'master'
        else:
            # 检查分支是否存在
            res = FCMMGitTools.get_remote_branch(repo_info, source_branch)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', source_branch)]
        # 检查分支是否同一个
        if branch_name == source_branch:
            return [1, FCMMTools.get_i18n_tips(config, 'check_branch_is_same', source_branch)]
        ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')
        # 检查版本号是否一致
        if ver is not None and not FCMMGitTools.check_tag_exists(repo_info, ver):
            return [1, FCMMTools.get_i18n_tips(config, 'tag_not_exists', ver)]
        # 获取版本号
        tag = FCMMTools.get_cmd_para_value(dict_cmd_para, '-t', '-tag')

        # 执行处理
        is_base = FCMMGitTools.check_branch_base_commit(
            repo_info, branch_name, source_branch, ver, tag)
        if is_base:
            return [0, FCMMTools.get_i18n_tips(config, 'branch_check_pass')]
        else:
            return [1, FCMMTools.get_i18n_tips(config, 'branch_check_failed')]

    @staticmethod
    def cmd_merge(dict_cmd_para=None):
        """
        将指定分支版本合并到当前分支中

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        # 进行初始化
        is_exit, res, config, fcmm_config, repo_info, current_branch = FCMMGitCmd.cmd_common_init(
            'merge', dict_cmd_para)
        if is_exit:
            return res

        # 进一步检查
        branch_name = FCMMTools.get_cmd_para_value(dict_cmd_para, '-d', '-dest')
        if branch_name is None:
            # 获取当前工作分支
            branch_name = FCMMGitTools.get_active_branch(repo_info)
        else:
            # 检查分支是否存在
            res = FCMMGitTools.get_remote_branch(repo_info, branch_name)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', branch_name)]
        source_branch = FCMMTools.get_cmd_para_value(dict_cmd_para, '-s', '-source')
        if source_branch is None:
            if fcmm_config['has_pkg'] == 'true':
                source_branch = 'lb-pkg'
            else:
                source_branch = 'master'
        else:
            # 检查分支是否存在
            res = FCMMGitTools.get_remote_branch(repo_info, source_branch)
            if res[0] != 0:
                return [1, FCMMTools.get_i18n_tips(config, 'branch_not_exists', source_branch)]
        # 检查分支是否同一个
        if branch_name == source_branch:
            return [1, FCMMTools.get_i18n_tips(config, 'check_branch_is_same', source_branch)]
        ver = FCMMTools.get_cmd_para_value(dict_cmd_para, '-v', '-version')
        # 检查版本号是否一致
        if ver is not None and not FCMMGitTools.check_tag_exists(repo_info, ver):
            return [1, FCMMTools.get_i18n_tips(config, 'tag_not_exists', ver)]
        # 获取版本号
        tag = FCMMTools.get_cmd_para_value(dict_cmd_para, '-t', '-tag')


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
