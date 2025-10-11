import discord
from discord.ext import commands
import json
import random
import os
from datetime import datetime, timedelta
import asyncio
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="astramon ", intents=intents, help_command=None)

# Monster database with elements
MONSTERS = {
    "common": [
        {"name": "Fire Pup", "emoji": "🐶", "element": "Fire", "hp": 50, "attack": 15},
        {"name": "Water Bunny", "emoji": "🐰", "element": "Water", "hp": 55, "attack": 14},
        {"name": "Earth Turtle", "emoji": "🐢", "element": "Earth", "hp": 60, "attack": 12},
        {"name": "Wind Purr", "emoji": "🐱", "element": "Wind", "hp": 45, "attack": 16},
        {"name": "Spark Mouse", "emoji": "🐭", "element": "Lightning", "hp": 50, "attack": 15},
        {"name": "Flame Fox", "emoji": "🦊", "element": "Fire", "hp": 52, "attack": 16},
        {"name": "Wave Frog", "emoji": "🐸", "element": "Water", "hp": 54, "attack": 13},
        {"name": "Stone Panda", "emoji": "🐼", "element": "Earth", "hp": 58, "attack": 13},
        {"name": "Gust Bird", "emoji": "🐦", "element": "Wind", "hp": 48, "attack": 15},
        {"name": "Bolt Hamster", "emoji": "🐹", "element": "Lightning", "hp": 47, "attack": 17},
    ],
    "rare": [
        {"name": "Inferno Wolf", "emoji": "🐺", "element": "Fire", "hp": 70, "attack": 22},
        {"name": "Tidal Dolphin", "emoji": "🐬", "element": "Water", "hp": 75, "attack": 20},
        {"name": "Stonefang", "emoji": "🐗", "element": "Earth", "hp": 80, "attack": 18},
        {"name": "Stormlynx", "emoji": "🐆", "element": "Wind", "hp": 65, "attack": 24},
        {"name": "Thunder Drake", "emoji": "🐉", "element": "Lightning", "hp": 72, "attack": 23},
    ],
    "legendary": [
        {"name": "Phoenix Emperor", "emoji": "🦅", "element": "Fire|Wind", "hp": 100, "attack": 35},
        {"name": "Leviathan King", "emoji": "🐋", "element": "Water|Earth", "hp": 110, "attack": 32},
        {"name": "Storm Dragon", "emoji": "🐲", "element": "Lightning|Wind", "hp": 105, "attack": 38},
        {"name": "Terra Beast", "emoji": "🦏", "element": "Earth|Fire", "hp": 115, "attack": 30},
    ]
}

# Evolution chains
EVOLUTIONS = {
    "Fire Pup": {"evolves_to": "Inferno Wolf", "cost": 500},
    "Water Bunny": {"evolves_to": "Tidal Dolphin", "cost": 500},
    "Earth Turtle": {"evolves_to": "Stonefang", "cost": 500},
    "Wind Purr": {"evolves_to": "Stormlynx", "cost": 500},
    "Spark Mouse": {"evolves_to": "Thunder Drake", "cost": 500},
}

# Shop items
SHOP_ITEMS = {
    "🍖 Basic Meat": {"price": 50, "hunger_restore": 30},
    "🍰 Sweet Cake": {"price": 100, "hunger_restore": 60},
    "🍜 Ramen Bowl": {"price": 150, "hunger_restore": 100},
    "🍕 Pizza Slice": {"price": 200, "hunger_restore": 150},
}

# Quiz questions
ANIME_QUIZ = [
    {"question": "Who is Naruto's mentor?", "answer": "kakashi", "reward": 100},
    {"question": "What is the name of Luffy's pirate crew?", "answer": "straw hat", "reward": 100},
    {"question": "Who is the main character of Attack on Titan?", "answer": "eren", "reward": 100},
    {"question": "What is the name of Goku's signature move?", "answer": "kamehameha", "reward": 100},
    {"question": "Who is the protagonist of Death Note?", "answer": "light", "reward": 100},
    {"question": "What is the name of Ash's first Pokemon?", "answer": "pikachu", "reward": 100},
    {"question": "Who is the main character of My Hero Academia?", "answer": "deku", "reward": 100},
    {"question": "What is the name of the titan that Eren can transform into?", "answer": "attack titan", "reward": 100},
]

