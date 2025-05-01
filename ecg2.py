import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def diagnostico_senal_ecg(tiempos, voltajes_filtrados, fs=250):
    print("📊 Diagnóstico de la señal ECG")

    # 1. Estadísticas básicas
    print(f"- Duración total: {tiempos[-1]:.2f} segundos")
    print(f"- Muestras totales: {len(voltajes_filtrados)}")
    print(f"- Voltaje máximo: {np.max(voltajes_filtrados):.4f} mV")
    print(f"- Voltaje mínimo: {np.min(voltajes_filtrados):.4f} mV")
    print(f"- Promedio: {np.mean(voltajes_filtrados):.4f}")
    print(f"- Desviación estándar: {np.std(voltajes_filtrados):.4f}")

    # 2. Gráfica de los primeros 10 segundos
    plt.figure(figsize=(12, 4))
    plt.plot(tiempos[:fs*10], voltajes_filtrados[:fs*10])
    plt.title("🔍 ECG filtrado - primeros 10 segundos")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Voltaje (mV)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 3. Prueba de detección de picos SIN umbral
    print("\n🔍 Detección de picos sin umbral (solo con distancia mínima)")
    distancia = int(0.4 * fs)  # 400 ms entre picos (~150 bpm)
    picos, _ = find_peaks(voltajes_filtrados, distance=distancia)
    print(f"- Picos detectados: {len(picos)}")

    # 4. Gráfica de picos detectados
    plt.figure(figsize=(12, 4))
    plt.plot(tiempos, voltajes_filtrados, label='ECG filtrado')
    plt.plot(np.array(tiempos)[picos], np.array(voltajes_filtrados)[picos], 'ro', label='Picos detectados')
    plt.title("📈 Picos detectados SIN umbral")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Voltaje (mV)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 5. Histograma de amplitud
    plt.figure(figsize=(6, 4))
    plt.hist(voltajes_filtrados, bins=100, color='gray')
    plt.title("Histograma de amplitud del ECG")
    plt.xlabel("Voltaje (mV)")
    plt.ylabel("Frecuencia")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 6. Diagnóstico
    if len(picos) < 100:
        print("\n⚠️ Se detectaron pocos picos R.")
        print("Posibles causas:")
        print("- Señal muy ruidosa, invertida o sin forma clara de QRS.")
        print("- Filtro incorrecto o señal mal escalada.")
        print("- Latidos reales no alcanzan el umbral mínimo.")
    else:
        print("\n✅ Se detectó una cantidad razonable de picos. La señal parece viable.")

# 💡 Ejemplo de uso (después de leer y filtrar la señal):
# diagnostico_senal_ecg(tiempos, voltajes_filtrados, fs=250)
