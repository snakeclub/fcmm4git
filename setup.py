#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""The setup.py file for Python fcmm4git."""

from setuptools import setup, find_packages


LONG_DESCRIPTION = """
fcmm4git 是为FCMM所开发的一个命令行工具，简化FCMM的管理操作
""".strip()

SHORT_DESCRIPTION = """
为FCMM所开发的一个命令行工具.""".strip()

DEPENDENCIES = [
    'GitPython>=2.1.10',
    'snakerlib'
]

TEST_DEPENDENCIES = []

VERSION = '0.1.0'
URL = 'https://github.com/snakeclub/fcmm4git'

setup(
    # pypi中的名称，pip或者easy_install安装时使用的名称
    name="fcmm4git",
    version=VERSION,
    author="黎慧剑",
    author_email="snakeclub@163.com",
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license="Apache License, Version 2.0",
    keywords="FCMM fcmm4git",
    url=URL,
    # 需要打包的目录列表, 可以指定路径packages=['path1', 'path2', ...]
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    # 此项需要，否则卸载时报windows error
    zip_safe=False
)
