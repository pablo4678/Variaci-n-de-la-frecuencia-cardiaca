from scipy.signal import butter
import numpy as np
from scipy.signal import lfilter
import matplotlib.pyplot as plt

fs = 250
lowcut=0.5
highcut=40
orden=4
nyq = 0.5 * fs
low = lowcut / nyq
high = highcut / nyq
b, a = butter(orden, [low, high], btype='band')

print("a")
print(a)
print("b")
print(b)

x = np.loadtxt("ECG_data.txt")
y = lfilter(b, a, x)

plt.plot(x, label='Original')
plt.plot(y, label='Filtrada')
plt.legend()
plt.title('Filtrado IIR')
plt.show()