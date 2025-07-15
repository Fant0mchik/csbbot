import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random

TOKEN = ""
DATA_FILE = "points.json"
BLACKLISTED_ROLES = ["🚫Чорний список", "😈 4/5", "😈 5/5", "😈 3/5"]
ALLOWED_ROLES = ["Власник сервера", "Менеджер Персоналу", "😈 1,534,847/5"]  # Ролі, яким дозволено змінювати бали

ROLE_PERMISSIONS = {
	"адмінзвіт": ["Адміністрація", "Діскорд менеджер", "Власник сервера","Адмін+", "😈 1,534,847/5"],
	"модерзвіт": ["Модерація", "Діскорд менеджер", "Власник сервера","😈 1,534,847/5"],
	"дівентерзвіт": ["Діскорд івентер", "Діскорд менеджер", "Власник сервера","😈 1,534,847/5"],
	"івентбал": ["Івентери", "Діскорд менеджер", "Власник сервера","Адмін+", "😈 1,534,847/5"]
}

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


def load_data():
	if os.path.exists(DATA_FILE):
		with open(DATA_FILE, "r") as f:
			return json.load(f)
	return {}

def save_data(data):
	with open(DATA_FILE, "w") as f:
		json.dump(data, f)

@bot.event
async def on_ready():
	await tree.sync()
	print(f"✅ Бот запущено як {bot.user}")

# ----------------- Команда /моїбали -----------------
@tree.command(name="моїбали", description="Показує твої бали")
async def моїбали(interaction: discord.Interaction):
	data = load_data()
	uid = str(interaction.user.id)
	бали = data.get(uid, 0)
	embed = discord.Embed(title="Твої бали", description=f"У тебе **{бали}** бал(ів)", color=discord.Color.blue())
	await interaction.response.send_message(embed=embed, ephemeral=True)

# ----------------- Команда /лідерборд -----------------
@tree.command(name="лідерборд", description="Показати топ 10 користувачів за балами")
async def лідерборд(interaction: discord.Interaction):
	data = load_data()

	if not data:
		await interaction.response.send_message("❗ Наразі немає даних про бали.", ephemeral=True)
		return

	# Сортуємо за балами (спадаючий порядок)
	sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

	# Створюємо Embed
	embed = discord.Embed(
		title="🏆 Топ користувачів за балами",
		description="Ось найактивніші учасники сервера!",
		color=discord.Color.gold()
	)

	for index, (user_id, points) in enumerate(sorted_data[:10], start=1):
		mention = f"<@{user_id}>"
		embed.add_field(name=f"#{index}", value=f"{mention} — **{points} балів**", inline=False)

	await interaction.response.send_message(embed=embed)


# ----------------- Команда /видатибали -----------------
@tree.command(name="видатибали", description="Видати комусь бали вручну")
@app_commands.describe(користувач="Кому видати бали", кількість="Скільки балів")
async def видатибали(interaction: discord.Interaction, користувач: discord.Member, кількість: int):
	roles = [role.name for role in interaction.user.roles]
	if not any(role in ALLOWED_ROLES for role in roles):
		await interaction.response.send_message("⛔ У вас немає дозволу використовувати цю команду.", ephemeral=True)
		return

	data = load_data()
	uid = str(користувач.id)
	data[uid] = data.get(uid, 0) + кількість
	save_data(data)

	await interaction.response.send_message(f"✅ Видано **{кількість}** бал(ів) для {користувач.mention}.", ephemeral=True)

# ----------------- Команда /знятибали -----------------
@tree.command(name="знятибали", description="Зняти певну кількість балів")
@app_commands.describe(користувач="З кого зняти бали", кількість="Скільки балів зняти")
async def знятибали(interaction: discord.Interaction, користувач: discord.Member, кількість: int):
	roles = [role.name for role in interaction.user.roles]
	if not any(role in ALLOWED_ROLES for role in roles):
		await interaction.response.send_message("⛔ У вас немає дозволу використовувати цю команду.", ephemeral=True)
		return

	data = load_data()
	uid = str(користувач.id)
	data[uid] = max(0, data.get(uid, 0) - кількість)
	save_data(data)

	await interaction.response.send_message(f"⚠️ Знято **{кількість}** бал(ів) з {користувач.mention}.", ephemeral=True)

# ----------------- Рольова перевірка для команд -----------------
def has_permission(interaction: discord.Interaction, command_name: str) -> bool:
	user_roles = [role.name for role in interaction.user.roles]
	allowed_roles = ROLE_PERMISSIONS.get(command_name, [])
	return any(role in allowed_roles for role in user_roles)


