"""The main file for the bot"""
# The discord fork used in this bot is py-cord

# Standard Library imports
from os import environ, getcwd
from pathlib import Path

# Third party imports
from discord import Intents, Bot, ActivityType, Game, Activity, option, Forbidden, Embed, Color, NotFound, \
    DMChannel, ApplicationContext, Message, User, ApplicationCommandError, Reaction, Member, CategoryChannel, \
    SlashCommandGroup
from dotenv import load_dotenv as loadDotenv

# Internal imports
from internals import Config
from internals.database import Database
from internals.logging import createLogger, SuppressedLoggerAdapter

# Load .env
loadDotenv()
debugMode: bool = environ.get("DEBUG").upper() == "TRUE"

token: str = environ.get("TOKEN") if debugMode is False else environ.get("TESTING_TOKEN")

# Ensure BotData and Logs directories exist
if not Path("BotData").exists():
    raise FileNotFoundError(f"BotData directory not found. Cwd: {getcwd()}")
if not Path("Logs").exists():
    raise FileNotFoundError(f"Logs directory not found. Cwd: {getcwd()}")

# Create required objects
config: Config = Config(Path("BotData/config.json"))
logger: SuppressedLoggerAdapter = createLogger("Main", config.loggingLevel)

database: Database = Database(config=config)  # TODO: Swap over to using postgres

logger.info("Initializing bot...")
# Set bot intents including Message intents for slash commands
intents: Intents = Intents.all()

bot: Bot = Bot(intents=intents)

logger.info("Bot initialized.")

# Create command groups
filterGroup: SlashCommandGroup = bot.create_group(name="filter", description="Commands for managing the gif filter")
gifModerationGroup: SlashCommandGroup = bot.create_group(name="gifmoderation", description="Commands for managing gifs")
reactionsGroup: SlashCommandGroup = bot.create_group(name="reactions", description="Commands for managing reactions")
roleReactionGroup: SlashCommandGroup = bot.create_group(name="rolereactions", description="Commands for managing role reactions")
auditGroup: SlashCommandGroup = bot.create_group(name="audit", description="Commands used for auditing bot values and data")

"""
Helper functions.
"""


def checkForGifClassifier(message: str) -> bool:
    """
    Checks if the message contains a gif classifier.

    Args:
        message(str): The message to check

    Returns:
        bool: Whether the message contains a gif classifier
    """
    logger.debug(f"Checking if message contains gif classifier message: {message}")
    logger.debug(f"gifClassifiers: {config.gifClassifiers}")
    for classifier in config.gifClassifiers:
        if classifier in message and message not in database.whitelistedGifs:
            logger.debug(f"Message contains gif classifier {classifier}")
            return True

    logger.debug(f"Message does not contain gif classifier")
    return False


@bot.slash_command(
    name="ping",
    description="Tests the bots latency."
)
async def pingCommand(ctx: ApplicationContext) -> None:
    """
    The ping command for the bot.

    Args:
        ctx(ApplicationContext): The bot context
    """
    await ctx.respond(f'Latency is {round(bot.latency * 1000)}ms')
    return


@filterGroup.command(
    name="addexception",
    description="Adds an exception to the gif filter"
)
@option(name="link", description="The link to the gif to add", required=True)
async def addException(ctx: ApplicationContext, link: str) -> None:
    """
    The add exception command for the bot.

    Args:
        ctx(ApplicationContext): The context of the command
        link(str): The link to the gif to add
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    if link in database.whitelistedGifs:
        await ctx.respond("This gif is already whitelisted!")
        return

    database.addWhitelistedGif(ctx.author.id, link)
    await ctx.respond("Gif whitelisted!")


@filterGroup.command(
    name="removeexception",
    description="Removes an exception from the gif filter"
)
@option(name="link", description="The link to the gif to remove", required=True)
async def removeException(ctx: ApplicationContext, link: str) -> None:
    """
    The remove exception command for the bot.

    Args:
        ctx(ApplicationContext): The context of the command
        link(str): The link to the gif to remove
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    if link not in database.whitelistedGifs:
        await ctx.respond("This gif is not whitelisted!")
        return

    database.removeWhitelistedGif(link)
    await ctx.respond("Gif unwhitelisted!")


