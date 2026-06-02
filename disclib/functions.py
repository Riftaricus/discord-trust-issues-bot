import discord

async def ping(message: discord.Message, params):
    await message.channel.send("Pong")
