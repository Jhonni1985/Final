import html
import json
import random
from datetime import datetime
from typing import Optional, List

import requests
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html

from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER
from tg_bot.__main__ import STATS, USER_INFO
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.helper_funcs.filters import CustomFilters

RUN_STRINGS = (
    "¿A donde vas?",
    "¿Eh? ¿Qué? ¿Se escaparon?",
    "ZZzzZZzz ... ¿Eh? ¿Qué? Oh, solo ellos de nuevo, no importa.",
    "¡Regresa aquí!",
    "No tan rapido...",
    "¡Cuidado con la pared!",
    "¡¡No me dejes solo con ellos !!",
    "Corres, te mueres",
    "Bromas sobre ti, estoy en todas partes",
    "Te vas a arrepentir de eso ...",
    "También podrías probar /kickme, escuché que es divertido",
    "Ve a molestar a alguien más, a nadie aquí le importa",
    "Puedes correr, pero no puedes esconderte",
    "¿Es todo lo que tienes?",
    "Estoy detrás tuyo...",
    "¡Tienes compañía!",
    "Podemos hacer esto de la manera fácil o de la manera difícil",
    "Simplemente no lo entiendes, ¿verdad?",
    "¡Sí, será mejor que corras!",
    "Por favor, recuérdame lo mucho que me importa",
    "Corría más rápido si fuera tú",
    "Ese es definitivamente el droide que estamos buscando",
    "Que las probabilidades estén siempre a tu favor",
    "Últimas palabras famosas.",
    "Y desaparecieron para siempre, para nunca más ser vistos",
    "Sí, sí, solo tócame, toca este comando /kickme",
    "Toma, toma este anillo y dirígete a Mordor mientras estás en eso",
    "Cuenta la leyenda, todavía están funcionando ...",
    "A diferencia de Harry Potter, tus padres no pueden protegerte de mí",
    "El miedo conduce a la ira. La ira conduce al odio. El odio conduce al sufrimiento. Si sigues corriendo con miedo, es posible que"
    "sé el próximo Vader",
    "Soca en /kickme y vé la magia ante tus ojos"
    "Después de varios cálculos, he decidido que mi interés en tus travesuras es exactamente 0",
    "Cuenta la leyenda, todavía están funcionando",
    "Sigue así, no estoy seguro de que te queramos aquí de todos modos",
    "Eres un wiza- Oh. Espera. No eres Harry, sigue moviéndote.",
    "¡NO CORRER EN LOS PASILLOS!",
    "Hasta la vista bebé.",
    "¿Quién soltó los perros?",
    "Es gracioso, porque a nadie le importa",
    "Ah, que desperdicio. Me gustó ese.",
    "Francamente, querida, me importa un carajo",
    "Mi batido trae a todos los chicos al patio ... ¡Así que corre más rápido!",
    "¡No puedes MANEJAR la verdad!",
    "Hace mucho tiempo, en una galaxia muy lejana ... A alguien le habría importado eso. Pero ya no.",
    "¡Oye, míralos! Están huyendo del inevitable BanHammer ... lindo.",
    "Han disparó primero. Yo también",
    "¿A qué corres, un conejo blanco?",
    "Como diría el Doctor ... ¡CORRE!",
)

SLAP_TEMPLATES = (
    "{user1} {hits} {user2} con {item}.",
    "{user1} {hits} {user2} en la cara con un {item}.",
    "{user1} {hits} {user2} los surtio con {item}.",
    "{user1} {throws} con {item} a {user2}.",
    "{user1} agarra una {item} y {throws} le dio la cara a {user2}.",
    "{user1} lanzo {item} a {user2}.",
    "{user1} Empezo a darle nalgadas a {user2} suave con {item}.",
    "{user1} Dejo atad@ {user2} y repetidamente {hits} con un {item}.",
    "{user1} Tomo un {item} y {hits} {user2} con eso.",
    "{user1} maniato a {user2} a la silla {throws} un {item} jaja.",
    
)

