import tkinter as tk
from tkinter import ttk
from typing import Tuple
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from SimConfig import (
    ConfigEconomica,
    ConfigPanelSolar,
    ConfigRiego,
    MesClimatico,
    obtener_clima_araucania,
)
from SimuladorDiagnostico import SimuladorDiagnostico
from SimuladorEconomico import SimuladorEconomico
from SimuladorRiego import SimuladorRiego
from ejecutar_simulacion import CARPETA_REPORTE, guardar_resultados_en_report


class VentanaSimulador:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Motor de Simulación - Segunda Vida de Paneles Solares")
        self.raiz.geometry("1260x800")

        self.clima_base = obtener_clima_araucania()
        self._inicializar_variables()
        self._construir_estructura()
        self._construir_controles()
        self._construir_lienzo_graficos()
        self.actualizar_graficos()

    def _inicializar_variables(self) -> None:
        self.var_potencia_panel = tk.DoubleVar(value=300.0)
        self.var_eficiencia = tk.DoubleVar(value=80.0)
        self.var_potencia_bomba = tk.DoubleVar(value=40.0)
        self.var_caudal_bomba = tk.DoubleVar(value=275.0)
        self.var_escala_agua = tk.DoubleVar(value=100.0)
        self.var_tamano_lote = tk.DoubleVar(value=10000.0)
        self.var_costo_triaje = tk.DoubleVar(value=5.0)
        self.var_costo_reciclaje = tk.DoubleVar(value=30.0)

    def _construir_estructura(self) -> None:
        self.panel_izquierdo = ttk.Frame(self.raiz, padding=14, width=350)
        self.panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

        self.panel_derecho = ttk.Frame(self.raiz, padding=10)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        titulo = ttk.Label(
            self.panel_izquierdo,
            text="Parámetros en Tiempo Real",
            font=("Segoe UI", 13, "bold"),
        )
        titulo.pack(anchor=tk.W, pady=(0, 8))

    def _agregar_slider(
        self,
        contenedor: ttk.LabelFrame,
        texto: str,
        variable: tk.DoubleVar,
        minimo: float,
        maximo: float,
        paso: float,
        unidad: str,
    ) -> None:
        fila_superior = ttk.Frame(contenedor)
        fila_superior.pack(fill=tk.X, pady=(4, 0))

        etiqueta_nombre = ttk.Label(fila_superior, text=texto, font=("Segoe UI", 9))
        etiqueta_nombre.pack(side=tk.LEFT)

        etiqueta_valor = ttk.Label(
            fila_superior,
            text=f"{variable.get():.0f} {unidad}",
            font=("Segoe UI", 9, "bold"),
        )
        etiqueta_valor.pack(side=tk.RIGHT)

        def al_mover(_valor_str: str) -> None:
            valor_redondeado = round(variable.get() / paso) * paso
            variable.set(valor_redondeado)
            etiqueta_valor.config(text=f"{valor_redondeado:.0f} {unidad}")
            self.actualizar_graficos()

        escala = ttk.Scale(
            contenedor,
            from_=minimo,
            to=maximo,
            variable=variable,
            orient=tk.HORIZONTAL,
            command=al_mover,
        )
        escala.pack(fill=tk.X, pady=(0, 4))

    def _construir_controles(self) -> None:
        grupo_energia = ttk.LabelFrame(
            self.panel_izquierdo, text=" Energía y Riego ", padding=8
        )
        grupo_energia.pack(fill=tk.X, pady=4)

        self._agregar_slider(
            grupo_energia, "Potencia nominal panel:", self.var_potencia_panel, 100, 500, 10, "W"
        )
        self._agregar_slider(
            grupo_energia, "Eficiencia del sistema:", self.var_eficiencia, 50, 95, 5, "%"
        )
        self._agregar_slider(
            grupo_energia, "Potencia de la bomba:", self.var_potencia_bomba, 15, 120, 5, "W"
        )
        self._agregar_slider(
            grupo_energia, "Caudal de la bomba:", self.var_caudal_bomba, 100, 500, 25, "L/h"
        )
        self._agregar_slider(
            grupo_energia, "Escala demanda de agua:", self.var_escala_agua, 50, 250, 10, "%"
        )

        grupo_eco = ttk.LabelFrame(
            self.panel_izquierdo, text=" Prefactibilidad Económica ", padding=8
        )
        grupo_eco.pack(fill=tk.X, pady=6)

        self._agregar_slider(
            grupo_eco, "Tamaño del lote:", self.var_tamano_lote, 1000, 30000, 1000, "paneles"
        )
        self._agregar_slider(
            grupo_eco, "Costo triaje por panel:", self.var_costo_triaje, 1, 25, 1, "US$"
        )
        self._agregar_slider(
            grupo_eco, "Costo reciclaje por panel:", self.var_costo_reciclaje, 10, 60, 2, "US$"
        )

        self.etiqueta_estado = tk.Label(
            self.panel_izquierdo,
            text="",
            font=("Segoe UI", 9, "bold"),
            justify=tk.LEFT,
            wraplength=310,
            padx=8,
            pady=8,
            relief=tk.GROOVE,
        )
        self.etiqueta_estado.pack(fill=tk.X, pady=8)

        boton_exportar = ttk.Button(
            self.panel_izquierdo,
            text="Exportar Reporte y Gráficos",
            command=self.exportar_resultados,
        )
        boton_exportar.pack(fill=tk.X, pady=(4, 4))

        boton_reset = ttk.Button(
            self.panel_izquierdo,
            text="Restablecer Valores del Documento",
            command=self.restablecer_valores,
        )
        boton_reset.pack(fill=tk.X, pady=2)

    def _construir_lienzo_graficos(self) -> None:
        self.figura = Figure(figsize=(8.8, 7.2), dpi=100)
        self.eje_energia = self.figura.add_subplot(2, 1, 1)
        self.eje_economico = self.figura.add_subplot(2, 1, 2)

        self.lienzo = FigureCanvasTkAgg(self.figura, master=self.panel_derecho)
        self.lienzo.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _obtener_configs_actuales(
        self,
    ) -> Tuple[Tuple[MesClimatico, ...], ConfigPanelSolar, ConfigRiego, ConfigEconomica]:
        factor_agua = self.var_escala_agua.get() / 100.0
        clima_escalado = tuple(
            MesClimatico(
                m.nombre_mes,
                m.horas_sol_pico,
                round(m.demanda_agua_litros_dia * factor_agua, 1),
            )
            for m in self.clima_base
        )
        config_panel = ConfigPanelSolar(
            potencia_nominal_watts=self.var_potencia_panel.get(),
            eficiencia_sistema=self.var_eficiencia.get() / 100.0,
        )
        config_riego = ConfigRiego(
            potencia_bomba_watts=self.var_potencia_bomba.get(),
            caudal_bomba_litros_hora=self.var_caudal_bomba.get(),
        )
        config_eco = ConfigEconomica(
            tamano_lote=int(self.var_tamano_lote.get()),
            costo_triaje_por_panel_usd=self.var_costo_triaje.get(),
            costo_reciclaje_por_panel_usd=self.var_costo_reciclaje.get(),
        )
        return clima_escalado, config_panel, config_riego, config_eco

    def actualizar_graficos(self) -> None:
        clima, config_panel, config_riego, config_eco = self._obtener_configs_actuales()

        sim_riego = SimuladorRiego(config_panel, config_riego)
        resultados_riego = sim_riego.simular_anio(clima)

        sim_eco = SimuladorEconomico(config_eco)
        resultados_eco = sim_eco.simular_todos()
        equilibrio = sim_eco.calcular_punto_equilibrio()

        self._dibujar_energia(clima, config_panel, config_riego, resultados_riego)
        self._dibujar_economia(resultados_eco, equilibrio)
        self._actualizar_indicador_estado(resultados_riego, equilibrio)

        self.figura.tight_layout(pad=2.5)
        self.lienzo.draw()

    def _actualizar_indicador_estado(self, resultados_riego, equilibrio: float) -> None:
        resultados_50 = [r for r in resultados_riego if r.salud_panel == 0.50]
        meses_fallidos = [r.nombre_mes for r in resultados_50 if not r.cubre_demanda]
        uso_maximo = max(r.porcentaje_uso_energia for r in resultados_50)

        if not meses_fallidos:
            texto = (
                f"VIABLE: Panel al 50% cubre los 12 meses.\n"
                f"Uso máximo en verano: {uso_maximo:.1f}% de su energía.\n"
                f"Punto de equilibrio económico: {equilibrio}%."
            )
            self.etiqueta_estado.config(text=texto, bg="#d4edda", fg="#155724")
        else:
            meses_str = ", ".join(meses_fallidos)
            texto = (
                f"ALERTA: Panel al 50% NO alcanza en: {meses_str}.\n"
                f"Uso máximo requerido: {uso_maximo:.1f}%.\n"
                f"Punto de equilibrio económico: {equilibrio}%."
            )
            self.etiqueta_estado.config(text=texto, bg="#f8d7da", fg="#721c24")

    def _dibujar_energia(
        self, clima, config_panel: ConfigPanelSolar, config_riego: ConfigRiego, resultados_riego
    ) -> None:
        self.eje_energia.clear()
        meses = [m.nombre_mes for m in clima]
        demanda = [
            r.energia_requerida_wh
            for r in resultados_riego
            if r.salud_panel == config_panel.niveles_salud[0]
        ]

        for salud in config_panel.niveles_salud:
            energia_mes = [
                r.energia_disponible_wh
                for r in resultados_riego
                if r.salud_panel == salud
            ]
            self.eje_energia.plot(
                meses,
                energia_mes,
                marker="o",
                linewidth=1.8,
                label=f"Panel {int(salud * 100)}%",
            )

        self.eje_energia.bar(
            meses,
            demanda,
            color="#2b5c8f",
            alpha=0.35,
            label="Demanda bomba (Wh/día)",
        )
        self.eje_energia.set_title(
            f"Balance Energético (Panel {config_panel.potencia_nominal_watts:.0f} W vs. Bomba {config_riego.potencia_bomba_watts:.0f} W)"
        )
        self.eje_energia.set_ylabel("Wh / día")
        self.eje_energia.grid(True, linestyle="--", alpha=0.5)
        self.eje_energia.legend(loc="upper right", fontsize=8)

    def _dibujar_economia(self, resultados_eco, equilibrio: float) -> None:
        self.eje_economico.clear()
        etiquetas = [f"{int(r.tasa_reutilizacion * 100)}% reut." for r in resultados_eco]
        costos = [r.costo_con_triaje_usd / 1000.0 for r in resultados_eco]
        base = resultados_eco[0].costo_reciclar_todo_usd / 1000.0

        barras = self.eje_economico.bar(
            etiquetas, costos, color="#2e8b57", width=0.4, label="Con triaje"
        )
        self.eje_economico.axhline(
            y=base,
            color="#c0392b",
            linestyle="--",
            linewidth=1.8,
            label=f"Reciclar todo (US${base:.0f}k)",
        )

        for barra, r in zip(barras, resultados_eco):
            altura = barra.get_height()
            ahorro_k = r.ahorro_neto_usd / 1000.0
            self.eje_economico.text(
                barra.get_x() + barra.get_width() / 2.0,
                altura + (base * 0.03),
                f"Ahorro: US${ahorro_k:.0f}k",
                ha="center",
                fontsize=9,
                fontweight="bold",
            )

        self.eje_economico.set_ylim(0, max(base, max(costos)) * 1.25)
        self.eje_economico.set_title(
            f"Sensibilidad Económica (Punto de equilibrio: {equilibrio}% reutilizable)"
        )
        self.eje_economico.set_ylabel("Miles de US$")
        self.eje_economico.grid(True, axis="y", linestyle="--", alpha=0.5)
        self.eje_economico.legend(loc="upper right", fontsize=8)

    def restablecer_valores(self) -> None:
        self.var_potencia_panel.set(300.0)
        self.var_eficiencia.set(80.0)
        self.var_potencia_bomba.set(40.0)
        self.var_caudal_bomba.set(275.0)
        self.var_escala_agua.set(100.0)
        self.var_tamano_lote.set(10000.0)
        self.var_costo_triaje.set(5.0)
        self.var_costo_reciclaje.set(30.0)
        for widget in self.panel_izquierdo.winfo_children():
            widget.destroy()
        titulo = ttk.Label(
            self.panel_izquierdo,
            text="Parámetros en Tiempo Real",
            font=("Segoe UI", 13, "bold"),
        )
        titulo.pack(anchor=tk.W, pady=(0, 8))
        self._construir_controles()
        self.actualizar_graficos()

    def exportar_resultados(self) -> None:
        clima, config_panel, config_riego, config_eco = self._obtener_configs_actuales()
        resultados_riego = SimuladorRiego(config_panel, config_riego).simular_anio(clima)
        sim_eco = SimuladorEconomico(config_eco)
        resultados_eco = sim_eco.simular_todos()
        equilibrio = sim_eco.calcular_punto_equilibrio()
        resultados_diag = SimuladorDiagnostico().simular_bateria_pruebas((0.85, 0.60, 0.45))

        guardar_resultados_en_report(
            clima,
            config_panel,
            resultados_riego,
            resultados_eco,
            equilibrio,
            resultados_diag,
        )

        self.etiqueta_estado.config(
            text=f"EXPORTADO en report/:\nReporte_Simulacion.md y gráficos PNG.",
            bg="#cce5ff",
            fg="#004085",
        )


def iniciar_interfaz() -> None:
    raiz = tk.Tk()
    VentanaSimulador(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()
