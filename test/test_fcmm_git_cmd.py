#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
import sys
import os
import shutil
sys.path.append('../fcmm4git/')
import fcmm
from fcmm_git_tools import FCMMGitTools
from fcmm_tools import FCMMTools
from snakerlib.generic import FileTools


__MOUDLE__ = 'test_fcmm_git_cmd'  # 模块名
__DESCRIPT__ = 'fcmm_git_cmd测试'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.07'  # 发布日期


# 临时测试目录
TEST_PATH = './temptest/'


class TestFcmmGitCmd(unittest.TestCase):
    """
    fcmm_git_cmd单元测试类测试
    """

    def setUp(self):
        """
        启动测试执行的初始化
        """
        self.current_path = os.path.realpath('')
        if os.path.exists(TEST_PATH):
            FileTools.remove_dir(TEST_PATH)

        FileTools.create_dir(TEST_PATH)

        shutil.copyfile('../fcmm4git/fcmm.json', 'fcmm.json')

        fcmm.fcmm_init()
        return

    def tearDown(self):
        """
        结束测试执行的销毁
        """
        os.chdir(self.current_path)
        FileTools.remove_dir(TEST_PATH)
        FileTools.remove_file('fcmm.json')
        return

    def test_json_file(self):
        """
        测试JSON文件处理
        """
        FileTools.create_dir(TEST_PATH + 'json_file/')
        json_obj = dict()
        json_obj['key_1'] = 'value1'
        json_obj['key_2'] = 'value2'
        json_obj['key_3'] = dict()
        json_obj['key_3']['key_3_1'] = 'value3_1'
        json_obj['key_3']['key_3_2'] = 'value3_2'
        json_obj['key_4'] = ['value4_1', 'value4_2']

        FCMMTools.save_to_json_file(TEST_PATH + 'json_file/.fcmm4git', json_obj)
        get_json_obj = FCMMTools.get_fcmm_config(TEST_PATH + 'json_file/')

        self.assertDictEqual(json_obj, get_json_obj, 'JSON文件处理失败')
        return

    def test_split_cmd_para(self):
        """
        split_cmd_para
        """
        cmd_para = 'a1 -b1 -c1 c1value  d1 -c2'
        want_obj = {
            'a1': '',
            '-b1': '',
            '-c1': 'c1value',
            'd1': '',
            '-c2': ''
        }
        real_obj = FCMMTools.split_cmd_para(cmd_para)
        self.assertDictEqual(want_obj, real_obj, 'split_cmd_para失败')
        return

    def test_get_remote_repo_name(self):
        """
        get_remote_repo_name
        """
        url = 'https://github.com/snakeclub/fcmm4git-unittest.git'
        name = FCMMGitTools.get_remote_repo_name(url)
        self.assertEqual(name, 'fcmm4git-unittest', 'get_remote_repo_name')

    def test_vailidate_cmd_para(self):
        """
        vailidate_cmd_para
        """
        print('测试vailidate_cmd_para')
        dict_cmd_para = {
        }
        ret = FCMMTools.vailidate_cmd_para(dict_cmd_para, cmd='init')
        print('测试必须带指定参数：' + ret[1])
        self.assertTrue(ret[0] == 1, '测试必须带指定参数失败：%s' % ('init'))
        dict_cmd_para = {
            '-f': '',
            '-err2': 'value1',
            '-err1': 'value2',
            '-b': 'remote',
            '-u': 'ddd'
        }
        ret = FCMMTools.vailidate_cmd_para(dict_cmd_para, cmd='init')
        print('测试不支持的参数:' + ret[1])
        self.assertTrue(ret[0] == 1, '测试不支持的参数失败：%s' % ('-err2'))
        dict_cmd_para = {
            '-b': 'testb'
        }
        ret = FCMMTools.vailidate_cmd_para(dict_cmd_para, cmd='init')
        print('测试参数取值错误:' + ret[1])
        self.assertTrue(ret[0] == 1, '测试参数取值错误失败：%s' % ('-testb'))
        dict_cmd_para = {
            '-b': 'remote',
            '-v': '',
            '-u': 'ddd'
        }
        ret = FCMMTools.vailidate_cmd_para(dict_cmd_para, cmd='init')
        print('测试参数未送值错误:' + ret[1])
        self.assertTrue(ret[0] == 1, '测试参数未送值错误失败：%s' % ('-v'))
        dict_cmd_para = {
            '-b': 'remote',
            '-u': 'ddd',
            '-v': 'V1.1'
        }
        ret = FCMMTools.vailidate_cmd_para(dict_cmd_para, cmd='init')
        print('测试参数校验通过:' + ret[1])
        self.assertTrue(ret[0] == 0, '测试参数校验通过失败：%s' % ('-v'))


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    unittest.main()
