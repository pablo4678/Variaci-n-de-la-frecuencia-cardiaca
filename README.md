# Variación-de-la-frecuencia-cárdiaca
## Fundamento teórico
# Sistema Nervioso Autónomo 
El Sistema Nervioso Autónomo regula funciones involuntarias como la frecuencia cardíaca, la presión arterial y la digestión. Se divide en dos sistemas principales, el sistema simpático se encarga de la respuesta huida aumentando la frecuencia cardíaca (disminuye el HVR). El sistema parasimpático disminuye la frecuencia cardíaca y se  activa en reposo o durante la recuperación (Aumenta el HVR).

## Variabilidad de la Frecuencia Cardíaca (HRV)  
La HRV es una medida de las variaciones en el intervalo entre latidos consecutivos (intervalos R-R del ECG).

## Transformada Wavelet
Es una herramienta matemática que permite analizar señales que cambian a lo largo del tiempo, como la señal del ECG.La transformada de wavelet descompone una señal en ondas pequeñas(wavelts) que estan tanto en tiempo como en frecuencia, permitiendo así mostrar que frecuencias están presententes y cuando.
## Wavelet cmor
La wavelet Morlet compleja es una onda sinusoidal modulada por una función gaussiana, esta al ser compleja también da información de la fase de la señal, esta se utiliza ya que permite detectar cambios suaves y graduales en las frecuencias asociadas al sistema autónomo, ayuda a visualizar cómo cambian estas frecuencias a lo largo del tiempo y permite identificar fluctuaciones rítmicas.

## Diagrama de flujo
![image](https://github.com/user-attachments/assets/b05c2db5-c9fe-4d7b-972b-cfe95a10ea82)



## Diseño del experimento y adquisición de la señal.
Se tomó la señal electrocardiográfica del paciente durante un lapso de tiempo de 6 minutos, durante los primeros 2 minutos el sujeto está en un estado de relajación absoluto con los ojos cerrados y como único estímulo música relajante, durante los siguientes dos minutos ese espera medir la actividad basal del sujeto, en este periodo de tiempo el sujeto está con los ojos abiertos entablando una conversación, finalmente durante los últimos 2 minutos este se expone a un estímulo estresante, en este caso videos de terror.

El código para exportar y graficar la señal es el siguiente:
```
def leer_archivo(nombre_archivo):
    tiempos = []
    voltajes = []

    with open(nombre_archivo, 'r') as archivo:
        # Saltar la primera línea (encabezados)
        next(archivo)

        for linea in archivo:
            # Eliminar espacios en blanco y dividir la línea
            datos = linea.strip().split()

            # Asegurarse de que hay al menos 2 columnas
            if len(datos) >= 2:
                try:
                    tiempo = float(datos[0])
                    voltaje = float(datos[2])
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
```
## Preprocesamiento de la señal y diseño del filtro
Para filtrar la señal se usó un filtro tipo pasabanda con frecuencias de corte entre 0,5 Hz y 40 Hz.
El filtro usado es de tipo IIR, tienen mayor atenuación que un filtro FIR del mismo orden, lo que permite un filtrado más eficiente (más atenuación usando la misma cantidad de procesamiento) el filtro usado también es de tipo Butterworth pues este tiene una plana hasta la frecuencia de corte y después disminuye 80dB por década para el filtro elegido de orden 4 es de 80dB por década.
código para filtrado:
```
fs=250
def filtro_pasabanda(voltajes, fs, lowcut=0.5, highcut=40, orden=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(orden, [low, high], btype='band')
    voltajes_filtrados = filtfilt(b, a, voltajes)
    return voltajes_filtrados
```
## Calculo de la frecuencia cárdiaca y análisis de la señal
Para hacer el análisis de la señal y analisar la variacion de la frecuencia cardiaca HRV. Se usaron las siguientes funciones:
### detectar_picos_r
Esta función detecta los picos, haciendo uso del voltaje de umbral y el tiempo mínimo entre 2 picos
```
def detectar_picos_r(tiempos, voltajes_filtrados, fs, umbral_altura=0.5, min_intervalo_s=0.6):
    distancia_muestras = int(fs * min_intervalo_s)
    picos, propiedades = find_peaks(voltajes_filtrados,distance=distancia_muestras,height=umbral_altura)
    tiempos_picos = [tiempos[i] for i in picos]
    return picos, tiempos_picos
```
### calcular_rr_intervals
Calcula la diferencia en tiempo entre cada par de picos R consecutivos
```
def calcular_rr_intervals(tiempos_picos):
    rr_intervals = np.diff(tiempos_picos)
    return rr_intervals
```
### calcular_hrv_tiempo
Realiza el análisis de la variación de la frecuencia cardiaca en el tiempo, esto lo logra mediante los siguientes parametros:
-SDNN: desviación estándar de los RR.

-RMSSD: raíz cuadrada de la media de las diferencias cuadradas sucesivas.

-pNN50: % de diferencias RR > 50 ms.

-media_rr: promedio de todos los RR.
```
def calcular_hrv_tiempo(rr_intervals):
    rr_intervals = np.array(rr_intervals)

    # Diferencias sucesivas
    rr_diff = np.diff(rr_intervals)

    # SDNN: desviación estándar de los RR
    sdnn = np.std(rr_intervals)

    # RMSSD: raíz de la media de las diferencias cuadradas sucesivas
    rmssd = np.sqrt(np.mean(rr_diff**2))

    # pNN50: porcentaje de diferencias sucesivas > 50 ms
    pnn50 = np.sum(np.abs(rr_diff) > 0.05) / len(rr_diff) * 100

    # Media de RR
    media_rr = np.mean(rr_intervals)

    return {
        'SDNN (s)': sdnn,
        'RMSSD (s)': rmssd,
        'pNN50 (%)': pnn50,
        'Media RR (s)': media_rr
    }
```















