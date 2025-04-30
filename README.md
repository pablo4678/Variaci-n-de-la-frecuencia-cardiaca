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















