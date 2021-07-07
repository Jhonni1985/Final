from functools import wraps
from typing import Optional

from tg_bot.modules.helper_funcs.misc import is_module_loaded

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import Bot, Update, ParseMode, Message, Chat
    from telegram.error import BadRequest, Unauthorized
    from telegram.ext import CommandHandler, run_async
    from telegram.utils.helpers import escape_markdown

    from tg_bot import dispatcher, LOGGER
    from tg_bot.modules.helper_funcs.chat_status import user_admin
    from tg_bot.modules.sql import log_channel_sql as sql


    def loggable(func):
        @wraps(func)
        def log_action(bot: Bot, update: Update, *args, **kwargs):
            result = func(bot, update, *args, **kwargs)
            chat = update.effective_chat  # type: Optional[Chat]
            message = update.effective_message  # type: Optional[Message]
            if result:
                if chat.type == chat.SUPERGROUP and chat.username:
                    result += "\n<b>Link:</b> " \
                              "<a href=\"http://telegram.me/{}/{}\">click aca</a>".format(chat.username,
                                                                                           message.message_id)
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    send_log(bot, log_chat, chat.id, result)
            elif result == "":
                pass
            else:
                LOGGER.warning("%s was set as loggable, but had no return statement.", func)

            return result

        return log_action


    def send_log(bot: Bot, log_chat_id: str, orig_chat_id: str, result: str):
        try:
            bot.send_message(log_chat_id, result, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            if excp.message == "Chat no encontrado":
                bot.send_message(orig_chat_id, "El canal de registros se elimino.")
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("Could not parse")

                bot.send_message(log_chat_id, result + "\n\nFormatting has been disabled due to an unexpected error.")


    @run_async
    @user_admin
    def logging(bot: Bot, update: Update):
        message = update.effective_message  # type: Optional[Message]
        chat = update.effective_chat  # type: Optional[Chat]

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = bot.get_chat(log_channel)
            message.reply_text(
                "Este grupo esta guardando registros en: {} (`{}`)".format(escape_markdown(log_channel_info.title),
                                                                         log_channel),
                parse_mode=ParseMode.MARKDOWN)

        else:
            message.reply_text("No hay canal de registro preparado todavia!")


    @run_async
    @user_admin
    def setlog(bot: Bot, update: Update):
        message = update.effective_message  # type: Optional[Message]
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == chat.CHANNEL:
            message.reply_text("Ahora, envia /setlog en el grupo que queres linkear con este canal!")

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Mensaje para borrar no encontrado":
                    pass
                else:
                    LOGGER.exception("Error eliminando mensaje en el log.")

            try:
                bot.send_message(message.forward_from_chat.id,
                                 "Este canal guarda los registros de {}.".format(
                                     chat.title or chat.first_name))
            except Unauthorized as excp:
                if excp.message == "Error: no soy miembro del canal o del grupo":
                    bot.send_message(chat.id, "Seteado como canal de registro!")
                else:
                    LOGGER.exception("ERROR preparando el canal de registro.")

            bot.send_message(chat.id, "Exito preparando el registro!")

        else:
            message.reply_text("Pasos para hacer el canal de reg:\n"
                               " - agrega el bot al canal\n"
                               " - envia /setlog en el canal\n"
                               " - *reenvia* /setlog al grupo\n")


    @run_async
    @user_admin
    def unsetlog(bot: Bot, update: Update):
        message = update.effective_message  # type: Optional[Message]
        chat = update.effective_chat  # type: Optional[Chat]

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            bot.send_message(log_channel, "Canal desvinculado de {}".format(chat.title))
            message.reply_text("Canal desvincualdo.")

        else:
            message.reply_text("Aun no se hizo canal de reg!")


    def __stats__():
        return "{} Registro pronto.".format(sql.num_logchannels())


    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)


    def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = dispatcher.bot.get_chat(log_channel)
            return "Este grupo envia los registros a: {} (`{}`)".format(escape_markdown(log_channel_info.title),
                                                                            log_channel)
        return "No hay canal!"


    __help__ = """
*Admin only:*
- /logchannel: Da la info del canal de reg
- /setlog: Setea el canal.
- /unsetlog: Quita el canal.

Setting the log channel is done by:
- Agregando el bot al canal (como admin!)
- enviando /setlog en el canal
- reenviando /setlog al grupo desde el canal
"""

    __mod_name__ = "Log Channels"

    LOG_HANDLER = CommandHandler("logchannel", logging)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog)

    dispatcher.add_handler(LOG_HANDLER)
    dispatcher.add_handler(SET_LOG_HANDLER)
    dispatcher.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func
