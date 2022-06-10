import os
import random
import aiohttp
import time
import json
from datetime import datetime, timedelta
import copy

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types
from khl.command import Rule

# init Bot
bot = Bot(token=os.environ['BOT_TOKEN'])

# -*- encoding : utf-8 -*-
import copy
import json
import os
import random
import re
import time

from khl import Bot, Message, Cert
from khl.card import Card, Types, Module, CardMessage, Element

# 解法来自于知乎用户 @曲晋云 在 https://zhuanlan.zhihu.com/p/37608401 评论区内的回答
class Solution:
    solutions = set()

    def point24(self, numbers):
        if len(numbers) == 1:
            if abs(eval(numbers[0]) - 24) < 0.00001:
                self.solutions.add(numbers[0])
        else:
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    rest_numbers = [x for p, x in enumerate(numbers) if p != i and p != j]
                    for op in "+-*/":
                        if op in "+-*" or eval(str(numbers[j])) != 0:
                            self.point24(["(" + str(numbers[i]) + op + str(numbers[j]) + ")"] + rest_numbers)
                        if op == "-" or (op == "/" and eval(str(numbers[i])) != 0):
                            self.point24(["(" + str(numbers[j]) + op + str(numbers[i]) + ")"] + rest_numbers)

    def clear(self):
        self.solutions.clear()

    def get_answer(self):
        return self.solutions

    def is_have_answer(self):
        return len(self.solutions) >= 1

    def get_answer_top5_text(self):
        if len(self.solutions) == 0:
            return '无答案'
        answer = ''
        count = 1
        for i in self.solutions:
            answer += f'{i[1:-1]}\n'
            count += 1
            if count >= 6:
                break
        return answer.replace('*', '\\*')


cache = {}
solution_object = Solution()

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
@bot.command(regex=r'(?:\.|\/|。|!)(?:xyz|幸运值|我的xyz)')
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



@bot.command(regex=r'(?:24点)')
async def twenty_four_init(msg: Message):
    global cache
    cache_id = f'{msg.ctx.guild.id}-{msg.ctx.channel.id}-{msg.author_id}'
    if cache_id not in cache:
        solution = copy.deepcopy(solution_object)
        while True:
            cards = [random.randint(1, 13) for _ in range(4)]
            solution.clear()
            solution.point24(cards)
            if solution.is_have_answer():
                break
        cache[cache_id] = {'cards': cards, 'time': time.time(), 'answer': solution.get_answer_top5_text()}
        del solution
        await msg.reply(f'来一把紧张刺激的 24 点！输入算式进行推导，输入「24退出」结束游戏\n(met){msg.author_id}(met) 现在你手上有：{cards}，怎么凑 24 点呢？')
    else:
        await msg.reply(f'24点游戏还没结束哦~')


@bot.command(regex=r'(?:24退出)')
async def twenty_four_exit(msg: Message):
    global cache
    cache_id = f'{msg.ctx.guild.id}-{msg.ctx.channel.id}-{msg.author_id}'
    if cache_id not in cache:
        await msg.reply(f'没有正在进行的24点游戏')
    else:
        time_used = '%.2f' % (time.time() - cache[cache_id]['time'])
        answer = cache[cache_id]['answer']
        await msg.reply(f'24点游戏已退出, 这不再来一把？\n用时: {time_used}s\n{answer}')
        del cache[cache_id]


@bot.command(regex=r'[\d\+\-\\\*\/]+')
async def twenty_four_step(msg: Message):
    global cache
    content = msg.content.replace('\\*', '*')
    cache_id = f'{msg.ctx.guild.id}-{msg.ctx.channel.id}-{msg.author_id}'
    if cache_id not in cache:
        return
    n_c = copy.deepcopy(cache[cache_id]['cards'])
    used = [int(i) for i in re.findall(r'\d+', content)]
    if 0 in map(lambda x: n_c.remove(x) if x in n_c else 0, used):
        await msg.reply('有错误！')
        return
    cards = n_c + [eval(content)]
    cards_new = []
    for i in cards:
        cards_new.append(int(i))
    cards = cards_new
    cache[cache_id]['cards'] = cards
    if len(cards) == 1 and cards[0] == 24:
        time_used = '%.2f' % (time.time() - cache[cache_id]['time'])
        await msg.reply(f'你赢啦！\n用时: {time_used}s')
        del cache[cache_id]
        await add_list(msg.author_id, time_used)
    elif len(cards) == 1 and cards[0] != 24:
        time_used = '%.2f' % (time.time() - cache[cache_id]['time'])
        answer = cache[cache_id]['answer']
        await msg.reply(f'你输啦！\n用时: {time_used}s\n{answer}')
        del cache[cache_id]
    else:
        await msg.reply(f'(met){msg.author_id}(met) 现在你手上有：{cards}，怎么凑 24 点呢？')


async def add_list(user_id, time_used):
    if not os.path.exists('top.json'):
        with open('top.json', 'w') as f:
            f.write(json.dumps({user_id: time_used}))
    else:
        with open('top.json', 'r') as f:
            data = json.loads(f.read())
        if len(data) == 0:
            data[user_id] = time_used
        elif len(data) < 10 and (user_id not in data):
            data[user_id] = time_used
        elif float(time_used) < float(data[list(data.keys())[len(data)-1]]):
            if user_id not in data or (user_id in data and float(time_used) < float(data[user_id])):
                data[user_id] = time_used
        data = dict(sorted(data.items(), key=lambda x: float(x[1])))
        if len(data) > 10:
            count = 1
            data_new = {}
            for k, v in data.items():
                data_new[k] = v
                count += 1
                if count >= 11:
                    break
            data = data_new
        with open('top.json', 'w') as f:
            f.write(json.dumps(data))


async def get_list():
    if not os.path.exists('top.json'):
        return {}
    else:
        with open('top.json', 'r') as f:
            data = json.loads(f.read())
        return data


@bot.command(regex=r'(?:24排行榜)')
async def twenty_four_list(msg: Message):
    d = await get_list()
    if len(d) != 0:
        text = ''
        count = 1
        for k, v in d.items():
            user = await msg.gate.request('GET', 'user/view', params={'user_id': k})
            name = f"{user['username']}#{user['identify_num']}"
            text += f'第{count}: {name} 用时: {v}s\n'
            count += 1
    else:
        text = '暂无数据'
    c = Card()
    c.theme = Types.Theme.WARNING
    c.append(Module.Header('24点前10排行榜'))
    c.append(Module.Section(Element.Text(content=text, type=Types.Text.KMD)))
    await msg.reply(CardMessage(c))


bot.run()
