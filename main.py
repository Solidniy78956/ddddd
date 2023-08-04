import discord
from discord.ext import commands
import asyncio
import requests
from discord import utils
from PIL import Image,ImageFont,ImageDraw
import io
from datetime import datetime, timedelta
import os,sqlite3
import json
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account


bot = commands.Bot(intents=discord.Intents.all() , command_prefix= "!" , description='The Best Bot For the Best User!')

credentials= service_account.Credentials.from_service_account_file('D:/telegram/dark-crypto777-8f55cd65f8a4.json')
service = build('sheets', 'v4', credentials=credentials)


spreadsheet_id = '1Yfkm_FkoHEgiZ5zPOm6_lG_MK51RDpndttV5O0n81C4'


range_name = 'Sheet1!A1:A6000'


roles_data = {}
if os.path.isfile("roles_data.json"):
    with open("roles_data.json", "r") as file:
        roles_data = json.load(file)

ROLE_NAME = "👩‍💻DARK_TEAM"
global base,cur
base = sqlite3.connect('base.db')
cur = base.cursor()

API_KEY = 'cfde056f-32c3-43c2-81ce-371a39cf9286'
BTC_ID = '1'
CURRENCY_LIST = 'BTC,ETH'
MESSAGE_CHANNEL_ID = '972527282667274261'





@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready.")

    cur.execute(""" CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        id INT,
        score BIGINT
    )""")

    for guild in bot.guilds:
        for member in guild.members:
            if cur.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cur.execute(f"INSERT INTO users VALUES ('{member}',{member.id},0)")
                base.commit()
            else:
                pass
        base.commit()
    bot.loop.create_task(send_currency_updates())

#-----------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_member_join(member):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    member_ids = [row[0] for row in values]
    if str(member.id) not in member_ids:
        await  member.send(f"Вас не має в базі даних.\n\nЯкщо ви оплатили доступ зверніться до менеджера і він вам допоможе вирішити проблему.")
        await member.kick(reason='ID not found in spreadsheet')
    else:
        channel = bot.get_channel(1064894931023450162)
        guild = bot.get_guild(966985516111241237)
        role = guild.get_role(1064816761414893619)
        role1 = guild.get_role(1064816761414893619)
        await channel.send(f"-----------------------------------------")
        await channel.send(f"{member} приєднався на наш сервер.")
        await channel.send(f"-----------------------------------------")
        if str(member.id) in roles_data:
            role_id = roles_data[str(member.id)]
            role = discord.utils.get(member.guild.roles, id=int(role_id))
            await member.add_roles(role)
            await  member.send(f"Дякуємо,що ви залишилися з нами")
            await channel.send(f"-----------------------------------------")
            await channel.send(f"{member}продовжив підписку")
            await channel.send(f"-----------------------------------------")
            await asyncio.sleep(2678400)
            if ROLE_NAME not in [role.name for role in member.roles]:
                await  member.send(f"У вас закінчилась підписка\n\nЗверніться до свого менеджера,щоб поновити її протягом 4-ох днів.")
                await channel.send(f"-----------------------------------------")
                await channel.send(f"У{member} закінчилась підписка!")
                await channel.send(f"-----------------------------------------")
                await member.kick(reason="Не олатив доступ")
            else:
                pass

        elif cur.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
            cur.execute(f"INSERT INTO users VALUES ('{member}',{member.id},0)")
            base.commit()
            await member.send(f"**----------------------WELCOME----------------------**")
            await member.send(f"**👋Вітаємо в нашому ком’юніті.**\n\nТепер ти став частиною нашої сім’ї.\n\nУважно прочитай всі правила та приступай до навчання")
            await member.add_roles(role1)
            await asyncio.sleep(2678400)
            if ROLE_NAME not in [role.name for role in member.roles]:
                await  member.send(f"У вас закінчилась підписка\n\nЗверніться до свого менеджера,щоб продовжити її протягом 4-ох днів.")
                await channel.send(f"-----------------------------------------")
                await channel.send(f"У{member} закінчилась підписка!")
                await channel.send(f"-----------------------------------------")
                await member.kick(reason="Не олатив доступ")
            else:
                pass

        else:
            pass




