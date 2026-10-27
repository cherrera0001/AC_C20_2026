# Definición de Alcance — Auditoría de Ciberseguridad de Cumplimiento (C4A)

> **Vigencia (2026-10-26)**: insumo de solo lectura para el copiloto (`docs/PROMPT_SPEC_KIT.md`),
> según `docs/DECISION_TESIS_CANONICA.md`. Las §4 y §6 valen para el ejercicio de laboratorio:
> la compuerta de autorización aplica a **cualquier acción de red contra un objetivo**; el análisis
> estático de archivos locales no la requiere. La versión CVSS objetivo es v4.0 (§7).

## 1. Identificación y propósito

| Campo | Valor |
|---|---|
| Servicio | Auditoría de Ciberseguridad de Cumplimiento (C4A) |
| Naturaleza | Híbrida: validación técnica ofensiva (ethical hacking) + auditoría normativa |
| Marcos | ISO/IEC 27001:2022, Ley 21.663 (Marco de Ciberseguridad), Ley 21.719 (Protección de Datos) |
| Alcance de este documento | Define qué se audita, cómo, con qué criterios y qué queda fuera |

El propósito es verificar, con evidencia reproducible, que los controles declarados por la organización **existen, funcionan y satisfacen sus obligaciones legales y de estándar**. La diferencia con una auditoría tradicional es que cada afirmación de cumplimiento se somete a prueba técnica (no se audita solo el papel, se audita el comportamiento real del sistema).

## 2. Doble naturaleza del servicio

- **Línea ofensiva (ethical hacking):** descubrimiento de activos, enumeración de servicios, identificación y verificación controlada de vulnerabilidades. Responde «¿esto es realmente explotable?».
- **Línea normativa (auditor de cumplimiento):** traduce cada hallazgo a un control ISO 27001:2022 y a una obligación de la Ley 21.663 y la Ley 21.719. Responde «¿esto incumple algo exigible, y qué?».

El valor está en el puente: un hallazgo técnico sin encuadre normativo es ruido para la gerencia; una brecha normativa sin prueba técnica es una opinión.

## 3. Marco de referencia y mapeo normativo

| Marco | Qué cubre en esta auditoría | Estado (sep-2026) |
|---|---|---|
| **ISO/IEC 27001:2022** | 93 controles del Anexo A en 4 temas (Organizacional, Personas, Físico, Tecnológico). Base de la evaluación de control | Vigente, estándar certificable |
| **Ley 21.663 + ANCI** | Gestión de incidentes, medidas mínimas, reporte a CSIRT/ANCI (3 h alerta temprana, 72 h reporte), delegado de ciberseguridad (si aplica OIV) | **Exigible**. ANCI operativa; IG N°2/3/4 y DS 295/2024 vigentes |
| **Ley 21.719** | Bases de licitud, derechos ARCO+, datos sensibles, seguridad del tratamiento, DPO, transferencias internacionales | **Preparación**. Vigencia 01-dic-2026 con proyecto de postergación a **01-dic-2027** (verificar al inicio del encargo) |
| Ley 21.459 (delitos informáticos) | No se audita: delimita lo legalmente permitido durante las pruebas | Vigente. Fundamenta la exigencia de autorización |

> Mientras la Ley 21.719 no rija, su componente se entrega como **análisis de brecha y hoja de ruta**, no como constatación de incumplimiento sancionable.

## 4. Alcance incluido (in-scope)

**Activos y red (ejemplo, laboratorio inicial):**
- Segmento `192.168.1.0/24`.
- Host objetivo `192.168.1.14` (Metasploitable2).

**Dominios técnicos evaluados:**
1. Superficie de red y servicios expuestos (puertos, versiones, banners).
2. Vulnerabilidades conocidas (CVE) y configuraciones inseguras.
3. Autenticación, credenciales por defecto y débiles.
4. Cifrado en tránsito (TLS/SSH) y exposición de datos.
5. Validación controlada de explotabilidad (solo prueba de concepto, no disrupción).

**Dominios de control auditados (ISO 27001:2022):**
- Tecnológicos (A.8): gestión de vulnerabilidades, hardening, criptografía, logging.
- Organizacionales (A.5): gestión de incidentes, políticas, proveedores.

## 5. Fuera de alcance (out-of-scope)

- Ataques de denegación de servicio (DoS/DDoS) y cualquier técnica disruptiva.
- Ingeniería social, phishing y acceso físico (salvo anexo contratado aparte).
- Sistemas, IP o dominios no listados explícitamente en la autorización.
- Modificación, borrado o exfiltración real de datos productivos.
- Auditoría financiera, contable o de RR.HH.

## 6. Reglas de enganche (Rules of Engagement)

1. **Autorización escrita previa** de un representante con facultad, con ventana temporal, IP de origen del auditor y rango objetivo. Sin esto no se ejecuta nada (Ley 21.459).
2. **Ventana de ejecución** acordada; fuera de ella, solo análisis documental.
3. **Técnicas permitidas:** reconocimiento pasivo/activo, enumeración, escaneo de vulnerabilidades, verificación de explotabilidad en modo seguro.
4. **Técnicas prohibidas:** disrupción de servicio, pivoting fuera del rango, persistencia, alteración de datos.
5. **Manejo de evidencia:** toda captura se almacena cifrada, con cadena de custodia y hash. Datos personales que aparezcan se minimizan/enmascaran de inmediato.
6. **Contacto de emergencia** y criterio de «stop»: ante señal de impacto productivo o hallazgo crítico activo, se detiene y se escala.

## 7. Criterios de evaluación y severidad

Cada hallazgo lleva **dos puntajes acoplados a su explicación**:

- **Severidad técnica:** CVSS v4.0 (vector completo registrado, no solo el número).
- **Impacto de cumplimiento:** alto / medio / bajo según si vulnera una obligación exigible (Ley 21.663), un control certificable (ISO 27001) o una brecha de preparación (Ley 21.719).

La prioridad de remediación combina ambos: un CVSS medio que incumple un deber de reporte de la Ley 21.663 escala por encima de un CVSS alto sin encuadre normativo.

## 8. Entregables

1. Informe técnico (pentest-report): hallazgos, evidencia reproducible, CVSS, plan de remediación con plazos.
2. Matriz de cumplimiento: hallazgo → control ISO → obligación legal → brecha → acción.
3. Resumen ejecutivo (1 página) para gerencia.
4. Repositorio de evidencia versionado y trazable.

## 9. Supuestos, dependencias y restricciones

- La organización entrega inventario de activos y punto de contacto técnico.
- La clasificación OIV / servicio esencial (si existe) se confirma al inicio, porque define las obligaciones exigibles de la Ley 21.663.
- El estado de vigencia de la Ley 21.719 se verifica a la fecha de ejecución.
