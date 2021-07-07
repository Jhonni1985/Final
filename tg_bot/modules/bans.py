import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram.error import BadRequest
from telegram.ext import run_async, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, User, CallbackQuery

from tg_bot import dispatcher, BAN_STICKER, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import bot_admin, user_admin, is_user_ban_protected, can_restrict, \
    is_user_admin, is_user_in_chat, is_bot_admin
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.log_channel import loggable
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



@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No es un usuario aparentemente.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could ban admins...")
        return ""

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return ""

    log = "<b>{}:</b>" \
          "\n#BANNED" \
          "\n<b>Admin:</b> {}" \
          "\n<b>User:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name))
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        keyboard = []
        reply = "{} Banned!".format(mention_html(member.user.id, member.user.first_name))
        message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Banned!', quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Well damn, I can't ban that user.")

    return ""


@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No es un usuario aparentemente.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could ban admins...")
        return ""

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return ""

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return ""

    log = "<b>{}:</b>" \
          "\n#TEMP BANNED" \
          "\n<b>Admin:</b> {}" \
          "\n<b>User:</b> {}" \
          "\n<b>Time:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name), time_val)
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("Banned! User will be banned for {}.".format(time_val))
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Banned! User will be banned for {}.".format(time_val), quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Well damn, I can't ban that user.")

    return ""


@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def kick(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id):
        message.reply_text("I really wish I could kick admins...")
        return ""

    if user_id == bot.id:
        message.reply_text("Yeahhh I'm not gonna do that")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("Kicked!")
        log = "<b>{}:</b>" \
              "\n#KICKED" \
              "\n<b>Admin:</b> {}" \
              "\n<b>User:</b> {}".format(html.escape(chat.title),
                                         mention_html(user.id, user.first_name),
                                         mention_html(member.user.id, member.user.first_name))
        if reason:
            log += "\n<b>Reason:</b> {}".format(reason)

        return log

    else:
        message.reply_text("Well damn, I can't kick that user.")

    return ""


@run_async
@bot_admin
@can_restrict
def kickme(bot: Bot, update: Update):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("I wish I could... but you're an admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("No problem.")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@run_async
@bot_admin
@can_restrict
@user_admin
@loggable
def unban(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if user_id == bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text("Why are you trying to unban someone that's already in the chat?")
        return ""

    chat.unban_member(user_id)
    message.reply_text("Yep, this user can join!")

    log = "<b>{}:</b>" \
          "\n#UNBANNED" \
          "\n<b>Admin:</b> {}" \
          "\n<b>User:</b> {}".format(html.escape(chat.title),
                                     mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name))
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    return log


@run_async
@bot_admin
def rban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("No es un usuario o grupo, fijate bien.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No es un usuario aparentemente.")
        return
    elif not chat_id:
        message.reply_text("No es un grupo, confima los datos.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("No encontre el grupo, confirma el id y si estoy en el como admin.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Lo lamento, chat privado!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("I can't restrict people there! Make sure I'm admin and can ban users.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could ban admins...")
        return

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return

    try:
        chat.kick_member(user_id)
        message.reply_text("Banned!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('Banned!', quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Well damn, I can't ban that user.")

@run_async
@bot_admin
def runban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("No es un usuario o grupo, fijate bien.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No es un usuario aparentemente.")
        return
    elif not chat_id:
        message.reply_text("No es un grupo, confima los datos.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("No encontre el grupo, confirma el id y si estoy en el como admin.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Lo lamento, chat privado!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("No puedo desbanear a nadie, fijate si soy admin ahi.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("No veo este user aca, se tomo el palo?")
            return
        else:
            raise
            
    if is_user_in_chat(chat, user_id):
        message.reply_text("Para que desbanear a alguien que no esta??")
        return

    if user_id == bot.id:
        message.reply_text("No me voy a desbanear yo mismo, idiota!")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Yep, Este usuario puede entrar al grupo!")
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
            message.reply_text("Ay carajo! no puedo desbanearlo jajaja.")


__help__ = """
 - /kickme: Autokick

*Admin only:*
 - /ban <userhandle>: Banea
 - /tban <userhandle> x(m/h/d): banea por x tiempo. (via nombre, id o respuesta). m = minutos, h = horas, d = dias.
 - /unban <userhandle>: Desbanea.
 - /kick <userhandle>: kickea
"""

__mod_name__ = "Bans"

BAN_HANDLER = CommandHandler("ban", ban, pass_args=True, filters=Filters.group)
TEMPBAN_HANDLER = CommandHandler(["tban", "tempban"], temp_ban, pass_args=True, filters=Filters.group)
KICK_HANDLER = CommandHandler("kick", kick, pass_args=True, filters=Filters.group)
UNBAN_HANDLER = CommandHandler("unban", unban, pass_args=True, filters=Filters.group)
KICKME_HANDLER = DisableAbleCommandHandler("kickme", kickme, filters=Filters.group)
RBAN_HANDLER = CommandHandler("rban", rban, pass_args=True, filters=CustomFilters.sudo_filter)
RUNBAN_HANDLER = CommandHandler("runban", runban, pass_args=True, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
