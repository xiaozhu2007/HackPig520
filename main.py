import os
import random
import aiohttp
import time
import json
from datetime import datetime, timedelta
import copy

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from khl.command import Rule

# Init Bot
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
# `/xyz 1 100` to dice 5 times once
@bot.command(regex=r'(?:\.|\/|。|!|！)(?:xyz|幸运值|我的xyz)')
async def xyz(msg: Message):  # 幸运值
    result = [random.randint(0, 100) for i in range(1)]
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_msg = f"[{time_now}] {msg.author.username}#{msg.author.identify_num} 查询幸运值 \n[{time_now}] 返回幸运值 {result} 给{msg.author.username}#{msg.author.identify_num}"
    print(log_msg)
    await msg.reply(f'你的幸运值是: {result}')


@bot.command(regex=r'(?:\.|\/|。|!)(?:查服|find|fs)(.+)')
async def look(msg: Message, d: str = ''):
    if d.startswith(' '):
        await check(msg, d[1:], '')
    elif d.find(' ') < 0:
        await check(msg, '', d)
    else:
        game = d[:d.find(' ')].strip()
        name = d[d.find(' '):].strip()
        await check(msg, name, game)


async def reflect(game: str) -> str:
    with open('reflect.json', 'r') as f:
        rt = json.loads(f.read())
    if game in rt:
        return rt[game]
    else:
        return game


async def check(msg: Message, name: str = '', game: str = ''):
    game = await reflect(game.lower())
    name = name.strip()
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_msg = f"[{time_now}] {msg.author.username}#{msg.author.identify_num} 查询 {game}:{name}"
    print(log_msg)
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://api.battlemetrics.com/servers?filter[search]={name}&filter[game]={game}'
        ) as resp:
            rj = await resp.json()
            if len(rj['data']) == 0:
                await msg.reply('搜索结果为空')
            elif len(rj['data']) == 1:
                name = rj['data'][0]['attributes']['name']
                players = rj['data'][0]['attributes']['players']
                max_players = rj['data'][0]['attributes']['maxPlayers']
                if 'map' in rj['data'][0]['attributes']['details']:
                    map_name = rj['data'][0]['attributes']['details']['map']
                if rj['data'][0]['attributes']['address'] is not None:
                    address = rj['data'][0]['attributes']['address']
                else:
                    ip = rj['data'][0]['attributes']['ip']
                    port = rj['data'][0]['attributes']['port']
                c = Card()
                c.theme = Types.Theme.WARNING
                c.append(Module.Header(f'{name}'))
                text = ''
                text += f'人数: {players}/{max_players}\n'
                if 'map' in rj['data'][0]['attributes']['details']:
                    text += f'地图: {map_name}\n'
                if rj['data'][0]['attributes']['address'] is not None:
                    text += f'IP: {address}'
                else:
                    text += f'IP: {ip}:{port}'
                c.append(
                    Module.Section(
                        Element.Text(content=text, type=Types.Text.KMD)))
                await msg.reply(CardMessage(c))
            else:
                count = 1
                c = Card()
                c.theme = Types.Theme.INFO
                c.append(Module.Header('查询到多个服务器, 显示前10个'))
                c.append(Module.Divider())
                for i in rj['data']:
                    name = i['attributes']['name']
                    players = i['attributes']['players']
                    max_players = i['attributes']['maxPlayers']
                    if 'map' in i['attributes']['details']:
                        map_name = i['attributes']['details']['map']
                    if i['attributes']['address'] is not None:
                        address = i['attributes']['address']
                    else:
                        ip = i['attributes']['ip']
                        port = i['attributes']['port']
                    c.append(Module.Header(f'{count}:  {name}'))
                    text = ''
                    text += f'人数: {players}/{max_players}\n'
                    if 'map' in i['attributes']['details']:
                        text += f'地图: {map_name}\n'
                    if i['attributes']['address'] is not None:
                        text += f'IP: {address}'
                    else:
                        text += f'IP: {ip}:{port}'
                    c.append(
                        Module.Section(
                            Element.Text(content=text, type=Types.Text.KMD)))
                    c.append(Module.Divider())
                    count += 1
                await msg.reply(CardMessage(c))

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

bot.run()
