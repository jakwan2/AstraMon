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
    "Basic Meat": {"emoji": "🍖", "price": 50, "hunger_restore": 30, "type": "food"},
    "Sweet Cake": {"emoji": "🍰", "price": 100, "hunger_restore": 60, "type": "food"},
    "Ramen Bowl": {"emoji": "🍜", "price": 150, "hunger_restore": 100, "type": "food"},
    "Pizza Slice": {"emoji": "🍕", "price": 200, "hunger_restore": 150, "type": "food"},
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
            "team": [],
            "inventory": {}
        }
        save_data(data)
    else:
        if "team" not in data[user_id]:
            data[user_id]["team"] = []
        if "inventory" not in data[user_id]:
            data[user_id]["inventory"] = {}
    return data[user_id]

# Helper function to find monster by name with stacking support
def find_monster_stack(user_data, monster_name):
    for monster in user_data["monsters"]:
        if monster["name"].lower() == monster_name.lower():
            return monster
    return None

# Helper function to add monster with stacking
def add_monster_to_collection(user_data, monster):
    existing = find_monster_stack(user_data, monster["name"])
    if existing:
        existing["count"] = existing.get("count", 1) + 1
        if "last_fed" not in existing:
            existing["last_fed"] = datetime.now().isoformat()
            existing["hunger"] = 0
    else:
        monster["count"] = 1
        monster["last_fed"] = datetime.now().isoformat()
        monster["hunger"] = 0
        monster["alert_sent"] = False
        if "level" not in monster:
            monster["level"] = 1
        user_data["monsters"].append(monster)

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
                    count_text = f" (x{monster.get('count', 1)})" if monster.get('count', 1) > 1 else ""
                    await user.send(f"⚠️ Your {monster['emoji']} {monster['name']}{count_text} is starving! Feed it before it fades away… 💔")
                    monster["alert_sent"] = True
                except:
                    pass
            
            if monster["hunger"] >= 100:
                count = monster.get("count", 1)
                if count > 1:
                    monster["count"] = count - 1
                    monster["last_fed"] = now.isoformat()
                    monster["hunger"] = 0
                    monster["alert_sent"] = False
                    try:
                        user = await bot.fetch_user(int(user_id))
                        await user.send(f"💔 One of your {monster['emoji']} {monster['name']} has faded away from starvation... You still have x{monster['count']} remaining. 😢")
                    except:
                        pass
                else:
                    monsters_to_remove.append(monster)
                    user_data["team"] = [m for m in user_data["team"] if m != monster["name"]]
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
    
    if user_data["last_catch"]:
        last = datetime.fromisoformat(user_data["last_catch"])
        if datetime.now() - last < timedelta(seconds=30):
            await ctx.send(f"Nyaa~ Please wait a bit before catching again! 😸")
            return
    
    rand = random.random()
    if rand < 0.05:
        rarity = "legendary"
    elif rand < 0.25:
        rarity = "rare"
    else:
        rarity = "common"
    
    monster = random.choice(MONSTERS[rarity]).copy()
    monster["rarity"] = rarity
    
    add_monster_to_collection(user_data, monster)
    user_data["shards"] += 50
    user_data["last_catch"] = datetime.now().isoformat()
    save_data(data)
    
    element_display = monster['element'].replace("|", " & ")
    existing = find_monster_stack(user_data, monster["name"])
    count = existing.get("count", 1)
    
    await ctx.send(
        f"✨ Nyaa~ You caught a wild {monster['emoji']} **{monster['name']}**! "
        f"({element_display} type)\n"
        f"You now have **x{count}** of this monster! 💫\n"
        f"You earned 50💎! Type 'astramon profile' to check your collection! UwU"
    )

