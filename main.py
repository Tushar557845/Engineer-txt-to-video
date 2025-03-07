import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess
import urllib.parse
import yt_dlp
import cloudscraper
import m3u8
from aiohttp import ClientSession, web
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

# Bot Configuration
API_ID = "24473318" # Replace with your API ID
API_HASH = "e7dd0576c5ac0ff8f90971d6bb04c8f5"  # Replace with your API HASH
BOT_TOKEN = ""  # Replace with your Bot Token

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Sudo (Owner) ID
SUDO_USERS = [5840594311]  # Replace with your Telegram ID

# Data storage for authorized users, channels, and groups
AUTHORIZED_USERS = set()
AUTHORIZED_CHANNELS = set()
AUTHORIZED_GROUPS = set()

# Load authorized data from file (if exists)
if os.path.exists("authorized_data.json"):
    with open("authorized_data.json", "r") as f:
        data = json.load(f)
        AUTHORIZED_USERS = set(data.get("users", []))
        AUTHORIZED_CHANNELS = set(data.get("channels", []))
        AUTHORIZED_GROUPS = set(data.get("groups", []))

# Save authorized data to file
def save_authorized_data():
    data = {
        "users": list(AUTHORIZED_USERS),
        "channels": list(AUTHORIZED_CHANNELS),
        "groups": list(AUTHORIZED_GROUPS)
    }
    with open("authorized_data.json", "w") as f:
        json.dump(data, f)

# Check if user is authorized
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS or user_id in SUDO_USERS

# Check if channel is authorized
def is_authorized_channel(channel_id):
    return channel_id in AUTHORIZED_CHANNELS

# Check if group is authorized
def is_authorized_group(group_id):
    return group_id in AUTHORIZED_GROUPS

# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Bot is running!")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_bot():
    await bot.start()
    print("Bot is up and running")

async def stop_bot():
    await bot.stop()

async def main():
    # Start the bot
    await start_bot()

    # Keep the program running
    try:
        while True:
            await asyncio.sleep(3600)  # Run forever, or until interrupted
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()

# Start command handler
@bot.on_message(filters.command("start"))
async def start(client: Client, msg: Message):
    if not is_authorized(msg.from_user.id):
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "denied" sticker
        await msg.reply_text("You are not authorized to use this bot.")
        return

    await msg.reply_text(
        "🌟 Welcome to the Bot! 🌟\n\n"
        "Use /help to see available commands."
    )

