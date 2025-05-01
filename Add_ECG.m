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