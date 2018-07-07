#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
import sys
import os
import subprocess
import platform
import git
sys.path.append('../fcmm4git/')
import fcmm
import fcmm_git_cmd
from snakerlib.generic import FileTools


__MOUDLE__ = 'test_fcmm'  # 模块名
__DESCRIPT__ = 'fcmm测试'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.07'  # 发布日期

# 临时测试目录
FCMM_PATH = os.path.realpath('../fcmm4git/')
TEST_PATH = os.path.realpath('./temptest/')
TEST_REPO_URL = 'https://github.com/snakeclub/fcmm4git-unittest.git'
"""
注意TEST_REPO_URL必须有一个tag标记为null的无文件的提交，我们将回滚到这个版本进行测试
git rm * -r
git commit -a -m "null update"
git tag -a null -m '空白测试版本'
git push origin master --tags
"""


class TestFcmm(unittest.TestCase):
    """
    fcmm单元测试类测试
    """

    def setUp(self):
        """
        启动测试执行的初始化
        """
        if os.path.exists(TEST_PATH):
            if platform.system() == 'Windows':
                subprocess.run('rmdir /S /Q %s' % (TEST_PATH), shell=True)
            else:
                FileTools.remove_dir(TEST_PATH)

        FileTools.create_dir(TEST_PATH)
        return

    def tearDown(self):
        """
        结束测试执行的销毁
        """
        # FileTools.remove_dir(TEST_PATH)
        return

    def test_init(self):
        """
        测试init
        """
        # 常用参数
        root_dir = TEST_PATH + '/init/'
        test_repo_name = fcmm_git_cmd.FcmmGitCmd.get_remote_repo_name(TEST_REPO_URL)
        repo_dir = root_dir + test_repo_name + '/'

        # 准备远程环境
        FileTools.create_dir(root_dir)
        os.chdir(root_dir)
        self.assertTrue(
            subprocess.run(
                'git clone %s' % (TEST_REPO_URL), shell=True).returncode == 0,
            'clone命令处理失败'
        )
        os.chdir(repo_dir)
        repo_info = fcmm_git_cmd.FcmmGitCmd.get_repo_info(repo_dir)
        commit = ''
        for tag in repo_info['repo'].tags:
            if tag.name == 'null':
                commit = str(tag.commit)
        self.assertTrue(commit != '', '找不到远程仓库null节点')
        self.assertTrue(
            subprocess.run(
                'git reset --hard %s' % (commit), shell=True).returncode == 0,
            '回退null命令处理失败'
        )
        self.assertTrue(
            subprocess.run(
                'git push origin master', shell=True).returncode == 0,
            'push命令处理失败'
        )

        os.chdir(root_dir)
        if platform.system() == 'Windows':
            subprocess.run('rmdir /S /Q %s' % (repo_dir), shell=True)
        else:
            FileTools.remove_dir(repo_dir)

        # 测试本地目录上传服务器
        local_repo_name = 'local'
        local_repo_path = root_dir + local_repo_name + '/'
        FileTools.create_dir(local_repo_path)
        os.chdir(local_repo_path)
        subprocess.run('echo "测试本地目录上传服务器" > readme.md', shell=True)
        self.assertTrue(
            subprocess.run(
                'python %s/fcmm.py init -b local -url %s -v v0.1.1' % (FCMM_PATH, TEST_REPO_URL), shell=True).returncode == 0,
            'commit命令处理失败'
        )


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    unittest.main()
