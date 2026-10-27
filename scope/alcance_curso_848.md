# Alcance — Objetivo «Aula virtual del ejercicio» (borrador S01 para el curso 848)

**Estado**: BORRADOR propuesto por la herramienta — requiere corrección, revisión y firma
del auditor (principio I). **Fecha**: 2026-10-27. **No sustituye** a `scope/alcance.md`
(laboratorio Metasploitable 2) ni a `scope/autorizacion.md`: es el alcance de un segundo
objetivo, activado por el encargo del curso 848 (`01_plan/minuta_curso_848.md`).
**Compuerta: CERRADA** — `scope/autorizacion.md` sigue sin firmar; este documento no la
abre. Firmar este alcance tampoco la abre (igual que en S01).

## 1. Activo

| Campo | Valor |
|---|---|
| Tipo / rol | Plataforma LMS (Moodle) del ejercicio académico — aula virtual |
| Identificación | URL registrada por el dueño en `.env` (clave `URL_CURSO`; el valor vive solo ahí y en runtime de los scripts; nunca se versiona) |
| Curso en examen | id 848, «Auditoría a la Ciberseguridad» (Cuarto Ciclo) |
| Cuenta de trabajo | Cuenta del auditor (clave `USUARIO`/`CLAVE` en `.env`; usada solo por scripts en runtime, con valores enmascarados en toda salida) |

## 2. Dominios incluidos (in-scope)

1. **Integridad del curso 848**: disponibilidad de su vista, coherencia de sus referencias
   internas (secciones/módulos), comportamiento ante el error medido (HTTP 500,
   `invalidcoursemodule`).
2. **Autenticación y sesión del aula**: login con la cuenta del auditor, permisos
   efectivos de la cuenta, alcance del acceso (qué ve y qué no).
3. **Superficie web del aula (solo lectura)**: rutas alcanzables por navegación GET —
   cursos, informes visibles, huellas pasivas de versión/configuración expuestas por el
   propio sitio.
4. **Código aportado por el cliente**: análisis estático del código de la plataforma
   (núcleo, plugins de formato/tema, manifiestos de dependencias) cuando el dueño lo
   aporte; nunca se extrae código del objetivo en red.

## 3. Exclusiones (out-of-scope)

- Tráfico activo de cualquier tipo sin `scope/autorizacion.md` firmada y con ventana
  vigente (pruebas de intrusión, fuzzing, escaneo, envío de payloads).
- Denegación de servicio y cualquier técnica disruptiva; modificación, borrado o
  exfiltración de datos (propios o de terceros); pivoting fuera del aula.
- Otros cursos del aula salvo como **contraste de solo lectura** (ya medido: responden 200).
- Datos personales de terceros: si aparecen en alguna captura, se minimizan/enmascaran
  antes de persistir; la evidencia cruda queda fuera de git.
- Sistemas ajenos al aula (infraestructura del proveedor, frente de red, servicios
  internos no expuestos por navegación autenticada).

## 4. Método permitido (sin compuerta)

- Diagnóstico de solo lectura autenticado (Fase 1, ya ejecutada; skill `diagnostico-curso`).
- Análisis estático de código y artefactos **aportados** (Fase 2; skill `auditoria-php`,
  detector `php-shell`, SCA de manifiestos, REA para binarios aportados).
- Correlación de hechos a riesgo y cumplimiento (Fase 4) sobre lo ya medido.

## 5. Decisiones registradas

| Id | Decisión | Estado |
|---|---|---|
| D1 | Activar un segundo objetivo sin tocar el alcance del laboratorio | propuesta |
| D2 | Tratar el aula como activo por tipo/rol (LMS Moodle), sin inventariarla activamente | propuesta |
| D3 | Cursos hermanos solo como contraste pasivo | propuesta |
| D4 | Hipótesis H4 (manipulación) queda «pendiente de confirmar» hasta Fase 2 o 3 | propuesta |

## 6. Pendientes de confirmar

- P1: identidad del representante que firmaría la autorización del nuevo objetivo (hoy
  el dueño del repo decide; el aula es de terceros, verificar facultad).
- P2: si este encargo se especifica como **S11** del ciclo SDD o corre como auditoría
  puntual (decisión humana; aplaza `/speckit-specify`).
- P3: recepción del código de la plataforma para Fase 2.

_Contenido canónico en `scope/alcance_curso_848.json` (mismos datos, forma estructurada)._
