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
from pyrogram.errors import BadRequest


class CmdModule(object):
    def __init__(self, _: Client, config: dict):
        self.commands = {  # Define the commands of the module
            'check': [  # Define the first command
                MessageHandler(self.check, Filters.command('check', config['prefix'])),
                # Define the handler of the command
                'Check if the userbot is online'  # Define the help message to be shown
            ]
            # Eventually add more commands with the same format
        }

    @staticmethod
    async def check(client, message):
        try:
            await client.edit_message_text(message.chat.id, message.message_id, '✌🏻 <b>Userbot online CHECK</b>')
        except BadRequest:
            await client.send_message(message.chat.id, '✌🏻 <b>Userbot online CHECK</b>')