@bot.event
async def on_member_remove(member):
    # Check if the member has a role assigned
    if len(member.roles) > 1:
        # Save the member's role id to the roles_data dictionary
        roles_data[str(member.id)] = str(member.roles[-1].id)
        # Write the updated roles_data to file
        with open("roles_data.json", "w") as file:
            json.dump(roles_data, file)

@bot.event
async def on_command_error(ctx, error):
    # Handle errors in a custom way, if needed
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Invalid command.")

@bot.command()
async def myscore(ctx,member:discord.Member = None):
    await ctx.message.delete()
    if ctx.channel.id == 1067363726254153738:
        if member is None:
            await  ctx.author.send(f"""**{ctx.author}** ваша кількість очок:**{cur.execute("SELECT score FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}**""" )
    else:
        await  ctx.author.send("Для цієї команди є виділений канал\n\n**!!!Не зловживайте командами бота!!!**")

@bot.command()
@commands.has_role(972521590669602866)
async def score(ctx,member:discord.Member = None):
    await ctx.message.delete()
    if ctx.channel.id == 1067363726254153738:

        if member is None:
            await  ctx.author.send(f"Такого користувача не знайдено")
        else:
            await  ctx.author.send(
                f"""**{member}** отримав:**{cur.execute("SELECT score FROM users WHERE id = {}".format(member.id)).fetchone()[0]}**""")
    else:
        await  ctx.author.send("Для цієї команди є виділений канал\n\n**!!!Не зловживайте командами бота!!!**")


@bot.command()
@commands.has_role(972521590669602866)
async def award(ctx,member:discord.Member = None, amount: int = None):
    await ctx.message.delete()
    guild = bot.get_guild(966985516111241237)
    channel = bot.get_channel(1064894931023450162)
    role9 = guild.get_role(1024270559137243226)

    if ctx.channel.id == 1067363726254153738:
        if member is None:
            await  ctx.author.send(f"Введіть користувача,якому бажаєте видати нагороду")
        else:
            if score is None:
                await  ctx.author.send(f"Введіть кількість очок,яку хочете видати")
            elif amount<1:
                await  ctx.author.send(f"Ви не можете видати суму менше 0")
            else:
                cur.execute("UPDATE users SET score = score + {} WHERE id = {}".format(amount,member.id))
                base.commit()
                warnFile = open("www.txt", "a")
                warnFile.write(str(member.mention) + "\n")
                warnFile.close()
                warnFile = open("www.txt", "r")
                warnedusers = []
                for line in warnFile:
                    warnedusers.append(line.strip())
                warnFile.close()

                for user in warnedusers:
                    if str(member.mention) == user:
                        amount += amount

                if  amount>= 25:
                    await member.add_roles(role9)
                    await member.send(f"Вітаємо тепер ви стали трейдером нашого проекту!")
                    await channel.send(f"{member} тепер став трейдером нашого проекту")

                await member.send(f"{ctx.author}дав вам нагороду за вашу допомогу!")
    else:
        await  ctx.author.send("Для цієї команди є виділений канал\n\n**!!!Не зловживайте командами бота!!!**")


@bot.command()
@commands.has_role(972521590669602866)
async def deletescore(ctx,member:discord.Member = None, amount: int = None):
    await ctx.message.delete()
    guild = bot.get_guild(966985516111241237)
    channel = bot.get_channel(1064894931023450162)
    role9 = guild.get_role(1024270559137243226)


    if ctx.channel.id == 1067363726254153738:
        if member is None:
            await  ctx.author.send(f"Введіть користувача,якому бажаєте зняти очки")
        else:
            if score is None:
                await  ctx.author.send(f"Введіть кількість очок,яку хочете зняти")
            elif amount<1:
                await  ctx.author.send(f"Ви не можете зняти суму менше 0")
            else:
                cur.execute("UPDATE users SET score = score - {} WHERE id = {}".format(amount,member.id))
                base.commit()
                await member.send(f"{ctx.author}зняв у вас {amount} очок!")
                if amount<25:
                    if role9 in member.roles:
                        await member.remove_roles(role9)
                        await member.send(f"Ви більше не є трейдером нашого проекту.")
                        await channel.send(f"{member} більше не є трейдером нашого каналу")


                warnFile = open("www.txt", "a")
                warnFile.write(str(member.mention) + "\n")
                warnFile.close()
                warnFile = open("www.txt", "r")
                warnedusers = []
                for line in warnFile:
                    warnedusers.append(line.strip())
                warnFile.close()

                for user in warnedusers:
                    if str(member.mention) == user:
                        amount -= amount

    else:
        await  ctx.author.send("Для цієї команди є виділений канал\n\n**!!!Не зловживайте командами бота!!!**")






