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

from pyrogram import Client, Filters, MessageHandler


class CmdModule(object):
    def __init__(self, _: Client, config: dict):
        self.commands = {
            'dump': [
                MessageHandler(self.dump, Filters.command('dump', config['prefix'])),
                'Show the dump of the inline queries of a reply markup'
            ]
        }

    @staticmethod
    async def dump(_, message):
        text = ''

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
                text += '%s -> %s\n' % (btn.text, data)
        await message.reply(text)
