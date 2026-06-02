import discord
import disclib.functions
import inspect
from dotenv import load_dotenv
from datetime import timedelta


class DiscordClient(discord.Client):
    def __init__(self, prefix:str = "!", illegal_words: set[str] = [], **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix
        self.illegal_words = illegal_words
        self.commands = [
            {
                "command": "ping",
                "function": disclib.functions.ping
            }
        ]
        
    async def clear_commands(self, message):
        self.commands.clear()
        await message.channel.send("Commands cleared")
        
    async def send(self, message, channel: discord.TextChannel):
        channel.send(message)

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        for word in self.illegal_words:
            if message.content.strip().lower().__contains__(word):
                await message.author.timeout(timedelta(seconds=120), reason="Illegal word detected")
                await message.delete()

        for command in self.commands:
            if message.content.strip().lower().startswith(self.prefix + command["command"]):
                func = command["function"]

                # support sync + async functions
                if inspect.iscoroutinefunction(func):
                    await func(message)
                else:
                    func(message)

    def register_command(self, command: str, func):
        self.commands.append({
            "command": command,
            "function": func
        })


def create_client(prefix: str = "!", illegal_words: set[str] = []):
    intents = discord.Intents.default()
    intents.message_content = True
    return DiscordClient(intents=intents, prefix=prefix, illegal_words=illegal_words)


def run(token: str, prefix: str = "!"):
    client = create_client(prefix=prefix)
    client.run(token)
    return client


if __name__ == "__main__":
    import os
    load_dotenv()
    run(prefix="!", token=os.getenv("DISCORD_TOKEN"))