#------------------------------------------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------------------------------

@bot.command(aliases=('Я','z','Z'))
async def я(ctx):
    await ctx.message.delete()
    await  ctx.author.send(f"**----------DARK CRYPTO CARD----------**")
    created_at = ctx.author.joined_at.strftime("%d.%m.%Y")
    dt = datetime.strptime(created_at, '%d.%m.%Y')
    result = dt + timedelta(days=31)
    result = datetime.strftime(result, '%d.%m.%Y')
    await  ctx.author.send(f"**Нік:**{ctx.author}")
    await  ctx.author.send(f"**ID:**{ctx.author.id}")
    await  ctx.author.send(f"**Приєднався:**{created_at}")
    await  ctx.author.send(f"**Картка перестане бути дійсною:**{result}")







#---------------------------------------------------------------------------------------------------------------------------------------------------------------predicate)

#-----------------------------------------------------------------------------------------------------------------------------------------------------


@bot.command( pass_context = True)
@commands.has_role(1064816761414893619)
async def start1(ctx):
    await ctx.message.delete()
    await  ctx.author.send(f"**--------------------Тест №1--------------------**")
    msg = await  ctx.author.send("**На якій технології побудована крипта?**\n\n**A** - на технології блокчейну\n\n**B** - на технології web 3.0\n\n**O** - на всесвітньо банківській")
    await msg.add_reaction(u"\U0001F170")
    await msg.add_reaction(u"\U0001F171")
    await msg.add_reaction(u"\U0001F17E")
    mark = 0
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171",u"\U0001F17E"], timeout=300.0)


    except asyncio.TimeoutError:
        await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

    else:
        if reaction.emoji == u"\U0001F170":
            mark += 1

        if reaction.emoji == u"\U0001F171":
            mark += 0
        if reaction.emoji == u"\U0001F17E":
            mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Альткоїни - це...?**\n\n**A** - Біткоін\n\n**B** - Всі інші криптомонети крім біткоіну\n\n**O** - NFT")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send( "**Чи потрібно давати комусь ваші перcональні дані від аккаунту на біржі?**\n\n**A** - Так,якщо пропонують скористатися даними,щоб заробити\n\n**B** - Ні в жодному разі\n\n**O** - Тільки,якщо викликає довіру")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Як зробити аккаунт на біржі більш безпечним?**\n\n**A** - Зробити трьох етапну автентифікацію\n\n**B** - Звичайного паролю достатньо")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark +=  1

            if reaction.emoji == u"\U0001F171":
                mark += 0

        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Головна особливість стейблкоїнів**\n\n**A** - Дає можливість заробити без вкладень\n\n**B** - Різко зімнює свій курс\n\n**O** - Стабільний та стійкий у ціні")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark +=  1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Як зрозуміти,що біржа є безпечною?**\n\n**A** - Важливо чи гарно виглядає сайт\n\n**B** -  Подивитись топ бірж за рейтингом,перевірити капіталізацію та об’єми торгів\n\n**O** - Всі біржі є безпечними")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Які гаманці є безпечнішими?**\n\n**A** - Холодні гаманці\n\n**B** -  Гарячі гаманці\n\n**O** - Всі гаманці є безпечними")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark +=  1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        await ctx.author.send(f"Ви отримали:{mark}/7\n\n")

        if mark >= 5:
            await ctx.author.send(f"**Вітаю ви успішно пройшли тест!!!!**\n\nПротягом 30 секунд,вам буде відкрито інший навчальний матеріал")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")
            await asyncio.sleep(30)
            author = ctx.message.author
            guild = bot.get_guild(966985516111241237)
            role = guild.get_role(1064820989118124112)

            await author.add_roles(role)

            guild = bot.get_guild(966985516111241237)
            role1 = guild.get_role(1064816761414893619)
            await author.remove_roles(role1)

            channel = bot.get_channel(1064894931023450162)
            await channel.send(f"{ctx.author} Пройшов тест до **модуля-1**\n\nЙого оцінка:{mark}/7\n\nТепер його роль:{role}")

        if mark < 5 :
            await ctx.author.send(f"Ви набрали менше 5 балів\n\nПочніть тест спочатку")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")





