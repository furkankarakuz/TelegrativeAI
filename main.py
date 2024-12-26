"""
This file serves as the entry point for the Telegram bot application.

It initializes the application, configures handlers for various types of user inputs, and starts the bot's polling mechanism to interact with users.

The functionalities covered include:
- Initializing the bot with the Telegram API token.
- Configuring command and message handlers for user interactions.
- Starting the bot to listen for and respond to user messages.
"""


from telegram_process import start, get_message, audio, button, handle_file, error_message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    def create_application():
        """
        Initialize the Telegram bot application with the API token.

        This function sets up the application object with the specified API token, which is required for the bot to communicate with Telegram's servers.

        Args:
            None

        Returns:
            None
        """
        global app
        app = Application.builder().token(os.getenv("API_KEY")).build()

    def configure_handlers():
        """
        Configure the handlers for various user interactions.

        This function sets up the command handlers, message handlers, and callback query handlers to process user inputs such as text, voice, documents, and button clicks.

        Args:
            None

        Returns:
            None
        """
        app.add_handler(CallbackQueryHandler(button))

        app.add_handler(CommandHandler("start", start))

        app.add_handler(MessageHandler(filters.VOICE, audio))
        app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_message))

        app.add_error_handler(error_message)
        app.run_polling()

    create_application()
    configure_handlers()


if __name__ == "__main__":
    main()