# Engineer/Upload command handler
@bot.on_message(filters.command(["engineer", "upload"]))
async def engineer_upload(client: Client, msg: Message):
    # Check authorization
    if not (is_authorized(msg.from_user.id) or is_authorized_channel(msg.chat.id) or is_authorized_group(msg.chat.id)):
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "denied" sticker
        await msg.reply_text("You are not authorized to use this command.")
        return

    editable = await msg.reply_text("🔹 Hi, I am a Powerful TXT Downloader Bot. Send me the TXT file and wait.")
    input: Message = await bot.listen(msg.chat.id)
    x = await input.download()
    await input.delete(True)

    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = "𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™"

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = [i.split("://", 1) for i in content]
        os.remove(x)
    except Exception as e:
        await msg.reply_text(f"Invalid file input. Error: {e}")
        os.remove(x)
        return

    await editable.edit(f"Total links found: **{len(links)}**\n\nSend the starting point (default is 1).")
    input0: Message = await bot.listen(msg.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    try:
        arg = int(raw_text)
    except:
        arg = 1

    await editable.edit("Enter your batch name or send 'd' to use the filename.")
    input1: Message = await bot.listen(msg.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    b_name = file_name if raw_text0 == 'd' else raw_text0

    await editable.edit("Enter resolution (e.g., 480 or 720).")
    input2: Message = await bot.listen(msg.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    res = {
        "144": "144x256",
        "240": "240x426",
        "360": "360x640",
        "480": "480x854",
        "720": "720x1280",
        "1080": "1080x1920"
    }.get(raw_text2, "UN")

    await editable.edit("Enter your name or send 'de' to use the default.")
    input3: Message = await bot.listen(msg.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    CR = credit if raw_text3 == 'de' else raw_text3

    await editable.edit("Enter your PW token for MPD URL or send 'not' to use the default.")
    input4: Message = await bot.listen(msg.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    MR = "default_token" if raw_text4 == 'not' else raw_text4

    await editable.edit("Send the thumbnail URL or 'no' to skip.")
    input6: Message = await bot.listen(msg.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    thumb = "thumb.jpg" if raw_text6.startswith(("http://", "https://")) else "no"

    if thumb != "no":
        os.system(f"wget '{raw_text6}' -O 'thumb.jpg'")

    count = arg
    for i in range(arg - 1, len(links)):
        try:
            url = "https://" + links[i][1]
            name = f"{str(count).zfill(3)}) {links[i][0][:60]}"
            cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            await editable.edit(f"Downloading: **{name}**")
            os.system(cmd)
            await bot.send_video(msg.chat.id, f"{name}.mp4", caption=f"**{name}**\n\nUploaded by {CR}")
            os.remove(f"{name}.mp4")
            count += 1
        except Exception as e:
            await msg.reply_text(f"Error downloading {url}: {e}")
            continue

    await msg.reply_text("✅ All downloads completed!")

# Add user command
@bot.on_message(filters.command("adduser") & filters.user(SUDO_USERS))
async def add_user(client: Client, msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        AUTHORIZED_USERS.add(user_id)
        save_authorized_data()
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "success" sticker
        await msg.reply_text(f"User {user_id} has been added to the authorized list.")
    else:
        await msg.reply_text("Please reply to a user's message to add them.")

# Remove user command
@bot.on_message(filters.command("removeuser") & filters.user(SUDO_USERS))
async def remove_user(client: Client, msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        if user_id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user_id)
            save_authorized_data()
            await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "removed" sticker
            await msg.reply_text(f"User {user_id} has been removed from the authorized list.")
        else:
            await msg.reply_text("User is not in the authorized list.")
    else:
        await msg.reply_text("Please reply to a user's message to remove them.")

# Add channel command
@bot.on_message(filters.command("addchannel") & filters.user(SUDO_USERS))
async def add_channel(client: Client, msg: Message):
    try:
        channel_id = int(msg.text.split()[1])
        AUTHORIZED_CHANNELS.add(channel_id)
        save_authorized_data()
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "success" sticker
        await msg.reply_text(f"Channel {channel_id} has been added to the authorized list.")
    except:
        await msg.reply_text("Invalid channel ID.")

# Remove channel command
@bot.on_message(filters.command("removechannel") & filters.user(SUDO_USERS))
async def remove_channel(client: Client, msg: Message):
    try:
        channel_id = int(msg.text.split()[1])
        if channel_id in AUTHORIZED_CHANNELS:
            AUTHORIZED_CHANNELS.remove(channel_id)
            save_authorized_data()
            await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "removed" sticker
            await msg.reply_text(f"Channel {channel_id} has been removed from the authorized list.")
        else:
            await msg.reply_text("Channel is not in the authorized list.")
    except:
        await msg.reply_text("Invalid channel ID.")

# Add group command
@bot.on_message(filters.command("addgroup") & filters.user(SUDO_USERS))
async def add_group(client: Client, msg: Message):
    try:
        group_id = int(msg.text.split()[1])
        AUTHORIZED_GROUPS.add(group_id)
        save_authorized_data()
        await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "success" sticker
        await msg.reply_text(f"Group {group_id} has been added to the authorized list.")
    except:
        await msg.reply_text("Invalid group ID.")

# Remove group command
@bot.on_message(filters.command("removegroup") & filters.user(SUDO_USERS))
async def remove_group(client: Client, msg: Message):
    try:
        group_id = int(msg.text.split()[1])
        if group_id in AUTHORIZED_GROUPS:
            AUTHORIZED_GROUPS.remove(group_id)
            save_authorized_data()
            await msg.reply_sticker("CAACAgUAAxkBAAEB...")  # Replace with a "removed" sticker
            await msg.reply_text(f"Group {group_id} has been removed from the authorized list.")
        else:
            await msg.reply_text("Group is not in the authorized list.")
    except:
        await msg.reply_text("Invalid group ID.")

# List users command
@bot.on_message(filters.command("userlist") & filters.user(SUDO_USERS))
async def list_users(client: Client, msg: Message):
    if AUTHORIZED_USERS:
        users_list = "\n".join([f"User ID: {user_id}" for user_id in AUTHORIZED_USERS])
        await msg.reply_text(f"Authorized Users:\n{users_list}")
    else:
        await msg.reply_text("No authorized users.")

# List channels command
@bot.on_message(filters.command("channellist") & filters.user(SUDO_USERS))
async def list_channels(client: Client, msg: Message):
    if AUTHORIZED_CHANNELS:
        channels_list = "\n".join([f"Channel ID: {channel_id}" for channel_id in AUTHORIZED_CHANNELS])
        await msg.reply_text(f"Authorized Channels:\n{channels_list}")
    else:
        await msg.reply_text("No authorized channels.")

# List groups command
@bot.on_message(filters.command("grouplist") & filters.user(SUDO_USERS))
async def list_groups(client: Client, msg: Message):
    if AUTHORIZED_GROUPS:
        groups_list = "\n".join([f"Group ID: {group_id}" for group_id in AUTHORIZED_GROUPS])
        await msg.reply_text(f"Authorized Groups:\n{groups_list}")
    else:
        await msg.reply_text("No authorized groups.")

# Help command
@bot.on_message(filters.command("help"))
async def help_command(client: Client, msg: Message):
    help_text = (
        "🌟 **Available Commands** 🌟\n\n"
        "/start - Start the bot\n"
        "/engineer or /upload - Download and upload files (Authorized only)\n"
        "/adduser - Add a user (Sudo only)\n"
        "/removeuser - Remove a user (Sudo only)\n"
        "/addchannel - Add a channel (Sudo only)\n"
        "/removechannel - Remove a channel (Sudo only)\n"
        "/addgroup - Add a group (Sudo only)\n"
        "/removegroup - Remove a group (Sudo only)\n"
        "/userlist - List authorized users (Sudo only)\n"
        "/channellist - List authorized channels (Sudo only)\n"
        "/grouplist - List authorized groups (Sudo only)\n"
        "/help - Show this help message"
    )
    await msg.reply_text(help_text)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