@start1.error
async def start1_error(ctx,error):
    await ctx.message.delete()
    if isinstance(error, commands.MissingRole):
        await ctx.author.send(f"У вас не дотстатньо прав для даного тесту")




#-------------------------------------ТЕСТ№2-------------------------------------------------------------------------------------

@bot.command(pass_context = True)
@commands.has_role(1064820989118124112)
async def start2(ctx):
    await ctx.message.delete()
    await  ctx.author.send(f"**--------------------Тест №2--------------------**")
    msg = await  ctx.author.send("**Чи ігри з NFT дають можливість заробити?**\n\n**A** - ні це не можливо\n\n**B** - так,заробити можна\n\n**O** - NFT не має відношення до ігор")
    await msg.add_reaction(u"\U0001F170")
    await msg.add_reaction(u"\U0001F171")
    await msg.add_reaction(u"\U0001F17E")
    mark = 0
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171",u"\U0001F17E"], timeout=300.0)


    except asyncio.TimeoutError:
        await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

    else:
        if reaction.emoji == u"\U0001F170":
            mark += 0

        if reaction.emoji == u"\U0001F171":
            mark += 1
        if reaction.emoji == u"\U0001F17E":
            mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**NFT може бути тільки картинкою?**\n\n**A** - це може бути,як аудіо чи відео файл,так і картинка\n\n**B** - це закодована картинка\n\n**O** - це картинка з кодом всередині")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send( "**Скільки процесів халвінгу біткоіну відбулося за весь час,та як це вплинуло на ринок?**\n\n**A** - 2 процеси халвінгу та винаогорода за видобуток збільшилась вдвоє\n\n**B** - 1 процес халвінгу,та змін не виникло\n\n**O** - 3 процеси,та винагорода за видобуток щоразу зменшується")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**У чому зручність смарт контракту?**\n\n**A** - його зручність у анонімності\n\n**B** - це договір з підвищеною безпекою для обміну будь-якими активами\n\n**O** - це контракт для обміну інформацією у необмеженому обсязі")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Назвіть недолік DEX**\n\n**A** - обмежений функціонал\n\n**B** - ніхто не заблокує ваш актив\n\n**O** - є підтримка фіату")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Назвіть перевагу DEX**\n\n**A** -  відсутні приватні ключі\n\n**B** -  доступна верифікація\n\n**O** - анонімність при обміні")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Що з запропонованих варіантів є стейблкоіном?**\n\n**A** - BTC\n\n**B** -  ETH\n\n**O** - BUSD")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Яка різниця між централізованими та децентралізованими стейблкоінами?**\n\n**A** - централізовані мають прив’язку до криптовалют,а децентралізовані до паперових грошей\n\n**B** -  централізовані мають прив’язку до паперових грошей,а децентралізовані до криптовалют\n\n**O** - вони не відрізняються")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark +=1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Що означає мінт NFT?**\n\n**A** - це продаж NFT\n\n**B** -  купівля NFT на стадії створення\n\n**O** - це розпродаж NFT колекції")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Які функції виконують ноди?**\n\n**A** - відповідають за підтвердження транзакцій\n\n**B** -  відповідють за створення нових монет\n\n**O** - відповідють за курс криптовалют")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Що відбувається з курсом після спалювання монет?**\n\n**A** - ціна на монету падає\n\n**B** -  ціна на монету не змінюється\n\n**O** - ціна на монету росте,але не завжди")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        await ctx.author.send(f"Ви отримали:{mark}/11\n\n")

        if mark >= 5:
            await ctx.author.send(f"**Вітаю ви успішно пройшли тест!!!!**\n\nПротягом 30 секунд,вам буде відкрито інший навчальний матеріал")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")
            await asyncio.sleep(30)
            author = ctx.message.author
            guild = bot.get_guild(966985516111241237)
            role = guild.get_role(1064821772970643498)

            await author.add_roles(role)

            guild = bot.get_guild(966985516111241237)
            role1 = guild.get_role(1064820989118124112)
            await author.remove_roles(role1)

            channel = bot.get_channel(1064894931023450162)
            await channel.send(f"{ctx.author} Пройшов тест до **модуля-2**\n\nЙого оцінка:{mark}/11\n\nТепер його роль:{role}")

        if mark < 5 :
            await ctx.author.send(f"Ви набрали менше 5 балів\n\nПочніть тест спочатку")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")





