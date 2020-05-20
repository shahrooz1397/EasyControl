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

import asyncio
from pyrogram.errors import BadRequest
from pyrogram import Client, Filters, MessageHandler, Message


class CmdModule(object):
    def __init__(self, _: Client, config: dict):
        self.commands = {
            'flood': [
                MessageHandler(self.flood, Filters.command('flood', config['prefix']) & Filters.me),
                'Flood a maximum of 100 messages'
            ]
        }

    async def flood(self, client: Client, message: Message):
        tasks = []

        if len(message.command) == 1:
            sent_message = await client.send_message(message.chat.id, 'flood')

            for _ in range(1, 10):
                tasks.append(self.flood_process(client, message.chat.id, sent_message.message_id))
        elif len(message.command) == 2:
            sent_message = await client.send_message(message.chat.id, 'flood')

            for _ in range(1, int(message.command[1])):
                tasks.append(self.flood_process(client, message.chat.id, sent_message.message_id))
        elif len(message.command) >= 3:
            sent_message = await client.send_message(message.chat.id, ' '.join(message.command[2:]))

            for _ in range(1, int(message.command[1])):
                tasks.append(self.flood_process(client, message.chat.id, sent_message.message_id))
        await asyncio.gather(*tasks)

    @staticmethod
    async def flood_process(client: Client, chat_id: int, message_id: int):
        await client.forward_messages(chat_id, chat_id, message_id)
