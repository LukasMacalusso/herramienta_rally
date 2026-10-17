from dataclasses import dataclass
from typing import Tuple
from simulaciones.SimConfig import ConfigPanelSolar, ConfigRiego, MesClimatico


@dataclass(frozen=True)
class ResultadoMensualRiego:
    nombre_mes: str
    salud_panel: float
    energia_disponible_wh: float
    horas_bombeo_necesarias: float
    energia_requerida_wh: float
    porcentaje_uso_energia: float
    cubre_demanda: bool


class SimuladorRiego:
    def __init__(self, panel: ConfigPanelSolar, riego: ConfigRiego) -> None:
        self.panel = panel
        self.riego = riego

    def calcular_energia_disponible_wh(self, mes: MesClimatico, salud_panel: float) -> float:
        potencia_real_watts = self.panel.potencia_nominal_watts * salud_panel
        return potencia_real_watts * mes.horas_sol_pico * self.panel.eficiencia_sistema

    def calcular_horas_bombeo(self, mes: MesClimatico) -> float:
        return mes.demanda_agua_litros_dia / self.riego.caudal_bomba_litros_hora

    def simular_mes(self, mes: MesClimatico, salud_panel: float) -> ResultadoMensualRiego:
        energia_disponible = self.calcular_energia_disponible_wh(mes, salud_panel)
        horas_bombeo = self.calcular_horas_bombeo(mes)
        energia_requerida = horas_bombeo * self.riego.potencia_bomba_watts

        porcentaje_uso = 0.0
        if energia_disponible > 0:
            porcentaje_uso = (energia_requerida / energia_disponible) * 100.0

        cubre_demanda = (
            energia_disponible >= energia_requerida
            and horas_bombeo <= mes.horas_sol_pico
        )

        return ResultadoMensualRiego(
            nombre_mes=mes.nombre_mes,
            salud_panel=salud_panel,
            energia_disponible_wh=round(energia_disponible, 1),
            horas_bombeo_necesarias=round(horas_bombeo, 2),
            energia_requerida_wh=round(energia_requerida, 1),
            porcentaje_uso_energia=round(porcentaje_uso, 1),
            cubre_demanda=cubre_demanda,
        )

    def simular_anio(
        self, clima: Tuple[MesClimatico, ...]
    ) -> Tuple[ResultadoMensualRiego, ...]:
        resultados = []
        for salud in self.panel.niveles_salud:
            for mes in clima:
                resultados.append(self.simular_mes(mes, salud))
        return tuple(resultados)