@start2.error
async def start2_error(ctx,error):
    await ctx.message.delete()
    if isinstance(error, commands.MissingRole):
        await ctx.author.send(f"У вас не дотстатньо прав для даного тесту")


#-----------------------------------------------------------------------ТЕСТ№3------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.has_role(1064821772970643498)
async def start3(ctx):
    await ctx.message.delete()
    await  ctx.author.send(f"**--------------------Тест №3--------------------**")
    msg = await  ctx.author.send("**Airdrop - це...?**\n\n**A** - Спалювання монет\n\n**B** - безкоштовна роздача крипти\n\n**O** - NFT майнінг крипти")
    await msg.add_reaction(u"\U0001F170")
    await msg.add_reaction(u"\U0001F171")
    await msg.add_reaction(u"\U0001F17E")
    mark = 0
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171",u"\U0001F17E"], timeout=300.0)


    except asyncio.TimeoutError:
        await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

    else:
        if reaction.emoji == u"\U0001F170":
            mark += 0

        if reaction.emoji == u"\U0001F171":
            mark += 1
        if reaction.emoji == u"\U0001F17E":
            mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Монети під час стейкінгу вважаються заблокованими чи їх можна вільно використовувати у будь-який час?**\n\n**A** - ними можна користуватися і знімати з гаманця\n\n**B** - монети під час стейкінгу не належать вам\n\n**O** - монети блокують на певний термін")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0
            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark +=1
        await ctx.author.send(f"-----------------------------------------")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send( "**Чи можливо заробляти без вкладень за допомогою p2e?**\n\n**A** - Так,можливо є достатня колькість таких проектів\n\n**B** - P2E взагалі не дає можливості заробити\n\n**O** - Ні,без вкладень це не можливо")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Для чого використовують лаунчпад?**\n\n**A** - для отримання,або надання інвестицій для нових проектів\n\n**B** - це потрібно для керування своїми активами\n\n**O** - лаунчпад може впливати на курс біткоіну")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріал краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Диверсифікація активів це?**\n\n**A** - зберігання ваших коштів у одному надійному гаманці\n\n**B** - розподіл активів по різним монетам з метою зменшення ризику\n\n**O** - внесення ваших активів в одну монету з метою збільшення прибутку")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")

        await ctx.author.send(f"Ви отримали:{mark}/5\n\n")

        if mark >=3:
            await ctx.author.send(f"**Вітаю ви успішно пройшли тест!!!!**\n\nПротягом 30 секунд,вам буде відкрито інший навчальний матеріал")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")
            await asyncio.sleep(30)
            author = ctx.message.author
            guild = bot.get_guild(966985516111241237)
            role = guild.get_role(1064822270234726400)

            await author.add_roles(role)

            guild = bot.get_guild(966985516111241237)
            role1 = guild.get_role(1064821772970643498)
            await author.remove_roles(role1)

            channel = bot.get_channel(1064894931023450162)
            await channel.send(f"{ctx.author} Пройшов тест до **модуля-3**\n\nЙого оцінка:{mark}/5\n\nТепер його роль:{role}")

        if mark < 3 :
            await ctx.author.send(f"Ви набрали менше 3 балів\n\nПочніть тест спочатку")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")





