from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ResultadoDiagnostico:
    salud_real: float
    irradiancia_w_m2: float
    corriente_panel_amp: float
    corriente_ref_amp: float
    salud_estimada_s_isc: float
    error_puntos_porcentuales: float
    clase_asignada: str


class SimuladorDiagnostico:
    def __init__(
        self,
        isc_nominal_panel_amp: float = 9.5,
        isc_nominal_ref_amp: float = 0.15,
        error_sensor_relativo: float = 0.015,
    ) -> None:
        self.isc_nominal_panel_amp = isc_nominal_panel_amp
        self.isc_nominal_ref_amp = isc_nominal_ref_amp
        self.error_sensor_relativo = error_sensor_relativo
        self.razon_inicial_t0 = isc_nominal_panel_amp / isc_nominal_ref_amp

    def clasificar_panel(self, salud_estimada: float) -> str:
        if salud_estimada >= 0.80:
            return "Clase A (Reventa)"
        if salud_estimada >= 0.50:
            return "Clase B (Segunda vida)"
        return "Clase D (Reciclaje)"

    def simular_medicion(
        self, salud_real: float, irradiancia_w_m2: float
    ) -> ResultadoDiagnostico:
        factor_sol = irradiancia_w_m2 / 1000.0
        corriente_panel_real = self.isc_nominal_panel_amp * factor_sol * salud_real
        corriente_ref_real = self.isc_nominal_ref_amp * factor_sol

        corriente_panel_medida = corriente_panel_real * (1.0 + self.error_sensor_relativo)
        corriente_ref_medida = corriente_ref_real * (1.0 - self.error_sensor_relativo)

        razon_actual = corriente_panel_medida / corriente_ref_medida
        salud_estimada = razon_actual / self.razon_inicial_t0
        error_puntos = abs(salud_estimada - salud_real) * 100.0

        return ResultadoDiagnostico(
            salud_real=salud_real,
            irradiancia_w_m2=irradiancia_w_m2,
            corriente_panel_amp=round(corriente_panel_medida, 2),
            corriente_ref_amp=round(corriente_ref_medida, 4),
            salud_estimada_s_isc=round(salud_estimada, 3),
            error_puntos_porcentuales=round(error_puntos, 2),
            clase_asignada=self.clasificar_panel(salud_estimada),
        )

    def simular_bateria_pruebas(
        self, niveles_salud: Tuple[float, ...]
    ) -> Tuple[ResultadoDiagnostico, ...]:
        irradiancias = (400.0, 700.0, 1000.0)
        resultados = []
        for salud in niveles_salud:
            for sol in irradiancias:
                resultados.append(self.simular_medicion(salud, sol))
        return tuple(resultados)
