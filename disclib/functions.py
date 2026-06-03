import discord

async def ping(message: discord.Message, params):
    await message.channel.send("Pong")
async def role_button(message: discord.Message, params):
    if not message.guild:
        await message.channel.send("This command can only be used in a server.")
        return

    role_query = (params or "").strip()
    if not role_query:
        await message.channel.send("Please provide a role mention, ID, or name.")
        return

    role = None

    if role_query.startswith("<@&") and role_query.endswith(">"):
        role_id = role_query.replace("<@&", "").replace(">", "")
        if role_id.isdigit():
            role = message.guild.get_role(int(role_id))
    elif role_query.isdigit():
        role = message.guild.get_role(int(role_query))
    else:
        role_query_lower = role_query.lower()
        for guild_role in message.guild.roles:
            if guild_role.name.lower() == role_query_lower:
                role = guild_role
                break

    if role is None:
        await message.channel.send("Role not found.")
        return

    class RoleButton(discord.ui.Button):
        def __init__(self, target_role: discord.Role):
            super().__init__(
                label=f"Get {target_role.name}",
                style=discord.ButtonStyle.primary,
            )
            self.target_role = target_role

        async def callback(self, interaction: discord.Interaction):
            member = interaction.user

            if not isinstance(member, discord.Member):
                await interaction.response.send_message(
                    "This button can only be used in a server.",
                    ephemeral=True,
                )
                return

            if self.target_role in member.roles:
                await interaction.response.send_message(
                    f"You already have {self.target_role.name}.",
                    ephemeral=True,
                )
                return

            try:
                await member.add_roles(self.target_role, reason="Role button used")
            except discord.Forbidden:
                await interaction.response.send_message(
                    "I can't assign that role. Check my role permissions and hierarchy.",
                    ephemeral=True,
                )
                return

            await interaction.response.send_message(
                f"Added {self.target_role.name} to you.",
                ephemeral=True,
            )

    class RoleButtonView(discord.ui.View):
        def __init__(self, target_role: discord.Role):
            super().__init__(timeout=None)
            self.add_item(RoleButton(target_role))

    await message.channel.send(
        f"Click the button below to get {role.mention}.",
        view=RoleButtonView(role),
    )