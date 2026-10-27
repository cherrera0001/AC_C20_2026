# Gestión ágil del proyecto C4A

## Tablero oficial

GitHub Project: [C4A — Gestión Ágil 2026](https://github.com/users/cherrera0001/projects/7), vinculado a `cherrera0001/AC_C20_2026`. El tablero remoto es la fuente de verdad para asignaciones, estado y planificación; este documento define el método. El proyecto se creó como **privado**; su visibilidad no se modifica aquí.

### Campos del Project

- **Status** (nativo): `Todo`, `In Progress`, `Done`.
- **Assignees** (nativo): una persona responsable principal; colaboradores y revisores se coordinan en la issue/PR.
- **Prioridad**: `P0 - Urgente`, `P1 - Alta`, `P2 - Media`, `P3 - Baja`.
- **Talla**: `XS`, `S`, `M`, `L`, `XL`, `XXL`, `Por definir`.
- **Fase C4A**: `Planificar`, `Recopilar`, `Analizar`, `Informar`, `Plataforma`, `Transversal`.
- **Tipo de trabajo**: `Épica`, `Historia de usuario`, `Tarea`, `Bug`, `Investigación`, `Documentación`.
- **Sprint**: texto corto, por ejemplo `2026-S01`; acordar duración y fechas en el equipo, no inferirlas.

## Flujo de trabajo

1. Crear una issue con el formulario adecuado y describir resultado, criterios de aceptación y dependencias.
2. Triage: confirmar tipo, fase, prioridad y talla; si falta información, mantener `Por definir` y no asignar un tamaño ficticio.
3. Dividir épicas en historias y tareas pequeñas, enlazadas con relaciones de sub-issues/bloqueos cuando sea posible.
4. Asignar una persona responsable, sprint y prioridad. Limitar trabajo en curso; mover el Status al iniciar y al terminar.
5. Cerrar solo cuando se cumplen los criterios de aceptación, existe evidencia/revisión requerida y se actualiza la documentación pertinente.

Para incorporar issues futuras automáticamente: en el Project, configura **Workflows → Auto-add to project** para el repositorio y selecciona las condiciones que el equipo quiera admitir. Comprueba el resultado con una issue de prueba; no se asume que la vinculación al repositorio active esta automatización.

## Guía de tallas y medición

La talla estima **esfuerzo relativo**, no horas ni fecha de entrega. Calibración inicial sugerida para obtener un indicador numérico agregable: `XS=1`, `S=2`, `M=3`, `L=5`, `XL=8`, `XXL=13`. Es una escala de planeación del equipo, no una equivalencia universal ni una promesa de duración. Recalibrarla tras 1–2 sprints usando trabajo terminado.

- **XS**: cambio acotado, conocido, pocas dependencias.
- **S**: alcance pequeño y criterios claros.
- **M**: trabajo moderado, incluye implementación y validación normales.
- **L**: varias partes o dependencias; requiere descomposición si se puede entregar por separado.
- **XL**: incertidumbre o integración significativa; preferir dividir en historias verticales.
- **XXL**: demasiado grande para comprometer como una historia; usar como señal para investigar y dividir antes de planificar.
- **Por definir**: falta descubrimiento suficiente; crear una tarea de investigación/refinamiento.

Si una historia parece superar XXL, dividirla. La incertidumbre alta se hace visible con una investigación (*spike*) con pregunta y límite de tiempo acordado, no se oculta inflando puntos. En triage, el equipo acuerda talla (por ejemplo, planning poker) y registra los supuestos.

### Métricas recomendadas

Medir por sprint/equipo: elementos terminados, suma de la escala de talla de elementos terminados, trabajo planificado frente a no planificado, tiempo de ciclo (inicio a Done), trabajo bloqueado/arrastrado y distribución de tallas. Usar varias iteraciones para tendencias y pronóstico; no convertir la suma en horas ni usarla para comparar o evaluar el rendimiento individual. Registrar la definición y el período de cada métrica.

## Definition of Ready (DoR)

- Objetivo y valor esperado comprensibles; criterios de aceptación comprobables.
- Tipo, fase, prioridad, talla o razón de `Por definir` identificados.
- Responsable y dependencias conocidos; alcance compatible con el sprint.
- Sin credenciales, datos personales ni detalles sensibles innecesarios en la issue.

## Definition of Done (DoD)

- Criterios de aceptación cumplidos y verificados; pruebas pertinentes pasan.
- Revisión aprobada cuando corresponda y cambios integrados mediante PR enlazado.
- Documentación, evidencia y trazabilidad actualizadas; secretos y datos personales protegidos.
- Estado de la issue y del Project actualizado; ninguna tarea abierta necesaria para declarar el resultado completo.

## Convenciones de seguridad del repositorio

Issues y Projects no autorizan pruebas sobre objetivos. Las tareas de auditoría de red siguen subordinadas a `scope/alcance.md` y `scope/autorizacion.md`; no ejecutar acciones de red sin autorización escrita, rango y ventana vigentes. No publicar evidencia cruda, secretos, datos personales ni artefactos ignorados por Git.
