from pathlib import Path
from typing import Tuple
import matplotlib.pyplot as plt
from simulaciones.SimConfig import (
    ConfigEconomica,
    ConfigPanelSolar,
    ConfigRiego,
    MesClimatico,
    obtener_clima_araucania,
    obtener_consumo_rural_regiones,
)
from simulaciones.SimuladorConsumoRural import (
    ResultadoConsumoRural,
    SimuladorConsumoRural,
)
from simulaciones.SimuladorDiagnostico import (
    ResultadoDiagnostico,
    SimuladorDiagnostico,
)
from simulaciones.SimuladorEconomico import (
    ResultadoEconomico,
    SimuladorEconomico,
)
from simulaciones.SimuladorRiego import ResultadoMensualRiego, SimuladorRiego


CARPETA_REPORTE = Path(__file__).resolve().parent.parent / "report"


def generar_grafico_energia(
    clima: Tuple[MesClimatico, ...],
    panel: ConfigPanelSolar,
    resultados_riego: Tuple[ResultadoMensualRiego, ...],
    ruta_salida: Path,
) -> None:
    meses = [m.nombre_mes for m in clima]
    demanda = [
        r.energia_requerida_wh
        for r in resultados_riego
        if r.salud_panel == panel.niveles_salud[0]
    ]

    plt.figure(figsize=(10, 5.5))
    for salud in panel.niveles_salud:
        energia_mes = [
            r.energia_disponible_wh
            for r in resultados_riego
            if r.salud_panel == salud
        ]
        etiqueta = f"Panel al {int(salud * 100)}%"
        plt.plot(meses, energia_mes, marker="o", linewidth=2, label=etiqueta)

    plt.bar(
        meses,
        demanda,
        color="#2b5c8f",
        alpha=0.35,
        label="Demanda bomba de riego (Wh/día)",
    )
    plt.title("Balance Energético Mensual en La Araucanía (Panel 300 W vs. Riego 100 m²)")
    plt.xlabel("Mes")
    plt.ylabel("Energía diaria (Wh/día)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()


def generar_grafico_economico(
    resultados_eco: Tuple[ResultadoEconomico, ...],
    ruta_salida: Path,
) -> None:
    etiquetas = [f"{int(r.tasa_reutilizacion * 100)}% reutilizable" for r in resultados_eco]
    costos_triaje = [r.costo_con_triaje_usd / 1000.0 for r in resultados_eco]
    base_reciclar = resultados_eco[0].costo_reciclar_todo_usd / 1000.0

    plt.figure(figsize=(8, 5))
    barras = plt.bar(etiquetas, costos_triaje, color="#2e8b57", width=0.45, label="Costo con triaje")
    plt.axhline(
        y=base_reciclar,
        color="#c0392b",
        linestyle="--",
        linewidth=2,
        label=f"Reciclar todo (US$ {base_reciclar:.0f}k)",
    )

    for barra, r in zip(barras, resultados_eco):
        altura = barra.get_height()
        ahorro_k = r.ahorro_neto_usd / 1000.0
        plt.text(
            barra.get_x() + barra.get_width() / 2.0,
            altura + 6,
            f"Ahorro: US${ahorro_k:.0f}k",
            ha="center",
            fontweight="bold",
        )

    plt.ylim(0, base_reciclar * 1.18)
    plt.title("Sensibilidad Económica (Lote de 10.000 paneles)")
    plt.ylabel("Costo Total (Miles de US$)")
    plt.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()


def generar_grafico_consumo_rural(
    resultados_rural: Tuple[ResultadoConsumoRural, ...],
    ruta_salida: Path,
) -> None:
    regiones = [r.nombre_region for r in reversed(resultados_rural)]
    consumos = [r.consumo_rural_gwh_anio for r in reversed(resultados_rural)]
    colores = [
        "#d95f02" if r == "La Araucanía" else "#3b7ea1" for r in regiones
    ]

    plt.figure(figsize=(10, 6.5))
    barras = plt.barh(regiones, consumos, color=colores, height=0.68)

    for barra, valor in zip(barras, consumos):
        plt.text(
            valor + 6,
            barra.get_y() + barra.get_height() / 2.0,
            f"{valor:.0f} GWh",
            va="center",
            fontsize=8.5,
        )

    plt.xlim(0, max(consumos) * 1.16)
    plt.title("Consumo Eléctrico de Sectores Rurales por Región de Chile (GWh/año)")
    plt.xlabel("Consumo Eléctrico Rural Estimado (GWh / año)")
    plt.ylabel("Región (Norte a Sur)")
    plt.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()


def construir_reporte_markdown(
    clima: Tuple[MesClimatico, ...],
    resultados_riego: Tuple[ResultadoMensualRiego, ...],
    resultados_eco: Tuple[ResultadoEconomico, ...],
    punto_equilibrio: float,
    resultados_diag: Tuple[ResultadoDiagnostico, ...],
    resultados_rural: Tuple[ResultadoConsumoRural, ...],
) -> str:
    lineas = [
        "# Resultados de la Simulación en Python",
        "",
        "## 1. Balance Energético e Hídrico Mes a Mes (La Araucanía)",
        "",
        "| Mes | HSP (h) | Agua (L/día) | Bombeo (h/día) | Demanda (Wh/día) | Panel 100% (Wh) | Panel 80% (Wh) | Panel 70% (Wh) | Panel 60% (Wh) | Panel 50% (Wh) | % Uso (al 50%) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    por_mes = {m.nombre_mes: {} for m in clima}
    for r in resultados_riego:
        por_mes[r.nombre_mes][r.salud_panel] = r

    for m in clima:
        datos_mes = por_mes[m.nombre_mes]
        r50 = datos_mes[0.50]
        fila = (
            f"| {m.nombre_mes} | {m.horas_sol_pico} | {m.demanda_agua_litros_dia:.0f} | "
            f"{r50.horas_bombeo_necesarias:.2f} | {r50.energia_requerida_wh:.1f} | "
            f"{datos_mes[1.00].energia_disponible_wh:.0f} | "
            f"{datos_mes[0.80].energia_disponible_wh:.0f} | "
            f"{datos_mes[0.70].energia_disponible_wh:.0f} | "
            f"{datos_mes[0.60].energia_disponible_wh:.0f} | "
            f"{r50.energia_disponible_wh:.0f} | "
            f"{r50.porcentaje_uso_energia:.1f}% |"
        )
        lineas.append(fila)

    lineas.extend(
        [
            "",
            "![Balance Energético Mensual](grafico_balance_energetico.png)",
            "",
            "## 2. Sensibilidad Económica del Triaje (Lote de 10.000 paneles)",
            "",
            f"- **Punto de equilibrio (break-even):** Basta con que el **{punto_equilibrio}%** del lote sea reutilizable para que el triaje se pague solo frente al reciclaje.",
            "",
            "| % Reutilizable | Paneles Reutilizados | Paneles a Reciclar | Costo Reciclar Todo (US$) | Costo con Triaje (US$) | Ahorro Neto (US$) | Ahorro (%) |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for e in resultados_eco:
        lineas.append(
            f"| {int(e.tasa_reutilizacion * 100)}% | {e.paneles_reutilizados} | {e.paneles_reciclados} | "
            f"{e.costo_reciclar_todo_usd:,.0f} | {e.costo_con_triaje_usd:,.0f} | "
            f"{e.ahorro_neto_usd:,.0f} | {e.ahorro_porcentaje:.1f}% |"
        )

    lineas.extend(
        [
            "",
            "![Sensibilidad Económica](grafico_sensibilidad_economica.png)",
            "",
            "## 3. Validación de la Razón de Diagnóstico (Isc / Isc_ref)",
            "",
            "| Salud Real | Irradiancia (W/m²) | Isc Panel (A) | Isc Ref (A) | Salud Estimada (S_Isc) | Error (puntos %) | Clasificación |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for d in resultados_diag:
        lineas.append(
            f"| {int(d.salud_real * 100)}% | {d.irradiancia_w_m2:.0f} | {d.corriente_panel_amp:.2f} | "
            f"{d.corriente_ref_amp:.4f} | {d.salud_estimada_s_isc * 100:.1f}% | "
            f"{d.error_puntos_porcentuales:.2f} | {d.clase_asignada} |"
        )

    lineas.extend(
        [
            "",
            "## 4. Consumo Eléctrico de Sectores Rurales por Región de Chile",
            "",
            "| Región | Consumo Rural (GWh/año) | Predios y Escuelas Rurales | Consumo Promedio (kWh/mes) | Energía Anual 1 Panel Clase B (kWh/año) | Paneles Clase B para cubrir 10% (Miles) |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for r in resultados_rural:
        lineas.append(
            f"| {r.nombre_region} | {r.consumo_rural_gwh_anio:.1f} | {r.predios_y_escuelas_rurales:,} | "
            f"{r.consumo_promedio_kwh_mes_por_predio:.1f} | {r.energia_anual_panel_clase_b_kwh:.0f} | "
            f"{r.paneles_para_cubrir_10_porciento_miles:.1f}k |"
        )

    lineas.extend(
        [
            "",
            "![Consumo Eléctrico Rural por Región](grafico_consumo_rural_chile.png)",
        ]
    )

    return "\n".join(lineas) + "\n"


def guardar_resultados_en_report(
    clima: Tuple[MesClimatico, ...],
    config_panel: ConfigPanelSolar,
    resultados_riego: Tuple[ResultadoMensualRiego, ...],
    resultados_eco: Tuple[ResultadoEconomico, ...],
    punto_equilibrio: float,
    resultados_diag: Tuple[ResultadoDiagnostico, ...],
    resultados_rural: Tuple[ResultadoConsumoRural, ...],
) -> None:
    CARPETA_REPORTE.mkdir(parents=True, exist_ok=True)
    generar_grafico_energia(
        clima,
        config_panel,
        resultados_riego,
        CARPETA_REPORTE / "grafico_balance_energetico.png",
    )
    generar_grafico_economico(
        resultados_eco,
        CARPETA_REPORTE / "grafico_sensibilidad_economica.png",
    )
    generar_grafico_consumo_rural(
        resultados_rural,
        CARPETA_REPORTE / "grafico_consumo_rural_chile.png",
    )
    reporte_md = construir_reporte_markdown(
        clima,
        resultados_riego,
        resultados_eco,
        punto_equilibrio,
        resultados_diag,
        resultados_rural,
    )
    ruta_md = CARPETA_REPORTE / "Reporte_Simulacion.md"
    ruta_md.write_text(reporte_md, encoding="utf-8")


def ejecutar_todo() -> None:
    clima = obtener_clima_araucania()
    regiones = obtener_consumo_rural_regiones()
    config_panel = ConfigPanelSolar()
    config_riego = ConfigRiego()
    config_eco = ConfigEconomica()

    resultados_riego = SimuladorRiego(config_panel, config_riego).simular_anio(clima)
    sim_eco = SimuladorEconomico(config_eco)
    resultados_eco = sim_eco.simular_todos()
    punto_equilibrio = sim_eco.calcular_punto_equilibrio()
    resultados_diag = SimuladorDiagnostico().simular_bateria_pruebas((0.85, 0.60, 0.45))
    resultados_rural = SimuladorConsumoRural(config_panel).simular_chile(regiones)

    guardar_resultados_en_report(
        clima,
        config_panel,
        resultados_riego,
        resultados_eco,
        punto_equilibrio,
        resultados_diag,
        resultados_rural,
    )
    print(f"Simulaciones completadas en: {CARPETA_REPORTE}")


if __name__ == "__main__":
    ejecutar_todo()
