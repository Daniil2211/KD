import os

import librosa as lr
import numpy as np

SR = 16000

def filter_audio(audio):
  # Считаем энергию голоса для каждого блока в 125 мс
  apower = lr.amplitude_to_db(np.abs(lr.stft(audio, n_fft=2048)), ref=np.max)

  # Суммируем энергию по каждой частоте, нормализуем
  apsums = np.sum(apower, axis=0)**2
  apsums -= np.min(apsums)
  apsums /= np.max(apsums)

  # Сглаживаем график, чтобы сохранить короткие пропуски и паузы, убрать резкость
  apsums = np.convolve(apsums, np.ones((9,)), 'same')
  # Нормализуем снова
  apsums -= np.min(apsums)
  apsums /= np.max(apsums)

  # Устанавливаем порог в 35% шума над голосом
  apsums = np.array(apsums > 0.35, dtype=bool)

  # Удлиняем блоки каждый по 125 мс
  # до отдельных семплов (2048 в блоке)
  apsums = np.repeat(apsums, np.ceil(len(audio) / len(apsums)))[:len(audio)]

  return audio[apsums] # Фильтруем!

def process_audio(aname):
  audio, _ = lr.load(aname, sr=SR)
  # Извлекаем коэффициенты
  afs = lr.feature.mfcc(audio,
                        sr=SR,
                        n_mfcc=34,
                        n_fft=2048)
  afss = np.sum(afs[3:6], axis=-1)
  afss = afss / np.max(np.abs(afss))
  # print(afss)
  return afss

def confidence(x, y):
    # print(f'x - {x}; y - {y}')
    return np.sum((x - y)**2)


## Загружаем несколько аудиодорожек
audio_oleg = process_audio("Untitled.wav")


audio1 = process_audio("oleg.wav")
audio2 = process_audio("videoplayback.wav")
audio3 = process_audio("f42b4fe2-a510-4d07-b824-bfd1aac4c269.wav")
audio4 = process_audio("f6ad9bf9-b930-4a90-ae04-adb32d3b8f7e.wav")

audio_not_oleg = process_audio("297a453b-a9d7-410d-9c24-9b8f3a338106.wav")
audio_not_oleg_2 = process_audio("a0b00788-d74f-429a-9f9a-68d5ee8dff29.wav")
audio_not_oleg_3 = process_audio("7ed42eec-916e-4687-99b6-6392b3e73fc2.wav")


# print('oleg', confidence(audio_oleg, audio1))
# print('oleg', confidence(audio_oleg, audio2))
# print('oleg', confidence(audio_oleg, audio3))
# print('oleg', confidence(audio_oleg, audio4))
# print('not_oleg', confidence(audio_oleg, audio_not_oleg))
# print('not_oleg', confidence(audio_oleg, audio_not_oleg_2))
# print('not_oleg', confidence(audio_oleg, audio_not_oleg_3))

# oleg 0.055502884
# oleg 1.8260665
# oleg 1.467437
# oleg 1.7696712
# not_oleg 1.6959887
# not_oleg 2.4354887
# not_oleg 3.0339985

path ="C:\\Users\\Lenovo\\PycharmProjects\\Oleg"
filelist = []

for root, dirs, files in os.walk(path):
	for file in files:
		filelist.append(os.path.join(root,file))

for name in filelist:
    test_audio = process_audio(name)
    print('Test', True if confidence(audio_oleg, test_audio) < 1 else False)