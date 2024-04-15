import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pytube import YouTube
from pydub import AudioSegment
import mysql.connector

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = ""
DOWNLOAD_FOLDER = './'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "BotDB"


mysql_connection = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
mysql_cursor = mysql_connection.cursor()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a YouTube link and I will convert it to MP3 for you.')

def download_audio(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if update.message.text and ('youtube.com' in update.message.text or 'youtu.be' in update.message.text):
        try:
            youtube_url = update.message.text
            yt = YouTube(youtube_url)
            if yt.age_restricted:
                update.message.reply_text("The video is age-restricted and cannot be processed.")
                return

            video_stream = yt.streams.filter(only_audio=True).first()
            video_stream.download(DOWNLOAD_FOLDER)
            mp3_file_path = f"{yt.title}.mp3"


            select_query = "SELECT file_name FROM uploaded_files WHERE file_name = %s"
            mysql_cursor.execute(select_query, (mp3_file_path,))
            result = mysql_cursor.fetchone()

            if result:

                context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file_path, 'rb'))
                os.remove(video_stream.default_filename)

            else:

                video_stream.download(DOWNLOAD_FOLDER)
                audio = AudioSegment.from_file(video_stream.default_filename)
                audio = audio.set_frame_rate(48000).set_channels(2).set_sample_width(2)
                audio.export(mp3_file_path, format="mp3", bitrate="320k")
                os.remove(video_stream.default_filename)
                context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file_path, 'rb'))
                insert_query = "INSERT INTO uploaded_files (file_name, youtube_url) VALUES (%s, %s)"
                mysql_cursor.execute(insert_query, (mp3_file_path, youtube_url))
                mysql_connection.commit()


        except Exception as e:
            logging.error(f"Error processing YouTube link: {e}")
            logging.exception("Exception traceback:")
            update.message.reply_text("Error processing YouTube link. Please try again.")

    else:
        update.message.reply_text("Please provide a valid YouTube link.")

def main() -> None:
    updater = Updater("")
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_audio))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
