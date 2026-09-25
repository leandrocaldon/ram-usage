# Monitor de RAM

Ventana pequeña en Python que muestra el uso de memoria en tiempo real. Está pensada para equipos con poca RAM: no instala dependencias y solo lee datos del sistema.

## Qué muestra

- Porcentaje de RAM usada, con color según el nivel: verde por debajo del 60 %, amarillo por debajo del 85 % y rojo a partir del 85 %.
- Historial de las últimas 60 lecturas (unos 90 segundos).
- Cantidad usada y total.
- Memoria en caché (`Buffers` + `Cached`).
- Uso de swap, o el aviso «Sin swap» si no hay.
- Los 5 procesos que más memoria residente ocupan, con su PID.

Al cruzar el 85 % se muestra un aviso del sistema con `notify-send`, si está instalado. No se repite hasta que el uso baje de ese nivel.

Los datos se actualizan cada 1,5 segundos. La RAM sale de `/proc/meminfo` y la lista de procesos de `ps`.

## Requisitos

- Linux
- Python 3 con Tkinter

En Debian o Ubuntu, si falta Tkinter:

```bash
sudo apt install python3-tk
```

## Uso

```bash
python3 ram_monitor.py
```

La ventana mide 360×390 y no se puede redimensionar. El botón **Cerrar** termina el programa.
