#!/usr/bin/env python3
"""
Monitor de RAM - Ventana simple con Tkinter
Muestra en tiempo real el consumo de memoria RAM y swap.
Optimizado para equipos con poca memoria.
"""

import tkinter as tk
from tkinter import font as tkfont
import os
import subprocess

# ---- Configuración ----
INTERVALO_MS = 1500          # Actualizar cada 1.5 segundos
N_PROCESOS = 5               # Cuántos procesos mostrar


def leer_meminfo():
    """Lee /proc/meminfo y devuelve un diccionario con los valores en KB."""
    datos = {}
    try:
        with open("/proc/meminfo", "r") as f:
            for linea in f:
                partes = linea.split(":")
                if len(partes) == 2:
                    clave = partes[0].strip()
                    valor = partes[1].strip().split()[0]
                    try:
                        datos[clave] = int(valor)
                    except ValueError:
                        pass
    except (OSError, IOError):
        pass
    return datos


def obtener_datos_ram():
    """Devuelve total, usada, disponible, porcentaje y swap en KB."""
    info = leer_meminfo()
    total = info.get("MemTotal", 0)
    disponible = info.get("MemAvailable", info.get("MemFree", 0))
    usada = total - disponible
    porcentaje = (usada / total * 100) if total else 0

    swap_total = info.get("SwapTotal", 0)
    swap_libre = info.get("SwapFree", 0)
    swap_usada = swap_total - swap_libre

    return {
        "total": total,
        "usada": usada,
        "disponible": disponible,
        "porcentaje": porcentaje,
        "swap_total": swap_total,
        "swap_usada": swap_usada,
    }


def obtener_top_procesos(n=5):
    """Devuelve una lista de (nombre, mem_mb) con los procesos que más RAM usan."""
    try:
        salida = subprocess.check_output(
            ["ps", "-eo", "comm,rss", "--sort=-rss", "--no-headers"],
            text=True, timeout=5
        )
    except Exception:
        return []

    procesos = []
    for linea in salida.strip().splitlines():
        partes = linea.split(None, 1)
        if len(partes) == 2:
            nombre = partes[0]
            try:
                mem_mb = int(partes[1]) / 1024
            except ValueError:
                continue
            procesos.append((nombre, mem_mb))
        if len(procesos) >= n:
            break
    return procesos


def kb_a_humano(kb):
    """Convierte KB a un texto legible (MB o GB)."""
    if kb >= 1024 * 1024:
        return f"{kb / (1024 * 1024):.2f} GB"
    return f"{kb / 1024:.0f} MB"


def color_por_porcentaje(p):
    """Verde < 60%, Amarillo < 85%, Rojo >= 85%."""
    if p < 60:
        return "#2ecc71"   # verde
    elif p < 85:
        return "#f1c40f"   # amarillo
    return "#e74c3c"       # rojo


class MonitorRAM:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Monitor de RAM")
        raiz.geometry("360x300")
        raiz.configure(bg="#1e1e1e")
        raiz.resizable(False, False)

        # Fuentes
        self.f_titulo = tkfont.Font(family="Sans", size=11, weight="bold")
        self.f_grande = tkfont.Font(family="Sans", size=32, weight="bold")
        self.f_normal = tkfont.Font(family="Sans", size=10)
        self.f_mono = tkfont.Font(family="Monospace", size=9)

        # Título
        tk.Label(raiz, text="MONITOR DE RAM", bg="#1e1e1e", fg="#aaaaaa",
                 font=self.f_titulo).pack(pady=(12, 4))

        # Porcentaje grande
        self.lbl_porcentaje = tk.Label(raiz, text="0%", bg="#1e1e1e",
                                       fg="#2ecc71", font=self.f_grande)
        self.lbl_porcentaje.pack()

        # Barra de progreso (Canvas)
        self.canvas = tk.Canvas(raiz, width=300, height=22, bg="#333333",
                                highlightthickness=0)
        self.canvas.pack(pady=6)
        self.barra = self.canvas.create_rectangle(2, 2, 2, 20, fill="#2ecc71",
                                                  outline="")

        # Texto usada / total
        self.lbl_detalle = tk.Label(raiz, text="", bg="#1e1e1e", fg="#dddddd",
                                    font=self.f_normal)
        self.lbl_detalle.pack()

        # Swap
        self.lbl_swap = tk.Label(raiz, text="", bg="#1e1e1e", fg="#888888",
                                 font=self.f_normal)
        self.lbl_swap.pack(pady=(2, 8))

        # Top procesos
        tk.Label(raiz, text="Top procesos (RAM)", bg="#1e1e1e", fg="#aaaaaa",
                 font=self.f_titulo).pack()
        self.lbl_procesos = tk.Label(raiz, text="", bg="#1e1e1e", fg="#cccccc",
                                     font=self.f_mono, justify="left", anchor="w")
        self.lbl_procesos.pack(fill="x", padx=20, pady=(2, 10))

        # Botón cerrar
        tk.Button(raiz, text="Cerrar", command=raiz.destroy, bg="#333333",
                  fg="#ffffff", activebackground="#444444", relief="flat",
                  font=self.f_normal, width=10).pack(pady=(0, 10))

        # Iniciar actualización
        self.actualizar()

    def actualizar(self):
        datos = obtener_datos_ram()
        p = datos["porcentaje"]
        color = color_por_porcentaje(p)

        # Porcentaje
        self.lbl_porcentaje.config(text=f"{p:.0f}%", fg=color)

        # Barra
        ancho_max = 296
        ancho = max(2, int(ancho_max * p / 100))
        self.canvas.coords(self.barra, 2, 2, ancho, 20)
        self.canvas.itemconfig(self.barra, fill=color)

        # Detalle
        self.lbl_detalle.config(
            text=f"{kb_a_humano(datos['usada'])} usados de "
                 f"{kb_a_humano(datos['total'])}"
        )

        # Swap
        if datos["swap_total"] > 0:
            self.lbl_swap.config(
                text=f"Swap: {kb_a_humano(datos['swap_usada'])} de "
                     f"{kb_a_humano(datos['swap_total'])}"
            )
        else:
            self.lbl_swap.config(text="Sin swap")

        # Procesos
        lineas = []
        for nombre, mem in obtener_top_procesos(N_PROCESOS):
            lineas.append(f"{nombre[:18]:<18} {mem:>7.1f} MB")
        self.lbl_procesos.config(text="\n".join(lineas))

        # Reprogramar
        self.raiz.after(INTERVALO_MS, self.actualizar)


def main():
    raiz = tk.Tk()
    MonitorRAM(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
