#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
fcmm的命令处理工具模块，提供fcmm的一些基础处理函数
@module fcmm_tools
@file fcmm_tools.py
"""

import os
import json
import tarfile
import subprocess
from snakerlib.generic import RunTools


__MOUDLE__ = 'fcmm_tools'  # 模块名
__DESCRIPT__ = 'fcmm的命令处理工具'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = '黎慧剑'  # 作者
__PUBLISH__ = '2018.07.19'  # 发布日期


class FCMMTools(object):
    """
    fcmm的命令处理工具类
    提供fcmm的一些基础处理函数
    """

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

    @staticmethod
    def run_sys_cmd_list(cmd_list):
        """
        执行多个操作系统命令

        @decorators staticmethod -

        @param {string[]} cmd_list - 操作系统命令列表

        @returns {list} - 执行结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        for _cmd in cmd_list:
            res = FCMMTools.run_sys_cmd(_cmd)
            if res[0] != 0:
                return res

    @staticmethod
    def get_fcmm_config(work_dir=''):
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
    def get_cmd_para_value(dict_cmd_para, short_para, long_para, default_value=None):
        """
        根据长短参数从命令中获取参数值

        @decorators staticmethod

        @param {dict} dict_cmd_para - 命令集
        @param {string} short_para - 短参数名
        @param {string} long_para - 长参数名
        @param {string} default_value - 如果取不到参数的默认取值

        @returns {string} - 获取到的参数值，如果获取不到返回None
        """
        value = dict_cmd_para.get(short_para)
        if value is None:
            value = dict_cmd_para.get(long_para)
        if value is None and default_value is not None:
            value = default_value
        return value

    @staticmethod
    def get_i18n_tips(config, tips_key, *replace_str):
        """
        获取配置中的多国语言提示信息

        @decorators staticmethod - [description]

        @param {dict} config - fcmm的配置对象
        @param {string} tips_key - 提示索引关键字
        @param {tuple} replace_str - 要传入的替换参数

        @returns {string} - 提示信息
        """
        if len(replace_str) == 0:
            return config['i18n_tips'][tips_key]
        else:
            return config['i18n_tips'][tips_key] % replace_str

    @staticmethod
    def vailidate_cmd_para(dict_cmd_para, cmd):
        """
        根据命令参数配置验证参数值是否正确

        @decorators staticmethod -

        @param {dict} dict_cmd_para - 传入的参数字典，key为参数名（带'-'），value为参数值
        @param {string} cmd - 要验证的命令

        @returns {list} - 校验结果[returncode, msgstring]
            returncode - 0代表成功，其他代表失败
            msgstring - 要返回显示的内容
        """
        config = RunTools.get_global_var('config')
        config_cmd_para = RunTools.get_global_var('config_cmd_para')
        # 检查必要参数是否有送
        if cmd in config['cmd_para_must'].keys() and config['cmd_para_must'][cmd] is not None:
            for _item in config['cmd_para_must'][cmd]:
                if not('-'+_item[0] in dict_cmd_para.keys() or '-'+_item[1] in dict_cmd_para.keys()):
                    return [1, FCMMTools.get_i18n_tips(config, 'must_has_para', '-%s / -%s' % (_item[0], _item[1]))]

        # 检查参数要包含值的情况
        para_list = config_cmd_para[cmd]['long_para']
        for _key in dict_cmd_para.keys():
            # 逐个参数判断
            para = _key.lstrip('-')
            if para not in para_list.keys():
                return [1, FCMMTools.get_i18n_tips(config, 'para_not_support', _key)]

            if para_list[para] is not None:
                if dict_cmd_para[_key] is None or dict_cmd_para[_key] == '':
                    return [1, FCMMTools.get_i18n_tips(config, 'para_must_has_value', _key)]
                elif len(para_list[para]) > 0 and dict_cmd_para[_key] not in para_list[para]:
                    return [1, FCMMTools.get_i18n_tips(config, 'para_value_not_support', _key, dict_cmd_para[_key])]

        return [0, '']


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
