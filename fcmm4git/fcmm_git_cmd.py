#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
FCMM针对Git的命令处理
@module fcmm_git_cmd
@file fcmm_git_cmd.py
"""

import json
import logging
from snakerlib.generic import ExceptionTools, RunTools, FileTools


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

        @returns {string} - 返回要显示的结果内容
        """
        back_str = ''
        # 通过switch字典实现switch的代码
        switch = {
            'init': FcmmGitCmd.cmd_init,
            'help': FcmmGitCmd.cmd_help
        }
        with ExceptionTools.ignored_all((), logging, '执行"%s %s"出现异常' % (cmd, cmd_para)):
            dict_cmd_para = FcmmGitCmd.split_cmd_para(cmd_para)
            if 'h' in dict_cmd_para.keys() or 'help' in dict_cmd_para.keys():
                # 只是返回帮助文档
                FcmmGitCmd.cmd_help({"cmd": ""})
            else:
                back_str = switch[cmd](dict_cmd_para)
        return back_str

    #############################
    # 工具函数
    #############################

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

    #############################
    # 具体命令处理函数
    #############################

    @staticmethod
    def cmd_help(dict_cmd_para=None):
        """
        帮助命令，返回帮助显示信息

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 命令参数，取第一个显示帮助

        @returns {string} - 返回帮助信息
        """
        config = RunTools.get_global_var('config')
        if len(dict_cmd_para) == 0:
            # 没有传入参数，返回全部命令的简要介绍
            return config['help_text']['all']
        else:
            # 返回指定命令的帮助信息
            return config['help_text'][dict_cmd_para[dict_cmd_para.keys()[0]]]

    @staticmethod
    def cmd_init(dict_cmd_para=None):
        """
        初始化FCMM版本库：根据指定的参数建立及初始化FCMM版本库

        @decorators staticmethod

        @param {dict} dict_cmd_para=None - 参数字典

        @returns {string} - 返回处理显示内容
        """
        return ''


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