@tree.command(name="івентбал", description="Видати бали за івент")
@app_commands.describe(
    хост_чи_допомога="Роль у івенті: хост або допомога",
    тип_івенту="Назва івенту (легкий, середній, складний, мега)",
    посилання="Посилання на лог або івент"
)
@app_commands.choices(
    хост_чи_допомога=[
        app_commands.Choice(name="Хост", value="хост"),
        app_commands.Choice(name="Допомога", value="допомога"),
    ],
    тип_івенту=[
        app_commands.Choice(name="Легкий", value="легкий"),
        app_commands.Choice(name="Середній", value="середній"),
        app_commands.Choice(name="Складний", value="складний"),
        app_commands.Choice(name="Мега", value="мега"),
    ]
)
async def івентбал(
    interaction: discord.Interaction,
    хост_чи_допомога: str,
    тип_івенту: str,
    посилання: str
):
    подяки = [
        "Твоя активність дуже цінується ❤️",
        "Дякуємо за працю!",
        "Чудова робота!",
        "Ми пишаємось вами!",
        "Молодець! Завдяки тобі сервер живий!"
    ]

    if not has_permission(interaction, "івентбал"):
        await interaction.response.send_message("⛔ У вас немає дозволу використовувати цю команду.", ephemeral=True)
        return

    хост_чи_допомога = хост_чи_допомога.lower()
    тип_івенту = тип_івенту.lower()

    if хост_чи_допомога not in ["хост", "допомога"]:
        await interaction.response.send_message(
            "❗ Аргумент `хост/допомога` має бути або **хост**, або **допомога**.",
            ephemeral=True
        )
        return

    # Автоматичне визначення балів
    if хост_чи_допомога == "допомога":
        бали = 3 if "мега" in тип_івенту else 1
    elif хост_чи_допомога == "хост":
        if "мега" in тип_івенту:
            бали = 5
        elif "складний" in тип_івенту:
            бали = 3
        elif "легкий" in тип_івенту or "середній" in тип_івенту:
            бали = 1
        else:
            await interaction.response.send_message(
                "❗ Тип івенту не розпізнано. Використовуй: легкий, середній, складний, мега.",
                ephemeral=True
            )
            return

    # Збереження балів
    user = interaction.user
    data = load_data()
    uid = str(user.id)
    data[uid] = data.get(uid, 0) + бали
    save_data(data)

    # Приватне повідомлення (DM)
    embed = discord.Embed(
        title=f"FLAME PROJECT ЦСБ - ТОБІ ПРИЙШЛО {бали} БАЛ(А/ІВ) ЗА ІВЕНТ!",
        description=(f"**Тип івенту:** {тип_івенту.title()}\n"
                     f"**Роль в івенті:** {хост_чи_допомога.capitalize()}\n"
                     f"**Кількість балів:** {бали}\n"
                     f"📎 [Посилання на івент]({посилання})\n\n"
                     f"> {random.choice(подяки)}"),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Видав: {user.display_name}", icon_url=user.avatar.url if user.avatar else None)

    try:
        await user.send(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message(
            f"⚠️ {user.mention} не отримав DM (закриті повідомлення).", ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ Видано {бали} балів для {user.mention} як {хост_чи_допомога}!", ephemeral=True
    )

    await interaction.channel.send(
        f"**Івентер звіт**\n\n"
        f"**Івентер:** {user.mention}\n"
        f"**Хост/Допомога:** {хост_чи_допомога.capitalize()}\n"
        f"**Тип івенту:** {тип_івенту.title()}\n"
        f"**Кількість балів:** {бали}\n"
        f"**Посилання на івент:** {посилання}"
    )




@tree.command(name="модерзвіт", description="Звіт модератора")
@app_commands.describe(
    порушник="Ім'я або тег порушника",
    правило="Порушене правило (наприклад 3.1)",
    покарання="Тип покарання: попередження, тайм-аут, бан",
    час_покарання="Тривалість покарання (необов'язково)",
    посилання="Посилання на повідомлення з видачю покарання"
)
@app_commands.choices(
    покарання=[
        app_commands.Choice(name="Попередження", value="попередження"),
        app_commands.Choice(name="Тайм-аут", value="тайм-аут"),
        app_commands.Choice(name="Бан", value="бан"),
    ],
    правило=[
        app_commands.Choice(name=f"Правило {i}", value=str(i)) for i in range(1, 15)
    ] + [
        app_commands.Choice(name="Правило 3.1", value="3.1")
    ]
)
async def модерзвіт(
    interaction: discord.Interaction,
    порушник: str,
    правило: app_commands.Choice[str],
    покарання: app_commands.Choice[str],
    посилання: str,
    час_покарання: str = None
):
    покарання = покарання.value
    правило = правило.value
    час = час_покарання if час_покарання else "-"

    подяки = [
        "Твоя активність дуже цінується ❤️",
        "Дякуємо за працю!",
        "Чудова робота!",
        "Ми пишаємось вами!",
        "Молодець! Завдяки тобі сервер живий!"
    ]

    if not has_permission(interaction, "модерзвіт"):
        await interaction.response.send_message("⛔ У вас немає дозволу використовувати цю команду.", ephemeral=True)
        return

    правильні = {"попередження": 1, "тайм-аут": 2, "бан": 2}
    бали = правильні.get(покарання)

    if бали is None:
        await interaction.response.send_message("❗ Невірне покарання.", ephemeral=True)
        return

    uid = str(interaction.user.id)
    data = load_data()
    data[uid] = data.get(uid, 0) + бали
    save_data(data)

    await interaction.response.send_message(
        f"✅ Модератор {interaction.user.mention} отримав {бали} бал(и) за `{покарання}`.", ephemeral=True
    )

    await interaction.channel.send(
        f"**Модерзвіт**\n\n"
        f"**Модератор:** {interaction.user.mention}\n"
        f"**Порушник:** {порушник}\n"
        f"**Порушене правило:** {правило}\n"
        f"**Покарання:** {покарання.title()}\n"
        f"**Час покарання:** {час}\n"
        f"**Бали:** {бали}\n"
        f"📎 **Посилання:** {посилання}"
    )

    embed = discord.Embed(
        title=f"FLAME PROJECT ЦСБ - ТОБІ ПРИЙШЛО {бали} БАЛ(А/ІВ) ЗА ЗВІТ!",
        description=(
            f"**Порушник:** {порушник}\n"
            f"**Порушене правило:** {правило}\n"
            f"**Покарання:** {покарання.title()}\n"
            f"**Час покарання:** {час}\n"
            f"📎 [Посилання на покарання]({посилання})\n"
            f"**Кількість балів:** {бали}\n\n"
            f"> {random.choice(подяки)}"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(
        text=f"Видав: {interaction.user.display_name}",
        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
    )

    try:
        await interaction.user.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send(
            f"⚠️ {interaction.user.mention} не отримав DM (закриті повідомлення).",
            ephemeral=True
        )




@tree.command(name="адмінзвіт", description="Звіт адміністратора")
@app_commands.describe(
    покарання="Тип покарання: попередження, овервотч, мут, кік, бан",
    час_покарання="Тривалість покарання (необов'язково)",
    нікнейм="Нікнейм порушника",
    правило="Порушене правило (від 1 до 11)",
    стімайді="Steam ID порушника"
)
@app_commands.choices(
    покарання=[
        app_commands.Choice(name="Попередження", value="попередження"),
        app_commands.Choice(name="Мут", value="мут"),
        app_commands.Choice(name="Кік", value="кік"),
        app_commands.Choice(name="Бан", value="бан"),
    ],
    правило=[
        app_commands.Choice(name=f"Правило {i}", value=str(i)) for i in range(1, 12)
    ]
)
async def адмінзвіт(
    interaction: discord.Interaction,
    покарання: app_commands.Choice[str],
    нікнейм: str,
    правило: app_commands.Choice[str],
    стімайді: str,
    час_покарання: str = None  
):
    покарання = покарання.value
    правило = правило.value
    подяки = [
        "Твоя активність дуже цінується ❤️",
        "Дякуємо за працю!",
        "Чудова робота!",
        "Ми пишаємось вами!",
        "Молодець! Завдяки тобі сервер живий!"
    ]

    if not has_permission(interaction, "адмінзвіт"):
        await interaction.response.send_message("⛔ У вас немає дозволу використовувати цю команду.", ephemeral=True)
        return

    типи_балів = {
        "попередження": 1,
        "мут": 2,
        "кік": 2,
        "бан": 2
    }

    бали = типи_балів.get(покарання)
    if бали is None:
        await interaction.response.send_message("❗ Невідомий тип покарання.", ephemeral=True)
        return

    user = interaction.user
    uid = str(user.id)
    data = load_data()
    data[uid] = data.get(uid, 0) + бали
    save_data(data)

    час_text = час_покарання if час_покарання else "-"

    # Відповідь у DM
    embed_dm = discord.Embed(
        title=f"FLAME PROJECT ЦСБ - ТОБІ ПРИЙШЛО {бали} БАЛ(А/ІВ) ЗА ЗВІТ!",
        description=(
            f"**Покарання:** {покарання.title()}\n"
            f"**Порушник:** {нікнейм}\n"
            f"**Порушене правило:** {правило}\n"
            f"**Steam ID:** {стімайді}\n"
            f"**Тривалість:** {час_text}\n"
            f"**Кількість балів:** {бали}\n\n"
            f"> {random.choice(подяки)}"
        ),
        color=discord.Color.green()
    )
    embed_dm.set_footer(text=f"Звіт подав: {user.display_name}", icon_url=user.avatar.url if user.avatar else None)

    try:
        await user.send(embed=embed_dm)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ {user.mention} не отримав DM (закриті повідомлення).", ephemeral=True)

    # Публічна відповідь у канал
    await interaction.channel.send(
        f"**Адмін звіт**\n\n"
        f"**Адмін:** {user.mention}\n"
        f"**Порушник:** {нікнейм}\n"
        f"**Правило:** {правило}\n"
        f"**Steam ID:** {стімайді}\n"
        f"**Покарання:** {покарання.title()}\n"
        f"**Тривалість:** {час_text}\n"
        f"**Бали:** {бали}"
    )

    # Відповідь у ephemeral
    await interaction.response.send_message(
        f"✅ {user.mention} отримав **{бали}** бал(ів) за покарання **{покарання}**.\n"
        f"**Нікнейм порушника:** {нікнейм}\n"
        f"**Порушене правило:** {правило}\n"
        f"**Steam ID:** {стімайді}\n"
        f"**Тривалість покарання:** {час_text}",
        ephemeral=True
    )






@tree.command(name="дівентерзвіт", description="Звіт дискорд-івентера")
@app_commands.describe(
    приз="Чи був приз (з призом / без приза)",
    посилання="Посилання на лог завершеного івенту"
)
@app_commands.choices(
    приз=[
        app_commands.Choice(name="З призом", value="з призом"),
        app_commands.Choice(name="Без приза", value="без приза"),
    ]
)

async def дівентерзвіт(
    interaction: discord.Interaction,
    приз: str,
    посилання: str
):
    подяки = [
        "Твоя активність дуже цінується ❤️",
        "Дякуємо за працю!",
        "Чудова робота!",
        "Ми пишаємось вами!",
        "Молодець! Завдяки тобі сервер живий!"
    ]

    if not has_permission(interaction, "дівентерзвіт"):
        await interaction.response.send_message("⛔ У вас немає дозволу використовувати цю команду.", ephemeral=True)
        return

    приз = приз.lower()
    if приз not in ["з призом", "без приза"]:
        await interaction.response.send_message("❗ Вкажи або `з призом`, або `без приза`.", ephemeral=True)
        return

    бали = 2 if приз == "з призом" else 1

    # Додавання балів до interaction.user
    uid = str(interaction.user.id)
    data = load_data()
    data[uid] = data.get(uid, 0) + бали
    save_data(data)

    # Відповідь автору команди
    await interaction.response.send_message(
        f"✅ Тобі нараховано **{бали} бал(ів)** за івент **({приз})**.", ephemeral=True
    )

    # Публічне повідомлення в канал
    await interaction.channel.send(
        f"**Діскорд-Івентер звіт**\n\n"
        f"**Івентер:** {interaction.user.mention}\n"
        f"**Приз:** {приз}\n"
        f"**Бали:** {бали}\n"
        f"**Посилання на лог:** {посилання}"
    )

    # DM-повідомлення
    embed = discord.Embed(
        title=f"FLAME PROJECT ЦСБ - ТОБІ ПРИЙШЛО {бали} БАЛ(А/ІВ) ЗА ІВЕНТ!",
        description=(
            f"**Призовий статус:** {приз.capitalize()}\n"
            f"📎 [Посилання на лог івенту]({посилання})\n\n"
            f"> {random.choice(подяки)}"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(
        text=f"Звіт подав: {interaction.user.display_name}",
        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
    )

    try:
        await interaction.user.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ {interaction.user.mention} не отримав DM (закриті повідомлення).", ephemeral=True)


bot.run(TOKEN)