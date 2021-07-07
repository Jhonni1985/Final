import html
from io import BytesIO
from typing import Optional, List

from telegram import Message, Update, Bot, User, Chat, ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html

import tg_bot.modules.sql.global_bans_sql as sql
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, STRICT_GBAN
from tg_bot.modules.helper_funcs.chat_status import user_admin, is_user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.misc import send_to_list
from tg_bot.modules.sql.users_sql import get_all_chats

GBAN_ENFORCE_GROUP = 6

GBAN_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "User_not_participant",
    "Peer_id_invalid",
    "Se desactivó el chat grupal",
    "Necesita invitar a un usuario para sacarlo de un grupo básico",
    "Chat_admin_required",
    "Solo el creador de un grupo básico puede expulsar a los administradores del grupo",
    "Channel_private",
    "No esta en el chat"
}

UNGBAN_ERRORS = {
    "El usuario es un administrador del chat",
    "Chat no encontrado",
    "No hay suficientes derechos para restringir / no restringir un miembro del chat",
    "User_not_participant",
    "El método está disponible solo para chats de canal y supergrupo",
    "No esta en el chat",
    "Channel_private",
    "Chat_admin_required",
}


@run_async
def gban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No es un usuario.")
        return

    if int(user_id) in SUDO_USERS:
        message.reply_text("Vi luz y entre, porque pelean chicas locas?")
        return

    if int(user_id) in SUPPORT_USERS:
        message.reply_text("OOOH un idiota intenta banear a alguien del equipo de Zero! *aca va a correr sangre*")
        return

    if user_id == bot.id:
        message.reply_text("-_- Claro, me baneo yo mismo.. simios.")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        message.reply_text(excp.message)
        return

    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gbanned(user_id):
        if not reason:
            message.reply_text("Ya fue globalmente baneado; Daberias darme una razon...")
            return

        old_reason = sql.update_gban_reason(user_id, user_chat.username or user_chat.first_name, reason)
        if old_reason:
            message.reply_text("Este user ya fue globalmente baneado por la siguiente razon:\n"
                               "<code>{}</code>\n"
                               "voy a updatearla con la tuya!".format(html.escape(old_reason)),
                               parse_mode=ParseMode.HTML)
        else:
            message.reply_text("Fue baneado global, pero no me dieron una razon!")

        return

    message.reply_text("⚡️ *Siente el poder de Thor y su Martillo* ⚡️")

    banner = update.effective_user  # type: Optional[User]
    send_to_list(bot, SUDO_USERS + SUPPORT_USERS,
                 "<b>Global Ban</b>" \
                 "\n#GBAN" \
                 "\n<b>Status:</b> <code>Enforcing</code>" \
                 "\n<b>Sudo Admin:</b> {}" \
                 "\n<b>User:</b> {}" \
                 "\n<b>ID:</b> <code>{}</code>" \
                 "\n<b>Reason:</b> {}".format(mention_html(banner.id, banner.first_name),
                                              mention_html(user_chat.id, user_chat.first_name), 
                                                           user_chat.id, reason or "Nunca me dieron un motivo, tampoco quiero uno"), 
                html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_all_chats()
    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.kick_chat_member(chat_id, user_id)
        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                message.reply_text("Could not gban due to: {}".format(excp.message))
                send_to_list(bot, SUDO_USERS + SUPPORT_USERS, "No puedo hacerlo porque: {}".format(excp.message))
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    send_to_list(bot, SUDO_USERS + SUPPORT_USERS, 
                  "{} Baneo perfecto! buena punteria!".format(mention_html(user_chat.id, user_chat.first_name)),
                html=True)
    message.reply_text("Idiota baneado globalmente.")


@run_async
def ungban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message  # type: Optional[Message]

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("No es un usuario.")
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != 'private':
        message.reply_text("Nop!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("No fue GBBaneado!")
        return

    banner = update.effective_user  # type: Optional[User]

    message.reply_text("Yo te perdono {}, globalmente con una segunda oportunidad.".format(user_chat.first_name))

    send_to_list(bot, SUDO_USERS + SUPPORT_USERS,
                 "<b>Retiro de Global Ban</b>" \
                 "\n#UNGBAN" \
                 "\n<b>Status:</b> <code>Ceased</code>" \
                 "\n<b>Sudo Admin:</b> {}" \
                 "\n<b>User:</b> {}" \
                 "\n<b>ID:</b> <code>{}</code>".format(mention_html(banner.id, banner.first_name),
                                                       mention_html(user_chat.id, user_chat.first_name), 
                                                                    user_chat.id),
                 html=True)

    chats = get_all_chats()
    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == 'kicked':
                bot.unban_chat_member(chat_id, user_id)

        except BadRequest as excp:
            if excp.message in UNGBAN_ERRORS:
                pass
            else:
                message.reply_text("No puedo quitar el gban: {}".format(excp.message))
                bot.send_message(OWNER_ID, "No puedo quitar el gban: {}".format(excp.message))
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    send_to_list(bot, SUDO_USERS + SUPPORT_USERS, 
                  "{} Fue perdonado del GB!".format(mention_html(user_chat.id, 
                                                                         user_chat.first_name)),
                  html=True)

    message.reply_text("Esta persona fue perdonada, aunque.. mas vale que se cuide!")


@run_async
def gbanlist(bot: Bot, update: Update):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text("There aren't any gbanned users! You're kinder than I expected...")
        return

    banfile = 'Que se jodan estos jueputas.\n'
    for user in banned_users:
        banfile += "[x] {} - {}\n".format(user["name"], user["user_id"])
        if user["reason"]:
            banfile += "Reason: {}\n".format(user["reason"])

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        update.effective_message.reply_document(document=output, filename="gbanlist.txt",
                                                caption="Lista de los actuales GBans.")


def check_and_ban(update, user_id, should_message=True):
    if sql.is_user_gbanned(user_id):
        update.effective_chat.kick_member(user_id)
        if should_message:
            update.effective_message.reply_text("Esta es una mala persona, y no debe estar aca.!")


@run_async
def enforce_gban(bot: Bot, update: Update):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    if sql.does_chat_gban(update.effective_chat.id) and update.effective_chat.get_member(bot.id).can_restrict_members:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        msg = update.effective_message  # type: Optional[Message]

        if user and not is_user_admin(chat, user.id):
            check_and_ban(update, user.id)

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user  # type: Optional[User]
            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id, should_message=False)


@run_async
@user_admin
def gbanstat(bot: Bot, update: Update, args: List[str]):
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            update.effective_message.reply_text("Habilite los gban en este grupo. Esto ayuda a protegerte "
                                                "de spammers, gente fea, y trolls (no sirve para suegras y ex toxic@s.")
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            update.effective_message.reply_text("Desabilite el gban en este grupo, asi que es menos seguro, aunque si viene alguna suegra no podria ser peor")
    else:
        update.effective_message.reply_text("Dame argumentos para los ajustes! on/off, yes/no!\n\n"
                                            "Actualmente es: {}\n"
                                            "Si esta on, cualquier gban tambien afecta tu grupo. "
                                            "Si es off, Te vamos a dejar arreglartelas "
                                            " asi que, suerte?.".format(sql.does_chat_gban(update.effective_chat.id)))


def __stats__():
    return "{} gbanned users.".format(sql.num_gbanned_users())


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)

    text = "Globally banned: <b>{}</b>"
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += "\nReason: {}".format(html.escape(user.reason))
    else:
        text = text.format("No")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return "This chat is enforcing *gbans*: `{}`.".format(sql.does_chat_gban(chat_id))


__help__ = """
*Admin only:*
 - /gbanstat <on/off/yes/no>: Desabilita la protexion global, o te devuelve a los parametros.

Gbans, conocido como global bans, es usado por los dueños de los bots para banear spamers, trolls, pedofilos, suegras.. Ayuda a proteger \
tu grupo de mucha gente lo mas rapido posible. Puede activarse usando \
/gbanstat
"""

__mod_name__ = "Global Bans"

GBAN_HANDLER = CommandHandler("gban", gban, pass_args=True,
                              filters=CustomFilters.sudo_filter | CustomFilters.support_filter)
UNGBAN_HANDLER = CommandHandler("ungban", ungban, pass_args=True,
                                filters=CustomFilters.sudo_filter | CustomFilters.support_filter)
GBAN_LIST = CommandHandler("gbanlist", gbanlist,
                           filters=CustomFilters.sudo_filter | CustomFilters.support_filter)

GBAN_STATUS = CommandHandler("gbanstat", gbanstat, pass_args=True, filters=Filters.group)

GBAN_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gban)

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
