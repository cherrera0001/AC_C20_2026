# S06 (móvil) — La lista: CIS Controls v8.1 aplicables, anclados en hechos

**Estado**: FIRMADO el 2026-10-29T01:50:33Z — `movil_lista_s06.firma.json`. Seleccionar un control no es un dictamen de cumplimiento; la versión del catálogo es v8.1 (fuente oficial CIS).

## 1 — Inventario y control de activos
Justificación de aplicabilidad: H1+H2+H6: inventario del dispositivo, la aplicación y su superficie exportada realizado y custodiado.

## 2 — Inventario y control de software
Justificación de aplicabilidad: H2: versión exacta, instalador (Play) y fecha de actualización registrados; APK con digest verificado.

## 3 — Protección de datos
Justificación de aplicabilidad: H5+H7: permisos sensibles concedidos/denegados y exclusión total de backups (datos protegidos por diseño de la app).

## 4 — Configuración segura de activos y software
Justificación de aplicabilidad: R1+R6+R8: superficie exportada sin permiso, parche 2026-09-01 y configuración de red (cleartext base, CA usuario con override de pins, pin-set en dominios clave).

## 6 — Gestión de accesos
Justificación de aplicabilidad: H5: gestión de accesos del usuario — denegaciones de SMS/llamadas/legacy storage; biometría concedida.

## 7 — Gestión continua de vulnerabilidades
Justificación de aplicabilidad: R6+R7: parche de plataforma (~2 meses) y versión vigente de la app con auto-actualización.

## 10 — Defensas contra malware
Justificación de aplicabilidad: R3: REQUEST_INSTALL_PACKAGES declarado — superficie a vigilar ante malvertising.

## 11 — Recuperación de datos
Justificación de aplicabilidad: H7: alcance de respaldo — la app excluye todo su almacén en backup y transferencia.

## 16 — Seguridad de aplicaciones
Justificación de aplicabilidad: R1+R8: seguridad de la aplicación — componentes exportados y configuración de red del APK analizados estáticamente.

No seleccionados (alcance personal/monousuario): 5, 8, 9, 12, 13, 14, 15, 17, 18 — orientados a organización, red corporativa o procesos no presentes en este ejercicio; quedan fuera sin perjuicio de reconsiderarlos si el alcance cambia.