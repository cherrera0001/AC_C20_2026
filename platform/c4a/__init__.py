"""C4A — Plataforma de Auditoría de Ciberseguridad de Cumplimiento.

Primer ciclo: auditoría estática de un repositorio (solo lectura), con
evidencia verificable (hash + timestamp), clasificación de hallazgos,
correlación a CWE/CVSS/controles/normativas, y reportes reproducibles.

Diseño: modular, sin dependencias externas (solo librería estándar), para
que cada ejecución sea reproducible en cualquier máquina con Python 3.10+.
"""

__version__ = "0.1.0"
