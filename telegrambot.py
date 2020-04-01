import io
import cowsay
import logging
import telegram
import contextlib
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import InlineQueryResultArticle
from telegram import ParseMode
from telegram import InputTextMessageContent
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler
from telegram.ext import InlineQueryHandler
from django_telegrambot.apps import DjangoTelegramBot
from kuhsag.constants import *
from kuhsag.commands import *
from uuid import uuid4


logger = logging.getLogger(__name__)
speakers = [
    {'name': 'Kuh', 'func': cowsay.cow, 'emoj': '🐄'},
    {'name': 'Tux', 'func': cowsay.tux, 'emoj': '🐧'},
    {'name': 'Tüdelizer', 'func': tuedelize, 'emoji': '🥴'},
]


def error(bot, update, error):
    logger.exception('Update "%s" caused error "%s"' % (update, error))


def inlinequery(bot, update):
    query = update.inline_query.query
    logger.debug(f'got query: {query}')

    if len(query) == 0:
        logger.info('empty query will not be processed')
        return
    options = []
    for speaker in speakers:
        cowtext = cowify(query, func=speaker['func'])
        options.append(
            InlineQueryResultArticle(
                #title=f'{speaker["emoj"]} {speaker["name"]} sagt:',
                title= speaker['emoj'] +' '+ speaker['name'],
                id=uuid4(),
                description=query,
                input_message_content = InputTextMessageContent(f'```{cowtext}```', parse_mode='Markdown')
            )
    )
    logger.debug(f'answered with {len(options)} options')
    #results = options #todo filter by query
    update.inline_query.answer(options, cache_time=0)


def main():
    logger.debug("Loading handlers for kuhsagbot")
    dp = DjangoTelegramBot.getDispatcher('kuhsagbot')
    for cmd in commands:
        pass_args = cmd.pass_args if hasattr(cmd, 'pass_args') else False
        name = cmd.command if hasattr(cmd, 'command') else cmd.__name__
        dp.add_handler(CommandHandler(name, cmd, pass_args=pass_args))
    #dp.add_handler(InlineQueryHandler(inlinequery))
    #dp.add_handler(CallbackQueryHandler(callback))
    #dp.add_error_handler(error)
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_error_handler(error)

    # log all errors
    #dp.add_error_handler(error)