# Element advantages
ELEMENT_ADVANTAGES = {
    "Fire": "Wind",
    "Water": "Fire",
    "Earth": "Lightning",
    "Wind": "Earth",
    "Lightning": "Water"
}

# Load or create data
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# Helper function to get or create user data
def get_user_data(user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "monsters": [],
            "shards": 100,
            "battles_won": 0,
            "battles_lost": 0,
            "last_catch": None,
            "last_daily": None,
            "quiz_cooldown": None,
        }
        save_data(data)
    return data[user_id]

# Helper function to check hunger and update
async def check_hunger(user_id):
    user_data = get_user_data(user_id)
    now = datetime.now()
    
    monsters_to_remove = []
    
    for monster in user_data["monsters"]:
        if "last_fed" not in monster:
            monster["last_fed"] = now.isoformat()
            monster["hunger"] = 0
        else:
            last_fed = datetime.fromisoformat(monster["last_fed"])
            hours_passed = (now - last_fed).total_seconds() / 3600
            monster["hunger"] = min(100, int(hours_passed * 10))
            
            if monster["hunger"] >= 90 and not monster.get("alert_sent"):
                try:
                    user = await bot.fetch_user(int(user_id))
                    await user.send(f"⚠️ Your {monster['emoji']} {monster['name']} is starving! Feed it before it fades away… 💔")
                    monster["alert_sent"] = True
                except:
                    pass
            
            if monster["hunger"] >= 100:
                monsters_to_remove.append(monster)
                try:
                    user = await bot.fetch_user(int(user_id))
                    await user.send(f"💔 Your {monster['emoji']} {monster['name']} has faded away from starvation... Rest in peace... 😢")
                except:
                    pass
    
    for monster in monsters_to_remove:
        user_data["monsters"].remove(monster)
    
    save_data(data)

@bot.event
async def on_ready():
    print("Astramon is online! 🐾")

@bot.command()
async def catch(ctx):
    user_data = get_user_data(ctx.author.id)
    
    # Check cooldown
    if user_data["last_catch"]:
        last = datetime.fromisoformat(user_data["last_catch"])
        if datetime.now() - last < timedelta(seconds=30):
            await ctx.send(f"Nyaa~ Please wait a bit before catching again! 😸")
            return
    
    # Determine rarity
    rand = random.random()
    if rand < 0.05:  # 5% legendary
        rarity = "legendary"
    elif rand < 0.25:  # 20% rare
        rarity = "rare"
    else:  # 75% common
        rarity = "common"
    
    monster = random.choice(MONSTERS[rarity]).copy()
    monster["rarity"] = rarity
    monster["last_fed"] = datetime.now().isoformat()
    monster["hunger"] = 0
    monster["alert_sent"] = False
    monster["level"] = 1
    
    user_data["monsters"].append(monster)
    user_data["shards"] += 50
    user_data["last_catch"] = datetime.now().isoformat()
    save_data(data)
    
    element_display = monster['element'].replace("|", " & ")
    await ctx.send(
        f"✨ Nyaa~ You caught a wild {monster['emoji']} **{monster['name']}**! "
        f"({element_display} type)\n"
        f"You earned 50💎! Type 'astramon profile' to check your collection! UwU"
    )

