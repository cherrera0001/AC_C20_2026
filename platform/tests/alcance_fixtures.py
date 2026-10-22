"""Insumos SINTÉTICOS para las pruebas de S01 — El alcance.

Rotulados como fixture (principio III de la constitución): su resultado demuestra
la herramienta, no audita el objetivo del ejercicio. Las direcciones usadas son
de documentación (RFC 5737) y existen solo para probar que no se copian.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

ROTULO = "FIXTURE SINTÉTICO — no es el ejercicio"

# Vacíos conocidos del fixture completo (SC-001). Cada uno es una fila pendiente:
#   marcos no declarados: NIST CSF 2.0, CIS Controls v8.1 ............ 2
#   obligaciones sin fuente/fecha/artículo/fundamento (VALIDAR) ...... 2
#   dominios sin motivo (2 técnicos + 2 de control) .................. 4
#   exclusión de §5 sin motivo ....................................... 1
#   exclusión de activos «por completar» en la autorización .......... 1
#   regla de evidencia cifrada (el sistema no la garantiza) .......... 1
#   organización auditada «por completar» ............................ 1
#   compuerta: firma, completitud y ventana no favorables ............ 3
VACIOS_FIXTURE_COMPLETO = 15


def _host_lines(hosts: int) -> str:
    nombres = ["MaquinaSintetica", "OtraMaquina", "TerceraMaquina"]
    return "".join(
        f"- Host objetivo `192.0.2.{10 + i}` ({nombres[i]}).\n" for i in range(hosts)
    )


def alcance_md(*, hosts: int = 1, version_iso: bool = True) -> str:
    iso = "ISO/IEC 27001:2022" if version_iso else "ISO/IEC 27001"
    return f"""# Definición de Alcance — {ROTULO}

## 1. Identificación y propósito

| Campo | Valor |
|---|---|
| Servicio | Auditoría sintética |

## 3. Marco de referencia y mapeo normativo

| Marco | Qué cubre en esta auditoría | Estado (sep-2026) |
|---|---|---|
| **{iso}** | 93 controles del Anexo A | Vigente |
| **Ley 21.663 + ANCI** | Gestión de incidentes y reporte | **Exigible** |
| Ley 21.459 (delitos informáticos) | No se audita: delimita lo legalmente permitido durante las pruebas | Vigente |

## 4. Alcance incluido (in-scope)

**Activos y red (ejemplo, laboratorio sintético):**
- Segmento `192.0.2.0/24`.
{_host_lines(hosts)}
**Dominios técnicos evaluados:**
1. Superficie de red y servicios expuestos.
2. Cifrado en tránsito (TLS/SSH) y exposición de datos.

**Dominios de control auditados (ISO 27001:2022):**
- Tecnológicos (A.8): gestión de vulnerabilidades.
- Organizacionales (A.5): gestión de incidentes, políticas, proveedores.

## 5. Fuera de alcance (out-of-scope)

- Ataques de denegación de servicio.

## 6. Reglas de enganche (Rules of Engagement)

1. **Autorización escrita previa** antes de ejecutar nada.
2. **Manejo de evidencia:** toda captura se almacena cifrada, con cadena de custodia y hash.

## 9. Supuestos, dependencias y restricciones

- La clasificación OIV se confirma al inicio.
"""


def autorizacion_md(
    *,
    firmada: bool = False,
    ventana: Optional[Tuple[str, str]] = None,
    organizacion: str = "_(completar)_",
    exclusiones: str = "_(IP/servicios que NO se tocan)_",
) -> str:
    estado = "FIRMADA — COMPUERTA ABIERTA" if firmada else "NO FIRMADA — COMPUERTA CERRADA"
    inicio, fin = ventana if ventana else ("_(fecha y hora)_", "_(fecha y hora)_")
    rep = "Representante Sintético, gerente" if firmada else "_(nombre y cargo)_"
    firma_nombre = "Representante Sintético" if firmada else "_(completar)_"
    firma_fecha = "2026-10-01" if firmada else "_(completar)_"
    firma = "firmado" if firmada else "_(completar)_"
    return f"""# Autorización de pruebas — {ROTULO}

> **ESTADO: {estado}.**

## 1. Partes

| Campo | Valor |
|---|---|
| Organización auditada | {organizacion} |
| Representante que autoriza | {rep} |
| Auditor responsable | Auditor Sintético |

## 2. Alcance autorizado

| Campo | Valor |
|---|---|
| Rango de red objetivo | `192.0.2.0/24` |
| Host(s) objetivo | `192.0.2.10` (MaquinaSintetica) |
| Exclusiones | {exclusiones} |

## 3. Ventana temporal

| Campo | Valor |
|---|---|
| Inicio | {inicio} |
| Fin | {fin} |
| Zona horaria | America/Santiago |

## 6. Firma

| Campo | Valor |
|---|---|
| Nombre y cargo | {firma_nombre} |
| Fecha | {firma_fecha} |
| Firma | {firma} |
"""


def construir(
    raiz: Path,
    *,
    alcance: bool = True,
    autorizacion: bool = True,
    hosts: int = 1,
    version_iso: bool = True,
    **kw_aut,
) -> Path:
    """Escribe scope/alcance.md y scope/autorizacion.md sintéticos bajo `raiz`."""
    scope = raiz / "scope"
    scope.mkdir(parents=True, exist_ok=True)
    if alcance:
        (scope / "alcance.md").write_text(
            alcance_md(hosts=hosts, version_iso=version_iso), encoding="utf-8")
    if autorizacion:
        (scope / "autorizacion.md").write_text(autorizacion_md(**kw_aut), encoding="utf-8")
    return raiz
