import json
from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct

# init Bot
bot = Bot(token=os.environ['BOT_TOKEN'])

@bot.command(regex=r'(?:\.|\/|。|!|！)(?:gq|放歌|点歌)')
async def music(msg: Message, src: str, img: str = 'https://s1.ax1x.com/2022/06/12/X2SPLn.png'):
    await msg.reply(
        CardMessage(
            Card(
                Module.Header('HackPig520实时点歌😄'),
                Module.Divider(),
                Module.File(src, '实时点歌', img),
                Module.Section(
                    '查看实现源码',
                    # LINK type: user will open the link in browser when clicked
                    Element.Button('Here', 'https://github.com/TWT233/khl.py', Types.Click.LINK)))))


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def print_btn_value(_: Bot, e: Event):
    await msg.reply(f'''{e.body['user_info']['nickname']} 选择了 {e.body['value']} ！''')
    print(f'''{e.body['user_info']['nickname']} 选择了 {e.body['value']}''')


# everything done, go ahead now!
bot.run()