@start3.error
async def start3_error(ctx,error):
    await ctx.message.delete()
    if isinstance(error, commands.MissingRole):
        await ctx.author.send(f"У вас не дотстатньо прав для даного тесту")

#-----------------------------------------------------------------------------------------------------------------------------------------------




#-------------------------------------ТЕСТ№4-------------------------------------------------------------------------------------

@bot.command(pass_context = True)
@commands.has_role(1064822270234726400)
async def start4(ctx):
    await ctx.message.delete()
    await  ctx.author.send(f"**--------------------Тест №4--------------------**")
    msg = await  ctx.author.send("**Яка різниця між кросс та ізольованою маржою?**\n\n**A** - Крос маржа безпечніша\n\n**B** - В разі невдачі кросс маржа може забрати усі кошти\n\n**O** - В разі невдачі ізольована маржа може забрати усі кошти")
    await msg.add_reaction(u"\U0001F170")
    await msg.add_reaction(u"\U0001F171")
    await msg.add_reaction(u"\U0001F17E")
    mark = 0
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171",u"\U0001F17E"], timeout=300.0)


    except asyncio.TimeoutError:
        await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

    else:
        if reaction.emoji == u"\U0001F170":
            mark += 0

        if reaction.emoji == u"\U0001F171":
            mark += 1
        if reaction.emoji == u"\U0001F17E":
            mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Яка різниця між спотом та ф’ючерсами?**\n\n**A** - спот торгує монетами,а фючерс угодами на ріст чи падіння\n\n**B** - на споті є кредитне плече \n\n**O** - Фючерс дає змогу купити угоду на володіння монетою,а спот-ні")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send( "**Скільки денних свічок в одній тижневій свічці?**\n\n**A** - 3\n\n**B** - 10\n\n**O** - 7")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Що буває,якщо не використовувати стоп-лос?**\n\n**A** - ліквідація\n\n**B** - необмежений прибуток\n\n**O** - шанс відігратися")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Для чого використовують тейк профіт?**\n\n**A** - фіксація прибутку\n\n**B** - Зупинка збитків\n\n**O** - примноження заробітку")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Ціна маркування - це...?**\n\n**A** -  ціна,що розраховується калькуляцією декількох спотових бірж\n\n**B** - ціна закриття угоди\n\n**O** - Ціна тейк-профіту")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("Остання ціна це -...?\n\nA - ціна за якою була укладена угода в історії біржі\n\nB - ціна стоп-лосу\n\nO - ціна тейк-профіту")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Яка маржа є більш безпечною для депозиту?**\n\n**A** - Кросс маржа\n\n**B** - ізольована маржа\n\n**O** - обидві")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріал краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Яка задача лімітного ордеру?**\n\n**A** - створення угоди за ринковою ціною\n\n**B** - створення угоди в заданій точці\n\n**O** - створення угоди тільки для біткоіну")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріал краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**По якій ціні відкривається рикновий ордер?**\n\n**A** - по бажаній\n\n**B** - по актуальній\n\n**O** - як повезе")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріал краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Хто формує рух ціни у свої цілях?**\n\n**A** - ритейл трейдер\n\n**B** - маркет мейкер\n\n**O** - біржа")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Що таке ліквідність?**\n\n**A** - це кошти маркет мейкерів\n\n**B** - це стоп-лоси та ліквідації трейдерів\n\n**O** - це закриття позицій у профіт")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріал краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        await ctx.author.send(f"Ви отримали:{mark}/12\n\n")

        if mark >= 6:
            await ctx.author.send(f"**Вітаю ви успішно пройшли тест!!!!**\n\nПротягом 30 секунд,вам буде відкрито інший навчальний матеріал")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")
            await asyncio.sleep(30)
            author = ctx.message.author
            guild = bot.get_guild(966985516111241237)
            role = guild.get_role(1064822692789887027)

            await author.add_roles(role)

            guild = bot.get_guild(966985516111241237)
            role1 = guild.get_role(1064822270234726400)
            await author.remove_roles(role1)

            channel = bot.get_channel(1064894931023450162)
            await channel.send(f"{ctx.author} Пройшов тест до **модуля-4**\n\nЙого оцінка:{mark}/12\n\nТепер його роль:{role}")

        if mark < 6 :
            await ctx.author.send(f"Ви набрали менше 6 балів\n\nПочніть тест спочатку")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")





