import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pytube import YouTube
from pydub import AudioSegment

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "6420918352:AAEPwQynSVtawUl1ZPEggFhYrNmHr_8kKG0"

DOWNLOAD_FOLDER = './'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a YouTube link and I will convert it to MP3 for you.')


def download_audio(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id


    if update.message.text and ('youtube.com' in update.message.text or 'youtu.be' in update.message.text):

        try:

            youtube_url = update.message.text
            yt = YouTube(youtube_url)
            video_stream = yt.streams.filter(only_audio=True).first()
            video_stream.download(DOWNLOAD_FOLDER)


            mp3_file_path = os.path.join(DOWNLOAD_FOLDER, f"your-song.mp3")
            audio = AudioSegment.from_file(video_stream.default_filename)


            audio = audio.set_frame_rate(48000).set_channels(2).set_sample_width(2)


            audio.export(mp3_file_path, format="mp3", bitrate="320k")


            context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file_path, 'rb'))

            os.remove(video_stream.default_filename)
            os.remove(mp3_file_path)

        except Exception as e:
            logging.error(f"Error processing YouTube link: {e}")
            update.message.reply_text("Error processing YouTube link. Please try again.")

    else:
        update.message.reply_text("Please provide a valid YouTube link.")


def main() -> None:
    updater = Updater("6420918352:AAEPwQynSVtawUl1ZPEggFhYrNmHr_8kKG0")


    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_audio))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