@bot.command()
async def feed(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to feed! Example: `astramon feed Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    await check_hunger(ctx.author.id)
    
    monster = find_monster_stack(user_data, monster_name)
    
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
    
    count_text = f" (x{monster.get('count', 1)})" if monster.get('count', 1) > 1 else ""
    await ctx.send(
        f"Yummy~ 🍖 Your {monster['emoji']} **{monster['name']}**{count_text} is now full and happy! "
        f"(-{cost}💎) Remaining: {user_data['shards']}💎 💕"
    )

@bot.command()
async def train(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to train! Example: `astramon train Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    monster = find_monster_stack(user_data, monster_name)
    
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
    
    count_text = f" (x{monster.get('count', 1)})" if monster.get('count', 1) > 1 else ""
    await ctx.send(
        f"✨ Training complete! Your {monster['emoji']} **{monster['name']}**{count_text} leveled up!\n"
        f"Level: **{monster['level']}** | ATK: **{monster['attack']}** (+2) 💪\n"
        f"(-{cost}💎) Remaining: {user_data['shards']}💎 UwU~"
    )

@bot.command()
async def shop(ctx):
    user_data = get_user_data(ctx.author.id)
    embed = discord.Embed(
        title="🏪 Astramon Shop - Feed your monsters!",
        description=f"Buy items with your shards 💎\nYour balance: **{user_data['shards']}💎**",
        color=discord.Color.purple()
    )
    
    for item_name, info in SHOP_ITEMS.items():
        embed.add_field(
            name=f"{info['emoji']} {item_name}",
            value=f"💰 Price: **{info['price']}💎**\n🍴 Hunger restore: **{info['hunger_restore']}%**",
            inline=True
        )
    
    embed.set_footer(text="Use 'astramon buy <item>' to purchase items!")
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, *, item_name: str = ""):
    if not item_name:
        await ctx.send("UwU, please specify what to buy! Example: `astramon buy Basic Meat`")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    item = None
    item_key = None
    for key, value in SHOP_ITEMS.items():
        if key.lower() == item_name.lower():
            item = value
            item_key = key
            break
    
    if not item:
        await ctx.send(f"Nyaa~ We don't have '{item_name}' in our shop! Use 'astramon shop' to see what's available~ 😿")
        return
    
    if user_data["shards"] < item["price"]:
        await ctx.send(f"Oh no~ You need {item['price']}💎 but only have {user_data['shards']}💎! 😢")
        return
    
    user_data["shards"] -= item["price"]
    
    if item_key not in user_data["inventory"]:
        user_data["inventory"][item_key] = 0
    user_data["inventory"][item_key] += 1
    
    save_data(data)
    
    await ctx.send(
        f"✨ Purchase successful! You bought {item['emoji']} **{item_key}**!\n"
        f"(-{item['price']}💎) Remaining: **{user_data['shards']}💎**\n"
        f"Use 'astramon inventory' to see your items! UwU~"
    )

@bot.command()
async def inventory(ctx):
    user_data = get_user_data(ctx.author.id)
    
    embed = discord.Embed(
        title=f"🎒 {ctx.author.name}'s Inventory",
        description=f"Your items and supplies! 💫",
        color=discord.Color.green()
    )
    
    if not user_data["inventory"] or all(count == 0 for count in user_data["inventory"].values()):
        embed.add_field(
            name="📦 Items",
            value="Empty~ Buy items from the shop! UwU",
            inline=False
        )
    else:
        items_list = []
        for item_name, count in user_data["inventory"].items():
            if count > 0:
                item_info = SHOP_ITEMS.get(item_name, {})
                emoji = item_info.get("emoji", "📦")
                items_list.append(f"{emoji} **{item_name}** x{count}")
        
        embed.add_field(
            name="📦 Items",
            value="\n".join(items_list) if items_list else "Empty~",
            inline=False
        )
    
    embed.set_footer(text="Use items with commands like 'astramon use <item> <monster>'")
    await ctx.send(embed=embed)

