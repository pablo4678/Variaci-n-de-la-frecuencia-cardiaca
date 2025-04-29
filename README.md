# Variación-de-la-frecuencia-cárdiaca
## Diseño del experimento y adquisición de la señal.
Se tomó la señal electrocardiográfica del paciente durante un lapso de tiempo de 6 minutos, durante los primeros 2 minutos el sujet está en un estado de relajación absoluto con los ojos cerrados y como único estímulo música relajante, durante los siguientes dos minutos ese espera medir la actividad basal del sujeto, en este periodo de tiempo el sujeto está con los ojos abiertos entablando una conversación, finalmente durante los últimos 2 minutos este se expone a un estímulo estresante, en este caso videos de terror.

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





