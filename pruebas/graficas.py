"""Graficas del reporte a partir de pruebas/resultados.csv.

Autor: Fernando Hernandez (23645)

Genera en pruebas/graficas/:
  exito_vs_tasa.png        tasa de entrega correcta vs prob. de error, por algoritmo
  no_detectados_vs_tasa.png errores que pasaron sin detectarse vs prob. de error
  overhead_vs_tamano.png   redundancia enviada segun tamano del mensaje
  desglose_resultados.png  desglose exito/detectado/no detectado por algoritmo

Uso:
    python3 pruebas/graficas.py
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CSV = os.path.join(RAIZ, "pruebas", "resultados.csv")
DIR_SALIDA = os.path.join(RAIZ, "pruebas", "graficas")

# Paleta categorica (validada para daltonismo) y colores de estado
COLOR_ALGO = {"hamming": "#2a78d6", "crc32": "#eb6834"}
ETIQUETA_ALGO = {"hamming": "Hamming (12,8)", "crc32": "CRC-32"}
COLOR_ESTADO = {"exito": "#0ca30c", "detectado": "#fab219", "no_detectado": "#d03b3b"}
ETIQUETA_ESTADO = {
    "exito": "Éxito",
    "detectado": "Error detectado",
    "no_detectado": "Error NO detectado",
}
TINTA = "#0b0b0b"
TINTA_SUAVE = "#52514e"
REJILLA = "#e4e4e1"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": REJILLA,
    "axes.labelcolor": TINTA,
    "axes.titlecolor": TINTA,
    "text.color": TINTA,
    "xtick.color": TINTA_SUAVE,
    "ytick.color": TINTA_SUAVE,
    "grid.color": REJILLA,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def cargar():
    with open(RUTA_CSV) as archivo:
        return [
            {
                "algoritmo": f["algoritmo"],
                "n_caracteres": int(f["n_caracteres"]),
                "tasa_error": float(f["tasa_error"]),
                "bits_datos": int(f["bits_datos"]),
                "bits_trama": int(f["bits_trama"]),
                "resultado": f["resultado"],
            }
            for f in csv.DictReader(archivo)
        ]


def proporcion(filas, resultado):
    """Agrupa por (algoritmo, tasa) y devuelve la proporcion de `resultado`."""
    conteo = defaultdict(lambda: [0, 0])
    for f in filas:
        clave = (f["algoritmo"], f["tasa_error"])
        conteo[clave][1] += 1
        if f["resultado"] == resultado:
            conteo[clave][0] += 1
    series = {}
    for (algoritmo, tasa), (casos, total) in sorted(conteo.items()):
        series.setdefault(algoritmo, ([], []))
        series[algoritmo][0].append(tasa)
        series[algoritmo][1].append(100.0 * casos / total)
    return series


def nueva_figura(titulo, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=200)
    ax.set_title(titulo, loc="left", fontsize=12, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", linewidth=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def lineas_por_algoritmo(series, titulo, ylabel, nombre):
    fig, ax = nueva_figura(titulo, "Probabilidad de error por bit", ylabel)
    for algoritmo in ("hamming", "crc32"):
        if algoritmo not in series:
            continue
        tasas, valores = series[algoritmo]
        ax.plot(
            tasas, valores,
            color=COLOR_ALGO[algoritmo], label=ETIQUETA_ALGO[algoritmo],
            linewidth=2, marker="o", markersize=7,
            markeredgecolor="white", markeredgewidth=1,
        )
    ax.set_xscale("log")
    ax.set_ylim(-3, 103)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_SALIDA, nombre), bbox_inches="tight")
    plt.close(fig)


def grafica_overhead(filas):
    overhead = defaultdict(dict)  # algoritmo -> n_caracteres -> %
    for f in filas:
        extra = 100.0 * (f["bits_trama"] - f["bits_datos"]) / f["bits_datos"]
        overhead[f["algoritmo"]][f["n_caracteres"]] = extra
    fig, ax = nueva_figura(
        "Overhead de redundancia según tamaño del mensaje",
        "Tamaño del mensaje (caracteres)", "Overhead (%)",
    )
    for algoritmo, puntos in overhead.items():
        tam = sorted(puntos)
        vals = [puntos[t] for t in tam]
        ax.plot(
            tam, vals,
            color=COLOR_ALGO[algoritmo], label=ETIQUETA_ALGO[algoritmo],
            linewidth=2, marker="o", markersize=7,
            markeredgecolor="white", markeredgewidth=1,
        )
        ax.annotate(
            f"{vals[-1]:.1f}%", (tam[-1], vals[-1]),
            textcoords="offset points", xytext=(8, 0),
            color=COLOR_ALGO[algoritmo], fontsize=10, va="center",
        )
    ax.set_xscale("log", base=2)
    ax.set_xticks(sorted({f["n_caracteres"] for f in filas}))
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_SALIDA, "overhead_vs_tamano.png"), bbox_inches="tight")
    plt.close(fig)


def grafica_desglose(filas, tasas_mostrar=(0.005, 0.02, 0.1)):
    conteo = defaultdict(lambda: defaultdict(int))  # (algo, tasa) -> resultado -> n
    total = defaultdict(int)
    for f in filas:
        if f["tasa_error"] in tasas_mostrar:
            clave = (f["algoritmo"], f["tasa_error"])
            conteo[clave][f["resultado"]] += 1
            total[clave] += 1

    grupos = [(a, t) for a in ("hamming", "crc32") for t in tasas_mostrar]
    etiquetas = [f"{'Hamming' if a == 'hamming' else 'CRC-32'}\np={t}" for a, t in grupos]
    fig, ax = nueva_figura(
        "Desglose de resultados por algoritmo y probabilidad de error",
        "", "Porcentaje de envíos (%)",
    )
    base = [0.0] * len(grupos)
    for resultado in ("exito", "detectado", "no_detectado"):
        alturas = [
            100.0 * conteo[g].get(resultado, 0) / total[g] for g in grupos
        ]
        ax.bar(
            etiquetas, alturas, bottom=base,
            color=COLOR_ESTADO[resultado], label=ETIQUETA_ESTADO[resultado],
            width=0.62, edgecolor="white", linewidth=2,
        )
        for i, (altura, b) in enumerate(zip(alturas, base)):
            if altura >= 8:  # etiqueta directa solo si el segmento es legible
                ax.text(
                    i, b + altura / 2, f"{altura:.0f}%",
                    ha="center", va="center", fontsize=9, color="white",
                    fontweight="bold",
                )
        base = [b + a for b, a in zip(base, alturas)]
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_SALIDA, "desglose_resultados.png"), bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(DIR_SALIDA, exist_ok=True)
    filas = cargar()
    lineas_por_algoritmo(
        proporcion(filas, "exito"),
        "Entrega correcta según probabilidad de error",
        "Envíos entregados sin corrupción (%)",
        "exito_vs_tasa.png",
    )
    lineas_por_algoritmo(
        proporcion(filas, "no_detectado"),
        "Errores que pasaron sin detectarse",
        "Envíos corruptos aceptados (%)",
        "no_detectados_vs_tasa.png",
    )
    grafica_overhead(filas)
    grafica_desglose(filas)
    print(f"Graficas en {DIR_SALIDA}/")


if __name__ == "__main__":
    main()
