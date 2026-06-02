import discord

async def ping(message: discord.Message):
    await message.channel.send("Pong")