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
import sqlite3
import json
from datetime import datetime
from pyrogram import Client, Filters, MessageHandler, Message
from pyrogram.errors import BadRequest


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

    def query(self, query: str, bindings: tuple = (), fetch: bool = True):
        conn = sqlite3.connect(os.path.join(os.path.dirname(self.config['conf_path']), 'EasyControl.session'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if bindings:
            cursor.execute(query, bindings)
        else:
            cursor.execute(query)

        if fetch:
            result = cursor.fetchall()

            if (result is not None
                    and len(result) == 1):
                result = result[0]
        conn.commit()
        cursor.close()
        conn.close()

        if fetch:
            return result

    async def afk(self, client: Client, message: Message):
        if ('afk' in self.config
                and self.config['afk']['is_afk']):
            await message.stop_propagation()
        self.config['afk'] = {
            'is_afk': True,
            'start': datetime.timestamp(datetime.now()),
            'notified': []
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
        del self.config['afk']['start']
        del self.config['afk']['notified']

        with open(self.config['conf_path'], 'w') as f:
            f.write(json.dumps(self.config, indent=2))

        try:
            await client.edit_message_text(message.chat.id, message.message_id, '<b>Afk mode disabled</b>')
        except BadRequest:
            await client.send_message(message.chat.id, '<b>Afk mode disabled</b>')

    async def wrapper(self, client: Client, message: Message):
        if (not 'afk' in self.config
                or not self.config['afk']['is_afk']
                or message.from_user.id in self.config['afk']['notified']):
            return
        peer = dict(self.query('SELECT * FROM peers WHERE id = ?', (message.from_user.id,)))

        if (peer is None
                or ('last_update_on' in peer
                and peer['last_update_on'] <= self.config['afk']['start'])):
            self.config['afk']['notified'].append(message.from_user.id)

            with open(self.config['conf_path'], 'w') as f:
                f.write(json.dumps(self.config, indent=2))
            await client.send_message(message.chat.id, os.linesep.join([
                "<b>Hi, I've gone afk at</b> <code>{0}</code>".format(
                    datetime.fromtimestamp(self.config['afk']['start']).strftime('%d/%m/%Y %H:%M:%S')
                ),
                'Before writing me other messages, please wait until my return'
            ]))