@start4.error
async def start4_error(ctx,error):
    await ctx.message.delete()
    if isinstance(error, commands.MissingRole):
        await ctx.author.send(f"У вас не дотстатньо прав для даного тесту")

#-------------------------------------------------ТЕСТ№5--------------------------------------------------------
@bot.command(pass_context = True)
@commands.has_role(1064822692789887027)
async def start5(ctx):
    await ctx.message.delete()
    await  ctx.author.send(f"**--------------------Тест №5--------------------**")
    msg = await  ctx.author.send("**Смарт мані – це…?**\n\n**A** - вид аналізу,який побудований на математичних фігурах\n\n**B** - вид аналізу,який дозволяє бачити сліди маркет мейкера\n\n**O** - вид аналізу,який довзоляє бачити об’єми")
    await msg.add_reaction(u"\U0001F170")
    await msg.add_reaction(u"\U0001F171")
    await msg.add_reaction(u"\U0001F17E")
    mark = 0
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171",u"\U0001F17E"], timeout=300.0)


    except asyncio.TimeoutError:
        await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

    else:
        if reaction.emoji == u"\U0001F170":
            mark += 0

        if reaction.emoji == u"\U0001F171":
            mark += 1
        if reaction.emoji == u"\U0001F17E":
            mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Ціна рухається за?**\n\n**A** - ліквідністю\n\n**B** - ордерблоками\n\n**O** - як вкаже система")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send( "**Імбаланс – це…?**\n\n**A** - остання свічка перед ростом,або падінням\n\n**B** - невеличка продажа,або покупка,яка свіпнула ліквідністьn\n\n**O** - патерн трьох рухів,який виступає сильним магнітом для ціни")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріал краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Ордерблок – це…?**\n\n**A** - остання зелена свічка перед імпульсним падінням,або остання червона свічка перед імпульсним ростом\n\n**B** - фейковий свіп ліквідності\n\n**O** - злам стуктури")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**POI – це…?**\n\n**A** - імпульсний пробій ордерблоку\n\n**B** - загальне поняття,яке включає в себе всі сильні зони підтримки і супротиву\n\n**O** - вид боковика")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Брейкер – це…?**\n\n**A** -  сильний оредрблок\n\n**B** - час коли маркет мейкер відпочиває\n\n**O** - імпульсно прошитий ордерблок")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Контекст сильної POI:**\n\n**A** - включає в себе зону підтримки,або супротиву,від якої дуже багато разів відпивалась ціна\n\n**B** - коли зону підримки,або супротиву пробили і ми знову до неї повертаємось\n\n**O** - зона пітдтримки,або супротиву,яка працювала з ліквідністю,не залишивши її перед собою і заламала структуру")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 1
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Для оновлення/зламу структури (choch/bos) потрібно :**\n\n**A** - закриття свічки тінню над / під минулою структурною точкою\n\n**B** - закриття свічки тілом над / під минулою структурною точкою\n\n**O** - закриття свічки тінню над / під любою минулою точкою")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark +=1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Як правильно відмічати імбаланс:**\n\n**A** - по тіням крайньої свічки справа та зліва від потенційного імбалансу\n\n**B** - по тілам крайньої свічки справа та зліва від потенційного імбалансу\n\n**O** -  по останньому ордерблоку зверху та знизу")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 1

            if reaction.emoji == u"\U0001F171":
                mark += 0
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("У якій зоні найбільш вигідно купувати будь-який актив :  \n\n**A** - зона преміуму\n\n**B** - зона діскаунту\n\n**O** - зона ордерблоку")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Чи є торгівля без стоп-лосу доцільною:**\n\n**A** - Так! А навіщо взагалі контролювати ризики ?\n\n**B** - Ні! Ніколи !\n\n**O** - Що таке стоп-лос?")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        msg = await  ctx.author.send("**Що таке ліквідність?**\n\n**A** - це кошти маркет мейкерів\n\n**B** - це стоп-лоси та ліквідації трейдерів\n\n**O** - це закриття позицій у профіт")
        await msg.add_reaction(u"\U0001F170")
        await msg.add_reaction(u"\U0001F171")
        await msg.add_reaction(u"\U0001F17E")

        try:
            reaction, user = await bot.wait_for("reaction_add",check=lambda reaction, user: user == ctx.author and reaction.emoji in [u"\U0001F170", u"\U0001F171", u"\U0001F17E"], timeout=300.0)


        except asyncio.TimeoutError:
            await ctx.author.send("Ви надто довго відповідаєте на запитання.\n\nПідівчіть матеріаль краще,та почніть тест з початку.")

        else:
            if reaction.emoji == u"\U0001F170":
                mark += 0

            if reaction.emoji == u"\U0001F171":
                mark += 1
            if reaction.emoji == u"\U0001F17E":
                mark += 0
        await ctx.author.send(f"-----------------------------------------")
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
        await ctx.author.send(f"Ви отримали:{mark}/12\n\n")

        if mark >= 6:
            await ctx.author.send(f"**✌️Вітаємо з проходженням базового рівня у нашій спільноті!**\n\nЩиро дякуємо за ваш час та наполегливість. Знаємо, що це було того варте,адже проходячи цей початковий рівень ви отримали:\n\n- базові знання в сфері криптовалюти.\n\n- безкоштовні методи заробітку та методи із залученням коштів.\n\n- базові знання з трейдингу у стилі smart-money.\n\n - базові знання про торгівлю криптоактивами.\n\nЦей рівень був фундаментом у світі криптовалют і підготовкою до реального заробітку та отримання інструментів, знань та вмінь, які дозволять вам вийти на новий рівень у якому ви зможете відчути свободу та жити бажаним життям!")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")
            await asyncio.sleep(30)
            author = ctx.message.author
            guild = bot.get_guild(966985516111241237)
            role = guild.get_role(972523035670224896)

            await author.add_roles(role)

            guild = bot.get_guild(966985516111241237)
            role1 = guild.get_role(1064822692789887027)
            await author.remove_roles(role1)

            channel = bot.get_channel(1064894931023450162)
            await channel.send(f"{ctx.author} Пройшов тест до **модуля-5**\n\nЙого оцінка:{mark}/12\n\nТепер його роль:{role}")

        if mark < 6 :
            await ctx.author.send(f"Ви набрали менше 6 балів\n\nПочніть тест спочатку")
            await ctx.author.send(f"----------------------------------------------------------------------------------------------------------")