@bot.command()
async def sell(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to sell! Example: `astramon sell Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    monster = find_monster_stack(user_data, monster_name)
    
    if not monster:
        await ctx.send(f"Nyaa~ You don't have a {monster_name} in your collection! 😿")
        return
    
    rarity = monster.get("rarity", "common")
    sell_values = {"common": 100, "rare": 300, "legendary": 800}
    sell_price = sell_values.get(rarity, 100)
    
    level_bonus = (monster.get("level", 1) - 1) * 20
    total_price = sell_price + level_bonus
    
    count = monster.get("count", 1)
    if count > 1:
        monster["count"] = count - 1
        user_data["shards"] += total_price
        
        team_indices_to_remove = []
        for i, team_monster_name in enumerate(user_data["team"]):
            if team_monster_name.lower() == monster_name.lower():
                team_indices_to_remove.append(i)
                break
        
        for i in reversed(team_indices_to_remove):
            user_data["team"].pop(i)
        
        save_data(data)
        await ctx.send(
            f"💰 Sold one {monster['emoji']} **{monster['name']}** for **{total_price}💎**!\n"
            f"You still have **x{monster['count']}** remaining! 💫\n"
            f"Your balance: **{user_data['shards']}💎** UwU~"
        )
    else:
        user_data["monsters"].remove(monster)
        user_data["shards"] += total_price
        
        user_data["team"] = [m for m in user_data["team"] if m.lower() != monster_name.lower()]
        
        save_data(data)
        await ctx.send(
            f"💰 Sold {monster['emoji']} **{monster['name']}** for **{total_price}💎**!\n"
            f"Goodbye, {monster['name']}... 😢\n"
            f"Your balance: **{user_data['shards']}💎** UwU~"
        )

@bot.command()
async def team(ctx, action: str = "", *, monster_name: str = ""):
    user_data = get_user_data(ctx.author.id)
    
    if action == "":
        if not user_data["team"]:
            await ctx.send("Nyaa~ Your team is empty! Use 'astramon team add <monster>' to build your team! 🐾")
            return
        
        embed = discord.Embed(
            title=f"⚔️ {ctx.author.name}'s Battle Team",
            description="Your monsters ready for battle! 💪",
            color=discord.Color.gold()
        )
        
        team_list = []
        for i, team_monster_name in enumerate(user_data["team"], 1):
            monster = find_monster_stack(user_data, team_monster_name)
            if monster:
                element_display = monster['element'].replace("|", " & ")
                level_text = f"Lv.{monster.get('level', 1)}"
                hunger_bar = "🟢" if monster.get("hunger", 0) < 30 else "🟡" if monster.get("hunger", 0) < 70 else "🔴"
                team_list.append(
                    f"{i}. {monster['emoji']} **{monster['name']}** {level_text}\n"
                    f"   ⚡ {element_display} | 💖 HP: {monster['hp']} | ⚔️ ATK: {monster['attack']} {hunger_bar}"
                )
        
        embed.add_field(
            name=f"🌟 Team ({len(user_data['team'])}/6)",
            value="\n".join(team_list) if team_list else "No monsters in team!",
            inline=False
        )
        
        embed.set_footer(text="Legend: 🟢 Fed | 🟡 Hungry | 🔴 Starving")
        await ctx.send(embed=embed)
        
    elif action.lower() == "add":
        if not monster_name:
            await ctx.send("UwU, please specify which monster to add! Example: `astramon team add Fire Pup`")
            return
        
        if len(user_data["team"]) >= 6:
            await ctx.send("Nyaa~ Your team is full! Remove a monster first with 'astramon team remove <monster>' 😸")
            return
        
        monster = find_monster_stack(user_data, monster_name)
        
        if not monster:
            await ctx.send(f"Nyaa~ You don't have a {monster_name} in your collection! 😿")
            return
        
        if monster["name"] in user_data["team"]:
            await ctx.send(f"This {monster['emoji']} **{monster['name']}** is already in your team! UwU")
            return
        
        user_data["team"].append(monster["name"])
        save_data(data)
        
        await ctx.send(
            f"✨ Added {monster['emoji']} **{monster['name']}** to your team! "
            f"({len(user_data['team'])}/6) 💪"
        )
        
    elif action.lower() == "remove":
        if not monster_name:
            await ctx.send("UwU, please specify which monster to remove! Example: `astramon team remove Fire Pup`")
            return
        
        found = False
        for team_monster_name in user_data["team"]:
            if team_monster_name.lower() == monster_name.lower():
                user_data["team"].remove(team_monster_name)
                found = True
                break
        
        if found:
            save_data(data)
            await ctx.send(f"Removed **{monster_name}** from your team! 😸")
        else:
            await ctx.send(f"Nyaa~ **{monster_name}** is not in your team! 😿")
            
    elif action.lower() == "clear":
        user_data["team"] = []
        save_data(data)
        await ctx.send("Your team has been cleared! Time to build a new one~ 🐾")
        
    else:
        await ctx.send(
            "UwU, use these team commands:\n"
            "• `astramon team` - View your team\n"
            "• `astramon team add <monster>` - Add to team\n"
            "• `astramon team remove <monster>` - Remove from team\n"
            "• `astramon team clear` - Clear entire team"
        )

@bot.command()
async def teamstatus(ctx):
    user_data = get_user_data(ctx.author.id)
    await check_hunger(ctx.author.id)
    
    if not user_data["team"]:
        await ctx.send("Nyaa~ Your team is empty! Use 'astramon team add <monster>' to build your team! 🐾")
        return
    
    embed = discord.Embed(
        title=f"📊 {ctx.author.name}'s Team Status",
        description="Detailed status of your battle team! 💫",
        color=discord.Color.blue()
    )
    
    for i, team_monster_name in enumerate(user_data["team"], 1):
        monster = find_monster_stack(user_data, team_monster_name)
        if monster:
            hunger = monster.get("hunger", 0)
            hunger_bar = "🟢 Fed" if hunger < 30 else "🟡 Hungry" if hunger < 70 else "🔴 STARVING"
            
            element_display = monster['element'].replace("|", " & ")
            level = monster.get('level', 1)
            
            last_fed = monster.get("last_fed")
            if last_fed:
                fed_time = datetime.fromisoformat(last_fed)
                time_diff = datetime.now() - fed_time
                hours = int(time_diff.total_seconds() / 3600)
                time_text = f"{hours}h ago" if hours > 0 else "Just now"
            else:
                time_text = "Never"
            
            status_text = (
                f"⚡ Element: **{element_display}**\n"
                f"📊 Level: **{level}** | HP: **{monster['hp']}** | ATK: **{monster['attack']}**\n"
                f"🍖 Hunger: **{hunger}%** {hunger_bar}\n"
                f"🕒 Last fed: {time_text}"
            )
            
            if hunger >= 70:
                status_text += f"\n⚠️ Feed soon!"
            
            embed.add_field(
                name=f"{i}. {monster['emoji']} {monster['name']}",
                value=status_text,
                inline=False
            )
    
    embed.set_footer(text="Use 'astramon feed <monster>' to restore hunger!")
    await ctx.send(embed=embed)

@bot.command()
async def evolve(ctx, *, monster_name: str = ""):
    if not monster_name:
        await ctx.send("UwU, please specify which monster to evolve! Example: `astramon evolve Fire Pup`")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    monster = find_monster_stack(user_data, monster_name)
    
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
    
    evolved = None
    for monsters_list in MONSTERS.values():
        for m in monsters_list:
            if m["name"] == evolution["evolves_to"]:
                evolved = m.copy()
                break
        if evolved:
            break
    
    if evolved:
        old_name = monster["name"]
        evolved["last_fed"] = monster.get("last_fed", datetime.now().isoformat())
        evolved["hunger"] = monster.get("hunger", 0)
        evolved["alert_sent"] = monster.get("alert_sent", False)
        evolved["rarity"] = "rare"
        evolved["level"] = monster.get("level", 1)
        evolved["count"] = monster.get("count", 1)
        
        user_data["monsters"].remove(monster)
        user_data["monsters"].append(evolved)
        
        for i, team_monster_name in enumerate(user_data["team"]):
            if team_monster_name == old_name:
                user_data["team"][i] = evolved["name"]
        
        user_data["shards"] -= cost
        save_data(data)
        
        element_display = evolved['element'].replace("|", " & ")
        await ctx.send(
            f"🌟✨ **EVOLUTION COMPLETE!** ✨🌟\n"
            f"Your {monster['emoji']} **{old_name}** evolved into "
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
    
    if user_data["team"]:
        player_monster_name = random.choice(user_data["team"])
        player_monster = find_monster_stack(user_data, player_monster_name)
        if not player_monster:
            player_monster = random.choice(user_data["monsters"])
    else:
        player_monster = random.choice(user_data["monsters"])
    
    if opponent and opponent.id != ctx.author.id:
        opp_data = get_user_data(opponent.id)
        if not opp_data["monsters"]:
            await ctx.send(f"Nyaa~ {opponent.name} doesn't have any monsters yet! 😿")
            return
        
        if opp_data["team"]:
            opp_monster_name = random.choice(opp_data["team"])
            opp_monster = find_monster_stack(opp_data, opp_monster_name)
            if not opp_monster:
                opp_monster = random.choice(opp_data["monsters"])
        else:
            opp_monster = random.choice(opp_data["monsters"])
        
        is_bot_battle = False
        opp_name = opponent.name
        opp_mention = opponent.mention
    else:
        opp_monster = random.choice(random.choice(list(MONSTERS.values()))).copy()
        is_bot_battle = True
        opp_name = "Astramon Bot"
        opp_mention = "**Astramon Bot**"
    
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
    
    round_num = 1
    
    while player_hp > 0 and opp_hp > 0:
        opp_hp -= player_dmg
        if opp_hp <= 0:
            break
        player_hp -= opp_dmg
        round_num += 1
        if round_num > 10:
            break
    
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
    target_member = member if member else ctx.author
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
        for m in user_data["monsters"][:10]:
            hunger_bar = "🟢" if m.get("hunger", 0) < 30 else "🟡" if m.get("hunger", 0) < 70 else "🔴"
            level_text = f"Lv.{m.get('level', 1)}" if m.get('level', 1) > 1 else ""
            count_text = f"x{m.get('count', 1)}" if m.get('count', 1) > 1 else ""
            in_team = "⭐" if m["name"] in user_data.get("team", []) else ""
            monsters_list.append(f"{m['emoji']} **{m['name']}** {level_text} {count_text} ({m['element']}) {hunger_bar} {in_team}")
        embed.add_field(
            name=f"🌟 Monsters ({len(user_data['monsters'])} types)",
            value="\n".join(monsters_list) if monsters_list else "None yet~",
            inline=False
        )
    else:
        embed.add_field(name="🌟 Monsters", value="No monsters yet! Use 'astramon catch' to get started~ 🐾", inline=False)
    
    embed.set_footer(text="Legend: 🟢 Fed | 🟡 Hungry | 🔴 Starving | ⭐ In Team")
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🐾 Astramon Commands - Your Monster Adventure Guide! 🐾",
        description="Collect, battle, and raise elemental monsters! UwU",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="🎯 Core Commands",
        value=(
            "`catch` - Catch a random wild monster (30s cooldown)\n"
            "`feed <monster>` - Feed your monster (50💎)\n"
            "`train <monster>` - Train to increase level & attack (100💎)\n"
            "`evolve <monster>` - Evolve to stronger form (500💎)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚔️ Team & Battle",
        value=(
            "`team` - View your battle team\n"
            "`team add <monster>` - Add monster to team\n"
            "`team remove <monster>` - Remove from team\n"
            "`teamstatus` - View team hunger & status\n"
            "`battle [@user]` - Battle another user or bot"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🏪 Shop & Items",
        value=(
            "`shop` - View the shop\n"
            "`buy <item>` - Purchase items\n"
            "`inventory` - View your items\n"
            "`sell <monster>` - Sell monster for shards"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 Info",
        value=(
            "`profile [@user]` - View monster collection\n"
            "`quiz` - Answer anime trivia (5min cooldown)\n"
            "`help` - Show this message"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💎 Elements",
        value="🔥 Fire > 🌪️ Wind > 🌱 Earth > ⚡ Lightning > 💧 Water > 🔥 Fire",
        inline=False
    )
    
    embed.set_footer(text="Nyaa~ Have fun collecting monsters! Remember to feed them regularly! 💕")
    await ctx.send(embed=embed)

app = Flask(__name__)

@app.route("/")
def home():
    return "Astramon bot is running 24/7!"

def run_web_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please add your Discord bot token to Replit Secrets.")
    else:
        web_thread = Thread(target=run_web_server)
        web_thread.daemon = True
        web_thread.start()
        print("✅ Keep-alive server running on port 5000!")
        
        bot.run(token)
