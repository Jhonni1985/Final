import random, re
from random import randint
from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler

ABUSE_STRINGS = (
    "Muerete",
    "Pegate un tirof",
    "Te lastras a pinocho? como un amigo de Zero?",
    "Ups, esta en una relacion consigo mism@ y se mete los cueron jajaja",
    "Me vales verga",
    "Nigga",
    "Ur granny tranny",
    "Queres algo de la casa de tu mamá? se lo pido antes de irme",
)

EYES = [
    ['⌐■', '■'],
    [' ͠°', ' °'],
    ['⇀', '↼'],
    ['´• ', ' •`'],
    ['´', '`'],
    ['`', '´'],
    ['ó', 'ò'],
    ['ò', 'ó'],
    ['⸌', '⸍'],
    ['>', '<'],
    ['Ƹ̵̡', 'Ʒ'],
    ['ᗒ', 'ᗕ'],
    ['⟃', '⟄'],
    ['⪧', '⪦'],
    ['⪦', '⪧'],
    ['⪩', '⪨'],
    ['⪨', '⪩'],
    ['⪰', '⪯'],
    ['⫑', '⫒'],
    ['⨴', '⨵'],
    ['⩿', '⪀'],
    ['⩾', '⩽'],
    ['⩺', '⩹'],
    ['⩹', '⩺'],
    ['◥▶', '◀◤'],
    ['◍', '◎'],
    ['/͠-', '┐͡-\\'],
    ['⌣', '⌣”'],
    [' ͡⎚', ' ͡⎚'],
    ['≋'],
    ['૦ઁ'],
    ['  ͯ'],
    ['  ͌'],
    ['ළ'],
    ['◉'],
    ['☉'],
    ['・'],
    ['▰'],
    ['ᵔ'],
    [' ﾟ'],
    ['□'],
    ['☼'],
    ['*'],
    ['`'],
    ['⚆'],
    ['⊜'],
    ['>'],
    ['❍'],
    ['￣'],
    ['─'],
    ['✿'],
    ['•'],
    ['T'],
    ['^'],
    ['ⱺ'],
    ['@'],
    ['ȍ'],
    ['  '],
    ['  '],
    ['x'],
    ['-'],
    ['$'],
    ['Ȍ'],
    ['ʘ'],
    ['Ꝋ'],
    [''],
    ['⸟'],
    ['๏'],
    ['ⴲ'],
    ['◕'],
    ['◔'],
    ['✧'],
    ['■'],
    ['♥'],
    [' ͡°'],
    ['¬'],
    [' º '],
    ['⨶'],
    ['⨱'],
    ['⏓'],
    ['⏒'],
    ['⍜'],
    ['⍤'],
    ['ᚖ'],
    ['ᴗ'],
    ['ಠ'],
    ['σ'],
    ['☯']
]

MOUTHS = [
    ['v'],
    ['ᴥ'],
    ['ᗝ'],
    ['Ѡ'],
    ['ᗜ'],
    ['Ꮂ'],
    ['ᨓ'],
    ['ᨎ'],
    ['ヮ'],
    ['╭͜ʖ╮'],
    [' ͟ل͜'],
    [' ͜ʖ'],
    [' ͟ʖ'],
    [' ʖ̯'],
    ['ω'],
    [' ³'],
    [' ε '],
    ['﹏'],
    ['□'],
    ['ل͜'],
    ['‿'],
    ['╭╮'],
    ['‿‿'],
    ['▾'],
    ['‸'],
    ['Д'],
    ['∀'],
    ['!'],
    ['人'],
    ['.'],
    ['ロ'],
    ['_'],
    ['෴'],
    ['ѽ'],
    ['ഌ'],
    ['⏠'],
    ['⏏'],
    ['⍊'],
    ['⍘'],
    ['ツ'],
    ['益'],
    ['╭∩╮'],
    ['Ĺ̯'],
    ['◡'],
    [' ͜つ']
]

