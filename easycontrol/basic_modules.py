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
from importlib import util
from pyrogram.errors import BadRequest
from pyrogram import Client, Filters, MessageHandler, Message


class BasicModulesLoader(object):
    def __init__(self, app: Client, config: dict, modules: dict):
        """
        Define the instance of this class and add the commands to the main's class modules dictionary.

        :param app: The Client instance of the started Pyrogram's client.
        :param config: The config instance of the main class.
        :param modules: The modules instance of the main class.
        """

        self.config = config
        self.modules = modules
        self.modules['_'] = {
            'help': [
                MessageHandler(self.help, Filters.command('help', self.config['prefix']) & Filters.me),
                'Show this message'
            ],
            'prefix': [
                MessageHandler(self.prefix, Filters.command('prefix', self.config['prefix']) & Filters.me),
                'Change the prefix of the commands'
            ],
            'load': [
                MessageHandler(self.load, Filters.command('load', self.config['prefix']) & Filters.me),
                'Load a module'
            ],
            'unload': [
                MessageHandler(self.unload, Filters.command('unload', self.config['prefix']) & Filters.me),
                'Unload a module'
            ]
        }

        for sub in self.modules['_'].values():
            app.add_handler(sub[0])

    async def help(self, client: Client, message: Message):
        """Help command's handler

        :param client: The Client instance of the started Pyrogram's client.
        :param message: The Message instance of the started Pyrogram's client.
        """

        text = ["<b>Here's the full list of the available commands:</b>"]

        for module_name, module in self.modules.items():
            if module_name in self.config['unloaded_modules']:
                continue
            text.append('<b>{0}:</b>'.format(
                'Default commands' if module_name == '_' else "</b><i>{0}</i> <b>module's commands".format(module_name)
            ))

            for command, sub in module.items():
                text.append('<code>{0}{1}</code>: {2}'.format(self.config['prefix'], command, sub[1]))
            text.append('')
        text.append('<code>Powered by EasyControl</code>')

        try:
            await client.edit_message_text(message.chat.id, message.message_id, os.linesep.join(text))
        except BadRequest:
            await client.send_message(message.chat.id, os.linesep.join(text))

    async def prefix(self, client: Client, message: Message):
        """Prefix command's handler

        :param client: The Client instance of the started Pyrogram's client.
        :param message: The Message instance of the started Pyrogram's client.
        """

        old_prefix = self.config['prefix']
        self.config['prefix'] = message.command[1] if len(message.command) == 2 else '/'

        for module in self.modules.values():
            for sub in module.values():
                if hasattr(sub[0].filters, 'base'):
                    sub[0].filters.base.prefixes = [self.config['prefix']]
                else:
                    sub[0].filters.prefixes = [self.config['prefix']]

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))

        try:
            await client.edit_message_text(message.chat.id, message.message_id, os.linesep.join([
                '<b>The prefix has been changed:</b>',
                'Old prefix: <code>{0}</code>'.format(old_prefix),
                'New prefix: <code>{0}</code>'.format(self.config['prefix']),
            ]))
        except BadRequest:
            await client.send_message(message.chat.id, os.linesep.join([
                '<bThe prefix has been changed:</b>',
                'Old prefix: <code>{0}</code>'.format(old_prefix),
                'New prefix: <code>{0}</code>'.format(self.config['prefix']),
            ]))

    async def load(self, client: Client, message: Message):
        """Load command's handler

        :param client: The Client instance of the started Pyrogram's client.
        :param message: The Message instance of the started Pyrogram's client.
        """

        if (not len(message.command) == 2
                or message.command[1] in self.modules
                or not message.command[1] + '.py' in os.listdir(self.config['modules_path'])):
            await message.stop_propagation()

        if message.command[1] in self.config['unloaded_modules']:
            self.config['unloaded_modules'].remove(message.command[1])
        spec = util.spec_from_file_location(
            message.command[1], os.path.join(self.config['modules_path'], message.command[1] + '.py')
        )
        imported_module = util.module_from_spec(spec)
        spec.loader.exec_module(imported_module)
        self.modules[message.command[1]] = imported_module.CmdModule(client, self.config).commands

        for sub in self.modules[message.command[1]].values():
            client.add_handler(sub[0])

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))

        try:
            await client.edit_message_text(
                message.chat.id, message.message_id,
                '<b>The module</b> <code>{0}</code> <b>has been loaded</b>'.format(message.command[1])
            )
        except BadRequest:
            await client.send_message(
                message.chat.id,
                '<b>The module</b> <code>{0}</code> <b>has been loaded</b>'.format(message.command[1])
            )

    async def unload(self, client: Client, message: Message):
        """Unload command's handler

        :param client: The Client instance of the started Pyrogram's client.
        :param message: The Message instance of the started Pyrogram's client.
        """

        if (not len(message.command) == 2
                or not message.command[1] in self.modules
                or message.command[1] == '_'):
            await message.stop_propagation()
        self.config['unloaded_modules'].append(message.command[1])

        for sub in self.modules[message.command[1]].values():
            client.remove_handler(sub[0])
        del self.modules[message.command[1]]

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))

        try:
            await client.edit_message_text(
                message.chat.id, message.message_id,
                '<b>The module</b> <code>{0}</code> <b>has been unloaded</b>'.format(message.command[1])
            )
        except BadRequest:
            await client.send_message(
                message.chat.id,
                '<b>The module</b> <code>{0}</code> <b>has been unloaded</b>'.format(message.command[1])
            )
