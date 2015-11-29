#!/usr/bin/env python
# coding: utf-8
import web
import os

web.config.db_reader="root"
web.config.db_writer="root"
web.config.read_db_name="todo"
web.config.write_db_name="todo"
#web.config.db_host="127.0.0.1"
web.config.db_host="localhost"
web.config.db_port=3306
web.config.db_pass="831112"

web.config.db_style="mysql"

web.config.mem_host="localhost:11211"

web.config.app_root = os.getcwd()

web.config.debug = False

web.config.site_config = web.storage(
    email='waile23@gmail.com',
    site_name = 'todo',
    site_desc = '安守岁月，风尘无恙。',
    static = '/static',
)