@filterGroup.command(  # This is working as intended
    name="togglefilter",
    description="Toggles the gif filter"
)
async def toggleFilter(ctx: ApplicationContext) -> None:
    """
    The toggle filter command for the bot.

    Args:
        ctx (ApplicationContext): The context of the command
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    config.filterEnabled = not config.filterEnabled
    await ctx.respond(f"Filter toggled! It is now `{config.filterEnabled}`")


@gifModerationGroup.command(  # This is working as intended
    name="bangif",
    description="Bans a gif"
)
@option(name="link", description="The link to the gif to ban", required=True)
@option(name="reason", description="The reason for the ban", required=False)
async def banGif(ctx: ApplicationContext, link: str, reason: str) -> None:
    """
    The ban gif command for the bot.

    Args:
        ctx(ApplicationContext): The context of the command
        link(str): The link to the gif to ban
        reason(str): The reason for the ban
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    if database.checkGifBanned(link):
        await ctx.respond("This gif is already banned!")
        return

    if reason is None:
        reason = "No reason given"

    database.addBannedGif(ctx.author.id, link, reason)
    await ctx.respond("Gif banned!")


@gifModerationGroup.command(  # This is working as intended
    name="unbangif",
    description="Unbans a gif"
)
@option(name="link", description="The link to the gif to unban", required=True)
async def unbanGif(ctx: ApplicationContext, link: str) -> None:
    """
    The unban gif command for the bot.

    Args:
        ctx (ApplicationContext): The context of the command
        link(str): The link to the gif to unban
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    if not database.checkGifBanned(link):
        await ctx.respond("This gif is not banned!")
        return

    database.removeBannedGif(link)
    await ctx.respond("Gif unbanned!")


@bot.slash_command(  # This is working as intended
    name="setstatus",
    description="Sets the bot's status"
)
@option(name="type", description="The type of status to set", required=True,
        choices=["playing", "watching", "listening", "streaming"])
@option(name="status", description="The status to set", required=True)
async def setStatus(ctx: ApplicationContext, status: str, type: str) -> None:
    """
    The set status command for the bot.
    Args:
        ctx (ApplicationContext): The context of the command
        status(str): The status to set
        type(str): The type of status to set
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return
    config.statusType = type
    config.status = status

    await setStatusInternal()

    await ctx.respond(f"Status set to {config.statusType.title()} {config.status}!")


@reactionsGroup.command(
    name="addreact",
    description="Adds a reaction to all new messages from a user"
)
@option(name="user", description="The user to add a reaction to", required=True)
@option(name="reaction", description="The reaction to add (escape sequence starting with /)", required=True)
async def addReaction(ctx, user: User, reaction: str):
    """
    The add reaction command for the bot.
    Args:
        ctx (ApplicationContext): The context of the command
        user(User): The user to add a reaction to
        reaction(str): The reaction to add
    """
    if not database.checkUserAdmin(ctx.author):
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    logger.info(f"User {ctx.author.name}({ctx.author.id}) adding reaction {reaction} to user "
                f"{user.name}({user.id})")

    database.addReaction(reaction, ctx.author.id, user.id)
    await ctx.respond(f"Added reaction {reaction} to user <@{user.id}>!")


@reactionsGroup.command(
    name="removereact",
    description="Removes a reaction from all new messages from a user"
)
@option(name="user", description="The user to remove a reaction from", required=True)
@option(name="reaction", description="The reaction to remove", required=True)
async def removeReaction(ctx, user: User, reaction: str):
    """
    The remove reaction command for the bot.
    Args:
        ctx (ApplicationContext): The context of the command
        user(User): The user to remove a reaction from
        reaction(str): The reaction to remove
    """

    if not database.checkUserAdmin(ctx.author) and ctx.author.id != user.id:
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    logger.info(
        f"User {ctx.author.name}({ctx.author.id}) removing reaction {reaction} from user "
        f"{user.name}({user.id})")

    database.removeReaction(reaction, user.id)
    await ctx.respond(f"Removed reaction {reaction} from user <@{user.id}>!")


