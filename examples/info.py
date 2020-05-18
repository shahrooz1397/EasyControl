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
import html
from pyrogram.errors import BadRequest
from pyrogram import Client, Filters, MessageHandler, Message


class CmdModule(object):
    def __init__(self, _: Client, config: dict):
        self.commands = {
            'info': [
                MessageHandler(self.info, Filters.command('info', config['prefix'])),
                'Show some info about the user of the replied message'
            ]
        }

    @staticmethod
    async def info(client: Client, message: Message):
        if message.reply_to_message is None:
            await message.stop_propagation()
        from_user = (await client.get_messages(
            message.chat.id,
            message.reply_to_message.message_id
        )).from_user
        from_chat = await client.get_chat(from_user.id)
        text = [
            '<b>Info about</b> <a href="tg://user?id={0}">{1}</a><b>:</b>'.format(
                from_user.id,
                html.escape(from_user.first_name)
            ),
            '<b>ID:</b> <code>{0}</code>'.format(from_user.id),
        ]

        if from_user.last_name is not None:
            text.append('<b>Last name:</b> <a href="tg://user?id={0}">{1}</a>'.format(
                from_user.id,
                html.escape(from_user.last_name)
            ))

        if from_user.username is not None:
            text.append('<b>Username:</b> @{0}'.format(from_user.username))

        if from_chat.description is not None:
            text.append('<b>Bio:</b> <code>{0}</code>'.format(from_chat.description))

        if from_user.language_code is not None:
            text.append('<b>Language code:</b> <code>{0}</code>'.format(from_user.language_code))

        if from_user.dc_id is not None:
            text.append('<b>DC ID:</b> <code>{0}</code>'.format(from_user.dc_id))
        text.append('<b>Is bot:</b> <code>{0}</code>'.format(from_user.is_bot))
        text.append('<b>Is verified:</b> <code>{0}</code>'.format(from_user.is_verified))
        text.append('<b>Is restricted:</b> <code>{0}</code>'.format(from_user.is_restricted))
        text.append('<b>Is scam:</b> <code>{0}</code>'.format(from_user.is_scam))
        text.append('<b>Is support:</b> <code>{0}</code>'.format(from_user.is_support))

        if not from_user.photo is None:
            try:
                await client.delete_messages(message.chat.id, message.message_id)
                profile_photo = (await client.get_profile_photos(from_user.id, limit=1))[0]
                await client.send_photo(
                    message.chat.id, profile_photo.file_id, profile_photo.file_ref,
                    os.linesep.join(text)
                )
            except BadRequest:
                try:
                    await client.edit_message(message.chat.id, message.message_id, os.linesep.join(text))
                except BadRequest:
                    await client.send_message(message.chat.id, os.linesep.join(text))
        else:
            try:
                await client.edit_message(message.chat.id, message.message_id, os.linesep.join(text))
            except BadRequest:
                await client.send_message(message.chat.id, os.linesep.join(text))
