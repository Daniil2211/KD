import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack as fftpk

from matplotlib import pyplot as plt
from mkl_fft import fft

s_rate, signal = wavfile.read("oleg.wav")

FFT = abs(fft(signal))
freqs = fftpk.fftfreq(len(FFT), (1.0/s_rate))

y = FFT[range(len(FFT)//2)]
x = freqs[range(len(FFT)//2)]

print(x)
print(y)

plt.plot(x, y)
plt.xlabel('Частота')
plt.ylabel('Амплитуда')
plt.show()