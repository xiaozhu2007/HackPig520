import os
import random
from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event, Game
from khl.card import CardMessage, Card, Module, Types
from khl.command import Rule

# init Bot
bot = Bot(token=os.environ['BOT_TOKEN'])


# register command, send `/hello` in channel to invoke
@bot.command(name='hello')
async def world(msg: Message):
    await msg.reply('Hi!')


@bot.command(rules=[Rule.is_mention_all])
async def yes(msg: Message, mention_str: str):
    await msg.reply(f'Yes! You mentioned all with {mention_str}')


def is_contains(keyword: str):
    def func(msg: Message):
        return msg.content.find(keyword) != -1

    return func


@bot.command()
async def card(msg: Message):
    c = Card(Module.Header('CardMessage'),
             Module.Section('convenient to convey structured information'))
    cm = CardMessage(
        c)  # Card can not be sent directly, need to wrapped with a CardMessage
    await msg.reply(cm)


@bot.command()
async def countdown(msg: Message):
    cm = CardMessage()
    c1 = Card(Module.Header('1小时倒计时'),
              color=(90, 59, 215))  # color='#5A3BD7' is another available form
    c1.append(Module.Divider())
    c1.append(
        Module.Countdown(datetime.now() + timedelta(hours=1),
                         mode=Types.CountdownMode.SECOND))
    cm.append(c1)

    await msg.reply(cm)


# 幸运值
# invoke this via saying `!roll 1 100` in channel
# or `/xyz 1 100 5` to dice 5 times once
@bot.command()
async def xyz(msg: Message):  # 幸运值
    result = [random.randint(0, 100) for i in range(1)]
    await msg.reply(f'你的幸运值是: {result}')




bot.run()
