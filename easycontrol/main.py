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
import json
import asyncio
import importlib
from pyrogram import Client
from .basic_modules import BasicModulesLoader


class EasyControl(object):
    def __init__(
            self, api_id: int, api_hash: str,
            conf_path: str = os.path.join(os.path.abspath(os.getcwd()), 'config.json')
    ):
        """
        Define the instance of this class, start the Pyrogram's client and load all the modules and commands.

        :param api_id: The api_id of the app used to start the client.
        :param api_hash: The api_hash of the app used to start the client.
        :param conf_path: The path to the config file.
        """

        self.conf_path = conf_path
        self.config = None
        self.modules = {}
        self.load_config()
        self.app = Client('EasyControl', api_id, api_hash)
        BasicModulesLoader(self.app, self.config, self.modules)
        self.load_modules()
        asyncio.get_event_loop().run_until_complete(self.start_app())

    def load_config(self):
        """Load the config from its path."""

        try:
            with open(self.conf_path, 'r') as f:
                self.config = json.loads(f.read())
        except IOError:
            with open(self.conf_path, 'w+') as f:
                self.config = {
                    'prefix': '/',
                    'conf_path': self.conf_path,
                    'modules_path': os.path.join(os.path.dirname(self.conf_path), 'modules'),
                    'unloaded_modules': []
                }
                f.write(json.dumps(self.config, indent=2))
        except ValueError:
            raise

    def load_modules(self):
        """Load all the modules from the path specified in the config"""

        modules_list = os.listdir(self.config['modules_path'])

        for module in modules_list:
            module_name = os.path.splitext(module)[0]

            if (not module.endswith('.py')
                    or module_name in self.config['unloaded_modules']):
                continue
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(self.config['modules_path'], module)
            )
            imported_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(imported_module)
            self.modules[module_name] = imported_module.CmdModule(self.app, self.config).commands

            for sub in self.modules[module_name].values():
                self.app.add_handler(sub[0])

    async def start_app(self):
        """Start the Pyrogram's client"""
        await self.app.start()
        await self.app.idle()
        await self.app.stop()
