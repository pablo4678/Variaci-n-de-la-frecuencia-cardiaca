% Cargar el archivo .mat generado por tu script
load('datos_EMG.mat'); % Carga recorded_time y recorded_voltage

% Verificar que las variables existen
if ~exist('recorded_time', 'var') || ~exist('recorded_voltage', 'var')
    error('El archivo no contiene las variables expected (recorded_time, recorded_voltage)');
end

% Crear nombre de archivo con marca de tiempo
timestamp = datestr(now, 'yyyy-mm-dd_HH-MM-SS');
output_filename = sprintf('ECG_data_%s.txt', timestamp);

% Abrir archivo para escritura
fileID = fopen(output_filename, 'w');

% Escribir encabezado
fprintf(fileID, 'Tiempo(s)\tVoltaje(V)\tValor_ADC\n');

% Calcular valores ADC (inverso de tu fórmula original)
ADC_values = round(recorded_voltage * 4095 / 3.3);

% Escribir datos
for i = 1:length(recorded_time)
    fprintf(fileID, '%.6f\t%.4f\t%d\n', ...
            recorded_time(i), ...
            recorded_voltage(i), ...
            ADC_values(i));
end

fclose(fileID);

% Mostrar resumen
disp('============================================');
disp(' Conversión completada exitosamente');
disp('============================================');
disp([' Archivo de entrada: datos_EMG.mat']);
disp([' Archivo de salida: ' output_filename]);
disp([' Muestras convertidas: ' num2str(length(recorded_time))]);
disp([' Duración total: ' num2str(max(recorded_time)) ' segundos']);
disp([' Frecuencia promedio: ' num2str(length(recorded_time)/max(recorded_time)) ' Hz']);
disp('============================================');

% Opcional: Graficar para verificar
figure;
subplot(2,1,1);
plot(recorded_time, recorded_voltage);
title('Señal EMG');
xlabel('Tiempo (s)');
ylabel('Voltaje (V)');
grid on;

subplot(2,1,2);
plot(recorded_time, ADC_values);
title('Valores ADC');
xlabel('Tiempo (s)');
ylabel('Valor ADC (0-4095)');
grid on;