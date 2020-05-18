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
from pyrogram import Client, Filters, MessageHandler, Message
from pyrogram.errors import BadRequest


class CmdModule(object):
    def __init__(self, _: Client, config: dict):
        self.commands = {
            'dump': [
                MessageHandler(self.dump, Filters.command('dump', config['prefix'])),
                'Show the dump of the inline queries of the reply markup of the replied message'
            ]
        }

    @staticmethod
    async def dump(client: Client, message: Message):
        if (message.reply_to_message is None
                or message.reply_to_message.reply_markup is None
                or message.reply_to_message.reply_markup.inline_keyboard is None):
            await message.stop_propagation()
        text = []

        for row in message.reply_to_message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data is not None:
                    data = btn.callback_data
                elif btn.url is not None:
                    data = btn.url
                elif btn.switch_inline_query is not None:
                    data = btn.switch_inline_query
                else:
                    data = btn.switch_inline_query_current_chat
                text.append('%s -> %s' % (btn.text, data))

        try:
            await client.edit_message_text(message.chat.id, message.message_id, os.linesep.join(text))
        except BadRequest:
            await client.send_message(message.chat.id, os.linesep.join(text))
