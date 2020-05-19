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
import math
import json
from datetime import datetime
from pyrogram.errors import BadRequest
from pyrogram import Client, Filters, MessageHandler, Message


class CmdModule(object):
    def __init__(self, app: Client, config: dict):
        self.config = config
        self.commands = {
            'afk': [
                MessageHandler(self.afk, Filters.command('afk', config['prefix'])),
                'Set the afk status on True'
            ],
            'unafk': [
                MessageHandler(self.unafk, Filters.command('unafk', config['prefix'])),
                'Set the afk status on False'
            ]
        }
        app.add_handler(MessageHandler(self.wrapper, Filters.private & ~Filters.me), group=-1)

    async def afk(self, client: Client, message: Message):
        if ('afk' in self.config
                and self.config['afk']['is_afk']):
            await message.stop_propagation()
        self.config['afk'] = {
            'is_afk': True,
            'since': datetime.timestamp(datetime.utcnow()),
            'notified': {}
        }

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))

        try:
            await client.edit_message_text(message.chat.id, message.message_id, '<b>Afk mode enabled</b>')
        except BadRequest:
            await client.send_message(message.chat.id, '<b>Afk mode enabled</b>')

    async def unafk(self, client: Client, message: Message):
        if (not 'afk' in self.config
                or not self.config['afk']['is_afk']):
            await message.stop_propagation()
        self.config['afk']['is_afk'] = False
        del self.config['afk']['since']
        del self.config['afk']['notified']

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))

        try:
            await client.edit_message_text(message.chat.id, message.message_id, '<b>Afk mode disabled</b>')
        except BadRequest:
            await client.send_message(message.chat.id, '<b>Afk mode disabled</b>')

    async def wrapper(self, client: Client, message: Message):
        now = datetime.timestamp(datetime.utcnow())

        if (message.from_user.is_bot
                or not 'afk' in self.config
                or not self.config['afk']['is_afk']
                or (message.from_user.id in self.config['afk']['notified'].keys()
                    and self.config['afk']['notified'][message.from_user.id] > now)):
            return
        self.config['afk']['notified'][message.from_user.id] = now + 3600

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))
        await client.send_message(message.chat.id, os.linesep.join([
            "<b>Hi, I'm afk since </b> <code>{0}</code>.".format(
                datetime.utcfromtimestamp(self.config['afk']['since']).strftime('%d/%m/%Y %H:%M:%S UTC')
            ),
            'Before writing me other messages, please wait me to get out of the afk status'
        ]))