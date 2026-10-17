from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MesClimatico:
    nombre_mes: str
    horas_sol_pico: float
    demanda_agua_litros_dia: float


@dataclass(frozen=True)
class DatosRegionRural:
    nombre_region: str
    consumo_rural_gwh_anio: float
    predios_y_escuelas_rurales: int
    horas_sol_pico_promedio: float


@dataclass(frozen=True)
class ConfigPanelSolar:
    potencia_nominal_watts: float = 300.0
    eficiencia_sistema: float = 0.80
    niveles_salud: Tuple[float, ...] = (1.00, 0.80, 0.70, 0.60, 0.50)


@dataclass(frozen=True)
class ConfigRiego:
    area_huerto_metros_cuadrados: float = 100.0
    potencia_bomba_watts: float = 40.0
    caudal_bomba_litros_hora: float = 275.0


@dataclass(frozen=True)
class ConfigEconomica:
    tamano_lote: int = 10000
    costo_triaje_por_panel_usd: float = 5.0
    costo_reciclaje_por_panel_usd: float = 30.0
    costo_vertedero_por_panel_usd: float = 3.0
    precio_reventa_clase_a_usd: float = 25.0
    tasas_reutilizacion: Tuple[float, ...] = (0.30, 0.50, 0.70)


def obtener_clima_araucania() -> Tuple[MesClimatico, ...]:
    return (
        MesClimatico("Ene", 5.2, 480.0),
        MesClimatico("Feb", 4.5, 450.0),
        MesClimatico("Mar", 3.5, 320.0),
        MesClimatico("Abr", 2.3, 120.0),
        MesClimatico("May", 1.5, 0.0),
        MesClimatico("Jun", 1.2, 0.0),
        MesClimatico("Jul", 1.4, 0.0),
        MesClimatico("Ago", 2.0, 0.0),
        MesClimatico("Sep", 2.9, 100.0),
        MesClimatico("Oct", 3.8, 250.0),
        MesClimatico("Nov", 4.6, 380.0),
        MesClimatico("Dic", 5.0, 450.0),
    )


def obtener_consumo_rural_regiones() -> Tuple[DatosRegionRural, ...]:
    return (
        DatosRegionRural("Arica y Parinacota", 28.0, 3200, 6.2),
        DatosRegionRural("Tarapacá", 24.0, 2800, 6.4),
        DatosRegionRural("Antofagasta", 32.0, 2500, 6.6),
        DatosRegionRural("Atacama", 65.0, 4800, 6.1),
        DatosRegionRural("Coquimbo", 185.0, 19500, 5.4),
        DatosRegionRural("Valparaíso", 260.0, 22000, 4.8),
        DatosRegionRural("Metropolitana", 310.0, 18500, 4.9),
        DatosRegionRural("O'Higgins", 420.0, 34000, 4.6),
        DatosRegionRural("Maule", 465.0, 48000, 4.3),
        DatosRegionRural("Ñuble", 240.0, 29000, 4.1),
        DatosRegionRural("Biobío", 315.0, 35000, 3.8),
        DatosRegionRural("La Araucanía", 380.0, 54000, 3.3),
        DatosRegionRural("Los Ríos", 195.0, 21000, 3.0),
        DatosRegionRural("Los Lagos", 340.0, 39000, 2.9),
        DatosRegionRural("Aysén", 42.0, 4500, 2.7),
        DatosRegionRural("Magallanes", 35.0, 3100, 2.4),
    )