EARS = [
    ['q', 'p'],
    ['ʢ', 'ʡ'],
    ['⸮', '?'],
    ['ʕ', 'ʔ'],
    ['ᖗ', 'ᖘ'],
    ['ᕦ', 'ᕥ'],
    ['ᕦ(', ')ᕥ'],
    ['ᕙ(', ')ᕗ'],
    ['ᘳ', 'ᘰ'],
    ['ᕮ', 'ᕭ'],
    ['ᕳ', 'ᕲ'],
    ['(', ')'],
    ['[', ']'],
    ['¯\\_', '_/¯'],
    ['୧', '୨'],
    ['୨', '୧'],
    ['⤜(', ')⤏'],
    ['☞', '☞'],
    ['ᑫ', 'ᑷ'],
    ['ᑴ', 'ᑷ'],
    ['ヽ(', ')ﾉ'],
    ['\\(', ')/'],
    ['乁(', ')ㄏ'],
    ['└[', ']┘'],
    ['(づ', ')づ'],
    ['(ง', ')ง'],
    ['⎝', '⎠'],
    ['ლ(', 'ლ)'],
    ['ᕕ(', ')ᕗ'],
    ['(∩', ')⊃━☆ﾟ.*'],
]

TOSS = (
    "Cara",
    "Cruz",
)

@run_async
def roll(bot: Bot, update: Update):
    update.message.reply_text(random.choice(range(1, 7)))
	
def toss(bot: Bot, update: Update):
    update.message.reply_text(random.choice(TOSS))

@run_async
def abuse(bot: Bot, update: Update):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(ABUSE_STRINGS))
	
@run_async
def shrug(bot: Bot, update: Update):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text("¯\_(ツ)_/¯")	
	
@run_async
def bluetext(bot: Bot, update: Update):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text("TEXTO AZUL\n Tenes que tocar\n Claramente sos un idiota atraido por colores")		

@run_async
def rlg(bot: Bot, update: Update):
    # reply to correct message
    eyes = random.choice(EYES)
    mouth = random.choice(MOUTHS)
    ears = random.choice(EARS)
    repl = format(ears + eyes + mouth + eyes + ears)
    update.message.reply_text(repl)
	
def decide(bot: Bot, update: Update):
        r = randint(1, 100)
        if r <= 65:
            update.message.reply_text("Si, olvidate.")
        elif r <= 90:
            update.message.reply_text("Nop, ni ahi.")
        else:
            update.message.reply_text("Podria ser.")
            
def table(bot: Bot, update: Update):
            r = randint(1, 100)
            if r <= 45:
                update.message.reply_text("(╯°□°）╯彡 ┻━┻")
            elif r <= 90:
                update.message.reply_text("Mandame plata para.. no importa, mandame")
            else:
                update.message.reply_text("No tenes nada mejor que hacer?.")
		
__help__ = """
 - /shrug : PROBA jaja.
 - /table : Un flip en patineta :v.
 - /decide : Responde aleatoriamente si/no/podria ser
 - /toss : Tira una moneda
 - /abuse : Insulta
 - /tts <any text> : Texto a voz
 - /bluetext : Proba :V
 - /roll : Tira un dado.
 - /rlg : Junta partes y arma una cara ;-;
 - /zal <texto> : zalgofy! cualquier texto
 Lyrics Plugin will take some moar time to come up.
"""

__mod_name__ = "Extras"

ROLL_HANDLER = DisableAbleCommandHandler("roll", roll)
TOSS_HANDLER = DisableAbleCommandHandler("toss", toss)
SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug)
BLUETEXT_HANDLER = DisableAbleCommandHandler("bluetext", bluetext)
RLG_HANDLER = DisableAbleCommandHandler("rlg", rlg)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide)
TABLE_HANDLER = DisableAbleCommandHandler("table", table)

dispatcher.add_handler(ROLL_HANDLER)
dispatcher.add_handler(TOSS_HANDLER)
dispatcher.add_handler(SHRUG_HANDLER)
dispatcher.add_handler(BLUETEXT_HANDLER)
dispatcher.add_handler(RLG_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(TABLE_HANDLER)
