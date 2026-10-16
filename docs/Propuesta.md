# Propuesta: paneles usados que se diagnostican solos

Oct 16, 2026 · @Vicente Rivera

## Resumen

Proponemos un medidor de salud de bajo costo, del orden de US$25, que acompaña a cada panel solar usado desde su retiro hasta su segunda vida. Compara la corriente y el voltaje del panel con una celda de referencia nueva, y esa razón indica la salud real del panel cada día, en terreno.

Hoy un panel usado termina como residuo porque demostrar que todavía sirve cuesta más de lo que vale. El medidor baja ese costo casi a cero, permite clasificar los paneles al desmontarlos y les da un historial verificable para su reutilización.

Como caso de demostración, un panel recuperado alimenta el riego por goteo de un huerto escolar rural. El sistema no usa batería ni controlador MPPT: el agua bombeada a un estanque elevado guarda la energía, y el costo total esencial se estima entre US$130 y US$310.

## Problema

La tecnología para diagnosticar, reutilizar y reciclar paneles existe, pero no se usa porque botar es más barato. Reciclar un módulo cuesta entre US$15 y US$45, frente a US$1 a US$5 por enviarlo a un vertedero ([Resource Recycling](https://resource-recycling.com/e-scrap/?p=18179)).

En Chile el problema crece:

- Se estiman unos 12 millones de módulos instalados, que al 2045 serían cerca de 120 mil toneladas de residuos acumulados ([Repositorio USM](https://repositorio.usm.cl/handle/123456789/74566)).
- El Ministerio de Energía reconoce que no hay industria local de mantenimiento, reparación o reciclaje, y lista como brecha la falta de un mercado de segunda vida ([Ministerio de Energía, 2025](https://energia.gob.cl/sites/default/files/documentos/2025.11.12_webinar_hoja_de_ruta_economia_circular_en_energia.pdf)).
- La Ley REP incluye los paneles como producto prioritario, pero a fines de 2025 aún se esperaba el decreto de metas ([Infraestructura Pública, 2025](https://www.infraestructurapublica.cl/?p=96259)).

La causa de fondo es la falta de información: un panel retirado llega sin historial, nadie sabe si sigue sirviendo y comprobarlo con equipos de laboratorio cuesta más que el propio panel usado. Sin esa información no hay confianza, y sin confianza no hay mercado de segunda vida.

## Solución

Un mismo medidor de bajo costo se usa en dos momentos de la vida del panel: cuando se retira y durante su segunda vida.

1. **Triaje al desmontar.** El medidor, con un condensador agregado, funciona como trazador de curva I-V. Junto a una prueba de aislamiento y una foto, clasifica cada panel en cuatro clases y le asigna un pasaporte digital con código QR.
2. **Destino según clase.** A: reventa (sobre 80% de su potencia). B: segunda vida en aplicaciones de baja exigencia (50–80%). C: reparación de diodos, caja de conexiones o conectores. D: reciclaje, solo para lo que de verdad es residuo.
3. **Diagnóstico continuo en terreno.** El medidor queda instalado junto al panel reutilizado y registra su salud cada día. Ese historial alimenta el pasaporte y le da al panel un valor verificable.

El triaje se financia con el costo que se evita: cada panel que vuelve a usarse es un panel que no se paga por reciclar.

## Funcionamiento del medidor

El medidor estima la salud del panel comparando lo que entrega con lo que debería entregar con el sol de ese momento. El sol real lo mide una celda de referencia nueva y pequeña instalada al lado del panel.

Una vez al día, con buena luz, un ESP32 hace dos mediciones de pocos milisegundos:

1. **Voltaje de circuito abierto (Voc):** un MOSFET desconecta la carga y se lee el voltaje.
2. **Corriente de cortocircuito (Isc):** un segundo MOSFET cortocircuita el panel a través de un sensor de corriente de 10 A.

La salud se calcula como la razón entre la corriente del panel y la de la celda de referencia, normalizada contra la primera medición tras el triaje:

```latex
S_{Isc} = \frac{I_{sc,panel} / I_{sc,ref}}{\left(I_{sc,panel} / I_{sc,ref}\right)_{t_0}}
```

Cada señal apunta a fallas distintas, las mismas que se usan en diagnóstico profesional:

| Señal | Qué indica una caída | Causa probable |
| --- | --- | --- |
| Isc frente a la referencia | Menos área o luz útil | Amarilleo del encapsulante, fisuras, suciedad persistente |
| Voc corregido por temperatura | Celdas o diodos afectados | PID, celdas en cortocircuito, diodo bypass fallado |

Un supercondensador mantiene encendido al ESP32 durante el cortocircuito, porque en ese instante el voltaje del panel cae a cero. Los datos quedan en la memoria del ESP32 y se leen por Bluetooth en cada visita.

## Caso de demostración: riego escolar

Un panel de clase B alimenta el riego por goteo de un huerto escolar de 100 m², sin batería ni controlador MPPT. Lo usamos para mostrar el medidor funcionando en un caso real, barato y verificable.

El panel alimenta, a través de un conversor DC-DC, una bomba de 12 V que llena con la dosis del día un estanque elevado. El agua baja por gravedad a goteros de baja presión, sin válvula. El medidor registra la salud del panel y enciende la bomba.

Diseñamos para lo mínimo que funciona. Cada componente quedó marcado según si es necesario:

| Componente | Estado | Por qué | US$ aprox. |
| --- | --- | --- | --- |
| Panel recuperado clase B | Esencial | Fuente de energía; un solo panel sobra | 0–30 |
| Conversor DC-DC | Esencial | Reemplaza al MPPT: la energía sobra, no hace falta exprimirla | 5–10 |
| ESP32 + sensor de corriente 10 A + 2 MOSFET | Esencial | Mide Isc y Voc y enciende la bomba | 15–25 |
| Celda de referencia | Esencial | Sin ella no hay medición de salud | 5–10 |
| Supercondensador | Esencial | Mantiene al ESP32 encendido durante la medición de Isc | 3–5 |
| Bomba 12 V | Esencial | Llena el estanque con la dosis del día | 20–40 |
| Estanque elevado + base | Esencial | Guarda la energía como agua en altura | 60–150 |
| Goteo por gravedad | Esencial | Goteros de baja presión, sin válvula | 20–40 |
| Sensor de humedad capacitivo | Opcional | Ajusta la dosis; sin él se riega por calendario | 3–5 |
| Reloj RTC con pila | Opcional | Pone fecha al registro; sin él se cuentan días | 2–4 |
| Batería LiFePO4 + BMS | Eliminado | El estanque la reemplaza, y no se carga bajo 0 °C | ahorra 150–250 |
| Controlador MPPT | Eliminado | El riego usa cerca del 15% de la energía | ahorra 40–80 |
| Varios paneles combinados | Eliminado | Un panel sobra; combinarlos exige un MPPT por panel | — |
| Válvula solenoide | Eliminado | El estanque suelta por gravedad la dosis bombeada | — |
| WiFi o LoRa | Eliminado | Sin internet rural; los datos se leen por Bluetooth | — |
| Invernadero e iluminación | Eliminado | Fuera de alcance del caso demostrativo | — |

Precios de referencia aproximados, por verificar con proveedores locales.

## Viabilidad técnica

El sistema es viable con componentes comerciales, porque un panel degradado entrega mucha más energía de la que el riego necesita. Las cifras son estimaciones de diseño que la simulación debe confirmar.

**Balance de energía en verano**, para un panel de 300 W al 60% (180 W), con unas 4 horas de sol equivalentes y 80% de eficiencia:

- Energía útil disponible: unos 576 Wh al día.
- Demanda del riego: un huerto de 100 m² con goteo necesita del orden de 400–500 litros al día. Una bomba de 40 W mueve unos 250–300 L/h a baja altura, es decir, cerca de 2 horas y 80 Wh al día.
- El riego usa cerca del 15% de la energía disponible. Por eso sirven incluso paneles al 50% y no se justifica un MPPT.

**En invierno** el panel rinde mucho menos, pero en La Araucanía el invierno es lluvioso y casi no hay que regar. La demanda coincide con la oferta de sol.

**Riesgos técnicos y cómo se resuelven:**

| Riesgo | Solución en el diseño |
| --- | --- |
| Poca presión del estanque para goteros estándar | Goteros de baja presión diseñados para gravedad; validar altura del estanque |
| El ESP32 se apaga al cortocircuitar el panel | Supercondensador en la alimentación del ESP32 |
| Corriente de cortocircuito de 9–10 A | Sensor de corriente y MOSFET dimensionados para 10 A, pulsos de milisegundos |
| Voc sube en mañanas frías | Conversor DC-DC con entrada de hasta 50 V o más |
| Heladas en invierno | Sin batería que cargar bajo 0 °C; vaciar cañerías en temporada sin riego |
| Panel con falla de seguridad | La prueba de aislamiento del triaje lo excluye antes de reutilizarlo |

## Prefactibilidad económica

La propuesta se paga con dinero que hoy ya se gasta o se pierde, sin depender de subsidios.

**Para el dueño de la planta.** Un ejemplo ilustrativo, con supuestos por validar: un lote de 10.000 paneles retirados, triaje a US$5 por panel y 50% reutilizable.

| Escenario | Triaje | Reciclaje (US$30 por panel) | Costo total |
| --- | --- | --- | --- |
| Reciclar todo | — | US$300.000 | US$300.000 |
| Con triaje | US$50.000 | US$150.000 | US$200.000, menos la venta de clase A |

**Para el usuario de segunda vida.** El sistema de riego cuesta entre US$130 y US$310 en componentes esenciales. Eliminar la batería LiFePO4 con su BMS y el controlador MPPT ahorra del orden de US$190 a US$330 frente al diseño inicial.

**El medidor** cuesta unos US$25 (ESP32, sensor de corriente, dos MOSFET, celda de referencia y supercondensador). Ese es el costo de saber, cada día, cuánto vale un panel usado.

El supuesto más sensible es el porcentaje reutilizable de un lote retirado; la simulación debe mostrar el resultado con 30%, 50% y 70%.

## Innovación e impacto

Lo nuevo no es un componente, sino dónde y para qué se usa: llevar a cada panel usado una medición de salud que hoy solo existe en laboratorios y plantas grandes.

- **Un solo hardware para todo el ciclo.** El mismo medidor clasifica el panel al retirarlo y lo sigue diagnosticando en su segunda vida.
- **Un panel con historial verificable.** El pasaporte digital convierte un residuo de valor incierto en un producto con datos, que se puede vender, donar o garantizar.
- **Diseño mínimo.** El estanque elevado reemplaza a la batería, y un conversor simple reemplaza al MPPT. Eso baja el costo y elimina el componente más sensible al frío.

**Impacto ambiental.** Cada panel reutilizado deja de ir al vertedero o a reciclaje. El medidor permite separar lo reutilizable de lo que es residuo real.

**Impacto social.** Las escuelas rurales obtienen riego de bajo costo, y el huerto se convierte en un espacio para enseñar energía y sostenibilidad.

## Límites y próximos pasos

La propuesta está en etapa conceptual. Estos son sus límites conocidos:

- Isc y Voc no detectan pérdidas por resistencia en serie (corrosión, soldaduras), que solo se ven en el factor de forma de la curva I-V completa.
- Las celdas de referencia ya se usan en plantas solares grandes; el aporte es su bajo costo y su uso por panel en segunda vida.
- La seguridad eléctrica no se mide en terreno; depende de la prueba de aislamiento del triaje.

Próximos pasos:

- [ ] Simular en Python paneles al 100, 80, 70, 60 y 50% frente a la demanda de riego mes a mes.
- [ ] Validar la precisión de la razón Isc/Isc\_ref para detectar degradación.
- [ ] Definir la altura del estanque frente a la presión mínima de los goteros.
- [ ] Construir un prototipo del medidor con un panel pequeño.
- [ ] Buscar el porcentaje reutilizable real de un lote retirado.

## Referencias

- Infraestructura Pública. (2025, 29 de diciembre). *Primera planta de reciclaje de paneles solares de Chile estará en Atacama*. <https://www.infraestructurapublica.cl/?p=96259>
- Ministerio de Energía. (2025, 12 de noviembre). *Hoja de ruta de economía circular en energía* \[Presentación\]. <https://energia.gob.cl/sites/default/files/documentos/2025.11.12_webinar_hoja_de_ruta_economia_circular_en_energia.pdf>
- pv magazine USA. (2026, 5 de junio). *Solar panel recycling costs outpace recovered material value as 2030 waste surge approaches*. <https://pv-magazine-usa.com/2026/06/05/solar-panel-recycling-costs-outpace-recovered-material-value-as-2030-waste-surge-approaches/>
- Resource Recycling. (s.f.). *DOE releases plan to cut PV recycling costs* \[Nota sobre el plan de acción de reciclaje fotovoltaico del Departamento de Energía de EE.UU.\]. <https://resource-recycling.com/e-scrap/?p=18179>
- Schott, E. (2025, 9 de junio). *La tercera vida de los paneles solares*. Portal Minero. <https://www.portalminero.com/la-tercera-vida-de-los-paneles-solares>
- Universidad Técnica Federico Santa María. (s.f.). *Diseño de una planta de valorización y reciclaje de paneles solares* \[Memoria de título\]. Repositorio USM. <https://repositorio.usm.cl/handle/123456789/74566>

**Declaración de uso de inteligencia artificial.** El equipo usó Claude (Anthropic, 2026), un modelo de lenguaje, como apoyo para explorar el problema, revisar la viabilidad técnica y dar formato a este documento. Las decisiones de diseño, los supuestos y la propuesta final son del equipo.

- Anthropic. (2026). *Claude* (Opus 5.5) \[Modelo de lenguaje de gran tamaño\]. <https://claude.ai>

Antes de entregar: completar los autores de la memoria USM y la fecha de la nota de Resource Recycling, y agregar la fuente de cualquier cifra nueva (por ejemplo, número de escuelas rurales).
