from dataclasses import dataclass
from typing import Tuple
from simulaciones.SimConfig import ConfigPanelSolar, DatosRegionRural


@dataclass(frozen=True)
class ResultadoConsumoRural:
    nombre_region: str
    consumo_rural_gwh_anio: float
    predios_y_escuelas_rurales: int
    consumo_promedio_kwh_mes_por_predio: float
    energia_anual_panel_clase_b_kwh: float
    paneles_para_cubrir_10_porciento_miles: float


class SimuladorConsumoRural:
    def __init__(self, panel: ConfigPanelSolar, salud_clase_b: float = 0.60) -> None:
        self.panel = panel
        self.salud_clase_b = salud_clase_b

    def simular_region(self, region: DatosRegionRural) -> ResultadoConsumoRural:
        consumo_total_kwh_anio = region.consumo_rural_gwh_anio * 1_000_000.0
        consumo_mensual_predio = (
            consumo_total_kwh_anio / region.predios_y_escuelas_rurales / 12.0
        )

        potencia_real_kw = (
            self.panel.potencia_nominal_watts * self.salud_clase_b
        ) / 1000.0
        energia_diaria_panel_kwh = (
            potencia_real_kw
            * region.horas_sol_pico_promedio
            * self.panel.eficiencia_sistema
        )
        energia_anual_panel_kwh = energia_diaria_panel_kwh * 365.0

        meta_10_porciento_kwh = consumo_total_kwh_anio * 0.10
        paneles_requeridos_miles = (
            meta_10_porciento_kwh / energia_anual_panel_kwh
        ) / 1000.0

        return ResultadoConsumoRural(
            nombre_region=region.nombre_region,
            consumo_rural_gwh_anio=round(region.consumo_rural_gwh_anio, 1),
            predios_y_escuelas_rurales=region.predios_y_escuelas_rurales,
            consumo_promedio_kwh_mes_por_predio=round(consumo_mensual_predio, 1),
            energia_anual_panel_clase_b_kwh=round(energia_anual_panel_kwh, 1),
            paneles_para_cubrir_10_porciento_miles=round(paneles_requeridos_miles, 1),
        )

    def simular_chile(
        self, regiones: Tuple[DatosRegionRural, ...]
    ) -> Tuple[ResultadoConsumoRural, ...]:
        return tuple(self.simular_region(r) for r in regiones)
