#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
fcmm针对Git的命令处理工具模块
@module fcmm_git_tools
@file fcmm_git_tools.py
"""

import os
import datetime
import subprocess
from git import Repo
from fcmm_tools import FCMMTools
from snakerlib.generic import FileTools


__MOUDLE__ = 'fcmm_git_tools'  # 模块名
__DESCRIPT__ = 'fcmm针对Git的命令处理工具模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.19'  # 发布日期


class FCMMGitTools(object):
    """
    fcmm针对Git的命令处理工具类
    """

    @staticmethod
    def get_git_config_user_name(repo_info=None, encoding='GBK'):
        """
        获取git用户名

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} encoding='GBK' - 命令终端编码
        """
        cmd_str = ''
        username = ''
        if repo_info is None:
            cmd_str = 'git config --global user.name'
        else:
            os.chdir(repo_info['work_dir'])
            cmd_str = 'git config user.name'
        res = subprocess.run(cmd_str, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            username = res.stdout.decode(encoding=encoding).rstrip('\n\r')

        return username

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
            repo_name = FCMMGitTools.get_remote_repo_name(url)
        full_path = os.path.realpath(path).rstrip('\\/') + '/'
        full_repo_path = full_path + repo_name

        # 删除已存在的目录
        if os.path.exists(full_repo_path):
            if is_del_exit_dir:
                FileTools.remove_dir(full_repo_path)
            else:
                print('path is already exists: %s !' % (full_repo_path))
                return [1, '']
        # 克隆远程库
        os.chdir(full_path)  # 转到目录下
        return FCMMTools.run_sys_cmd('git clone %s %s' % (url, repo_name))

    @staticmethod
    def check_tag_exists(repo_info, tag_name):
        """
        检查版本号是否已存在

        @decorators staticmethod

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} tag_name - 要检查的版本号

        @returns {bool} - 版本号是否已存在
        """
        is_exits = False
        if repo_info is not None:
            for tag in repo_info['repo'].tags:
                if tag.name == tag_name:
                    is_exits = True
                    break
        return is_exits

    @staticmethod
    def check_branch_exists(repo_info, branch_name):
        """
        检查分支是否已存在

        @decorators staticmethod

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} branch_name - 要检查的分支名称

        @returns {bool} - 分支是否已存在

        """
        is_exits = False
        if repo_info is not None:
            for branch in repo_info['repo'].branches:
                if branch.name == branch_name:
                    is_exits = True
                    break
        return is_exits

    @staticmethod
    def check_branch_base_commit(repo_info, check_branch, source_branch, tag_name=None, commit=None):
        """
        检查指定分支是否基于源分支的某版本

        @decorators staticmethod

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} check_branch - 需要检查的分支
        @param {string} source_branch - 源分支
        @param {string} tag_name=None - 指定的tag标签
        @param {string} commit=None - 指定的commit标识

        @returns {bool} - 检查分支是否基于源分支指定版本
        """
        is_base = False
        check_commit = commit
        if tag_name is not None:
            for tag_item in repo_info['repo'].tags:
                if tag_item.name == tag_name:
                    check_commit = str(tag_item.commit)
                    break
            if check_commit is None:
                return False
        else:
            if check_commit is None:
                # 获取最新的版本
                for repo_branch in repo_info['repo'].branches:
                    if repo_branch.name == source_branch:
                        check_commit = str(repo_branch.commit)
                        break
                if check_commit is None:
                    return False
        # 根据check_commit进行检查
        for repo_branch in repo_info['repo'].branches:
            if repo_branch.name == check_branch:
                for commit_item in repo_branch.commit.tree:
                    if str(commit_item) == check_commit:
                        return True
        return is_base

    @staticmethod
    def get_active_branch(repo_info):
        """
        返回当前工作分支

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info

        @returns {string} - 分支名称
        """
        current_branch = ''
        if repo_info is not None:
            current_branch = repo_info['repo'].active_branch.name
        return current_branch

    @staticmethod
    def is_bare(repo_info):
        """
        检查仓库是否为空

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info

        @returns {bool} - 是否为空，True-空仓库，False-非空仓库
        """
        return repo_info['repo'].bare

    @staticmethod
    def is_dirty(repo_info):
        """
        检查仓库当前分支是否存在未提交内容

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info

        @returns {bool} - 是否存在未提交信息，True-存在未提交信息，False-已提交所有内容
        """
        return repo_info['repo'].is_dirty()

    @staticmethod
    def get_remote_branch(repo_info, branch):
        """
        获取远程分支到本地

        @decorators staticmethod

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} branch - 分支名

        @returns {list} - 执行结果[returncode, msgstring, is_local_new]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
            is_local_new - 本地是否新增分支
        """
        res = [0, '', False]
        local_has_branch = FCMMGitTools.check_branch_exists(repo_info, branch)
        if local_has_branch:
            # 本地已有分支
            res1 = FCMMTools.run_sys_cmd_list([
                'git checkout ' + branch,
                'git pull origin ' + branch
            ])
            res[0] = res1[0]
        else:
            # 本地没有分支，需新创建
            res1 = FCMMTools.run_sys_cmd_list([
                'git checkout -b %s origin/%s' % (branch, branch)
            ])
            res[0] = res1[0]
            res[2] = True
        return res

    @staticmethod
    def rollback_to_tag(repo_info, branch, tag):
        """
        回滚指定分支到指定的标签

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} branch - 分支名
        @param {string} tag - 标签名

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        commit_id = ''
        for tag_item in repo_info['repo'].tags:
            if tag_item.name == tag:
                commit_id = str(tag_item.commit)
                break
        if commit_id == '':
            return [1, 'tag_not_exists']

        current_branch = FCMMGitTools.get_active_branch(repo_info)
        os.chdir(repo_info['work_dir'])
        return FCMMTools.run_sys_cmd_list([
            'git checkout %s' % (branch),
            'git reset --hard %s' % (commit_id),
            'git push -f origin %s' % (branch),
            'git checkout %s' % (current_branch)
        ])

    @staticmethod
    def rollback_to_commit(repo_info, branch, commit):
        """
        回滚指定分支到指定的提交版本

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} branch - 分支名
        @param {string} commit - 提交标签

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        current_branch = FCMMGitTools.get_active_branch(repo_info)
        os.chdir(repo_info['work_dir'])
        return FCMMTools.run_sys_cmd_list([
            'git checkout %s' % (branch),
            'git reset --hard %s' % (commit),
            'git push -f origin %s' % (branch),
            'git checkout %s' % (current_branch)
        ])

    @staticmethod
    def add_branch(repo_info, new_branch, src_branch=None, tag=None, is_bare=False, commit=None):
        """
        通过其他分支或版本标签创建新分支

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} new_branch - 新分支名
        @param {string} src_branch=None - 源分支名
        @param {string} tag=None - 标签名
        @param {is_bare} is_bare=False - 是否创建空分支
            tag、src_branch、is_bare=True参数只需传入其中一个，优先取tag、其次为src_branch，最后为is_bare
        @param {string} commit=None - 如果是src_branch的情况，通过该参数获取指定commit的版本

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        current_branch = FCMMGitTools.get_active_branch(repo_info)
        os.chdir(repo_info['work_dir'])
        cmd_list = []
        if tag is not None:
            # 通过标签版本创建
            commit_id = ''
            for tag_item in repo_info['repo'].tags:
                if tag_item.name == tag:
                    commit_id = str(tag_item.commit)
                    break
            if commit_id == '':
                return [1, 'tag_not_exists']
            cmd_list.append('git branch %s %s' % (new_branch, tag))
            cmd_list.append('git checkout %s' % (new_branch))
        elif src_branch is not None:
            # 通过其他分支创建
            cmd_list.append('git checkout %s' % (src_branch))
            if commit is None:
                cmd_list.append('git checkout -b %s' % (new_branch))
            else:
                cmd_list.append('git checkout -b %s %s' % (new_branch, commit))
        elif is_bare:
            # 创建空库
            cmd_list.append('git checkout master')
            cmd_list.append('git checkout --orphan %s' % (new_branch))
            cmd_list.append('git rm -rf .')
            cmd_list.append('git commit -am "add bare branch by fcmm4git"')
        else:
            return [1, 'para tag、src_branch、is_bare=True must input one!']

        cmd_list.append('git push origin %s' % (new_branch))
        cmd_list.append('git checkout %s' % (current_branch))
        return FCMMTools.run_sys_cmd_list(cmd_list)

    @staticmethod
    def overwrite_branch(repo_info, dest_branch, src_branch=None, tag=None, is_bare=False, commit=None):
        """
        通过某分支覆盖指定分支

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} src_branch - 源分支名
        @param {string} dest_branch - 目标分支名
        @param {string} tag - 指定覆盖的版本标签
        @param {is_bare} is_bare=False - 是否创建空分支
            tag、src_branch、is_bare=True参数只需传入其中一个，优先取tag、其次为src_branch，最后为is_bare
        @param {string} commit=None - 如果是src_branch的情况，通过该参数获取指定commit的版本

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        current_branch = FCMMGitTools.get_active_branch(repo_info)
        os.chdir(repo_info['work_dir'])
        cmd_list = []
        cmd_list.append('git checkout master')
        cmd_list.append('git branch -d %s' % (dest_branch))  # 删除分支
        if tag is not None:
            # 使用标签创建
            commit_id = ''
            for tag_item in repo_info['repo'].tags:
                if tag_item.name == tag:
                    commit_id = str(tag_item.commit)
                    break
            if commit_id == '':
                return [1, 'tag_not_exists']
            cmd_list.append('git branch %s %s' % (dest_branch, tag))
            cmd_list.append('git checkout %s' % (dest_branch))
        elif src_branch is not None:
            # 使用其他分支创建
            cmd_list.append('git checkout %s' % (src_branch))
            if commit is None:
                cmd_list.append('git checkout -b %s' % (dest_branch))
            else:
                cmd_list.append('git checkout -b %s %s' % (dest_branch, commit))
        elif is_bare:
            # 创建空库
            cmd_list.append('git checkout master')
            cmd_list.append('git checkout --orphan %s' % (dest_branch))
            cmd_list.append('git rm -rf .')
            cmd_list.append('git commit -am "add bare branch by fcmm4git"')
        else:
            return [1, 'para tag、src_branch、is_bare=True must input one!']

        cmd_list.append('git push -f origin %s' % (dest_branch))
        cmd_list.append('git checkout %s' % (current_branch))
        return FCMMTools.run_sys_cmd_list(cmd_list)

    @staticmethod
    def backup_branch(repo_info, branch, op_user=''):
        """
        备份指定分支

        @decorators staticmethod - [description]

        @param {dict} repo_info - repo信息字典
            @see FCMMGitTools.get_repo_info
        @param {string} branch - 要备份的分支
        @param {string} op_user='' - 操作人

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        backup_name = 'tb-bak-' + branch + '-' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if op_user != '':
            backup_name = backup_name + '-by-' + op_user
        return FCMMGitTools.add_branch(repo_info, backup_name, branch)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