@reactionsGroup.command(
    name="listreacts",
    description="Lists all reactions for a user"
)
@option(name="user", description="The user to list reactions for", required=True)
async def listReactions(ctx, user: User):
    """
    The list reactions command for the bot.
    Args:
        ctx (ApplicationContext): The context of the command
        user(User): The user to list reactions for
    """

    if not database.checkUserAdmin(ctx.author) and ctx.author.id != user.id:
        await ctx.respond("You are not an admin!", ephemeral=True)
        return

    logger.info(
        f"User {ctx.author.name}({ctx.author.id}) listing reactions for user {user.name}({user.id})")

    reactions = database.getUserReactions(user.id)
    if len(reactions) == 0:
        logger.info(f"No reactions found for user {user.name}({user.id})")
        await ctx.respond(f"No reactions found for user <@{user.id}>!")
        return

    for react in reactions:
        reactions[reactions.index(react)] = f"{react[0]}"
    logger.debug(f"Reactions for user {user.name}({user.id}) are {', '.join(reactions)}")
    await ctx.respond(f"Reactions for user <@{user.id}> are {', '.join(reactions)}")


@bot.command(
    name="messagecount",
    description="Gets the message count for a user"
)
@option(name="user", description="The user to get the message count for", required=True)
@option(name="type", description="The type of message count to get", choices=["sent", "deleted"])
async def getMessageCount(ctx, user: User, type: str = "sent"):
    """
    The get message count command for the bot.

    Args:
        ctx (ApplicationContext): The context of the command
        user(User): The user to get the message count for
        type(str): The type of message count to get
            "sent": The number of messages sent by the user
            "deleted": The number of messages deleted by the user
    """

    logger.info(
        f"User {ctx.author.name}({ctx.author.id}) getting {type} message count for user {user.name}"
        f"({user.id})")
    if not database.checkUserExists(user.id):
        logger.info(f"User {user.name}({user.id}) does not exist")
        await ctx.respond(f"User <@{user.id}> does not exist!")
        return

    if type == "sent":
        count = database.getMessagesSent(user.id)
    elif type == "deleted":
        count = database.getMessagesDeleted(user.id)
    else:
        await ctx.respond("Invalid message count type!", ephemeral=True)
        return

    logger.debug(f"User {user.name}({user.id}) has {type} {count} messages")
    await ctx.respond(f"User <@{user.id}> has {type} {count} messages!")


@bot.command(
    name="messagesleaderboard",
    description="Gets the messages leaderboard"
)
@option(name="type", description="The type of message count to get", choices=["sent", "deleted"])
@option(name="count", description="The number of users to get")
async def messagesLeaderboard(ctx, type: str = "sent", count: int = 10):
    """
    The messages leaderboard command for the bot. Gets the top 10 users by message count.
    Returns the top 10 users by message count in a leaderboard embed.

    Args:
        ctx (ApplicationContext): The context of the command
        type(str): The type of message count to get
            "sent": The number of messages sent by the user
            "deleted": The number of messages deleted by the user
        count(int): The number of users to get
    """
    logger.info(f"User {ctx.author.name}({ctx.author.id}) getting {type} messages leaderboard")
    if type == "sent":
        users = database.getTopMessagesSent(count)
    elif type == "deleted":
        users = database.getTopMessagesDeleted(count)
    else:
        await ctx.respond("Invalid message count type!", ephemeral=True)
        return

    if len(users) == 0:
        logger.info(f"No users found")
        await ctx.respond("No users found!")
        return

    embed = Embed(title=f"Top {count} Users by {type.capitalize()} Messages", color=Color.blue())
    for user in users:
        embed.add_field(name=f"{user[1]}", value=f"{user[2]} messages", inline=False)

    if len(users) > count:
        embed.set_footer(text=f"Only showing top {count} users")

    if len(users) < count:
        embed.set_footer(text=f"Only {len(users)} users found")

    await ctx.respond(embed=embed)


