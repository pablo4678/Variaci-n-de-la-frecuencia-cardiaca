# Variación-de-la-frecuencia-cárdiaca
## Fundamento teórico
### Sistema Nervioso Autónomo 
El Sistema Nervioso Autónomo regula funciones involuntarias como la frecuencia cardíaca, la presión arterial y la digestión. Se divide en dos sistemas principales, el sistema simpático se encarga de la respuesta huida aumentando la frecuencia cardíaca (disminuye el HVR). El sistema parasimpático disminuye la frecuencia cardíaca y se  activa en reposo o durante la recuperación (Aumenta el HVR).

### Variabilidad de la Frecuencia Cardíaca (HRV)  
La HRV es una medida de las variaciones en el intervalo entre latidos consecutivos (intervalos R-R del ECG).

### Transformada Wavelet
Es una herramienta matemática que permite analizar señales que cambian a lo largo del tiempo, como la señal del ECG.La transformada de wavelet descompone una señal en ondas pequeñas(wavelts) que estan tanto en tiempo como en frecuencia, permitiendo así mostrar que frecuencias están presententes y cuando.
### Wavelet cmor
La wavelet Morlet compleja es una onda sinusoidal modulada por una función gaussiana, esta al ser compleja también da información de la fase de la señal, esta se utiliza ya que permite detectar cambios suaves y graduales en las frecuencias asociadas al sistema autónomo, ayuda a visualizar cómo cambian estas frecuencias a lo largo del tiempo y permite identificar fluctuaciones rítmicas.

