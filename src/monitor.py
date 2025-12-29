import os
import asyncio
import time
import psutil
import discord

# Load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
raw_interval = os.getenv("MONITOR_INTERVAL", "30")

# Convert interval to float with fallback
try:
    interval = float(raw_interval)
except:
    interval = 30.0

# Thresholds for alerts
CPU_THRESHOLD = 80   # %
RAM_THRESHOLD = 90   # %

# Cooldown to avoid alert spam (in seconds)
ALERT_COOLDOWN = 300  # 5 minutes
last_alert_time = 0

# Intents setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Global variable to store the live metrics message
live_message = None

async def metrics_loop():
    """Background task that updates live metrics and sends alerts if needed."""
    global live_message, last_alert_time

    await client.wait_until_ready()

    if not client.guilds:
        print("Bot is not in any server!")
        return

    # Use the first server the bot is in (can be extended for multiple servers)
    guild = client.guilds[0]

    # === TARGET CHANNEL NAME ===
    TARGET_CHANNEL_NAME = "live-metrics"  # Change to your desired channel name: "general", "monitoring", etc.

    # Find the channel by name (case-insensitive)
    channel = discord.utils.get(guild.text_channels, name=TARGET_CHANNEL_NAME.lower())

    if not channel:
        print(f"Channel '{TARGET_CHANNEL_NAME}' not found!")
        print("Available channels:", [c.name for c in guild.text_channels])
        return

    # Check if bot has permission to send messages
    if not channel.permissions_for(guild.me).send_messages:
        print(f"No permission to send messages in #{channel.name}")
        return

    print(f"Monitoring started → channel #{channel.name}, interval {interval} seconds")

    while not client.is_closed():
        # Collect system metrics
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        ram_used = round(psutil.virtual_memory().used / (1024**3), 2)
        ram_total = round(psutil.virtual_memory().total / (1024**3), 2)

        current_time = time.strftime("%H:%M:%S %d.%m.%Y")

        # === LIVE DASHBOARD MESSAGE (quietly edited) ===
        live_text = f"""
**System Metrics (Live Dashboard)**
Updated: `{current_time}`
CPU: `{cpu}%`
RAM: `{ram}%` (`{ram_used} / {ram_total} GB`)
        """.strip()

        try:
            if live_message and live_message.channel.id == channel.id:
                await live_message.edit(content=live_text)
            else:
                live_message = await channel.send(live_text)
        except Exception as e:
            print(f"Error editing/sending live message: {e}")

        # === HIGH LOAD ALERTS ===
        current_timestamp = time.time()
        need_alert = False
        alert_reasons = []

        if cpu >= CPU_THRESHOLD:
            alert_reasons.append(f"CPU {cpu}% ≥ {CPU_THRESHOLD}%")
            need_alert = True

        if ram >= RAM_THRESHOLD:
            alert_reasons.append(f"RAM {ram}% ≥ {RAM_THRESHOLD}%")
            need_alert = True

        # Send alert only if needed and cooldown has passed
        if need_alert and (current_timestamp - last_alert_time > ALERT_COOLDOWN):
            alert_text = f"""
**High Load Warning!**
{chr(10).join(alert_reasons)}
Time: `{current_time}`
CPU: `{cpu}%` | RAM: `{ram}%`
            """.strip()

            try:
                # Remove "@everyone" if you don't want to ping everyone
                await channel.send(alert_text + " @everyone")
                last_alert_time = current_timestamp
                print(f"Alert sent: {'; '.join(alert_reasons)}")
            except Exception as e:
                print(f"Error sending alert: {e}")

        await asyncio.sleep(interval)


@client.event
async def on_ready():
    """Event triggered when the bot is fully connected."""
    print(f'{client.user} successfully connected to Discord!')
    print(f"Servers: {len(client.guilds)}")
    for g in client.guilds:
        print(f" - {g.name} (ID: {g.id})")

    # Start the metrics monitoring task
    client.loop.create_task(metrics_loop())


@client.event
async def on_message(message):
    """Handle incoming messages (optional commands)."""
    if message.author == client.user:
        return

    # Example command
    if message.content.lower() == "status":
        await message.channel.send("Monitoring is active ✅ Live metrics are updated below.")

# Safety check for token
if not TOKEN:
    print("Error: DISCORD_TOKEN is not set!")
    exit(1)

# Run the bot
client.run(TOKEN)