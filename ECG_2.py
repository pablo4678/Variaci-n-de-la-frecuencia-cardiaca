import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, welch
import numpy as np
import pywt
from scipy.interpolate import interp1d

def leer_archivo(nombre_archivo):
    tiempos = []
    voltajes = []
    with open(nombre_archivo, 'r') as archivo:
        next(archivo)
        for linea in archivo:
            datos = linea.strip().split()
            if len(datos) >= 1:
                try:
                    tiempo = float(datos[0])
                    voltaje = float(datos[1])
                    tiempos.append(tiempo)
                    voltajes.append(voltaje)
                except ValueError:
                    print(f"Advertencia: No se pudo convertir los valores en la línea: {linea}")
    return tiempos, voltajes

def graficar(tiempos, voltajes):
    plt.figure(figsize=(10, 5))
    plt.plot(tiempos, voltajes, 'b-', linewidth=1, marker='o', markersize=4)
    plt.title('Gráfica Tiempo vs Voltaje')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Voltaje (mV)')
    plt.grid(True)
    plt.show()

fs = 250

def filtro_pasabanda(voltajes, fs, lowcut=0.5, highcut=40, orden=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(orden, [low, high], btype='band')
    voltajes_filtrados = filtfilt(b, a, voltajes)
    return voltajes_filtrados

def graficar2(tiempos, voltajes_filtrados):
    plt.figure(figsize=(10, 5))
    plt.plot(tiempos, voltajes_filtrados, 'r-', linewidth=1)
    plt.title('ECG Filtrado (0.5 Hz - 40 Hz)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Voltaje (mV)')
    plt.grid(True)
    plt.show()

def detectar_picos_r(tiempos, voltajes_filtrados, fs, plot=True):
 
    ecg_norm = (voltajes_filtrados - np.mean(voltajes_filtrados)) / np.std(voltajes_filtrados)    # Normalización
    
    distancia_muestras = int(0.03 * fs)  # Probar con 30 ms 
    umbral_altura = np.percentile(ecg_norm, 50)  # Ajustar umbral adaptativo al percentil 50 o 60
    picos, _ = find_peaks(ecg_norm, distance=distancia_muestras, height=umbral_altura)
    tiempos_picos = [tiempos[i] for i in picos]
    
    if plot:
        plt.figure(figsize=(12, 4))
        plt.plot(tiempos, ecg_norm, label='ECG normalizado')
        plt.plot(np.array(tiempos)[picos], ecg_norm[picos], 'ro', label='Picos R detectados')
        plt.title('Detección de Picos R')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('ECG (normalizado)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        print(f"Se detectaron {len(picos)} picos R.")

    return picos, tiempos_picos

def calcular_rr_intervals(tiempos_picos):
    return np.diff(tiempos_picos)

def crear_senal_rr(tiempos, indices_r, rr_intervals):
    senal_rr = np.zeros(len(tiempos))
    for i in range(1, len(indices_r)):
        inicio = indices_r[i - 1]
        fin = indices_r[i]
        rr = rr_intervals[i - 1]
        senal_rr[inicio:fin] = rr
    if len(indices_r) > 1:
        senal_rr[indices_r[-1]:] = rr_intervals[-1]
    return senal_rr

def calcular_hrv_tiempo(rr_intervals):
    rr_intervals = np.array(rr_intervals)
    rr_diff = np.diff(rr_intervals)
    sdnn = np.std(rr_intervals)
    rmssd = np.sqrt(np.mean(rr_diff**2))
    pnn50 = np.sum(np.abs(rr_diff) > 0.05) / len(rr_diff) * 100
    media_rr = np.mean(rr_intervals)
    return {
        'SDNN (s)': sdnn,
        'RMSSD (s)': rmssd,
        'pNN50 (%)': pnn50,
        'Media RR (s)': media_rr
    }

def interpolar_rr(tiempos_r, rr_intervals, fs_interpolado=4):
    # Asegurar que rr_intervals tenga misma longitud que tiempos_r[1:]
    if len(rr_intervals) != len(tiempos_r) - 1:
        raise ValueError("rr_intervals debe tener una longitud de len(tiempos_r) - 1")

    # Usar los tiempos entre picos (tiempos medios) para interpolar
    tiempos_rr = [(tiempos_r[i] + tiempos_r[i+1]) / 2 for i in range(len(rr_intervals))]

    tiempo_interp = np.arange(tiempos_rr[0], tiempos_rr[-1], 1 / fs_interpolado)
    interp_func = interp1d(tiempos_rr, rr_intervals, kind='cubic', fill_value='extrapolate')
    rr_uniforme = interp_func(tiempo_interp)

    return tiempo_interp, rr_uniforme


def espectrograma_wavelet(tiempo_interp, rr_uniforme, fs_interp):
    wavelet = 'cmor1.5-1.0'
    scales = np.arange(1, 128)
    coef, freqs = pywt.cwt(rr_uniforme, scales, wavelet, sampling_period=1/fs_interp)
    potencias = np.abs(coef)**2

    # Espectrograma limpio y con líneas claras de frecuencia
    plt.figure(figsize=(12, 6))
    plt.imshow(potencias, extent=[tiempo_interp.min(), tiempo_interp.max(), freqs.min(), freqs.max()],
               cmap='jet', aspect='auto', origin='lower', vmax=np.percentile(potencias, 99))
    
    # Líneas horizontales para bandas LF y HF
    plt.axhline(0.04, color='white', linestyle='-', linewidth=2, label='0.04 Hz (Límite LF)')
    plt.axhline(0.15, color='cyan', linestyle='-', linewidth=2, label='0.15 Hz (Límite HF)')
    plt.axhline(0.4, color='magenta', linestyle='-', linewidth=2, label='0.4 Hz')

    plt.colorbar(label='Potencia espectral')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Frecuencia (Hz)')
    plt.title('Espectrograma Wavelet Continua')
    plt.legend(loc='upper right')
    plt.grid(False)  
    plt.tight_layout()
    plt.show()

    # Análisis de potencia en bandas LF y HF
    lf_band = (freqs >= 0.04) & (freqs <= 0.15)
    hf_band = (freqs > 0.15) & (freqs <= 0.4)
    pot_lf = np.mean(potencias[lf_band, :], axis=0)
    pot_hf = np.mean(potencias[hf_band, :], axis=0)

    # Gráfica de evolución de potencia en el tiempo
    plt.figure(figsize=(12, 5))
    plt.plot(tiempo_interp, pot_lf, label='Potencia LF (0.04–0.15 Hz)', color='orange')
    plt.plot(tiempo_interp, pot_hf, label='Potencia HF (0.15–0.4 Hz)', color='green')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Potencia relativa')
    plt.title('Evolución de la potencia LF y HF')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def analizar_estres_tiempo(hrv_metrica):
    sdnn = hrv_metrica['SDNN (s)']
    rmssd = hrv_metrica['RMSSD (s)']
    pnn50 = hrv_metrica['pNN50 (%)']
    
    print("\n--- Evaluación de Estrés en el Dominio del Tiempo ---")
    if sdnn < 0.05:
        print("SDNN bajo (posible estrés)")
    else:
        print("SDNN adecuado")
    
    if rmssd < 0.03:
        print("RMSSD bajo (posible inhibición vagal)")
    else:
        print("RMSSD adecuado")
    
    if pnn50 < 10:
        print("pNN50 bajo (bajo tono parasimpático)")
    else:
        print("pNN50 adecuado.")

def calcular_estres_frecuencia(rr_intervals, fs=4):
    # Creamos un tiempo acumulado a partir de rr_intervals
    tiempo_total = np.cumsum(rr_intervals)
    if len(tiempo_total) < 2:
        print("No hay suficientes datos para calcular espectro de frecuencia.")
        return
def calcular_estres_frecuencia(rr_intervals, tiempos_r, fs=4):
    if len(rr_intervals) != len(tiempos_r) - 1:
        raise ValueError("rr_intervals debe tener una longitud de len(tiempos_r) - 1")

    tiempos_rr = [(tiempos_r[i] + tiempos_r[i+1]) / 2 for i in range(len(rr_intervals))]
    tiempo_interp = np.arange(tiempos_rr[0], tiempos_rr[-1], 1 / fs)

    interp_func = interp1d(tiempos_rr, rr_intervals, kind='cubic', fill_value='extrapolate')
    rr_interp = interp_func(tiempo_interp)

    freqs, psd = welch(rr_interp, fs=fs, nperseg=min(256, len(rr_interp)))

    # Potencia en bandas LF y HF
    lf_band = (freqs >= 0.04) & (freqs < 0.15)
    hf_band = (freqs >= 0.15) & (freqs < 0.4)
    
    lf_power = np.trapz(psd[lf_band], freqs[lf_band])
    hf_power = np.trapz(psd[hf_band], freqs[hf_band])
    lf_hf_ratio = lf_power / hf_power if hf_power > 0 else np.inf

    print("\n--- Evaluación de Estrés en el Dominio de la Frecuencia ---")
    print(f"LF Power: {lf_power:.4f}")
    print(f"HF Power: {hf_power:.4f}")
    print(f"LF/HF Ratio: {lf_hf_ratio:.2f}")

    if lf_hf_ratio > 2.5:
        print("LF/HF alto - predominancia simpática (estrés).")
    elif lf_hf_ratio < 1.0:
        print("Predominio parasimpático (relajación).")
    else:
        print("Balance simpático-parasimpático razonable.")


# ==================== PROGRAMA PRINCIPAL ========================
nombre_archivo = 'ECG_GRUPO_LAURA.txt'
try:
    tiempos, voltajes = leer_archivo(nombre_archivo)
    graficar(tiempos, voltajes)

    voltajes_filtrados = filtro_pasabanda(voltajes, fs)
    graficar2(tiempos, voltajes_filtrados)
    indices_r, tiempos_r = detectar_picos_r(tiempos, voltajes_filtrados, fs)
    rr_intervals = calcular_rr_intervals(tiempos_r)

    if len(rr_intervals) < 2:
        raise ValueError("No hay suficientes picos R detectados para analizar HRV.")

    senal_rr = crear_senal_rr(tiempos, indices_r, rr_intervals)
    hrv_metrica = calcular_hrv_tiempo(rr_intervals)

    for k, v in hrv_metrica.items():
        print(f"{k}: {v:.4f}")

    analizar_estres_tiempo(hrv_metrica)

    fs_interp = 4
    tiempo_interp, rr_uniforme = interpolar_rr(tiempos_r, rr_intervals, fs_interp)
    espectrograma_wavelet(tiempo_interp, rr_uniforme, fs_interp)

    calcular_estres_frecuencia(rr_intervals, tiempos_r)

except FileNotFoundError:
    print(f"Error: No se encontró el archivo {nombre_archivo}")
except Exception as e:
    print(f"Ocurrió un error: {e}")
