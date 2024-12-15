import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your Telegram Bot Token
BOT_TOKEN = "ENTER YOUR TOKEN"

# Replace with your Fortnite API Key
FORTNITE_API_KEY = "ENTER YOUR API"

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a welcome message and instructions on how to use the bot.
    """
    welcome_message = (
        "Welcome to the Fortnite Bot! 🎮\n\n"
        "Here are the available commands you can use:\n\n"
        "/map - Fetches the current Fortnite map 🗺️\n"
        "/itemshop - Displays the current Fortnite item shop 🛒\n"
        "/cosmetics_new - Fetches the latest Fortnite cosmetics 🆕\n"
        "/cosmetic_search <name> - Search for a specific Fortnite cosmetic by name or ID 🔍\n\n"
        "Feel free to use any of these commands to get the latest Fortnite data!"
    )

    await update.message.reply_text(welcome_message)

# Command: /map
async def fortnite_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and sends the current Fortnite map image.
    """
    url = "https://fortnite-api.com/v1/map"
    headers = {"Authorization": FORTNITE_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        image_url = data.get("data", {}).get("images", {}).get("pois", "")

        if image_url:
            await update.message.reply_photo(photo=image_url, caption="🗺️ Here is the current Fortnite map!")
        else:
            await update.message.reply_text("Error: No map image URL found.")
    else:
        await update.message.reply_text(f"Failed to fetch the Fortnite map. Status code: {response.status_code}")


# Command: /itemshop
async def fortnite_itemshop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and sends the current Fortnite item shop.
    """
    url = "https://fortnite-api.com/v2/shop"
    headers = {"Authorization": FORTNITE_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        entries = data.get("data", {}).get("featured", []) + data.get("data", {}).get("daily", [])

        if not entries:
            await update.message.reply_text("No items found in the item shop.")
            return

        shop_items = []
        for entry in entries:
            for item in entry.get("items", []):
                name = item.get("name", "Unknown Item")
                rarity = item.get("rarity", {}).get("displayValue", "Unknown Rarity")
                price = entry.get("finalPrice", "N/A")
                image_url = item.get("images", {}).get("icon", "")

                shop_items.append(
                    f"**{name}**\nRarity: {rarity}\nPrice: {price} V-Bucks\n{image_url}"
                )

        message = "\n\n".join(shop_items)

        if len(message) > 4096:
            with open("itemshop.txt", "w", encoding="utf-8") as file:
                file.write(message)
            await update.message.reply_document(
                document=InputFile("itemshop.txt"),
                caption="The item shop is too large. Here's the full list as a file."
            )
        else:
            await update.message.reply_text(f"🛒 *Fortnite Item Shop*\n\n{message}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Failed to fetch the item shop. Status code: {response.status_code}")


# Command: /cosmetics_new
async def cosmetics_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and sends the latest Fortnite cosmetics.
    """
    url = "https://fortnite-api.com/v2/cosmetics/new"
    headers = {"Authorization": FORTNITE_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        cosmetics = data.get("data", {}).get("items", [])

        if not cosmetics:
            await update.message.reply_text("No new cosmetics found.")
            return

        cosmetic_details = []
        for cosmetic in cosmetics:
            name = cosmetic.get("name", "Unknown Cosmetic")
            rarity = cosmetic.get("rarity", {}).get("displayValue", "Unknown Rarity")
            image_url = cosmetic.get("images", {}).get("icon", "")

            cosmetic_details.append(
                f"**{name}**\nRarity: {rarity}\n{image_url}"
            )

        message = "\n\n".join(cosmetic_details)

        if len(message) > 4096:
            with open("cosmetics_new.txt", "w", encoding="utf-8") as file:
                file.write(message)
            await update.message.reply_document(
                document=InputFile("cosmetics_new.txt"),
                caption="The list of new cosmetics is too large. Here's the full list as a file."
            )
        else:
            await update.message.reply_text(f"🆕 *New Fortnite Cosmetics*\n\n{message}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Failed to fetch new cosmetics. Status code: {response.status_code}")


# Command: /cosmetic_search <name>
async def cosmetic_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Searches for Fortnite cosmetics by name or ID.
    """
    if not context.args:
        await update.message.reply_text("Please provide a cosmetic name or ID. Example: /cosmetic_search Skull Trooper")
        return

    query = " ".join(context.args)
    url = f"https://fortnite-api.com/v2/cosmetics/br/search?name={query}"
    headers = {"Authorization": FORTNITE_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {})

        if not data:
            await update.message.reply_text("No cosmetic found with that name or ID.")
            return

        name = data.get("name", "Unknown Cosmetic")
        rarity = data.get("rarity", {}).get("displayValue", "Unknown Rarity")
        introduction = data.get("introduction", {}).get("text", "Unknown Release")
        last_seen = data.get("shopHistory", ["Never"])[-1]
        image_url = data.get("images", {}).get("icon", "")

        message = (
            f"**{name}**\n"
            f"Rarity: {rarity}\n"
            f"Introduced: {introduction}\n"
            f"Last Seen: {last_seen}\n"
            f"{image_url}"
        )

        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Failed to search for cosmetics. Status code: {response.status_code}")


# Main function to start the bot
def main():
    """
    Starts the Telegram bot and registers all commands.
    """
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Registering commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("map", fortnite_map))
    app.add_handler(CommandHandler("itemshop", fortnite_itemshop))
    app.add_handler(CommandHandler("cosmetics_new", cosmetics_new))
    app.add_handler(CommandHandler("cosmetic_search", cosmetic_search))

    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
