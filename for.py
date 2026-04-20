import discord
from discord.ext import commands

# ========== НАСТРОЙКИ ==========
TOKEN = "MTQ5NTQzMzkwNDUxNjEwNDI0Mg.G6mlcE.6fQWwii4Kro6n56oBZ9siRNqqfKc4LbPXV9QnE"        # ← ВСТАВЬТЕ СВОЙ ТОКЕН
PREFIX = "!"                      # Префикс команд
# ================================

# Включаем интенты
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True       # Чтобы видеть, в каких голосовых каналах находятся участники

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ========== БАЗА ОТВЕТОВ (FAQ) ==========
FAQ = {
    "привет": "Привет! Чем могу помочь?",
    "как дела": "У меня всё отлично, спасибо! А у тебя?",
    "погода": "Я не метеоролог, но советую посмотреть прогноз в приложении :)",
    "бот": "Я бот, который умеет ставить реакции, отвечать на вопросы, показывать статистику сервера и перемещать участников по голосовым каналам!",
    "помощь": "Доступные команды:\n"
              "!react <id_сообщения> <эмодзи> – поставить реакцию\n"
              "!ask <вопрос> – задать вопрос (или просто упомяни меня)\n"
              "!stats – статистика сервера (всего участников и онлайн)\n"
              "!move @участник #канал – переместить участника в другой голосовой канал"
}

def get_faq_answer(text: str) -> str | None:
    text_lower = text.lower()
    for keyword, answer in FAQ.items():
        if keyword in text_lower:
            return answer
    return None

# ========== СОБЫТИЕ: БОТ ГОТОВ ==========
@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} подключился к Discord!")
    print(f"📊 Серверов: {len(bot.guilds)}")

# ========== КОМАНДА: РЕАКЦИЯ ==========
@bot.command(name="react")
async def add_reaction(ctx, message_id: int, emoji: str):
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.add_reaction(emoji)
        await ctx.send(f"✅ Реакция {emoji} добавлена на сообщение {message_id}")
    except discord.NotFound:
        await ctx.send("❌ Сообщение с таким ID не найдено.")
    except discord.Forbidden:
        await ctx.send("❌ У бота нет прав добавлять реакции.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ошибка: {e}")

# ========== КОМАНДА: СПРОСИТЬ ==========
@bot.command(name="ask")
async def ask_command(ctx, *, question: str):
    answer = get_faq_answer(question)
    if answer:
        await ctx.send(answer)
    else:
        await ctx.send("Извините, я не знаю ответа. Попробуйте: " + ", ".join(FAQ.keys()))

# ========== КОМАНДА: СТАТИСТИКА СЕРВЕРА ==========
@bot.command(name="stats")
async def server_stats(ctx):
    guild = ctx.guild
    if guild is None:
        await ctx.send("❌ Эта команда работает только на сервере.")
        return
    total = guild.member_count
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    embed = discord.Embed(title="📊 Статистика", color=discord.Color.green())
    embed.add_field(name="👥 Всего", value=total, inline=True)
    embed.add_field(name="🟢 Онлайн", value=online, inline=True)
    await ctx.send(embed=embed)

# ========== КОМАНДА: ПЕРЕМЕЩЕНИЕ В ГОЛОСОВОМ КАНАЛЕ ==========
@bot.command(name="move")
async def move_member(ctx, member: discord.Member, channel: discord.VoiceChannel):
    """Перемещает указанного участника в указанный голосовой канал.
    Пример: !move @Пользователь "Общий чат" """
    if member.voice is None:
        await ctx.send(f"❌ {member.mention} не находится в голосовом канале.")
        return
    try:
        await member.move_to(channel)
        await ctx.send(f"✅ {member.mention} перемещён в {channel.mention}")
    except discord.Forbidden:
        await ctx.send("❌ У бота нет права `Move Members`. Выдайте ему эту роль.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ошибка: {e}")

@move_member.error
async def move_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас нет права `Move Members`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Неверный формат. Пример: `!move @Пользователь #НазваниеКанала`")

# ========== ОТВЕТ НА УПОМИНАНИЕ ==========
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user in message.mentions:
        content = message.clean_content.replace(f"@{bot.user.name}", "").strip()
        if content:
            answer = get_faq_answer(content)
            if answer:
                await message.reply(answer)
            else:
                await message.reply(f"Не понял. Напиши `{PREFIX}ask` или `{PREFIX}help` (встроенная справка Discord).")
        else:
            await message.reply(f"Мои команды: `{PREFIX}ask`, `{PREFIX}react`, `{PREFIX}stats`, `{PREFIX}move`")
    await bot.process_commands(message)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    if TOKEN == "MTQ5NTQzMzkwNDUxNjEwNDI0Mg.G6mlcE.6fQWwii4Kro6n56oBZ9siRNqqfKc4LbPXV9QnE":
        bot.run("MTQ5NTQzMzkwNDUxNjEwNDI0Mg.G6mlcE.6fQWwii4Kro6n56oBZ9siRNqqfKc4LbPXV9QnE")