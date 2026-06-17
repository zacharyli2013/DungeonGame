import random
import time
import os

from constants import *

# =========================================
# CLASSES
# =========================================

class Player:
    """Represents the player character."""

    def __init__(self):
        self.max_hp = 10
        self.hp = 10
        self.gold = 0
        self.str = 2
        self.defense = 2
        self.weapon = "Training Sword"
        self.inventory = ["Health Potion"]
        self.floor = 1
        self.floor1_axe_taken = False
        self.has_mysterious_key = False

    @property
    def is_alive(self):
        return self.hp > 0

    def get_weapon_bonus(self):
        """Roll a random damage bonus from the current weapon."""
        w = WEAPONS[self.weapon]
        return random.randint(w["min_bonus"], w["max_bonus"])

    def add_to_inventory(self, item_name):
        """Try to add a consumable item to inventory. Returns True on success."""
        if item_name == "Mysterious Key":
            self.has_mysterious_key = True
            return True
        if len(self.inventory) < MAX_INVENTORY_SIZE:
            self.inventory.append(item_name)
            return True
        return False

    def use_item(self, index, enemy=None):
        """Use an item from inventory by index. Returns a result dict or None."""
        if index < 0 or index >= len(self.inventory):
            return None

        item_name = self.inventory.pop(index)
        item = ITEMS.get(item_name, {})

        if not item:
            return None

        if item["effect"] == "heal":
            heal_amount = int(self.max_hp * item["value"])
            self.hp = min(self.max_hp, self.hp + heal_amount)
            return {"type": "heal", "amount": heal_amount, "item": item_name}

        elif item["effect"] == "sleep":
            if enemy and random.random() < item["success_chance"]:
                return {"type": "sleep", "success": True, "actions": item["actions"], "item": item_name}
            else:
                return {"type": "sleep", "success": False, "item": item_name}

        elif item["effect"] == "grenade":
            if enemy and random.random() < item["success_chance"]:
                damage = max(1, int(enemy.hp * item["damage_pct"]))
                enemy.hp -= damage
                return {"type": "grenade", "success": True, "damage": damage, "target": "enemy", "item": item_name}
            else:
                damage = max(1, int(self.hp * item["damage_pct"]))
                self.hp -= damage
                return {"type": "grenade", "success": False, "damage": damage, "target": "player", "item": item_name}

        return None


class Enemy:
    """Represents an enemy in battle."""

    def __init__(self, data):
        self.name = data["name"]
        self.max_hp = data["hp"]
        self.hp = data["hp"]
        self.str = data["str"]
        self.defense = data["def"]
        self.gold_given = data["gold_given"]
        self.drop_chance = data.get("drop_chance", 0.2)
        self.is_boss = data.get("is_boss", False)

    @property
    def is_alive(self):
        return self.hp > 0

    def take_turn(self, player):
        """Enemy attacks the player. Returns damage dealt."""
        if self.is_boss and random.random() < 0.25:
            # Crushing Blow: double damage
            raw_damage = self.str * 2
            damage = max(1, raw_damage - player.defense)
            announce(f"\n💥 {self.name} uses CRUSHING BLOW! Double damage!")
            return damage

        damage = max(1, self.str - player.defense)
        return damage


# =========================================
# UTILITY FUNCTIONS
# =========================================

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def announce(text, delay=0.02):
    """Print text character by character for dramatic effect."""
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()


def print_header(title):
    """Print a centered header."""
    print("\n" + "=" * 54)
    print(f"{'★ ' + title + ' ★':^54}")
    print("=" * 54)


def print_divider():
    print("─" * 54)


def show_player_stats(player):
    """Display current player stats."""
    print()
    print_divider()
    print(f" ❤️  HP: {player.hp:>2}/{player.max_hp:<2}      💰 Gold: {player.gold}G")
    print(f" ⚔️  STR: {player.str:>2}          🛡️  DEF: {player.defense}")
    print(f" 🔪 Weapon: {player.weapon}")
    inv_str = ", ".join(player.inventory) if player.inventory else "(empty)"
    key_str = " [🔑 Mysterious Key]" if player.has_mysterious_key else ""
    print(f" 📦 Inventory ({len(player.inventory)}/{MAX_INVENTORY_SIZE}): {inv_str}{key_str}")
    print_divider()


