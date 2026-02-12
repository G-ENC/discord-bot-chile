import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
from datetime import timedelta
import asyncio
import sqlite3
import csv



load_dotenv()
token = os.getenv('DISCORD_TOKEN')

#Database 1
connection_anime = sqlite3.connect("anime.db")

cursor_anime = connection_anime.cursor()
#cursor.execute("DROP TABLE IF EXISTS anime")
cursor_anime.execute("""
CREATE TABLE IF NOT EXISTS anime (
    anime_id INTEGER PRIMARY KEY,
    title TEXT,
    score REAL
)
""")

#file opening for anime database initialization
with open("animeDB/anime.csv",encoding="utf-8") as file:
   reader = csv.DictReader(file)

   for row in reader:
  
    #  print(row["title"] + " - " + row["score"])
      cursor_anime.execute(
         "INSERT OR IGNORE INTO anime (anime_id, title, score) VALUES (?,?,?)",
         (
            int(row["anime_id"]),
            row["title"],
            float(row["score"]) if row["score"] else None
         ))
      
cursor_anime.execute("SELECT COUNT(*) FROM anime")
print(cursor_anime.fetchone())

connection_anime.commit()

#Database 2
connection_milyoner = sqlite3.connect("kim_mil.db")

cursor_milyoner = connection_milyoner.cursor()
cursor_milyoner.execute("DROP TABLE IF EXISTS milyoner")
cursor_milyoner.execute("""
CREATE TABLE IF NOT EXISTS milyoner(
      question TEXT,
      options TEXT,
      answer TEXT,
      category TEXT
)
""")

#file opening for milyoner database initialization
with open("kim_milyoner_olmak_ister.csv",encoding="utf-8") as file:
   reader = csv.DictReader(file)

   for row in reader:
      cursor_milyoner.execute(
        "INSERT OR IGNORE INTO milyoner (question, options, answer, category) VALUES (?,?,?,?)",
        (
          row["question"],
          row["options"],
          row["correct_answer"],
          row["category"]
        )
      )
      
# cursor_milyoner.execute("SELECT question, options, answer FROM milyoner LIMIT 10")
# print(cursor_milyoner.fetchall())

connection_milyoner.commit()

#Bot innit
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
  print(f"Mind Controll, {bot.user.name}")


#eats the pickle when seen and repeats every message ever written (have to change this)
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if((message.content)):
    await message.channel.send(f'Bro said "{message.content}☝️🤓"')


  if 'pickle' in message.content.lower():
    await message.delete()
    await message.channel.send(f'{message.author.mention} - give me pickle')

  await bot.process_commands(message)

#adds two numbers by trying 
@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    a = left + right
    valid = (a>0 or a<100)
    count = 0
    rand = random.randrange(0,100)
    await ctx.channel.send('Give me a sec')
    while(rand != a and valid):
      rand = random.randrange(0,100)
      await ctx.send(rand)
      count+=1
      if(a-20<rand<a+20):
         await ctx.channel.send('Getting closer')
         while(rand!=a):
          rand = random.randrange(a-20,a+20)
          await ctx.send(rand)
          count +=1
          if(a-10<rand<a+10):
             await ctx.channel.send('Right there...')
             while(rand!=a):
                rand = random.randrange(a-10,a+10)
                await ctx.send(rand)
                count += 1
    if(count == 0):
      await ctx.senc(f'Computed number is too large but my guess is: {random.randrange(a-5,a+5)}' )
    else:
      await ctx.send(f'Total tries: {count}')


  #chooses froem an arbitairay amount of choices 
@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

#repaet a massage x amount of times
@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)

#assignes a role by invoking subcommand
@bot.group()
async def give(ctx):
   if ctx.invoked_subcommand is None:
    await ctx.send('Give a role to be assigned and to who')

@give.command(name='cool1')
async def _cool(ctx, member:discord.Member):
   role = discord.utils.get(ctx.guild.roles, name="cool")
   await ctx.send(f'giving cool role to {member}')
   await member.add_roles(role)

#muting
@bot.command()
async def mute(ctx,member:discord.Member):

  msg = await ctx.send(f"Should {member} be muted?")
  await msg.add_reaction("👍")
  await msg.add_reaction("👎")
  await asyncio.sleep(2)

  msg = await ctx.channel.fetch_message(msg.id)  # refresh
  up = discord.utils.get(msg.reactions,emoji="👍")
  down = discord.utils.get(msg.reactions,emoji="👎")


  if(up.count-1>down.count):
    await ctx.send("MUTED!")
    await member.edit(mute=True)
  else:
    await ctx.send("Next time")
    await member.edit(mute=False)



@bot.command()
async def randomAnime(ctx):
   
   cursor_anime.execute("SELECT title FROM anime ORDER BY RANDOM() LIMIT 1")
   await ctx.send(cursor_anime.fetchone()[0])


@bot.command()
async def milyoner(ctx):

  cursor_milyoner.execute("""
  SELECT question, options, answer 
  FROM milyoner 
  WHERE category!= 'Müzik' 
  ORDER BY RANDOM() 
  LIMIT 1 """)
  
  question, options, answer = cursor_milyoner.fetchone()
  options = options.split(",")

  options = [o.strip("[]' ") for o in options]
  
  # print(question,options)
  msg = await ctx.send(f"Q: {question}\n{options[0]}\n{options[1]}\n{options[2]}\n{options[3]}")
  await msg.add_reaction("🅰️")
  await msg.add_reaction("🅱️")
  await msg.add_reaction("🥐")
  await msg.add_reaction("\U0001F1E9")

  await ctx.bot.wait_for(
      "reaction_add",
      check=lambda r, u: r.message.id == msg.id and not u.bot
  )

  await asyncio.sleep(5)

  msg = await ctx.channel.fetch_message(msg.id)
  A = discord.utils.get(msg.reactions,emoji="🅰️")
  B = discord.utils.get(msg.reactions,emoji="🅱️")
  C = discord.utils.get(msg.reactions,emoji="🥐")
  D = discord.utils.get(msg.reactions,emoji="\U0001F1E9")
  
  max_vote = max(A.count,B.count,C.count,D.count)

  counts = {
     "A":A.count,
     "B":B.count,
     "C":C.count,
     "D":D.count,
  }

  
  
  winner = [k for k,v in counts.items() if v == max_vote]

  msg = await ctx.channel.fetch_message(msg.id)
  # print("Winner arr:"+winner)
  if(answer in winner):
    for w in winner:
      if(answer == w):
        await ctx.send(f"Correct answer is {w}")
      else:
        await ctx.send(f"Who said {w} are you dumb?")
  else:
     await ctx.send(f"Correct answer was {answer}")


@bot.command()
async def h(ctx):
   await ctx.send("\n!add\n!mute\n!choose\n!repeat\n!milyoner")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
connection_milyoner.close()
connection_anime.close()



#to do 
#help funciton
#fun facts about japanise veding machines
#make a japordy game

