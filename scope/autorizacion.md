# Autorización de pruebas — PLANTILLA (Ley 21.459)

> **ESTADO: NO FIRMADA — COMPUERTA CERRADA.**
> Mientras este documento no esté completo y firmado por un representante con
> facultad, **no se ejecuta ningún comando contra el objetivo**. Solo se permite
> análisis documental. Esto lo exige el `AUDIT_PROMPT.md` y la Ley 21.459.

## 1. Partes

| Campo | Valor |
|---|---|
| Organización auditada | _(completar)_ |
| Representante que autoriza | _(nombre y cargo)_ |
| Facultad para autorizar | _(cargo / poder que lo habilita)_ |
| Auditor responsable | Cristóbal Herrera Jara |
| IP de origen del auditor | _(IP desde la que se ejecutan las pruebas)_ |

## 2. Alcance autorizado

| Campo | Valor |
|---|---|
| Rango de red objetivo | `192.168.1.0/24` _(laboratorio)_ |
| Host(s) objetivo | `192.168.1.14` (Metasploitable2) |
| Activos explícitamente incluidos | _(listar; nada fuera de esta lista se toca)_ |
| Exclusiones | _(IP/servicios que NO se tocan)_ |

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
ABIERTA** con fecha, y recién entonces el flujo del `AUDIT_PROMPT.md` puede pasar
de la Fase 1 a la Fase 2._
