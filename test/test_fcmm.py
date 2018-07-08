#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
import sys
import os
import inspect
import subprocess
import platform
import git
sys.path.append('../fcmm4git/')
import fcmm
import fcmm_git_cmd
from snakerlib.generic import FileTools, DebugTools


__MOUDLE__ = 'test_fcmm'  # 模块名
__DESCRIPT__ = 'fcmm测试'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.07'  # 发布日期

# 临时测试目录
FCMM_PATH = os.path.realpath('../fcmm4git/')
TEMP_PATH = FCMM_PATH + '/temp/'
BACKUP_PATH = FCMM_PATH + '/backup/'
TEST_PATH = os.path.realpath('./temptest/')
TEST_ROOT_PATH = ''
TEST_REPO_URL = 'https://github.com/snakeclub/fcmm4git-unittest.git'


class TestFcmm(unittest.TestCase):
    """
    fcmm单元测试类测试
    """

    def setUp(self):
        """
        启动测试执行的初始化
        """
        global TEST_PATH
        if os.path.exists(TEST_PATH):
            FileTools.remove_dir(TEST_PATH)

        FileTools.create_dir(TEST_PATH)

        # 删除临时和备份目录
        if os.path.exists(TEMP_PATH):
            FileTools.remove_dir(TEMP_PATH)

        if os.path.exists(BACKUP_PATH):
            FileTools.remove_dir(BACKUP_PATH)

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
        print('测试init')
        global TEST_PATH, TEST_REPO_URL, FCMM_PATH, TEMP_PATH, BACKUP_PATH
        # 常用参数
        root_dir = TEST_PATH + '/init/'
        test_repo_name = fcmm_git_cmd.FcmmGitCmd.get_remote_repo_name(TEST_REPO_URL)
        repo_dir = root_dir + test_repo_name + '/'

        # 准备远程环境
        print('准备远程环境')
        FileTools.create_dir(root_dir)
        os.chdir(root_dir)
        self.assertTrue(
            subprocess.run(
                'git clone %s' % (TEST_REPO_URL), shell=True).returncode == 0,
            '准备远程环境: clone命令处理失败'
        )
        os.chdir(repo_dir)
        # 清空文件夹
        subprocess.run('git rm * -r', shell=True)
        repo_info = fcmm_git_cmd.FcmmGitCmd.get_repo_info(repo_dir)
        if repo_info['repo'].is_dirty():
            # 有修改，要提交及上传
            self.assertTrue(
                subprocess.run(
                    'git commit -m "fcmm4git test clear file"', shell=True).returncode == 0,
                '准备远程环境: rm命令处理失败'
            )
            self.assertTrue(
                subprocess.run(
                    'git push -f origin master', shell=True).returncode == 0,
                '准备远程环境: push命令处理失败'
            )

        os.chdir(root_dir)
        FileTools.remove_dir(repo_dir)

        # 测试本地目录上传服务器
        print('测试本地目录上传服务器')
        local_repo_name = 'local'
        local_repo_path = root_dir + local_repo_name + '/'
        FileTools.create_dir(local_repo_path)
        os.chdir(local_repo_path)
        subprocess.run('echo "test local to remote: no pkg v0.1.2" > readme.md', shell=True)

        print('测试本地目录上传服务器，成功但不建立lb-pkg')
        self.assertTrue(
            subprocess.run(
                'python %s/fcmm.py init -b local -url %s -v v0.1.2 -force -n' % (FCMM_PATH, TEST_REPO_URL), shell=True).returncode == 0,
            '本地目录上传: init命令处理失败'
        )
        # 检查处理情况，先是备份
        file_list = FileTools.get_filelist(path=BACKUP_PATH,
                                           regex_str=test_repo_name.replace('.', '\.')+'\.bak\..*\.tar')
        self.assertTrue(len(file_list) > 0, '本地目录上传: 备份文件不存在')
        # 分支信息
        repo_info = fcmm_git_cmd.FcmmGitCmd.get_repo_info(local_repo_path)
        has_pkg = False
        for branch in repo_info['repo'].branches:
            if branch.name == 'lb-pkg':
                has_pkg = True
                break
        self.assertFalse(has_pkg, '本地目录上传: 不应建立lb-pkg')

        print('测试本地目录上传服务器，非强制被拒绝')
        self.assertFalse(
            subprocess.run(
                'python %s/fcmm.py init -b local -url %s -v v0.0.9' % (FCMM_PATH, TEST_REPO_URL), shell=True).returncode == 0,
            '本地目录上传: init命令处理失败'
        )

        print('测试本地目录上传服务器，成功并建立lb-pkg')
        subprocess.run('echo "test local to remote: with pkg v0.0.9" > readme1.md', shell=True)
        FileTools.remove_file(local_repo_path + '.fcmm4git')
        FileTools.remove_file(local_repo_path + 'readme.md')
        self.assertTrue(
            subprocess.run(
                'python %s/fcmm.py init -b local -url %s -v v0.0.9 -force' % (FCMM_PATH, TEST_REPO_URL), shell=True).returncode == 0,
            '本地目录上传: init命令处理失败'
        )
        # 检查处理情况，先是备份
        file_list = FileTools.get_filelist(path=BACKUP_PATH,
                                           regex_str=test_repo_name.replace('.', '\.')+'\.bak\..*\.tar')
        self.assertTrue(len(file_list) > 0, '本地目录上传: 备份文件不存在')
        # 分支信息
        repo_info = fcmm_git_cmd.FcmmGitCmd.get_repo_info(local_repo_path)
        has_pkg = False
        for branch in repo_info['repo'].branches:
            if branch.name == 'lb-pkg':
                has_pkg = True
                break
        self.assertTrue(has_pkg, '本地目录上传: 没有成功建立lb-pkg')


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
    # 跳转到程序所在的路径
    TEST_ROOT_PATH = os.path.split(os.path.realpath(inspect.getfile(inspect.currentframe())))[0]
    os.chdir(TEST_ROOT_PATH)
    FCMM_PATH = os.path.realpath(FCMM_PATH)
    TEST_PATH = os.path.realpath(TEST_PATH)

    DebugTools.set_debug(True)
    unittest.main()
