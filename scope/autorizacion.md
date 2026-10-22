# Autorización de pruebas — PLANTILLA (Ley 21.459)

> **ESTADO: NO FIRMADA — COMPUERTA CERRADA.**
> Mientras este documento no esté completo y firmado por un representante con
> facultad, **no se ejecuta ningún comando contra el objetivo**. Solo se permite
> análisis documental. Esto lo exige el `docs/AUDIT_PROMPT.md` y la Ley 21.459.

> **Decisión del dueño (2026-10-21)**: el dueño del repositorio autoriza el ejercicio por tratarse
> de un laboratorio de pruebas (Metasploitable2, alcance declarado en `scope/alcance.md`). Se
> completaron solo los datos que ya constaban en el repositorio. Firmante, facultad, origen del
> auditor, ventana, contacto de emergencia y firma siguen por completar, así que la compuerta técnica
> sigue **cerrada** hasta que el documento esté firmado y con ventana vigente. Esta decisión habilita
> el ciclo de especificación y construcción; no habilita comandos de red.

## 1. Partes

| Campo | Valor |
|---|---|
| Organización auditada | Comercial Andes Sur SpA (cliente del informe de cierre según `docs/PROMPT_SPEC_KIT.md`; ejercicio de laboratorio) |
| Representante que autoriza | _(nombre y cargo)_ |
| Facultad para autorizar | _(cargo / poder que lo habilita)_ |
| Auditor responsable | Cristóbal Herrera Jara |
| IP de origen del auditor | _(IP desde la que se ejecutan las pruebas)_ |

## 2. Alcance autorizado

| Campo | Valor |
|---|---|
| Rango de red objetivo | `192.168.1.0/24` _(laboratorio)_ |
| Host(s) objetivo | `192.168.1.14` (Metasploitable2) |
| Activos explícitamente incluidos | Metasploitable2, host objetivo único del laboratorio (`scope/alcance.md` §4); nada fuera de esta lista se toca |
| Exclusiones | Todo sistema, dirección o dominio no listado en este documento, y las actividades de `scope/alcance.md` §5 |

## 3. Ventana temporal

| Campo | Valor |
|---|---|
| Inicio | _(fecha y hora)_ |
| Fin | _(fecha y hora)_ |
| Zona horaria | America/Santiago |

Fuera de esta ventana: solo análisis documental.

## 4. Reglas de enganche (resumen; detalle en `scope/alcance.md` §6)

- **Permitido:** reconocimiento pasivo/activo, enumeración, escaneo de
  vulnerabilidades, verificación de explotabilidad en modo seguro (solo PoC).
- **Prohibido:** DoS o técnicas disruptivas, persistencia, pivoting fuera de
  rango, modificación/borrado/exfiltración de datos reales, ingeniería social.
- **Evidencia:** toda captura se almacena en `evidence/` con timestamp y hash;
  los datos personales que aparezcan se enmascaran de inmediato.
- **Criterio de «stop»:** ante señal de impacto productivo o hallazgo crítico
  activo, se detiene y se escala al contacto de emergencia.

## 5. Contacto de emergencia

| Campo | Valor |
|---|---|
| Nombre | _(completar)_ |
| Vía y disponibilidad | _(teléfono / canal, horario)_ |

## 6. Firma

| Campo | Valor |
|---|---|
| Nombre y cargo | _(completar)_ |
| Fecha | _(completar)_ |
| Firma | _(completar)_ |

---
_Al completar y firmar, cambia el encabezado a **ESTADO: FIRMADA — COMPUERTA
ABIERTA** con fecha, y recién entonces el flujo del `docs/AUDIT_PROMPT.md` puede pasar
de la Fase 1 a la Fase 2._
