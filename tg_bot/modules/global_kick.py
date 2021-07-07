
import html
from telegram import Message, Update, Bot, User, Chat, ParseMode
from typing import List, Optional
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, STRICT_GBAN
from tg_bot.modules.helper_funcs.chat_status import user_admin, is_user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.misc import send_to_list
from tg_bot.modules.sql.users_sql import get_all_chats

GKICK_ERRORS = {
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
    "No en el chat",
    "El método está disponible solo para chats de canal y supergrupo",
    "Mensaje de respuesta no encontrado"
}

@run_async
def gkick(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    user_id = extract_user(message, args)
    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message in GKICK_ERRORS:
            pass
        else:
            message.reply_text("No puede ser globalmente kickeado porque: {}".format(excp.message))
            return
    except TelegramError:
            pass

    if not user_id:
        message.reply_text("no es un usuario")
        return
    if int(user_id) in SUDO_USERS or int(user_id) in SUPPORT_USERS:
        message.reply_text("OHHH! alguien intenta kickear globalmente a un amigo de Zero! *Hora de pochoclos*")
        return
    if int(user_id) == OWNER_ID:
        message.reply_text("Wow! Alguien es tan idiota que intenta kickear globalmente a mi creador! Idiota *Comiendo papitas*")
        return
    if int(user_id) == bot.id:
        message.reply_text("OHH...claro, porque no kickearme yo mismo... das lastima ")
        return
    chats = get_all_chats()
    message.reply_text("Kickeado globalmente el user @{}".format(user_chat.username))
    for chat in chats:
        try:
             bot.unban_chat_member(chat.chat_id, user_id)  # Unban_member = kick (and not ban)
        except BadRequest as excp:
            if excp.message in GKICK_ERRORS:
                pass
            else:
                message.reply_text("El usuario no puede ser GK porque: {}".format(excp.message))
                return
        except TelegramError:
            pass

GKICK_HANDLER = CommandHandler("gkick", gkick, pass_args=True,
                              filters=CustomFilters.sudo_filter | CustomFilters.support_filter)
dispatcher.add_handler(GKICK_HANDLER)                              