@start5.error
async def start5_error(ctx,error):
    await ctx.message.delete()
    if isinstance(error, commands.MissingRole):
        await ctx.author.send(f"У вас не дотстатньо прав для даного тесту")

#---------------------------------------------------------------------------------------------------------------

async def send_currency_updates():
    channel = bot.get_channel(1076901481095123018)  # заменить на ID канала, куда бот будет отправлять сообщение
    await channel.send(f"**Бот змінює ціну кожних 30 секунд **")
    while True:
        response = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC,ETH",
                                headers={"X-CMC_PRO_API_KEY": "cfde056f-32c3-43c2-81ce-371a39cf9286"})
        data = response.json()
        btc_price = data['data']['BTC']['quote']['USD']['price']
        eth_price = data['data']['ETH']['quote']['USD']['price']
        message = await channel.send(f"**BTC price**: ${btc_price}\n**ETH price**: ${eth_price}")
        await asyncio.sleep(30)
        new_response = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC,ETH",
                                    headers={"X-CMC_PRO_API_KEY": "cfde056f-32c3-43c2-81ce-371a39cf9286"})
        new_data = new_response.json()
        new_btc_price = new_data['data']['BTC']['quote']['USD']['price']
        new_eth_price = new_data['data']['ETH']['quote']['USD']['price']
        await message.edit(content=f"BTC price: ${new_btc_price}\nETH price: ${new_eth_price}")
        await message.delete()


#----------------------------------------------------------------------------------------------------------------------




bot.run('MTA2NDUyMDM1ODEwMDc0NjMwMQ.GWGq-p.UQG1XuARAOTtWMRdKVg1xYHpStKlhoS8hWpkGI')