@auditGroup.command(
    name="messages",
    description="Audits message count for all sent in all servers. Can only be run by the bot owner."
)
async def audit(ctx: ApplicationContext) -> None:
    """
    The audit command for the bot. Audits message count for all sent in all servers. Can only be run by the bot owner.

    Args:
        ctx (ApplicationContext): The context of the command
    """
    logger.warning(f"User {ctx.author.name}({ctx.author.id}) running audit messages")
    if ctx.author.id not in config.owonerId:
        await ctx.respond("You are not the bot owner!", ephemeral=True)
        return

    await ctx.respond(f"Auditing message count for all servers. This may take a while.")

    # Create a message count object
    messageCount: dict[int, dict[int, dict[int, int]]] = {}

    # Get all guilds
    for guild in bot.guilds:
        logger.debug(f"Getting message count for guild {guild.name}({guild.id})")
        messageCount[guild.id] = {}

        # Get all channels
        for channel in guild.channels:
            logger.debug(f"Getting message count for channel {channel.name}({channel.id}) in {guild.name}({guild.id})")
            messageCount[guild.id][channel.id] = {}

            # Get all members in the guild
            for member in guild.members:
                messageCount[guild.id][channel.id][member.id] = 0

            # Get all messages in the channel
            if not isinstance(channel, CategoryChannel):
                try:
                    async for message in channel.history(limit=999999999999999999999999999999999999999999999999999999):
                        try:
                            messageCount[guild.id][channel.id][message.author.id] += 1

                        except KeyError:
                            messageCount[guild.id][channel.id][message.author.id] = 1
                except Forbidden:
                    logger.error(f"Bot does not have permission to read messages in {channel.name}({channel.id}) in "
                                 f"{guild.name}({guild.id})")

                except NotFound:
                    logger.error(f"Channel {channel.name}({channel.id}) not found in {guild.name}({guild.id})")

    # Count all messages in the messageCount object from every user globally
    users: dict[int, int] = {}
    for guild in messageCount:
        logger.debug(f"Counting messages for guild {guild}")
        for channel in messageCount[guild]:
            for user in messageCount[guild][channel]:
                if user not in users:
                    users[user] = 0
                users[user] += messageCount[guild][channel][user]

    # Update the database with the new message counts
    for user in users:
        logger.debug(f"Updating message count for user {user}")
        if not database.checkUserExists(user):
            database.addUser(user, bot.get_user(user).name if bot.get_user(user) is not None else "deleted user")

        database.setMessagesSent(user, users[user])

    await ctx.respond("Audit complete!")


@auditGroup.command(
    name="usernames",
    description="Audits usernames for all users in all servers. Can only be run by the bot owner."
)
async def auditUsernames(ctx: ApplicationContext) -> None:
    """
    The audit usernames command for the bot. Audits usernames for all users in all servers. Can only be run by the bot
    owner.

    Args:
        ctx (ApplicationContext): The context of the command
    """
    logger.warning(f"User {ctx.author.name}({ctx.author.id}) running audit usernames")
    if ctx.author.id not in config.owonerId:
        await ctx.respond("You are not the bot owner!", ephemeral=True)
        return

    await ctx.respond(f"Auditing usernames for all users in all servers. This may take a while.")

    # Get all users in the database and check that their usernames are up to date
    for user in database.users:
        if bot.get_user(user[0]) is not None:
            if user[1] != bot.get_user(user[0]).name:
                database.setUsername(user[0], bot.get_user(user[0]).name)

"""
Bot Events
------------------------------------------------------------------------------------------------------------------------
"""


