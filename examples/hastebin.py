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

import requests
from pyrogram.errors import BadRequest
from pyrogram import Client, Filters, MessageHandler, Message


class CmdModule(object):
    def __init__(self, _: Client, config: dict):
        self.commands = {
            'hastebin': [
                MessageHandler(self.hastebin, Filters.command('hastebin', config['prefix'])),
                'Create an hastebin link with the text in a reply message'
            ]
        }

    @staticmethod
    async def dump(client: Client, message: Message):
        if message.reply_to_message is None:
            await message.stop_propagation()
        key = requests.post('https://hastebin.com', data=message.reply_to_message.text.encode('UTF-8'))['key']

        try:
            await client.edit_message_text(
                message.chat.id, message.message_id,
                '<b>Result:</b> https://hastebin.com/{0}'.format(key)
            )
        except BadRequest:
            await client.send_message(message.chat.id, '<b>Result:</b> https://hastebin.com/{0}'.format(key))
