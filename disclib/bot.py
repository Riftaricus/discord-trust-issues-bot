import discord
import inspect
import json
import os
from dotenv import load_dotenv
from datetime import timedelta
from disclib import functions

DATA_FILE = "bot_data.json"


class DiscordClient(discord.Client):
    def __init__(self, prefix: str = "!", illegal_words: set[str] = None, **kwargs):
        super().__init__(**kwargs)

        self.prefix = prefix
        self.illegal_words = illegal_words or set()

        data = self.load_data()
        self.messages = data.get("messages", [])
        self.blacklisted = data.get("blacklisted", [])

        self.commands = [
            {
                "command": "ping",
                "function": self.ping,
                "has_params": False
            },
            {
                "command": "blacklist",
                "function": self.blacklist_command,
                "has_params": True,
                "param_type": "user"
            },
            {
                "command": "role",
                "function": functions.role_button,
                "has_params": True,
                "param_type": "role"
            }
        ]

    # -------------------------
    # Persistence
    # -------------------------
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {"messages": [], "blacklisted": []}

        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "messages": self.messages,
                "blacklisted": self.blacklisted
            }, f, indent=4)

    # -------------------------
    # Helpers
    # -------------------------
    async def send(self, content, channel):
        await channel.send(content)

    def resolve_user(self, guild, query: str):
        """
        Accepts:
        - user ID
        - username
        - display name
        - mention (<@id>)
        """

        if not guild:
            return None

        query = query.strip()

        # mention <@123>
        if query.startswith("<@") and query.endswith(">"):
            query = query.replace("<@", "").replace(">", "").replace("!", "")

        # ID lookup
        if query.isdigit():
            return guild.get_member(int(query))

        # name lookup (case-insensitive)
        query_lower = query.lower()

        for member in guild.members:
            if member.name.lower() == query_lower:
                return member
            if member.display_name.lower() == query_lower:
                return member

        return None

    # -------------------------
    # Commands
    # -------------------------
    async def ping(self, message, param=None):
        await message.channel.send("Pong!")

    async def blacklist_command(self, message, param):
        member = self.resolve_user(message.guild, param)

        if not member:
            await message.channel.send("User not found.")
            return

        if member.id not in self.blacklisted:
            self.blacklisted.append(member.id)
            self.save_data()

        await message.channel.send(f"Blacklisted {member.display_name}")

    # -------------------------
    # Events
    # -------------------------
    async def on_ready(self):
        print(f"Logged on as {self.user}")

        channel_id = int(os.getenv("MOD_CHANNEL"))
        channel = self.get_channel(channel_id)

        if channel is None:
            channel = await self.fetch_channel(channel_id)

        await channel.send("Started logging private DMs to the bot...")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        # Illegal words moderation
        content_lower = message.content.lower()
        for word in self.illegal_words:
            if word in content_lower:
                try:
                    await message.author.timeout(
                        timedelta(seconds=120),
                        reason="Illegal word detected"
                    )
                except:
                    pass
                await message.delete()
                return

        # -------------------------
        # DM logging
        # -------------------------
        if isinstance(message.channel, discord.DMChannel):

            if message.author.id in self.blacklisted:
                return

            channel_id = int(os.getenv("MOD_CHANNEL"))
            channel = self.get_channel(channel_id)

            if channel is None:
                channel = await self.fetch_channel(channel_id)

            if self.messages and self.messages[-1]["author_id"] != message.author.id:
                await channel.send("----")

            self.messages.append({
                "author_id": message.author.id,
                "content": message.content
            })

            self.save_data()

            await channel.send(f"{message.author} > {message.content}")

        # -------------------------
        # Commands
        # -------------------------
        for command in self.commands:
            if message.content.lower().startswith(self.prefix + command["command"]):

                func = command["function"]
                has_params = command["has_params"]

                param = None

                if has_params:
                    param = message.content[len(self.prefix + command["command"]):].strip()

                if inspect.iscoroutinefunction(func):
                    await func(message, param)
                else:
                    func(message, param)


# -------------------------
# Setup
# -------------------------
def create_client(prefix: str = "!", illegal_words=None):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    return DiscordClient(
        intents=intents,
        prefix=prefix,
        illegal_words=illegal_words
    )


def run(token: str, prefix: str = "!"):
    client = create_client(prefix=prefix)
    client.run(token)
    return client


if __name__ == "__main__":
    load_dotenv()
    run(prefix="!", token=os.getenv("DISCORD_TOKEN"))