ITEMS = (
    "sartén de hierro fundido",
    "trucha grande",
    "bate de béisbol",
    "Bate de cricket",
    "bastón de madera",
    "clavo",
    "impresora",
    "pala",
    "Monitor CRT",
    "libro de texto de física",
    "tostadora",
    "retrato de Richard Stallman",
    "televisión",
    "camión de cinco toneladas",
    "rollo de cinta adhesiva",
    "libro",
    "computadora portátil",
    "televisión vieja",
    "saco de rocas",
    "trucha arcoiris",
    "pollo de goma",
    "murciélago con púas",
    "extintor de incendios",
    "rock pesado",
    "trozo de tierra",
    "Colmena",
    "trozo de carne podrida",
    "soportar",
    "tonelada de ladrillos",
)

THROW = (
    "throws",
    "flings",
    "chucks",
    "hurls",
)

HIT = (
    "hits",
    "whacks",
    "slaps",
    "smacks",
    "bashes",
)

GMAPS_LOC = "https://maps.googleapis.com/maps/api/geocode/json"
GMAPS_TIME = "https://maps.googleapis.com/maps/api/timezone/json"


@run_async
def runs(bot: Bot, update: Update):
    update.effective_message.reply_text(random.choice(RUN_STRINGS))


@run_async
def slap(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id:
        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user

    temp = random.choice(SLAP_TEMPLATES)
    item = random.choice(ITEMS)
    hit = random.choice(HIT)
    throw = random.choice(THROW)

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@run_async
def get_bot_ip(bot: Bot, update: Update):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@run_async
def get_id(bot: Bot, update: Update, args: List[str]):
    user_id = extract_user(update.effective_message, args)
    if user_id:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(
                "El envio original, {}, tiene el ID `{}`.\nQuien reenvia, {}, Tiene el ID `{}`.".format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id),
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = bot.get_chat(user_id)
            update.effective_message.reply_text("{}'tiene el id `{}`.".format(escape_markdown(user.first_name), user.id),
                                                parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            update.effective_message.reply_text("Tu id es `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            update.effective_message.reply_text("Este grupo tiene el id `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)


@run_async
def info(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        msg.reply_text("No podes sacar un id de esto.")
        return

    else:
        return

    text = "<b>User info</b>:" \
           "\nID: <code>{}</code>" \
           "\nPrimer nombre: {}".format(user.id, html.escape(user.first_name))

    if user.last_name:
        text += "\nApellido: {}".format(html.escape(user.last_name))

    if user.username:
        text += "\nNombre de usuario: @{}".format(html.escape(user.username))

    text += "\nLink al usuario: {}".format(mention_html(user.id, "link"))

    if user.id == OWNER_ID:
        text += "\n\nEsta persona es mi creador - Si hago algo contra el tengo miedo de que me borre!"
    else:
        if user.id in SUDO_USERS:
            text += "\nEste es miembro del equipo de Zero! " \
                    "Casi con el mismo poder que el - asi que ojo con el gban."
        else:
            if user.id in SUPPORT_USERS:
                text += "\nEste es uno de los colaboradores de Zero! " \
                        "No como uno de su equipo, pero aun asi puede gbanearte del mapa."

            if user.id in WHITELIST_USERS:
                text += "\nEsta persona esta en la lista blanca...! " \
                        "Quiere decir que no puedo tocarlo/a."

    for mod in USER_INFO:
        mod_info = mod.__user_info__(user.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def get_time(bot: Bot, update: Update, args: List[str]):
    location = " ".join(args)
    if location.lower() == bot.first_name.lower():
        update.effective_message.reply_text("Nada me gusta mas que banear!")
        bot.send_sticker(update.effective_chat.id, BAN_STICKER)
        return

    res = requests.get(GMAPS_LOC, params=dict(address=location))

    if res.status_code == 200:
        loc = json.loads(res.text)
        if loc.get('status') == 'OK':
            lat = loc['results'][0]['geometry']['location']['lat']
            long = loc['results'][0]['geometry']['location']['lng']

            country = None
            city = None

            address_parts = loc['results'][0]['address_components']
            for part in address_parts:
                if 'country' in part['types']:
                    country = part.get('long_name')
                if 'administrative_area_level_1' in part['types'] and not city:
                    city = part.get('long_name')
                if 'locality' in part['types']:
                    city = part.get('long_name')

            if city and country:
                location = "{}, {}".format(city, country)
            elif country:
                location = country

            timenow = int(datetime.utcnow().timestamp())
            res = requests.get(GMAPS_TIME, params=dict(location="{},{}".format(lat, long), timestamp=timenow))
            if res.status_code == 200:
                offset = json.loads(res.text)['dstOffset']
                timestamp = json.loads(res.text)['rawOffset']
                time_there = datetime.fromtimestamp(timenow + timestamp + offset).strftime("%H:%M:%S on %A %d %B")
                update.message.reply_text("It's {} in {}".format(time_there, location))


@run_async
def echo(bot: Bot, update: Update):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)
    message.delete()


@run_async
def gdpr(bot: Bot, update: Update):
    update.effective_message.reply_text("Deleting identifiable data...")
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text("Your personal data has been deleted.\n\nNote that this will not unban "
                                        "you from any chats, as that is telegram data, not Zero data. "
                                        "Flooding, warns, and gbans are also preserved, as of "
                                        "[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-to-erasure/), "
                                        "which clearly states that the right to erasure does not apply "
                                        "\"for the performance of a task carried out in the public interest\", as is "
                                        "the case for the aforementioned pieces of data.",
                                        parse_mode=ParseMode.MARKDOWN)


MARKDOWN_HELP = """
(Codde pasado, no pienso traducirlo) Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
""".format(dispatcher.bot.first_name)


@run_async
def markdown_help(bot: Bot, update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text("Intenta reenviarme el siguiente mensaje y vas a ver!")
    update.effective_message.reply_text("/save test This is a markdown test. _italics_, *bold*, `code`, "
                                        "[URL](example.com) [button](buttonurl:github.com) "
                                        "[button2](buttonurl://google.com:same)")


@run_async
def stats(bot: Bot, update: Update):
    update.effective_message.reply_text("Current stats:\n" + "\n".join([mod.__stats__() for mod in STATS]))

@run_async
def stickerid(bot: Bot, update: Update):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text("Hello " +
                                            "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)
                                            + ", The sticker id you are replying is :\n```" + 
                                            escape_markdown(msg.reply_to_message.sticker.file_id) + "```",
                                            parse_mode=ParseMode.MARKDOWN)
    else:
        update.effective_message.reply_text("Hello " + "[{}](tg://user?id={})".format(msg.from_user.first_name,
                                            msg.from_user.id) + ", Please reply to sticker message to get id sticker",
                                            parse_mode=ParseMode.MARKDOWN)
@run_async
def getsticker(bot: Bot, update: Update):
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        bot.sendChatAction(chat_id, "typing")
        update.effective_message.reply_text("Hello " + "[{}](tg://user?id={})".format(msg.from_user.first_name,
                                            msg.from_user.id) + ", Please check the file you requested below."
                                            "\nPlease use this feature wisely!",
                                            parse_mode=ParseMode.MARKDOWN)
        bot.sendChatAction(chat_id, "upload_document")
        file_id = msg.reply_to_message.sticker.file_id
        newFile = bot.get_file(file_id)
        newFile.download('sticker.png')
        bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
        bot.sendChatAction(chat_id, "upload_photo")
        bot.send_photo(chat_id, photo=open('sticker.png', 'rb'))
        
    else:
        bot.sendChatAction(chat_id, "typing")
        update.effective_message.reply_text("Hello " + "[{}](tg://user?id={})".format(msg.from_user.first_name,
                                            msg.from_user.id) + ", Please reply to sticker message to get sticker image",
                                            parse_mode=ParseMode.MARKDOWN)

# /ip is for private use
__help__ = """
 - /id: El id del grupo, pero si respondes un mensaje es el id del usuario.
 - /runs: Da una respuesta aleatoria.
 - /slap: das o recibes golpes.
 - /time <place>: da la hora en x lugar.
 - /info: Da info de un usuario.
 - /gdpr: Borra tu propia info. Private chats only.
 - /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats.
 - /stickerid: Da el ID de un sticker.
 - /getsticker: Responde a un sticker con esto y te doy el png. 
"""

__mod_name__ = "Misc"

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True)
IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))

TIME_HANDLER = CommandHandler("time", get_time, pass_args=True)

RUNS_HANDLER = DisableAbleCommandHandler("runs", runs)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True)

ECHO_HANDLER = CommandHandler("echo", echo, filters=Filters.user(OWNER_ID))
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)

STATS_HANDLER = CommandHandler("stats", stats, filters=CustomFilters.sudo_filter)
GDPR_HANDLER = CommandHandler("gdpr", gdpr, filters=Filters.private)

STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker)


dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(TIME_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(STICKERID_HANDLER)
dispatcher.add_handler(GETSTICKER_HANDLER)