@bot.event
async def on_message(message: Message) -> None:
    """
    The on message event for the bot.

    Args:
        message (Message): The context of the message
    """
    # This has all been rewritten, I believe it is as readable as it can be
    if message.channel is DMChannel:  # This might not work, if it does not use isinstance()
        logger.info(f"Message from {message.author.name}({message.author.id} in DMs")

    else:
        logger.info(
            f"Message({message.id}) from {message.author.name}({message.author.id}) in {message.channel.name}({message.channel.id})"
            f"in {message.guild.name}({message.guild.id}): "
            f"{message.content}")

    # Check if the user is in the database
    if not database.checkUserExists(message.author.id):
        database.addUser(message.author.id, message.author.name)

    # Increment the messages count
    database.incrementMessagesSent(message.author.id)

    if message.author.id == bot.user.id:
        return

    # Perform banned gifs check
    if database.checkMessageBannedGifs(message.content) and message.author.id not in config.owonerId:
        logger.info(f"Deleting message {message.id}, contains banned gif.")
        await message.delete(reason="Contains banned gif.")
        await message.channel.send(f"{message.author.mention} no.")

    # Run reply filter
    if message.reference is not None and not message.is_system():  # Only these two checks are run here for optimization
        if message.reference.resolved.author.id in database.filteredUsers and not database.checkUserAdmin(
                message.author) \
                and checkForGifClassifier(message.content):
            logger.debug(f"Message is a reply to a message from a filtered user, deleting")
            await message.delete()
            await message.channel.send(f"{message.author.mention} no.")

    # Handle reactions
    userReactions: list[str] = database.getUserReactions(message.author.id)
    if userReactions is not None:
        logger.debug(f"User {message.author.name}({message.author.id}) has reactions {userReactions}")
        for reaction in userReactions:
            logger.info(f"Adding reaction {reaction[0]} to message {message.id}")
            try:
                await message.add_reaction(reaction[0])

            # When the bot does not have permission to add reactions or the user has blocked the bot
            except Forbidden:
                logger.error(
                    f"Bot does not have permission to add reactions in {message.channel.name}({message.channel.id}) in "
                    f"{message.guild.name}({message.guild.id}) OR {message.author.name}({message.author.id}) has "
                    f"blocked the bot"
                )

            # When the message has been deleted
            except NotFound:
                logger.error(
                    f"Message {message.id} not found in {message.channel.name}({message.channel.id}) in "
                    f"{message.guild.name}({message.guild.id})"
                )


@bot.event
async def on_message_delete(message: Message) -> None:
    """
    The on message delete event for the bot.

    Args:
        message (Message): The context of the message
    """

    logger.info(
        f"Message from {message.author.name}({message.author.id}) in {message.channel.name}({message.channel.id}) in "
        f"{message.guild.name}({message.guild.id}) deleted: \"{message.content}\""
    )

    logger.debug("Checking if user exists in database")
    if not database.checkUserExists(message.author.id):
        logger.debug("User does not exist, adding to database")
        database.addUser(message.author.id, message.author.name)


@bot.event
async def on_reaction_add(reaction: Reaction, user: Member | User) -> None:
    """
    The on reaction add event for the bot. Used for the random reaction event.

    Args:
        reaction (Reaction): The reaction that was added
        user (Member | User): The user that added the reaction
    """
    logger.info(f"Reaction {reaction.emoji} added by {user.name}({user.id}) to message {reaction.message.id} in "
                f"{reaction.message.channel.name}({reaction.message.channel.id}) in "
                f"{reaction.message.guild.name}({reaction.message.guild.id})")

    # TODO: Implement reaction roles


@bot.event
async def on_command_error(ctx: ApplicationContext, error: ApplicationCommandError):
    """
    The on slash command error event for the bot.
    Args:
        ctx (Message): The context of the command
        error (ApplicationCommandError): The exception
    """
    logger.error(f"Exception in slash command {ctx.command.name}:\n{error}")
    await ctx.respond(f"Exception in slash command {ctx.command.name}:\n{error}")


@bot.event  # This is working properly
async def on_ready():
    """
    The on ready event for the bot.
    """
    logger.info(f"Logged in as {bot.user.name}({bot.user.id})")

    try:
        await setStatusInternal()
    except TypeError as error:
        exit(error.__cause__)

    # Get all users in all server the bot is in
    users: list[Member] = []
    for guild in bot.guilds:
        users.extend(guild.members)

    for user in users:
        if not database.checkUserExists(user.id):
            database.addUser(user.id, user.name)

    # TODO: Add a users check to ensure all users are in the database and then prompt 537400103044907028 asking if they
    #  want to count all messages for all users

    logger.debug(f"Status set to {config.statusType.title()} {config.status}!")

    logger.info("Bot ready!")


async def setStatusInternal():
    """
    Sets the status of the bot.

    Raises:
        TypeError: If the statusType is invalid.
    """
    match config.statusType.lower():
        case "playing":
            await bot.change_presence(activity=Game(name=config.status))
        case "watching":
            await bot.change_presence(activity=Activity(type=ActivityType.watching, name=config.status))
        case "listening":
            await bot.change_presence(activity=Activity(type=ActivityType.listening, name=config.status))
        case "streaming":
            await bot.change_presence(activity=Activity(type=ActivityType.streaming, name=config.status))
        case _:
            return TypeError("Invalid statusType")


if __name__ == '__main__':
    logger.info("Starting bot...")
    bot.run(token)