## Diagrama de flujo
![image](https://github.com/user-attachments/assets/b05c2db5-c9fe-4d7b-972b-cfe95a10ea82)

## Diseño del experimento y adquisición de la señal.
Se tomó la señal electrocardiográfica del paciente durante un lapso de tiempo de 5 minutos, durante los primeros 2 minutos el sujeto está en un estado de relajación absoluto con los ojos cerrados y como único estímulo música relajante, durante los siguientes dos minutos ese espera medir la actividad basal del sujeto, en este periodo de tiempo el sujeto está con los ojos abiertos entablando una conversación, finalmente durante el último minuto este se expone a un estímulo estresante, en este caso videos de terror.
Para la adquicicon de la señal se hizo uso de la stm32, un moludo de electrocardiograma, y un codigo de MATLAB

Codigo de MATLAB para la adquicion de la señal:

```
clear; clc;

% Configuración del puerto serie
PORT = "COM4";  
BAUDRATE = 115200;  
BUFFER_SIZE = 100;  % Número de muestras a graficar en tiempo real
ADC_RESOLUTION = 4095;  % Ajusta según tu ADC (4095 para 12 bits, 1023 para 10 bits)
VREF = 3.3;  % Voltaje de referencia del ADC

% Inicializar conexión serie
ser = serialport(PORT, BAUDRATE);
configureTerminator(ser, "LF"); % Configurar terminador de línea
flush(ser); % Limpiar buffer de entrada

disp(['Conectado a ', PORT, ' a ', num2str(BAUDRATE), ' baudios']);

% Buffers para almacenar todos los datos grabados
recorded_time = [];
recorded_voltage = [];

% Buffers para gráfica en tiempo real
time_buffer = nan(1, BUFFER_SIZE);
voltage_buffer = nan(1, BUFFER_SIZE);
start_time = tic;  % Tiempo inicial

% Configurar la gráfica
figure;
hold on;
hLine = animatedline('Marker', 'o', 'Color', 'b');
xlabel('Tiempo (s)');
ylabel('Voltaje (V)');
title('Señal en Tiempo Real');
ylim([0 VREF]);
grid on;

% Duración de la grabación (5 minutos)
DURATION = 300; % en segundos

% Bucle de adquisición de datos
while toc(start_time) < DURATION
    if ser.NumBytesAvailable >= 2
        raw_data = read(ser, 2, "uint8");
        int_value = bitor(bitshift(raw_data(1), 8), raw_data(2));
        voltage = (int_value * VREF) / ADC_RESOLUTION;
        current_time = toc(start_time);
        
        % Guardar en buffers de grabación
        recorded_time(end+1) = current_time;
        recorded_voltage(end+1) = voltage;
        
        % Desplazar buffers de la gráfica
        time_buffer = [time_buffer(2:end), current_time];
        voltage_buffer = [voltage_buffer(2:end), voltage];
        
        % Actualizar gráfica
        addpoints(hLine, current_time, voltage);
        xlim([max(0, current_time - 5), current_time + 0.5]);
        drawnow;
        
        % Mostrar datos
        fprintf('Decimal: %d | Voltaje: %.3f V | Tiempo: %.2f s\n', int_value, voltage, current_time);
    end
    pause(0.01);
end

% Guardar datos
save('datos_EMG.mat', 'recorded_time', 'recorded_voltage');
disp('Grabación finalizada. Datos guardados en "datos_EMG.mat".');
```
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
![image](https://github.com/user-attachments/assets/2acba5dd-3424-4d47-9e2c-3c282a3335ad)

## Preprocesamiento de la señal y diseño del filtro
Para filtrar la señal se usó un filtro tipo pasabanda con frecuencias de corte entre 0,5 Hz y 40 Hz.
El filtro usado es de tipo IIR, tienen mayor atenuación que un filtro FIR del mismo orden, lo que permite un filtrado más eficiente (más atenuación usando la misma cantidad de procesamiento) el filtro usado también es de tipo Butterworth pues este tiene una plana hasta la frecuencia de corte y después disminuye 80dB por década para el filtro elegido de orden 4 es de 80dB por década.
La frecuencia de muestreo es de 250, teniendo en cuenta el teorema de Nyquist que establece que la frecuencia de muestreo debe ser más del doble de la frecuencia máxima de la señal, dado que la frecuencia máxima de las señales electrocardiograficas es 100Hz se escoge 250Hz como frecuencia de muestreo.

Después se halla la frecuencia de Nyquist  
![ecuación](https://latex.codecogs.com/svg.image?F_{N}=\frac{F_{s}}{2}=125&space;)

Se normalizan las frecuencias de corte 

![ecuación](https://latex.codecogs.com/svg.image?F_{low}=\frac{0.5}{125}=0.004&space;)

![ecuación](https://latex.codecogs.com/svg.image?F_{high}=\frac{40}{125}=0.32&space;)

Estas frecuencias normalizadas se colocan como parametros para realizar el filtro
```
nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(orden, [low, high], btype='band')
```

### Ecuacion en diferencias del filtro
![ecuación](https://latex.codecogs.com/svg.image?y[n]=\sum_{k=1}^{8}a_{k}y[n-k]&plus;\sum_{k=0}^{8}b_{k}y[n-k])

La sumatoria va hasta ocho dado que es un filtro pasabanda de orden 4, entonces el orden se duplica, en realidad se estaria generando un filtro de orden 8, cuatro pares de polos para cada orden de banda. Se utilizó el sigiente codigo para hallar los coeficiente a y b.
```
b, a = butter(4, [0.004, 0.32], btype='band')
print("a")
print(a)
print("b")
print(b)

```
![image](https://github.com/user-attachments/assets/3fbb6be6-cfaa-4dbf-b409-1686562b3af1)

![ecuación](https://latex.codecogs.com/svg.image?y[n]=5.4062\,y[n-1]-12.7689\,y[n-2]&plus;17.4196\,y[n-3]-15.1907\,y[n-4]&plus;8.7164\,y[n-5]-3.1973,y[n-6]&plus;0.6804\,y[n-7]-0.0656\,y[n-8]&plus;0.02196\,x[n]-0.08785\,x[n-2]&plus;0.13177,x[n-4]-0.08785\,x[n-6]&plus;0.02196\,x[n-8])
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
![image](https://github.com/user-attachments/assets/a582c64c-cfd8-409e-9a8f-9fd871d42c83)

### Detectar picos R
Primero se normaliza la señal para que tenga media cero y desviación estándar uno. Luego define un umbral adaptativo usando el percentil 50 (la mediana) de la señal normalizada y establece una distancia mínima de 30 ms entre picos, en función de la frecuencia de muestreo `fs`. Utiliza la función `find_peaks` de SciPy para detectar los picos que cumplen con estos criterios, y convierte sus índices a tiempos correspondientes. Si `plot=True`, grafica la señal normalizada junto con los picos detectados. Finalmente, retorna los índices de los picos y sus tiempos.
```
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
        plt.title('Detección de Picos R (ajustada e inteligente)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('ECG (normalizado)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        print(f"Se detectaron {len(picos)} picos R.")

    return picos, tiempos_picos
```
![image](https://github.com/user-attachments/assets/379afaa2-9c0c-4e22-89b2-3e6beff200fb)

![image](https://github.com/user-attachments/assets/16a74185-f892-4f4c-9c07-584edde31e94)

### Calcular R-R intervals y crear señal R-R
La función `calcular_rr_intervals` calcula los intervalos RR, que representan el tiempo entre latidos cardíacos consecutivos, tomando la diferencia entre los tiempos de los picos R usando `np.diff`. Luego, `crear_senal_rr` genera una señal continua del mismo largo que el vector de tiempos, donde cada segmento entre dos picos R se llena con el valor del intervalo R-R correspondiente.
```
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
```
## Calcular HRV en el tiempo
Se calcula métricas de variabilidad de la frecuencia cardíaca (HRV) en el dominio del tiempo a partir de los intervalos RR. Se convierten los intervalos a un arreglo NumPy, calcula las diferencias entre intervalos consecutivos (`rr_diff`) y luego computa: **SDNN**, la desviación estándar de los RR (variabilidad general); **RMSSD**, la raíz del promedio de las diferencias cuadráticas entre RR consecutivos (sensibilidad a cambios rápidos); **pNN50**, el porcentaje de diferencias sucesivas mayores a 50 ms (indicador de tono parasimpático); y la **media de los intervalos RR**, que refleja la frecuencia cardíaca promedio.
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
![image](https://github.com/user-attachments/assets/d999ac38-fcb3-408c-993f-7400e9b05c09)

## Calcular HRV en la frecuencia
Antes de aplicar la tranformada Wavelet es importante interpolar la señal, para garantizar que la señal esté adecuadamente muestreada y alineada con la frecuencia de muestreo deseada, evitando posibles efectos de aliasing o distorsión.

```
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

```
La función `espectrograma_wavelet` analiza una señal temporal usando la Transformada Wavelet Continua (CWT), que descompone la señal en diferentes frecuencias a lo largo del tiempo. Utiliza una wavelet llamada `cmor1.5-1.0`, que es una wavelet compleja de Morlet. Los números 1.5 y 1.0 indican cómo se comporta esta wavelet: el 1.5 controla lo "ancha" o "estrecha" que es la onda en términos de frecuencia (más ancho, menor resolución en el tiempo) y el 1.0 indica cuántas oscilaciones hace la onda portadora. Esto ayuda a capturar diferentes componentes de la señal en distintas escalas. Además, la función define un rango de escalas (de 1 a 127) que ajusta la resolución temporal y frecuencial según el análisis. Luego, calcula la potencia espectral de la señal (basada en los coeficientes de la wavelet) y genera un espectrograma visual, resaltando bandas de baja frecuencia (LF) y alta frecuencia (HF) con líneas horizontales. Finalmente, se analiza cómo cambia la potencia en estas bandas a lo largo del tiempo, mostrando una gráfica que ilustra la evolución de la potencia en estas frecuencias.
```
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
```
![image](https://github.com/user-attachments/assets/570167f5-67a2-4449-841b-52944b050a9e)
![image](https://github.com/user-attachments/assets/83e9726b-f10c-4d18-9f93-f3828dccb96e)

## Evualuación del estres 
### En el tiempo
Se evalúa el nivel de estrés del sistema nervioso autónomo utilizando métricas de la variabilidad de la frecuencia cardíaca (HRV) medidas en el dominio del tiempo. Toma como entrada un diccionario que contiene tres métricas clave: SDNN, RMSSD y pNN50. Cada una refleja distintos aspectos de la actividad cardíaca y del sistema nervioso. Si SDNN (desviación estándar de los intervalos RR) es menor a 0.05 segundos, se interpreta como una baja variabilidad, lo que podría indicar estrés. Si RMSSD, que está más relacionado con el control del nervio vago (parasimpático), es menor a 0.03 segundos, también sugiere una baja regulación parasimpática. Finalmente, un valor de pNN50 menor al 10% indica que el tono parasimpático es bajo. En conjunto, esta función permite hacer una evaluación rápida de si el sistema nervioso está bajo estrés o si está en un estado equilibrado.
```
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
```
![image](https://github.com/user-attachments/assets/7a9912e9-332a-42ba-a5a5-28c644800770)

### En la frecuencia
Analiza el estrés en el dominio de la frecuencia a partir de los intervalos RR. Primero, interpola los datos para convertirlos en una señal uniforme en el tiempo, lo cual es necesario para aplicar análisis espectral. Luego, usa el método de Welch para calcular el espectro de potencia, es decir, cómo se distribuye la energía de la señal en diferentes frecuencias. El análisis se centra en dos bandas: la banda de baja frecuencia (LF: 0.04 a 0.15 Hz), que refleja tanto la actividad simpática como parasimpática, y la banda de alta frecuencia (HF: 0.15 a 0.4 Hz), que se asocia principalmente con la actividad parasimpática. La relación entre estas dos bandas (LF/HF ratio) se interpreta como un indicador del balance autonómico: un valor alto sugiere predominancia simpática (estrés), mientras que un valor bajo indica predominancia parasimpática (relajación).
```
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
```
![image](https://github.com/user-attachments/assets/88e60f10-c16f-4f6c-ad46-d7ca02415c05)

## Análisis
Después de realizar el experimento, tomar y procesar la señal se llegaron a algunas conclusiones y análisis. En primer lugar el uso de filtros IIR, y la normalizacion de la señal fueron fundamentales para poder hacer un correcto análisis de la señal, al realizar el análisis de la señal en el tiempo nos dió una idea general del nivel de actividad simpática y parasimpática del sujeto, sin embargo esta información es insuficiente para correlacionar los estímulos producidos, con la respuesta fisiológica esperada.
De entre todas las transformadas wavelet se eligió Morlet compleja (cmor1.5-1.0), ya que esta es especialmente adecuada para analizar señales suaves y no estacionarias como el ECG, y permite obtener información tanto de frecuencia como de fase. 
Si se utilizaran otras wavelets, como Haar o Daubechies, los resultados podrían variar sen el caso de la tipo Haar esta cuenta con mejor resolución temporal, lo cual es útil para detectar eventos rápidos, pero sacrifican precisión en la resolución frecuencial. Por otro lado, wavelets más largas como las Daubechies permiten una mejor discriminación en frecuencia, pero tienden a suavizar los detalles temporales rápidos. Por ello, la elección de la wavelet tiene un impacto directo en la capacidad para identificar con precisión las bandas de baja frecuencia (LF) y alta frecuencia (HF), lo que a su vez afecta la interpretación del estado del sistema nervioso autónomo.
Con el análisis en tiempo-frecuencia usando la transformada wavelet, intentamos responder la pregunta problema de si el estrés produce alteraciones en la variabilidad de la frecuencia cardiaca, después de tener la hipótesis de que si afecta de manera importante la hrv, se planteo el experimento donde el sujeto estará en 3 estados diferentes de relajación, una de relajación completa, una de nivel medio y finalmente una de estrés (esto se explica más a detalle en el apartado de diseño del experimento), después de aplicar la transformada wavelet tipo Morlet, se ve como hay un predominio de la actividad parasimpática indicando la relajación en los primeros dos minutos, al interrumpir la actividad relajante y hacer que el sujeto abra los ojos se ve un claro aumento en la potencia espectral de las frecuencias de la banda de alta frecuencia indicando un pico en la actividad simpática, luego de este cambio vuelve a bajar y no aumenta hasta ser sometido a un estímulo estresante.
## Bibliografía
Montoya, J. R. A. (2001). La transformada  wavelet. https://www.um.edu.ar/ojs2019/index.php/RUM/article/view/22
Kim, H. J., Park, Y., & Lee, J. (2024). The Validity of Heart Rate Variability (HRV) in Educational Research and a Synthesis of Recommendations. Educational Psychology Review, 36(2). https://doi.org/10.1007/s10648-024-09878-x
## Colaboradores
* Catalina Martínez 
* Pablo Acevedo
* Laura Ávila







