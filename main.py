import os
from datetime import datetime
# from pytube import YouTube
from pytubefix import YouTube

def create_download_folder():
    folder_name = f"Downloads_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(folder_name, exist_ok=True)
    print(f"Файлы будут сохранены в папке: {folder_name}")
    return folder_name

def download_mp3(link):
    try:
        yt = YouTube(link)
        video = yt.streams.get_audio_only()

        folder_name = create_download_folder()

        print("----- Loading -----")
        out_of_file = video.download(output_path=folder_name)

        base, _ = os.path.splitext(out_of_file)
        new_file = base + '.mp3'
        os.rename(out_of_file, new_file)

        print(f"Файл сохранен: {new_file}")
        print("--- End loading ---")
    except Exception as e:
        print(f"Произошла ошибка при скачивании MP3: {e}")

def download_video(link):
    yt = YouTube(link)
    video = yt.streams.get_highest_resolution()

    folder_name = create_download_folder()

    # Загрузка видео в созданную папку
    print("----- Loading Video -----")
    video_file = video.download(output_path=folder_name)
    
    print(f"Видео сохранено: {video_file}")
    print("--- End loading Video ---")

if __name__ == '__main__':
    print("Введите ссылку на видео с YouTube.")
    link = input("Введите ссылку: ")
    print("Выберите действие: '1' для скачивания MP3 или '2' для скачивания видео.")
    print("--- Start ---")
    choice = input("Введите '1' для скачивания MP3 или '2' для скачивания видео: ")
    if choice == '1':
        download_mp3(link)
    elif choice == '2':
        download_video(link)
    else:
        print("Неверный выбор!")










