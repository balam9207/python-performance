import os
import time
import requests
from gtts import gTTS
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
)

# === НАСТРОЙКИ ===
RUNWAY_API_KEY = "ТВОЙ_API_КЛЮЧ_ЗДЕСЬ"
BACKGROUND_MUSIC = "background.mp3"

HEADERS = {
    "Authorization": f"Bearer {RUNWAY_API_KEY}",
    "Content-Type": "application/json"
}

# === ЗАПРОС НА ГЕНЕРАЦИЮ ВИДЕО В RUNWAY ===
def create_video(prompt, duration=5, seed=42, resolution="720p"):
    payload = {
        "prompt": prompt,
        "seed": seed,
        "duration": duration,
        "output_format": "mp4",
        "fps": 24,
        "resolution": resolution
    }
    r = requests.post("https://api.runwayml.com/v2/generate/video", headers=HEADERS, json=payload)
    if r.status_code != 202:
        print("❌ Ошибка генерации:", r.text)
        return None
    status_url = r.json()["urls"]["get"]
    print("⏳ Ожидание генерации...")
    while True:
        resp = requests.get(status_url, headers=HEADERS).json()
        if resp.get("status") == "succeeded":
            return resp["output"]["video"]
        elif resp.get("status") == "failed":
            print("❌ Не удалось сгенерировать сцену")
            return None
        time.sleep(3)

def download_file(url, dest):
    r = requests.get(url)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)

def text_to_speech(text, filename):
    tts = gTTS(text=text, lang="ru", slow=False)
    tts.save(filename)

def mix_audio(voice_path, music_path, output_path, music_volume=0.1):
    voice = AudioFileClip(voice_path)
    music = AudioFileClip(music_path).subclip(0, voice.duration).volumex(music_volume)
    mixed = CompositeAudioClip([music, voice])
    mixed.write_audiofile(output_path)

def main():
    os.makedirs("video", exist_ok=True)
    os.makedirs("tts", exist_ok=True)

    # 1. Загрузка сценария
    with open("script.txt", encoding="utf-8") as f:
        scenes = [line.strip() for line in f if line.strip()]
    if not scenes:
        print("❗ В файле script.txt нет текста.")
        return

    video_clips = []

    for idx, scene_text in enumerate(scenes, 1):
        print(f"\n🎬 Сцена {idx}: {scene_text}")

        # 2. Генерация видео
        video_url = create_video(scene_text)
        if not video_url:
            print("⚠️ Сцена пропущена.")
            continue
        video_path = f"video/scene_{idx}.mp4"
        download_file(video_url, video_path)

        # 3. Озвучка
        voice_path = f"tts/voice_{idx}.mp3"
        final_audio_path = f"tts/audio_mix_{idx}.mp3"
        text_to_speech(scene_text, voice_path)

        # 4. Микс с фоновой музыкой
        mix_audio(voice_path, BACKGROUND_MUSIC, final_audio_path)

        # 5. Комбинирование видео + озвучка
        video = VideoFileClip(video_path)
        audio = AudioFileClip(final_audio_path)
        video = video.set_audio(audio)
        video_clips.append(video)

    # 6. Сборка финального видео
    if video_clips:
        print("\n🎞 Объединение всех сцен...")
        final = concatenate_videoclips(video_clips)
        final.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")
        print("\n✅ Видео создано: final_video.mp4")
    else:
        print("❌ Не удалось создать ни одной сцены.")

if __name__ == "__main__":
    main()
