"""
This file contains the implementation of Telegram bot processing functionalities.

The module includes:
- User authentication and API key management.
- Handling user interactions such as text, file, and voice inputs.
- Integrating with OpenAI models for text generation, document summarization, and voice transcription.
- Managing Telegram-specific events like button clicks and animations.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from model_manager import OpenAIModelManager
import os
import time
import tempfile
import requests


async def check_user(update: Update, context: CallbackContext, data: str = None):
    """
    Authenticate the user and manage their OpenAI API key.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.
        data (str, optional): The OpenAI API key provided by the user. Defaults to None.

    Returns:
        None
    """
    global manager

    start_message = """
    Here are the skills I can offer you,

    -> text chat
    -> have voice conversations
    -> create images based on your requests.
    -> analyze and review documents you provide.

    To perform these tasks, you will need to provide your OpenAI API key.
    Note: Please do not share your personal information and use a test API key. If you want to delete API key, you can use /off code.
    """
    start_message = "\n".join(line.lstrip() for line in start_message.splitlines())

    if user not in context.user_data:
        if data:
            manager = OpenAIModelManager(data)
            await update.message.reply_text(f"Key : {data[:3]}*************{data[-3:]} success")
            await hello(update, context)
            context.user_data[user] = manager
        else:
            await update.message.reply_markdown(start_message)
            time.sleep(1)
            await question(update, context)
    else:
        await hello(update, context)


async def start(update: Update, context: CallbackContext):
    """
    Initialize the bot for a new user session.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    global user, user_name

    user, user_name = update.message.from_user.id, update.message.from_user.full_name

    await update.message.reply_markdown(f"Hello {user_name}, I'm TelegrativeAI 🤖🙂")
    await update.message.reply_animation(animation="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnpibnB3OWd2OWtvdm13cWl1NGFhaHQ3eDJvZnN1MHJ1a3I4NmFldyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JFz7YZA0vhiGlAYCSn/giphy.gif")
    time.sleep(1)
    await check_user(update, context)


async def hello(update: Update, context: CallbackContext):
    """
    Send a greeting message to the user.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    await update.message.reply_markdown(f"Hello {user_name} , What Can I Help With ?")


async def handle_file(update: Update, context: CallbackContext):
    """
    Handle file uploads, process the file, and generate a response.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    document = update.message.document
    file = await context.bot.get_file(document.file_id)

    caption = update.message.caption
    caption = caption if caption is not None else "Summarize this file"

    if document.mime_type == "text/plain":
        response = requests.get(file.file_path)
        message = context.user_data[user].lang_model.rag_with_documents_from_text(response.text, caption)
        await update.message.reply_text(message)

    elif document.mime_type == "application/pdf":
        message = context.user_data[user].lang_model.rag_with_documents(file.file_path, caption)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Please send the file in PDF or TXT format")


async def get_message(update: Update, context: CallbackContext):
    """
    Handle text messages from the user and generate appropriate responses.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    if update.message.reply_to_message:
        replied_message = update.message.reply_to_message
        send_message = context.user_data[user].model.chat_message(f"{replied_message.text} in addition to {update.message.text}")
    else:
        if "draw" in update.message.text.lower():
            await send_image(update, context)
            return
        elif update.message.text.startswith("sk-"):
            api_text = update.message.text
            await update.message.delete()
            await check_user(update, context, api_text)
            return
        else:
            send_message = context.user_data[user].model.chat_message(update.message.text)
    await update.message.reply_markdown(send_message)


async def send_image(update: Update, context: CallbackContext):
    """
    Generate an image based on user input and send it.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    image, text = context.user_data[user].model.create_image(update.message.text)
    await update.message.reply_photo(photo=image, caption=text)


async def download_audio_to_local(file) -> str:
    """
    Download an audio file locally.

    Args:
        file: The Telegram temp file object.

    Returns:
        str: The path to the downloaded file.
    """
    audio = await file.download_as_bytearray()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as tmp_file:
        tmp_file.write(audio)
        tmp_file_path = tmp_file.name
    return tmp_file_path


async def audio(update: Update, context: CallbackContext):
    """
    Handle voice messages, transcribe them, and generate a response.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    if update.message.voice:
        file_id = update.message.voice.file_id
        file = await context.bot.get_file(file_id)
        temp_file_path = await download_audio_to_local(file)

        with open(temp_file_path, "rb") as audio_file:
            voice_text = context.user_data[user].model.transcribe_voice(audio_file)
            await update.message.reply_markdown(context.user_data[user].model.chat_message(voice_text))

        os.remove(temp_file_path)


async def question(update: Update, context: CallbackContext):
    """
    Ask the user if they would like to continue and provide options.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    options = [[InlineKeyboardButton("Yes", callback_data='yes')], [InlineKeyboardButton("No", callback_data='no')]]
    keyboard = InlineKeyboardMarkup(options)

    await update.message.reply_text("Would you like to continue?", reply_markup=keyboard)


async def button(update: Update, context: CallbackContext):
    """
    Handle button clicks in the Telegram chat.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    query = update.callback_query
    await query.answer()
    if query.data == 'yes':
        await query.message.reply_text(text="OK. Let's Start")
        await query.message.reply_animation(animation="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHE2dzFqeTJ1ZmlybDJzcmQ2dWdkaHk0NXp6ejI5M2lodTNveGh1biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/06yiZTyUNXmdSFlutV/giphy.gif")
        await query.message.reply_text(text="Write your API Key")
    else:
        await query.message.reply_text(text="OK. See you later!")
        await query.message.reply_animation(animation="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmc5dWQ2dTc4dTNvMnpyNGdjaHFxbXl2dHQwamlsaGJ0bGxtcHplOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9kzGqfk7xgN0AZw3jo/giphy.gif")


async def off(update: Update, context: CallbackContext):
    """
    Remove the user's API key and end the session.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The context object containing user data.

    Returns:
        None
    """
    if user in context.user_data:
        context.user_data.pop(user)
        await update.message.reply_text("Your API Key deleted")


async def error_message(update: Update, context: CallbackContext):
    """
    Handles errors by checking if the user exists in the context and sending an appropriate message.

    Args:
        update (Update): The incoming update containing information about the user's message.
        context (CallbackContext): The context object containing the user's data and other information.

    Returns:
        None
    """
    if user not in context.user_data:
        await start(update, context)
    else:
        await update.message.reply_text("An error occurred please try again later")
