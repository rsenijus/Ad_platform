import discord
from discord.ext import commands
from kodland_db import db
from os import remove

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='$')

@bot.command('get_id')
async def get_id(ctx):
    pub = db.publicity.get("moderated", 0)
    await ctx.send(f"{pub.id} {pub.name}")

@bot.command('get_pub')
async def get_pub(ctx, id):
    pub = db.publicity.get("id", id)
    await ctx.send(f'''http://localhost:5000/file={id}.{pub.imagetype}type=image
http://localhost:5000/file={id}.{pub.videotype}type=video
Название: {pub.name}
Описание:
{pub.description}''')

@bot.command('moderated_pub')
async def moderated(ctx, id, moder):
    pub = db.publicity.get("id", id)
    if not pub:
        await ctx.send("Её не существует")
    if pub.moderated:
        await ctx.send("Она не на модерации")
    if int(moder):
        db.publicity.update("id", id, "moderated", 1)
    else:
        remove(f"static/images/{id}.{pub.imagetype}")
        remove(f"static/videos/{id}.{pub.videotype}")
        db.publicity.delete("id", id)
    await ctx.send("Операция была произведена успешна")

@bot.command('get_id_proof')
async def get_id_proof(ctx):
    await ctx.send(str(db.proofs.get("moderated", 0).id))
    
@bot.command('get_login_proofs')
async def get_login_proofs(ctx, login):
    proofs = ""
    for i in db.proofs.get_all():
        if i.moderated and i.author == login:
            proofs += f'''{i.proof} Реклама: i.pub_id
'''
    await ctx.send(proofs)
    
@bot.command('get_proof')
async def get_proof(ctx, id):
    proof = db.proofs.get("id", id)
    await ctx.send(f'''Реклама: {proof.id}
Доказательство: {proof.proof}''')

@bot.command('moderated_proof')
async def moderated_proof(ctx, id, moder):
    proof = db.proofs.get("id", id)
    if not proof:
        await ctx.send("Её не существует")
    if proof.moderate:
        await ctx.send("Она не на модерации")
    if moder:
        db.proofs.update("id", id, "moderated", 1)
        db.login.update("login", proof.author, "coins", proof.coins+1)
    else:
        db.proofs.delete("id", id)
    await ctx.send("Операция была произведена успешна")

bot.run("MTE0ODYzNjYxNDYxNzIwMjcxOA.Gp0LQT.f0Ctea0xfaEBKJ0xZARsPzNf0-HPLcE65WlCRk")