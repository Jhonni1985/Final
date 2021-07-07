from io import BytesIO
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from tg_bot.modules.helper_funcs.chat_status import is_user_ban_protected, bot_admin

import tg_bot.modules.sql.users_sql as sql
from tg_bot import dispatcher, OWNER_ID, LOGGER
from tg_bot.modules.helper_funcs.filters import CustomFilters

USERS_GROUP = 4


@run_async
def quickscope(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("No se identifico un usuarios/grupo valido")
    try:
        bot.kick_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Intentando banear " + to_kick + " desde" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
def quickunban(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("No se identifico un usuarios/grupo valido")
    try:
        bot.unban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Intentando desbanear " + to_kick + " desde" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
def banall(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text("Intentando " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue


@run_async
def snipe(bot: Bot, update: Update, args: List[str]):
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Dame tambien un chat de refencia!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("No puedo enviar al grupo %s", str(chat_id))
            update.effective_message.reply_text("No pude mandar el mensaje. Puede que yo no este en ese grupo?")


@run_async
@bot_admin
def getlink(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("No parece que te refieras a un grupo")
    chat = bot.getChat(chat_id)
    bot_member = chat.get_member(bot.id)
    if bot_member.can_invite_users:
        invitelink = bot.get_chat(chat_id).invite_link
        update.effective_message.reply_text(invitelink)
    else:
        update.effective_message.reply_text("No te acceso al link de invitacion!")


@bot_admin
def leavechat(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
        bot.leaveChat(chat_id)
    else:
        update.effective_message.reply_text("No parece que te estes refiriendo a un grupo")

__help__ = """
**SOLO Zero:**
- /getlink **chatid**: Para el link de inv te x grupo.
- /banall: Banear a todos los miembros de un grupo
- /leavechat **chatid** : Salir de un chat
**Solo Zero y su equipo AntiCP:**
- /quickscope **userid** **chatid**: Banear un usuario de un grupo.
- /quickunban **userid** **chatid**: Desbanearlo.
- /snipe **chatid** **string**: Enviar un mensaje a un grupo X.
- /rban **userid** **chatid** Banear remotamente
- /runban **userid** **chatid** Lo contrario
- /Stats: checkea el estado del bot
- /chatlist: Lista de grupos que usan el bot
- /gbanlist: Lista de baneados globales
- /gmutelist: Lista de muteados globales
- Chat bans via /restrict chat_id and /unrestrict chat_id commands
**Solo administradores de confianza de Zero:**
- /Gban : Banear globalmente
- /Ungban : lo contrario
- /Gmute : Mutear globalmente
- /Ungmute : Lo contrario
Equipo/dueño.
**Users:**
- /listsudo Lista de Confianza
- /listsupport Lista de soporte de confianza
"""
__mod_name__ = "Special"

SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
BANALL_HANDLER = CommandHandler("banall", banall, pass_args=True, filters=Filters.user(OWNER_ID))
QUICKSCOPE_HANDLER = CommandHandler("quickscope", quickscope, pass_args=True, filters=CustomFilters.sudo_filter)
QUICKUNBAN_HANDLER = CommandHandler("quickunban", quickunban, pass_args=True, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
LEAVECHAT_HANDLER = CommandHandler("leavechat", leavechat, pass_args=True, filters=Filters.user(OWNER_ID))

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANALL_HANDLER)
dispatcher.add_handler(QUICKSCOPE_HANDLER)
dispatcher.add_handler(QUICKUNBAN_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(LEAVECHAT_HANDLER)
