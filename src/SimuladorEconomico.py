from dataclasses import dataclass
from typing import Tuple
from SimConfig import ConfigEconomica


@dataclass(frozen=True)
class ResultadoEconomico:
    tasa_reutilizacion: float
    paneles_reutilizados: int
    paneles_reciclados: int
    costo_reciclar_todo_usd: float
    costo_con_triaje_usd: float
    ahorro_neto_usd: float
    ahorro_porcentaje: float


class SimuladorEconomico:
    def __init__(self, config: ConfigEconomica) -> None:
        self.config = config

    def calcular_punto_equilibrio(self) -> float:
        return round(
            (self.config.costo_triaje_por_panel_usd / self.config.costo_reciclaje_por_panel_usd) * 100.0,
            1,
        )

    def simular_escenario(self, tasa_reutilizacion: float) -> ResultadoEconomico:
        lote = self.config.tamano_lote
        reutilizados = int(round(lote * tasa_reutilizacion))
        reciclados = lote - reutilizados

        costo_reciclar_todo = lote * self.config.costo_reciclaje_por_panel_usd
        costo_triaje_total = lote * self.config.costo_triaje_por_panel_usd
        costo_reciclaje_remanente = reciclados * self.config.costo_reciclaje_por_panel_usd

        costo_con_triaje = costo_triaje_total + costo_reciclaje_remanente
        ahorro_neto = costo_reciclar_todo - costo_con_triaje
        ahorro_porcentaje = (ahorro_neto / costo_reciclar_todo) * 100.0

        return ResultadoEconomico(
            tasa_reutilizacion=tasa_reutilizacion,
            paneles_reutilizados=reutilizados,
            paneles_reciclados=reciclados,
            costo_reciclar_todo_usd=round(costo_reciclar_todo, 2),
            costo_con_triaje_usd=round(costo_con_triaje, 2),
            ahorro_neto_usd=round(ahorro_neto, 2),
            ahorro_porcentaje=round(ahorro_porcentaje, 1),
        )

    def simular_todos(self) -> Tuple[ResultadoEconomico, ...]:
        return tuple(
            self.simular_escenario(tasa) for tasa in self.config.tasas_reutilizacion
        )
