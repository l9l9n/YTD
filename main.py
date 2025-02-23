import os
from datetime import datetime
# from pytube import YouTube
from pytubefix import YouTube

def download_mp3(link):
    yt = YouTube(link)
    video = yt.streams.get_audio_only()

    # Создаем папку с текущей датой и временем
    folder_name = "Downloads_file"
    os.makedirs(folder_name, exist_ok=True)

    print(f"Файлы будут сохранены в папке: {folder_name}")

    # Загрузка файла в созданную папку
    print("----- Loading -----")
    out_of_file = video.download(output_path=folder_name)

    # Переименовываем .mp4 в .mp3
    base, _ = os.path.splitext(out_of_file)
    new_file = base + '.mp3'
    os.rename(out_of_file, new_file)
    
    print(f"Файл сохранен: {new_file}")
    print("--- End loading ---")

if __name__ == '__main__':
    link = input("Введите ссылку: ")
    print("--- Start ---")
    download_mp3(link)










