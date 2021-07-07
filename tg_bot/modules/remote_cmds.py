import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram.error import BadRequest
from telegram.ext import run_async, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher
from tg_bot.modules.helper_funcs.chat_status import bot_admin, user_admin, is_user_ban_protected, can_restrict, \
    is_user_admin, is_user_in_chat, is_bot_admin
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.helper_funcs.filters import CustomFilters

RBAN_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "Usuario_no_participante",
    "Peer_id_invalid",
    "Se desactivó el chat grupal",
    "Necesita invitar a un usuario para sacarlo de un grupo básico",
    "Chat_admin_required",
    "Solo el creador de un grupo básico puede expulsar a los administradores del grupo",
    "Channel_private",
    "No en el chat"
}

RUNBAN_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "Usuario_no_participante",
    "Peer_id_invalid",
    "Se desactivó el chat grupal",
    "Necesita invitar a un usuario para sacarlo de un grupo básico",
    "Chat_admin_required",
    "Solo el creador de un grupo básico puede expulsar a los administradores del grupo",
    "Channel_private",
    "No en el chat"
}

RKICK_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "Usuario_no_participante",
    "Peer_id_invalid",
    "Se desactivó el chat grupal",
    "Necesita invitar a un usuario para sacarlo de un grupo básico",
    "Chat_admin_required",
    "Solo el creador de un grupo básico puede expulsar a los administradores del grupo",
    "Channel_private",
    "No en el chat"
}

RMUTE_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "Usuario_no_participante",
    "Peer_id_invalid",
    "Se desactivó el chat grupal",
    "Necesita invitar a un usuario para sacarlo de un grupo básico",
    "Chat_admin_required",
    "Solo el creador de un grupo básico puede expulsar a los administradores del grupo",
    "Channel_private",
    "No en el chat"
}

RUNMUTE_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "Usuario_no_participante",
    "Peer_id_invalid",
    "Se desactivó el chat grupal",
    "Necesita invitar a un usuario para sacarlo de un grupo básico",
    "Chat_admin_required",
    "Solo el creador de un grupo básico puede expulsar a los administradores del grupo",
    "Channel_private",
    "No en el chat"
}

@run_async
@bot_admin
def rban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("No parece que hables de un grupo o usuario.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No parece que hables de un grupo o usuario.")
        return
    elif not chat_id:
        message.reply_text("No parece que te refieras a un grupo.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("Grupo no encontrado! Confirma el ID y si estoy en el.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Nop, es un chat privado, sonamos!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("No puedo restringir gente aca! Seguro que soy admin? (muy inteligente).")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("No puedo encontrar el user y lpm..")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Me encantaria banear admins y adueñarme de todo, pero...")
        return

    if user_id == bot.id:
        message.reply_text("No me voy a banear a mi mismo, WTF?")
        return

    try:
        chat.kick_member(user_id)
        message.reply_text("Baneado de un grupo!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Baneado es pollo!', quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Carajo!, No puedo banear ese user, raro.")

@run_async
@bot_admin
def runban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("No parece que hables de un user o grupo.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No parece ser un usuario, algo esta mal.")
        return
    elif not chat_id:
        message.reply_text("No parece ser un grupo, algo esta mal.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("No encontre el grupo, confirma el ID y si estou en el.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Nop, chat privado (tarado)!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("No puedo banear a nadie ahi, seguro que soy admin, no? (idiota).")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Aca no esta ese user, se fue? rata")
            return
        else:
            raise
            
    if is_user_in_chat(chat, user_id):
        message.reply_text("Porque tratar de desbanear remotamente a alguien que ya esta en un chat?")
        return

    if user_id == bot.id:
        message.reply_text("Como me voy a desbanear yo mismo de donde soy admin? Cualquiera maneja un bot hoy")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Yep, este user puede entrar en ese grupo!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Unbanned!', quote=False)
        elif excp.message in RUNBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR unbanning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Ups, no puedo desbanearlo jajaja.")

@run_async
@bot_admin
def rkick(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("No parece que hables de un grupo o un usuario.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No parece que hables de un usuario.")
        return
    elif not chat_id:
        message.reply_text("No parece que hables de un grupo.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("No encontre el grupo, confirma el ID y si estoy en el (idiota).")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Nop, chat privado!!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("Na, no puedo kickear! Soy admin? anda a fijarte.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Este user no esta, se tomo el palo?")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Me encantaria kickear admins, pero es mala idea...")
        return

    if user_id == bot.id:
        message.reply_text("No me voy a kickear yo! Estamos locos?")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Afuera, rata!!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Kickead@ :)!', quote=False)
        elif excp.message in RKICK_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR kicking user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("No puedo keckearle, lpm.")

@run_async
@bot_admin
def rmute(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("No veo el grupo o usuario.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Seguro que es un user?.")
        return
    elif not chat_id:
        message.reply_text("Seguro que es un grupo?.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("No lo encuentro, seguro que el ID del grupo esta bien y yo estoy ahi?.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Ne, chat privado!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("No puedo mutear gente ahi! seguro soy admin?.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Parece que no lo encuentro")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Ojala pudiera mutear admins, sabes como cerrarian el...")
        return

    if user_id == bot.id:
        message.reply_text("No voy a mutearme yo mismo, amo escribir, idiota!")
        return

    try:
        bot.restrict_chat_member(chat.id, user_id, can_send_messages=False)
        message.reply_text("Ahh que pacho? cerramos la boca?!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Muteado!', quote=False)
        elif excp.message in RMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR mute user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("No quiero leerle mas y no puedo mutear!.")

@run_async
@bot_admin
def runmute(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("Seguro que es un usuario o grupo?.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No creo que sea un usuario valido.")
        return
    elif not chat_id:
        message.reply_text("Na, eso no es un id de grupo.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("Fijate otra vez el id o usuario.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Esta en privado, no se puede!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("Seguro que soy admin? Porque no pude.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("No encuentro nada, se fue?")
            return
        else:
            raise
            
    if is_user_in_chat(chat, user_id):
       if member.can_send_messages and member.can_send_media_messages \
          and member.can_send_other_messages and member.can_add_web_page_previews:
        message.reply_text("Ya puede hablar (por desgracia).")
        return

    if user_id == bot.id:
        message.reply_text("El colmo; desmutearme yo mismo!")
        return

    try:
        bot.restrict_chat_member(chat.id, int(user_id),
                                     can_send_messages=True,
                                     can_send_media_messages=True,
                                     can_send_other_messages=True,
                                     can_add_web_page_previews=True)
        message.reply_text("Sep, este user puede hablar.. (me cae mejor cuando no lo hace)!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Unmuted (al pepe)!', quote=False)
        elif excp.message in RUNMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR unmnuting user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Imposible desmutear, que cagada che.")

__help__ = ""

__mod_name__ = "Remote Commands"

RBAN_HANDLER = CommandHandler("rban", rban, pass_args=True, filters=CustomFilters.sudo_filter)
RUNBAN_HANDLER = CommandHandler("runban", runban, pass_args=True, filters=CustomFilters.sudo_filter)
RKICK_HANDLER = CommandHandler("rkick", rkick, pass_args=True, filters=CustomFilters.sudo_filter)
RMUTE_HANDLER = CommandHandler("rmute", rmute, pass_args=True, filters=CustomFilters.sudo_filter)
RUNMUTE_HANDLER = CommandHandler("runmute", runmute, pass_args=True, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
dispatcher.add_handler(RKICK_HANDLER)
dispatcher.add_handler(RMUTE_HANDLER)
dispatcher.add_handler(RUNMUTE_HANDLER)
