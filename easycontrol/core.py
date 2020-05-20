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
import importlib
from pyrogram.errors import BadRequest
from pyrogram import Client, Filters, MessageHandler, Message


class CoreModule(object):
    def __init__(self, modules_class):
        self.modules_class = modules_class
        self.config = self.modules_class.config
        self.modules = self.modules_class.modules
        self.modules_class.add_command(
            MessageHandler(self.help, Filters.command('help', self.config['prefix']) & Filters.me),
            'Show this message'
        )
        self.modules_class.add_command(
            MessageHandler(self.prefix, Filters.command('prefix', self.config['prefix']) & Filters.me),
            'Change the prefix of the commands'
        )
        self.modules_class.add_command(
            MessageHandler(self.load, Filters.command('load', self.config['prefix']) & Filters.me),
            'Load a module'
        )
        self.modules_class.add_command(
            MessageHandler(self.unload, Filters.command('unload', self.config['prefix']) & Filters.me),
            'Unload a module'
        )

    async def help(self, client: Client, message: Message):
        text = ["<b>Here's the full list of the available commands:</b>"]

        for module_name, module in self.modules.items():
            if module_name in self.config['unloaded_modules']:
                continue
            text.append("<i>{0}</i> <b>module's commands</b>".format(module_name))

            for command, value in module.items():
                text.append('<code>{0}{1}</code>: {2}'.format(self.config['prefix'], command, value[1]))
            text.append('')
        text.append('<code>Powered by EasyControl</code>')

        try:
            await client.edit_message_text(message.chat.id, message.message_id, os.linesep.join(text))
        except BadRequest:
            await client.send_message(message.chat.id, os.linesep.join(text))

    async def prefix(self, client: Client, message: Message):
        old_prefix = self.config['prefix']
        self.config['prefix'] = message.command[1] if len(message.command) == 2 else '/'

        for commands in self.modules.values():
            for value in commands.values():
                if hasattr(value[0].filters, 'base'):
                    value[0].filters.base.prefixes = [self.config['prefix']]
                else:
                    value[0].filters.prefixes = [self.config['prefix']]

        with open(self.config['config_path'], 'w') as f:
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
        if (not len(message.command) == 2
                or message.command[1] in self.modules
                or not message.command[1] + '.py' in os.listdir(self.config['modules_path'])):
            await message.stop_propagation()
        imported = importlib.import_module(message.command[1])
        imported.Module(self.modules_class.get_commands_dict(message.command[1]))

        if message.command[1] in self.config['unloaded_modules']:
            self.config['unloaded_modules'].remove(message.command[1])

            with open(self.config['config_path'], 'w') as f:
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
        if (not len(message.command) == 2
                or not message.command[1] in self.modules
                or message.command[1] == 'core'):
            await message.stop_propagation()

        for value in self.modules[message.command[1]].values():
            client.remove_handler(value[0])
        self.config['unloaded_modules'].append(message.command[1])
        del self.modules[message.command[1]]

        with open(self.config['config_path'], 'w') as f:
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