@bot.command()
async def feed(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to feed! Example: `astramon feed Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    await check_hunger(ctx.author.id)
    
    monster = None
    for m in user_data["monsters"]:
        if m["name"].lower() == monster_name.lower():
            monster = m
            break
    
    if not monster:
        await ctx.send(f"Nyaa~ You don't have a {monster_name} in your collection! 😿")
        return
    
    cost = 50
    if user_data["shards"] < cost:
        await ctx.send(f"Oh no~ You need {cost}💎 to feed your monster! You only have {user_data['shards']}💎 😢")
        return
    
    user_data["shards"] -= cost
    monster["last_fed"] = datetime.now().isoformat()
    monster["hunger"] = 0
    monster["alert_sent"] = False
    save_data(data)
    
    await ctx.send(
        f"Yummy~ 🍖 Your {monster['emoji']} **{monster['name']}** is now full and happy! "
        f"(-{cost}💎) Remaining: {user_data['shards']}💎 💕"
    )

@bot.command()
async def train(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to train! Example: `astramon train Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    monster = None
    for m in user_data["monsters"]:
        if m["name"].lower() == monster_name.lower():
            monster = m
            break
    
    if not monster:
        await ctx.send(f"Nyaa~ You don't have a {monster_name} in your collection! 😿")
        return
    
    cost = 100
    if user_data["shards"] < cost:
        await ctx.send(f"Oh no~ You need {cost}💎 to train! You only have {user_data['shards']}💎 😢")
        return
    
    if "level" not in monster:
        monster["level"] = 1
    
    monster["level"] += 1
    monster["attack"] += 2
    user_data["shards"] -= cost
    save_data(data)
    
    await ctx.send(
        f"✨ Training complete! Your {monster['emoji']} **{monster['name']}** leveled up!\n"
        f"Level: **{monster['level']}** | ATK: **{monster['attack']}** (+2) 💪\n"
        f"(-{cost}💎) Remaining: {user_data['shards']}💎 UwU~"
    )

@bot.command()
async def shop(ctx):
    embed = discord.Embed(
        title="🏪 Astramon Shop - Feed your monsters!",
        description="Buy food with your shards 💎",
        color=discord.Color.purple()
    )
    
    for item, info in SHOP_ITEMS.items():
        embed.add_field(
            name=item,
            value=f"Price: {info['price']}💎\nHunger restore: {info['hunger_restore']}%",
            inline=True
        )
    
    embed.set_footer(text="Use 'astramon feed <monster>' to feed your monsters (costs 50💎)")
    await ctx.send(embed=embed)

@bot.command()
async def evolve(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to evolve! Example: `astramon evolve Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    monster = None
    monster_index = None
    for i, m in enumerate(user_data["monsters"]):
        if m["name"].lower() == monster_name.lower():
            monster = m
            monster_index = i
            break
    
    if not monster:
        await ctx.send(f"Nyaa~ You don't have a {monster_name} in your collection! 😿")
        return
    
    if monster["name"] not in EVOLUTIONS:
        await ctx.send(f"This {monster['name']} cannot evolve anymore! It's already at its peak~ ✨")
        return
    
    evolution = EVOLUTIONS[monster["name"]]
    cost = evolution["cost"]
    
    if user_data["shards"] < cost:
        await ctx.send(f"Oh no~ You need {cost}💎 to evolve! You only have {user_data['shards']}💎 😢")
        return
    
    # Find the evolved monster
    evolved = None
    for monsters_list in MONSTERS.values():
        for m in monsters_list:
            if m["name"] == evolution["evolves_to"]:
                evolved = m.copy()
                break
        if evolved:
            break
    
    if evolved:
        evolved["last_fed"] = monster.get("last_fed", datetime.now().isoformat())
        evolved["hunger"] = monster.get("hunger", 0)
        evolved["alert_sent"] = monster.get("alert_sent", False)
        evolved["rarity"] = "rare"
        
        user_data["monsters"][monster_index] = evolved
        user_data["shards"] -= cost
        save_data(data)
        
        element_display = evolved['element'].replace("|", " & ")
        await ctx.send(
            f"🌟✨ **EVOLUTION COMPLETE!** ✨🌟\n"
            f"Your {monster['emoji']} **{monster['name']}** evolved into "
            f"{evolved['emoji']} **{evolved['name']}**! Amazing~ 💫\n"
            f"Element: {element_display} | HP: {evolved['hp']} | ATK: {evolved['attack']}\n"
            f"(-{cost}💎) Remaining: {user_data['shards']}💎"
        )

@bot.command()
async def battle(ctx, opponent: discord.Member = None):
    user_data = get_user_data(ctx.author.id)
    
    if not user_data["monsters"]:
        await ctx.send("UwU, you need monsters to battle! Use 'astramon catch' first~ 🐾")
        return
    
    player_monster = random.choice(user_data["monsters"])
    
    if opponent and opponent.id != ctx.author.id:
        opp_data = get_user_data(opponent.id)
        if not opp_data["monsters"]:
            await ctx.send(f"Nyaa~ {opponent.name} doesn't have any monsters yet! 😿")
            return
        opp_monster = random.choice(opp_data["monsters"])
        is_bot_battle = False
        opp_name = opponent.name
        opp_mention = opponent.mention
    else:
        # Battle against bot
        opp_monster = random.choice(random.choice(list(MONSTERS.values()))).copy()
        is_bot_battle = True
        opp_name = "Astramon Bot"
        opp_mention = "**Astramon Bot**"
    
    # Calculate damage based on elements
    player_elements = player_monster["element"].split("|")
    opp_elements = opp_monster["element"].split("|")
    
    player_advantage = False
    opp_advantage = False
    
    for p_elem in player_elements:
        for o_elem in opp_elements:
            if ELEMENT_ADVANTAGES.get(p_elem) == o_elem:
                player_advantage = True
            if ELEMENT_ADVANTAGES.get(o_elem) == p_elem:
                opp_advantage = True
    
    player_dmg = player_monster["attack"]
    opp_dmg = opp_monster["attack"]
    
    if player_advantage:
        player_dmg = int(player_dmg * 1.5)
    if opp_advantage:
        opp_dmg = int(opp_dmg * 1.5)
    
    player_hp = player_monster["hp"]
    opp_hp = opp_monster["hp"]
    
    # Simulate battle
    battle_log = []
    round_num = 1
    
    while player_hp > 0 and opp_hp > 0:
        opp_hp -= player_dmg
        if opp_hp <= 0:
            break
        player_hp -= opp_dmg
        round_num += 1
        if round_num > 10:  # Prevent infinite battles
            break
    
    # Determine winner
    if player_hp > opp_hp:
        user_data["battles_won"] += 1
        reward = 150
        user_data["shards"] += reward
        result_msg = f"🎉 Victory! Your {player_monster['emoji']} **{player_monster['name']}** won!\n+{reward}💎 shards! UwU"
        if not is_bot_battle and opponent:
            opp_data = get_user_data(opponent.id)
            opp_data["battles_lost"] += 1
    else:
        user_data["battles_lost"] += 1
        result_msg = f"💔 Oh no~ Your {player_monster['emoji']} **{player_monster['name']}** lost... Better luck next time! 😢"
        if not is_bot_battle and opponent:
            opp_data = get_user_data(opponent.id)
            opp_data["battles_won"] += 1
            opp_data["shards"] += 150
    
    save_data(data)
    
    advantage_text = ""
    if player_advantage:
        advantage_text = f"\n⚡ Type advantage: {player_monster['element']} > {opp_monster['element']}"
    elif opp_advantage:
        advantage_text = f"\n⚡ Type disadvantage: {opp_monster['element']} > {player_monster['element']}"
    
    battle_embed = discord.Embed(
        title="⚔️ Battle Arena! ⚔️",
        description=f"{ctx.author.mention}'s {player_monster['emoji']} **{player_monster['name']}** VS {opp_mention}'s {opp_monster['emoji']} **{opp_monster['name']}**{advantage_text}",
        color=discord.Color.gold()
    )
    
    battle_embed.add_field(
        name=f"{ctx.author.name}'s Monster",
        value=f"{player_monster['emoji']} **{player_monster['name']}**\nHP: {player_monster['hp']} | ATK: {player_monster['attack']}\nElement: {player_monster['element']}",
        inline=True
    )
    
    battle_embed.add_field(
        name=f"{opp_name}'s Monster",
        value=f"{opp_monster['emoji']} **{opp_monster['name']}**\nHP: {opp_monster['hp']} | ATK: {opp_monster['attack']}\nElement: {opp_monster['element']}",
        inline=True
    )
    
    battle_embed.add_field(
        name="Battle Result",
        value=result_msg,
        inline=False
    )
    
    await ctx.send(embed=battle_embed)

@bot.command()
async def quiz(ctx):
    user_data = get_user_data(ctx.author.id)
    
    # Check cooldown
    if user_data["quiz_cooldown"]:
        last = datetime.fromisoformat(user_data["quiz_cooldown"])
        if datetime.now() - last < timedelta(minutes=5):
            remaining = 300 - int((datetime.now() - last).total_seconds())
            await ctx.send(f"Nyaa~ Please wait {remaining} seconds before the next quiz! 📚")
            return
    
    question = random.choice(ANIME_QUIZ)
    
    await ctx.send(f"📺 **Anime Quiz Time!** 📺\n{question['question']}\n\nYou have 15 seconds to answer! UwU")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        
        if msg.content.lower().strip() in question["answer"].lower():
            user_data["shards"] += question["reward"]
            user_data["quiz_cooldown"] = datetime.now().isoformat()
            save_data(data)
            await ctx.send(f"✨ Correct! You earned {question['reward']}💎! Amazing~ 🎉\nYou now have {user_data['shards']}💎")
        else:
            await ctx.send(f"Oh no~ That's not quite right! The answer was: **{question['answer']}** 😅")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up~ The answer was: **{question['answer']}** ⏰")

@bot.command()
async def profile(ctx, member: discord.Member = None):
    target_member = member or ctx.author
    user_data = get_user_data(target_member.id)
    await check_hunger(target_member.id)
    
    embed = discord.Embed(
        title=f"🐾 {target_member.name}'s Astramon Profile",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="💎 Shards", value=str(user_data["shards"]), inline=True)
    embed.add_field(name="⚔️ Battles Won", value=str(user_data["battles_won"]), inline=True)
    embed.add_field(name="💔 Battles Lost", value=str(user_data["battles_lost"]), inline=True)
    
    if user_data["monsters"]:
        monsters_list = []
        for m in user_data["monsters"][:10]:  # Show up to 10
            hunger_bar = "🟢" if m.get("hunger", 0) < 30 else "🟡" if m.get("hunger", 0) < 70 else "🔴"
            level_text = f"Lv.{m.get('level', 1)}" if m.get('level', 1) > 1 else ""
            monsters_list.append(f"{m['emoji']} **{m['name']}** {level_text} ({m['element']}) {hunger_bar}")
        embed.add_field(
            name=f"🌟 Monsters ({len(user_data['monsters'])} total)",
            value="\n".join(monsters_list) if monsters_list else "None yet~",
            inline=False
        )
    else:
        embed.add_field(name="🌟 Monsters", value="No monsters yet! Use 'astramon catch' to get started~ 🐾", inline=False)
    
    embed.set_footer(text="Legend: 🟢 Fed | 🟡 Hungry | 🔴 Starving!")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🐾 Astramon Commands - Your Monster Adventure Guide! 🐾",
        description="Collect, battle, and raise elemental monsters! UwU",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="astramon catch",
        value="✨ Catch a random wild monster! (30s cooldown)",
        inline=False
    )
    
    embed.add_field(
        name="astramon feed <monster>",
        value="🍖 Feed your monster to keep it happy (costs 50💎)",
        inline=False
    )
    
    embed.add_field(
        name="astramon train <monster>",
        value="💪 Train your monster to increase level & attack (costs 100💎)",
        inline=False
    )
    
    embed.add_field(
        name="astramon shop",
        value="🏪 View the food shop",
        inline=False
    )
    
    embed.add_field(
        name="astramon evolve <monster>",
        value="🌟 Evolve your monster into a stronger form (costs 500💎)",
        inline=False
    )
    
    embed.add_field(
        name="astramon battle [@user]",
        value="⚔️ Battle another user or the bot!",
        inline=False
    )
    
    embed.add_field(
        name="astramon quiz",
        value="📺 Answer anime trivia for shard rewards! (5min cooldown)",
        inline=False
    )
    
    embed.add_field(
        name="astramon profile [@user]",
        value="👤 View your or someone's monster collection",
        inline=False
    )
    
    embed.add_field(
        name="astramon help",
        value="❓ Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="💎 Elements",
        value="🔥 Fire > 🌪️ Wind > 🌱 Earth > ⚡ Lightning > 💧 Water > 🔥 Fire",
        inline=False
    )
    
    embed.set_footer(text="Nyaa~ Have fun collecting monsters! Remember to feed them regularly! 💕")
    await ctx.send(embed=embed)

# Flask keep-alive web server (for 24/7 uptime)
app = Flask(__name__)

@app.route("/")
def home():
    return "Astramon bot is running 24/7!"

def run_web_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please add your Discord bot token to Replit Secrets.")
    else:
        # Start the Flask web server in a separate thread
        web_thread = Thread(target=run_web_server)
        web_thread.daemon = True
        web_thread.start()
        print("✅ Keep-alive server running on port 5000!")
        
        # Run the Discord bot (this blocks until the bot stops)
        bot.run(token)
