# EasyControl, an easy-to-use template for creating a fully working userbot on Telegram
# Copyright (C) 2020  Mattia Chiabrando
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import json
import asyncio
import importlib
from pyrogram import Client
from .core import CoreModule

class EasyControl(object):
    ABSOLUTE_CWD = os.path.abspath(os.getcwd())
    DEFAULT_CONFIG_PATH = os.path.join(ABSOLUTE_CWD, 'config.json')
    DEFAULT_MODULES_PATH = os.path.join(ABSOLUTE_CWD, 'modules')

    def __init__(self, api_id: int, api_hash: str, config_path: str = DEFAULT_CONFIG_PATH):
        self.config = None
        self.load_config(config_path)
        self.app = Client('EasyControl', api_id, api_hash)
        self.load_modules()
        asyncio.get_event_loop().run_until_complete(self.start_app())

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = json.loads(f.read())
        except IOError:
            config_path = self.DEFAULT_CONFIG_PATH

            with open(config_path, 'w+') as f:
                self.config = {
                    'prefix': '/',
                    'config_path': self.DEFAULT_CONFIG_PATH,
                    'modules_path': self.DEFAULT_MODULES_PATH,
                    'unloaded_modules': []
                }
                f.write(json.dumps(self.config, indent=2))
        except ValueError:
            raise
        edited = False

        if not 'prefix' in self.config:
            edited = True
            self.config['prefix'] = '/'
        elif not 'config_path' in self.config:
            edited = True
            self.config['config_path'] = config_path
        elif not 'modules_path' in self.config:
            edited = True
            self.config['modules_path'] = self.DEFAULT_MODULES_PATH
        elif not 'unloaded_modules' in self.config:
            edited = True
            self.config['modules_path'] = []

        if edited:
            with open(config_path, 'w') as f:
                f.write(json.dumps(self.config, indent=2))

    def load_modules(self):
        modules_class = Modules(self.app, self.config)
        CoreModule(modules_class.get_commands_dict('core'))
        sys.path.append(self.config['modules_path'])

        for file in os.listdir(self.config['modules_path']):
            name = os.path.splitext(file)[0]

            if (file == '__init__.py'
                    or not file.endswith('.py')
                    or name in self.config['unloaded_modules']):
                continue
            imported = importlib.import_module(name)
            imported.Module(modules_class.get_commands_dict(name))

    async def start_app(self):
        await self.app.start()
        await self.app.idle()
        await self.app.stop()


class Modules(object):
    def __init__(self, app: Client, config: dict):
        self.app = app
        self.config = config
        self.modules = {}
        self.name = None

    def get_commands_dict(self, name: str):
        self.modules[name] = {}
        self.name = name
        return self

    def add_command(self, handler, help: str):
        if hasattr(handler.filters, 'base'):
            commands = handler.filters.base.commands
        else:
            commands = handler.filters.commands

        for command in commands:
            self.modules[self.name][command] = [
                handler,
                help
            ]
        self.app.add_handler(handler)