def get_choice(options, prompt="\n>> Choose an option: "):
    """Display a numbered menu and return the 1-based user choice."""
    while True:
        print()
        for i, opt in enumerate(options, 1):
            print(f"   {i}. {opt}")
        try:
            raw = input(prompt).strip()
            n = int(raw)
            if 1 <= n <= len(options):
                return n
            print(f"   ❌ Enter a number between 1 and {len(options)}.")
        except ValueError:
            print("   ❌ Invalid input. Enter a number.")


def press_enter():
    """Wait for the player to press Enter."""
    input("\n   [Press Enter to continue...]")


# =========================================
# ENEMY GENERATION
# =========================================

def generate_enemy(floor_num, enemy_type="normal"):
    """Create an enemy appropriate for the given floor and type."""
    if enemy_type == "boss":
        data = dict(BOSS_DATA)
        data["is_boss"] = True
        return Enemy(data)

    if enemy_type == "elite":
        pool = ELITE_ENEMIES
        idx = min(floor_num // 3, len(pool) - 1)
    else:
        pool = NORMAL_ENEMIES
        idx = min(floor_num // 3, len(pool) - 1)

    data = dict(pool[idx])
    #bonus = floor_num * 2 if enemy_type == "elite" else floor_num
    bonus = 0
    data["hp"] += bonus
    data["max_hp"] = data["hp"]
    data["drop_chance"] = pool[idx]["drop_chance"]
    return Enemy(data)


# =========================================
# BATTLE SYSTEM
# =========================================

def battle(player, enemy, floor_label="Unknown"):
    """
    Run a turn-based battle between player and enemy.
    Returns True if player wins, False if player dies.
    """
    print_header(f"⚔️  BATTLE — {floor_label} ⚔️")
    announce(f"\nA wild {enemy.name} appears!")
    print(f"   HP: {enemy.hp}  |  STR: {enemy.str}  |  DEF: {enemy.defense}")
    if enemy.is_boss:
        print(f"   ⚠️  Boss Enemy — special ability: Crushing Blow (25% chance)")
    time.sleep(1)

    extra_actions = 0

    while player.is_alive and enemy.is_alive:
        print(f"\n{'─'*54}")
        print(f" ❤️  {player.hp}/{player.max_hp} HP         {enemy.name}: {max(0, enemy.hp)}/{enemy.max_hp} HP")
        print(f"{'─'*54}")

        if extra_actions > 0:
            print(f"\n   ⏰ Bonus action! ({extra_actions} remaining)")
            extra_actions -= 1

        actions = ["Attack", "Special", "Item"]
        choice = get_choice(actions, "   What will you do? ")

        if choice == 1:
            w_bonus = player.get_weapon_bonus()
            raw_damage = player.str + w_bonus
            damage = max(1, raw_damage - enemy.defense)
            enemy.hp -= damage
            announce(f"\n   ⚔️  You attack with your {player.weapon}!")
            print(f"      Weapon bonus: +{w_bonus}   STR: {player.str}")
            print(f"      Enemy DEF: {enemy.defense}")
            announce(f"      You deal {damage} damage! 💥")

        elif choice == 2:
            if random.random() < 0.5:
                raw_damage = player.str * 3
                damage = max(1, raw_damage - enemy.defense)
                enemy.hp -= damage
                announce(f"\n   💥 SPECIAL ATTACK! STR × 3 = {raw_damage}!")
                print(f"      Enemy DEF: {enemy.defense}")
                announce(f"      You deal {damage} damage!")
            else:
                announce("\n   ❌ Missed! Your special attack fails!")

        elif choice == 3:
            if not player.inventory:
                announce("\n   📦 Your inventory is empty!")
                continue

            print("\n   Select item to use:")
            for i, item in enumerate(player.inventory, 1):
                print(f"      {i}. {item}")
            print(f"      {len(player.inventory) + 1}. Cancel")

            try:
                ic = int(input("\n   >> Choose: ").strip())
                if ic == len(player.inventory) + 1:
                    continue
                if 1 <= ic <= len(player.inventory):
                    result = player.use_item(ic - 1, enemy)
                    if result:
                        if result["type"] == "heal":
                            announce(f"\n   💚 Used {result['item']}! Restored {result['amount']} HP!")
                        elif result["type"] == "sleep":
                            if result["success"]:
                                announce(f"\n   💤 {enemy.name} fell asleep! You get {result['actions']} extra actions!")
                                extra_actions += result["actions"]
                            else:
                                announce(f"\n   💤 {enemy.name} resists! Nothing happens.")
                        elif result["type"] == "grenade":
                            if result["success"]:
                                announce(f"\n   💥 Grenade hits {enemy.name} for {result['damage']} damage!")
                            else:
                                announce(f"\n   💥 Grenade backfires! You take {result['damage']} damage!")
            except ValueError:
                print("   ❌ Invalid input.")

        if not enemy.is_alive:
            break

        if extra_actions > 0:
            continue

        announce(f"\n   🔄 {enemy.name}'s turn!")
        time.sleep(0.5)
        dmg = enemy.take_turn(player)
        player.hp -= dmg
        announce(f"   💢 {enemy.name} deals {dmg} damage!")
        time.sleep(0.5)

    if player.is_alive:
        announce(f"\n   🎉 Victory! You defeated the {enemy.name}!")
        return True
    else:
        announce(f"\n   💀 You were slain by the {enemy.name}...")
        return False


# =========================================
# FLOOR EVENTS
# =========================================

def event_rest_site(player):
    """Rest site: sleep, train, or perform a ritual."""
    print_header("🏕️  REST SITE 🏕️")
    announce("\nYou find a safe place to rest. What will you do?")
    print()
    show_player_stats(player)

    options = [
        "Sleep — Restore HP to full",
        "Train — Gain +1 STR or +1 DEF (no healing)",
    ]

    if player.floor == 3:
        options.append("Ritual — Perform an unknown ritual (may require blood sacrifice)")

    choice = get_choice(options)

    if choice == 1:
        player.hp = player.max_hp
        announce("\n   💤 You sleep soundly and fully restore your HP!")
    elif choice == 2:
        stat_opts = ["STR", "DEF"]
        sc = get_choice(stat_opts, "   Train which stat? ")
        if sc == 1:
            player.str += 1
            announce("\n   💪 You train relentlessly! STR +1!")
        else:
            player.defense += 1
            announce("\n   🛡️  You train your guard! DEF +1!")
    else:
        # Ritual
        announce("\n   🔮 You kneel before a strange altar and begin chanting...")
        time.sleep(1.5)
        announce("   The air grows cold. Shadows dance around you.")
        time.sleep(1)
        announce("   A spectral hand reaches out from the darkness...")
        time.sleep(0.5)
        announce("   It pierces your chest! (-3 HP)")
        player.hp = max(1, player.hp - 3)
        time.sleep(1)
        announce("   A Mysterious Key materializes in your hand!")
        player.has_mysterious_key = True
        announce("   The key hums with ancient energy...")

    press_enter()


def event_locked_door(player, floor_num):
    """Handle the locked door event on floors 7 and 9."""
    print_header("🚪  LOCKED DOOR 🚪")

    if floor_num == 7:
        announce("\n   You find a heavy stone door inscribed with ancient runes.")
        time.sleep(1)
        announce("   You push with all your might, but it won't budge.")
        announce("   Perhaps you need something special to open it...")
        announce("\n   You'll have to take another path.")
        press_enter()
        return "stuck"  # Player didn't get through

    elif floor_num == 9:
        announce("\n   You find another ancient door — identical to the one on Floor 7.")
        time.sleep(1)

        if not player.has_mysterious_key:
            announce("   You try to force it open, but it won't budge.")
            announce("   Without something special, this door stays shut.")
            announce("\n   You'll have to take another path.")
            press_enter()
            return "stuck"
        else:
            announce("   The Mysterious Key in your pocket begins to glow!")
            time.sleep(1)
            print()
            opts = ["Use the Mysterious Key", "Leave the door alone"]
            sc = get_choice(opts, "   >> What will you do? ")

            if sc == 2:
                announce("\n   You decide not to risk it and turn away.")
                press_enter()
                return "stuck"

            announce("\n   🗝️  You insert the Mysterious Key into the lock...")
            time.sleep(1.5)
            announce("   The door rumbles and slowly grinds open!")
            time.sleep(1.5)
            announce("   A blinding light pours through the crack...")
            time.sleep(1)

            # Secret Guardian encounter
            return event_secret_guardian(player)


def event_secret_guardian(player):
    """The Secret Guardian encounter on floor 9."""
    clear_screen()
    print_header("👁️  THE SECRET GUARDIAN 👁️")

    announce("\n   You step through the door into a vast, shimmering chamber.")
    time.sleep(1.5)
    announce("   Floating in the center is a figure wreathed in golden light.")
    time.sleep(1.5)
    announce("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    announce('   SECRET GUARDIAN: "So... you found me."')
    time.sleep(1)
    announce('   SECRET GUARDIAN: "Few ever reach this place. Fewer still possess the key."')
    time.sleep(1.5)
    announce('   SECRET GUARDIAN: "I have watched your journey through the dungeon."')
    time.sleep(1)
    announce('   SECRET GUARDIAN: "Your struggles. Your victories. Your sacrifices."')
    time.sleep(1.5)
    announce('   SECRET GUARDIAN: "But tell me, adventurer... I must know."')
    time.sleep(1)
    announce("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    time.sleep(1)

    announce("\n   The Guardian leans in close, eyes burning with ancient fire.")
    time.sleep(1.5)
    announce("\n   They ask you a single question:")
    time.sleep(1)
    print()
    announce('   "What is more important — doing what is right for the world,')
    announce('    or escaping this dungeon for yourself?"')
    time.sleep(1)
    print()

    opts = [
        "Do what's right for the world",
        "Escape the dungeon — survival comes first"
    ]
    sc = get_choice(opts, "   >> Your answer: ")

    if sc == 1:
        announce("\n   The Guardian's stern expression softens into a warm smile.")
        time.sleep(1.5)
        announce('   SECRET GUARDIAN: "You have passed the trial. Your heart is pure."')
        time.sleep(2)
        announce('   SECRET GUARDIAN: "Take this blade. It was forged for one such as you."')
        time.sleep(1.5)
        announce("\n   🗡️  The Guardian hands you the legendary EXCALIBUR!")
        player.weapon = "Excalibur"
        announce("   ⚔️  Weapon upgraded to Excalibur! (+15 to +20 damage)")
        time.sleep(1.5)
        announce('\n   SECRET GUARDIAN: "Use it well. The Cave King awaits."')
        time.sleep(1)
        announce('   SECRET GUARDIAN: "I will be with you in spirit, adventurer. You will be protected."')
        time.sleep(1.5)
        announce("\n   The Guardian fades into the light, and you find yourself back in the dungeon.")
        time.sleep(1.5)
        announce("\n   You feel as if the Guardian charged you with full energy. Your HP is fully restored!")
        player.hp = player.max_hp
        time.sleep(1)
        announce("\n   You feel the power of the Guardian radiating inside you... (+4 DEF)")
        player.defense += 4
        time.sleep(1)
        announce("\n   You step forward, ready to face the final challenge...")
        announce("\n   ✅ Floor 9 complete — you are ready.")
        press_enter()
        return "passed"

    else:
        announce("\n   The Guardian's eyes narrow into cold slits.")
        time.sleep(1.5)
        announce('   SECRET GUARDIAN: "So be it."')
        time.sleep(1)
        announce('   SECRET GUARDIAN: "If you would abandon the world to save yourself...')
        time.sleep(1.5)
        announce('   SECRET GUARDIAN: "...then you are not worthy to escape."')
        time.sleep(1.5)
        announce("\n   The Guardian raises their hand, and a cold darkness engulfs you.")
        time.sleep(1.5)
        announce("\n   💀 You feel your life force drain away...")
        time.sleep(2)
        announce("\n   YOU DIED.")
        press_enter()
        return "dead"


def event_merchant(player, floor_num):
    """Merchant shop with per-floor stock."""
    if floor_num == 5:
        stock = MERCHANT_FLOOR_5
    elif floor_num == 8:
        stock = MERCHANT_FLOOR_8
    else:
        stock = MERCHANT_FLOOR_8

    print_header("🏪  MERCHANT 🏪")
    announce("\nA travelling merchant sets up shop before you.")
    print()
    show_player_stats(player)

    while True:
        print("\n   Items for sale:")
        print_divider()
        for i, (name, cost) in enumerate(stock, 1):
            if name in WEAPONS:
                owned = " (equipped)" if player.weapon == name else ""
                print(f"   {i}. {name:20s}  {cost:>3}G{owned}")
            else:
                print(f"   {i}. {name:20s}  {cost:>3}G")
        print(f"   {len(stock) + 1}. Leave shop")
        print_divider()

        try:
            c = int(input("\n   >> Buy which item? ").strip())
        except ValueError:
            print("   ❌ Invalid input.")
            continue

        if c == len(stock) + 1:
            announce("\n   👋 You leave the merchant.")
            break

        if 1 <= c <= len(stock):
            name, cost = stock[c - 1]

            if player.gold < cost:
                announce("\n   ❌ Not enough gold!")
                press_enter()
                continue

            if name in WEAPONS:
                player.weapon = name
                player.gold -= cost
                announce(f"\n   🔪 You purchased the {name}!")
            else:
                if not player.add_to_inventory(name):
                    announce(f"\n   ❌ Inventory full! Cannot carry {name}.")
                    press_enter()
                    continue
                player.gold -= cost
                announce(f"\n   📦 You bought {name}!")

            show_player_stats(player)
            press_enter()

    press_enter()


def grant_floor_rewards(player, is_elite=False, is_boss=False):
    """Grant gold, drops, and stat upgrade after a battle."""
    if is_boss:
        announce("\n   🏆 BOSS DEFEATED!")
        announce(f"   💰 Gained {BOSS_DATA['gold_given']} Gold!")
        player.gold += BOSS_DATA["gold_given"]
        if player.add_to_inventory("Golden Apple"):
            announce("   🍎 Bonus item: Golden Apple!")
        announce("\n   🎉 YOU ESCAPED THE DUNGEON!")
        return

    if is_elite:
        gold = random.randint(15, 25)
        announce("\n   🏆 ELITE VICTORY REWARDS!")
    else:
        gold = random.randint(5, 10)
        announce("\n   🏆 VICTORY REWARDS!")

    player.gold += gold
    announce(f"   💰 Gained {gold} Gold!")

    # Item drop
    drop_chance = 0.75 if is_elite else 0.20
    if random.random() < drop_chance:
        announce("\n   🎁 Item Drop!")
        drop_type = random.choice(POSSIBLE_DROPS)

        if drop_type == "Gold":
            extra = random.randint(5, 15)
            player.gold += extra
            announce(f"   💰 Found {extra} extra Gold!")
        elif drop_type == "Weapon Upgrade":
            available = [w for w in WEAPON_TIERS
                         if w not in (player.weapon,)]
            if available:
                upgrade = min(available, key=lambda w: WEAPON_TIERS.index(w))
                player.weapon = upgrade
                announce(f"   🔪 Weapon upgraded to {upgrade}!")
            else:
                extra = random.randint(10, 20)
                player.gold += extra
                announce(f"   💰 No better weapon available. Found {extra} Gold instead!")
        elif drop_type in ITEMS:
            if player.add_to_inventory(drop_type):
                announce(f"   📦 Found {drop_type}!")
            else:
                announce(f"   ❌ Found {drop_type} but inventory is full!")

    # Stat upgrade
    if is_elite:
        announce("\n   📈 Elite victory! Choose TWO stat upgrades:")
        elite_opts = ["+4 Max HP", "+2 STR", "+2 DEF"]
        elite_vals = [(4, "max_hp"), (2, "str"), (2, "defense")]

        for pick_num in [1, 2]:
            announce(f"\n   Upgrade {pick_num} of 2:")
            sc = get_choice(elite_opts, "   >> Upgrade: ")
            amount, stat = elite_vals[sc - 1]

            if stat == "max_hp":
                player.max_hp += amount
                player.hp += amount
                announce(f"   ❤️  Max HP increased by {amount}!")
            elif stat == "str":
                player.str += amount
                announce(f"   💪 STR increased by {amount}!")
            else:
                player.defense += amount
                announce(f"   🛡️  DEF increased by {amount}!")
    else:
        announce("\n   📈 Choose a stat upgrade:")
        opts = ["+2 Max HP", "+1 STR", "+1 DEF"]
        vals = [(2, "max_hp"), (1, "str"), (1, "defense")]

        sc = get_choice(opts, "   >> Upgrade: ")
        amount, stat = vals[sc - 1]

        if stat == "max_hp":
            player.max_hp += amount
            player.hp += amount
            announce(f"\n   ❤️  Max HP increased by {amount}!")
        elif stat == "str":
            player.str += amount
            announce(f"\n   💪 STR increased by {amount}!")
        else:
            player.defense += amount
            announce(f"\n   🛡️  DEF increased by {amount}!")

    press_enter()


# =========================================
# FLOOR PROCESSING
# =========================================

def process_floor(player):
    """Run the current floor events. Returns True to continue, False if player died."""
    floor_num = player.floor
    floor_data = FLOORS[floor_num - 1]

    clear_screen()
    print_header(f"📜 FLOOR {floor_num}")

    desc = floor_data.get("description", "")
    if desc:
        announce(f"\n   {desc}")
        time.sleep(1)

    # Floor 10: boss only
    if floor_num == 10:
        announce("\n   🏰 The Cave King looms before you...")
        time.sleep(1.5)
        enemy = generate_enemy(floor_num, "boss")
        victory = battle(player, enemy, f"Floor {floor_num}")
        if victory:
            grant_floor_rewards(player, is_boss=True)
            return True
        return False

    paths = floor_data["paths"]
    options = [PATH_LABELS[p] for p in paths]

    show_player_stats(player)
    announce("\n   A fork in the dungeon... choose your path:")
    choice = get_choice(options, "   >> Take path: ")

    selected = paths[choice - 1]
    announce(f"\n   ➡️  You venture toward the {PATH_LABELS[selected]}...")
    time.sleep(1)

    if selected == "rest":
        event_rest_site(player)

    elif selected == "merchant":
        event_merchant(player, floor_num)

    elif selected == "locked_door":
        result = event_locked_door(player, floor_num)
        if result == "dead":
            return False  # Player killed by guardian
        if result == "stuck":
            # On floor 7, they need to pick another path
            # Re-offer the path choices without the locked door
            if floor_num == 7:
                alt_paths = [p for p in paths if p != "locked_door"]
                alt_options = [PATH_LABELS[p] for p in alt_paths]
                announce("\n   You must choose a different path:")
                alt_choice = get_choice(alt_options, "   >> Take path: ")
                selected = alt_paths[alt_choice - 1]
                announce(f"\n   ➡️  You venture toward the {PATH_LABELS[selected]}...")
                time.sleep(1)

                if selected == "rest":
                    event_rest_site(player)
                elif selected == "merchant":
                    event_merchant(player, floor_num)
                elif selected in ("normal", "elite"):
                    is_elite = selected == "elite"
                    enemy = generate_enemy(floor_num, selected)
                    victory = battle(player, enemy, f"Floor {floor_num} — {PATH_LABELS[selected]}")
                    if victory:
                        grant_floor_rewards(player, is_elite=is_elite)
                    else:
                        return False
            # On floor 9 stuck, they can still do normal/elite
            elif floor_num == 9:
                alt_paths = [p for p in paths if p != "locked_door"]
                alt_options = [PATH_LABELS[p] for p in alt_paths]
                announce("\n   You must choose a different path:")
                alt_choice = get_choice(alt_options, "   >> Take path: ")
                selected = alt_paths[alt_choice - 1]
                announce(f"\n   ➡️  You venture toward the {PATH_LABELS[selected]}...")
                time.sleep(1)

                if selected in ("normal", "elite"):
                    is_elite = selected == "elite"
                    enemy = generate_enemy(floor_num, selected)
                    victory = battle(player, enemy, f"Floor {floor_num} — {PATH_LABELS[selected]}")
                    if victory:
                        grant_floor_rewards(player, is_elite=is_elite)
                    else:
                        return False
        # If passed, floor 9 is complete

    elif selected in ("normal", "elite"):
        is_elite = selected == "elite"
        enemy = generate_enemy(floor_num, selected)
        victory = battle(player, enemy, f"Floor {floor_num} — {PATH_LABELS[selected]}")
        if victory:
            grant_floor_rewards(player, is_elite=is_elite)
            if floor_num == 1 and not player.floor1_axe_taken:
                player.floor1_axe_taken = True
                announce("\n   🪓 You found a Sturdy Axe among the rat's belongings!")
                player.weapon = "Sturdy Axe"
                announce("   🔪 Weapon upgraded to Sturdy Axe!")
                press_enter()
        else:
            return False

    return True


# =========================================
# MAIN GAME LOOP
# =========================================

def show_title():
    """Display the title screen."""
    clear_screen()
    print()
    print("╔" + "═" * 52 + "╗")
    print("║" + " " * 52 + "║")
    print("║" + "   _____                            _   _           " + "║")
    print("║" + "  | ____|___  ___ __ _ _ __   ___  | |_| |__   ___  " + "║")
    print("║" + "  |  _| / __|/ __/ _` | '_ \ / _ \ | __| '_ \ / _ \ " + "║")
    print("║" + "  | |___\__ \ (_| (_| | |_) |  __/ | |_| | | |  __/ " + "║")
    print("║" + "  |_____|___/\___\__,_| .__/ \___|  \__|_| |_|\___| " + "║")
    print("║" + "  |  _ \ _   _ _ __   |_|_  ___  ___  _ __          " + "║")
    print("║" + "  | | | | | | | '_ \ / _` |/ _ \/ _ \| '_ \         " + "║")
    print("║" + "  | |_| | |_| | | | | (_| |  __/ (_) | | | |        " + "║")
    print("║" + "  |____/ \__,_|_| |_|\__, |\___|\___/|_| |_|        " + "║")
    print("║" + "                     |___/                          " + "║")
    print("║" + "     ──  A Text-Based Dungeon Crawler  v1.0  ──     " + "║")
    print("║" + " " * 52 + "║")
    print("╚" + "═" * 52 + "╝")


def game_over_screen():
    """Display the game over screen."""
    clear_screen()
    print()
    print_header("💀  GAME OVER  💀")
    announce("\n   Your HP reached 0.")
    announce("\n   YOU DIED.")
    print()
    announce("   The dungeon claims another soul...")
    press_enter()


def victory_screen():
    """Display the victory screen."""
    clear_screen()
    print()
    print_header("🎉  VICTORY!  🎉")
    announce("\n   YOU ESCAPED THE DUNGEON!")
    print()
    announce("   You defeated the Cave King and emerged into the sunlight.")
    announce("   The kingdom celebrates your return as a hero!")
    print()
    print("   " + "✦" * 46)
    announce("   Your legend will be told for generations.")
    print("   " + "✦" * 46)
    press_enter()


def main():
    """Main game loop."""
    while True:
        show_title()
        print("\n   [1] New Game")
        print("   [2] Quit")

        try:
            raw_input = input("\n   >> ").strip()
        except EOFError:
            continue

        if raw_input == "2":
            announce("\n   Farewell, adventurer!")
            break

        # Check for admin cheat commands
        if raw_input.startswith("1 /admin cheat --hp "):
            try:
                hp_val = int(raw_input.split("--hp ")[1].strip())
                player = Player()
                player.max_hp = hp_val
                player.hp = hp_val
                announce(f"\n   ⚡ ADMIN CHEAT: HP set to {hp_val}!")
                time.sleep(1)
            except (ValueError, IndexError):
                announce("\n   ❌ Invalid cheat syntax. Use: 1 /admin cheat --hp 1000")
                continue

        elif raw_input.startswith("1 /admin cheat --g "):
            try:
                gold_val = int(raw_input.split("--g ")[1].strip())
                player = Player()
                player.gold = gold_val
                announce(f"\n   ⚡ ADMIN CHEAT: Gold set to {gold_val}G!")
                time.sleep(1)
            except (ValueError, IndexError):
                announce("\n   ❌ Invalid cheat syntax. Use: 1 /admin cheat --g 1000")
                continue

        elif raw_input == "1":
            player = Player()
        else:
            continue
        game_won = False

        for floor_num in range(1, 11):
            player.floor = floor_num
            alive = process_floor(player)
            if not alive:
                game_won = False
                break
            if floor_num == 10:
                game_won = True

        if game_won:
            victory_screen()
        else:
            game_over_screen()


# =========================================
# ENTRY POINT
# =========================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        announce("\n\n   Game interrupted. Farewell!")