from gtts import gTTS
from moviepy.editor import AudioFileClip, CompositeAudioClip

text = "Привет, это тестовая озвучка."
voice_file = "voice.mp3"
music_file = "background.mp3"
output_file = "audio_mix.mp3"

# Синтез речи
tts = gTTS(text, lang="ru")
tts.save(voice_file)

# Объединение с музыкой
voice = AudioFileClip(voice_file)
music = AudioFileClip(music_file).subclip(0, voice.duration).volumex(0.1)
mix = CompositeAudioClip([music, voice])
mix.write_audiofile(output_file)
