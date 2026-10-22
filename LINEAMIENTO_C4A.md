# Auditoría del repositorio y lineamiento C4A

Fecha de revisión: 19-10-2026, America/Santiago. Base local: `6a68de78e7d5f7900dbcd8b022b7ae24fb1bea9f`. Revisión documental y de código; no se ejecutaron pruebas contra Metasploitable. El archivo local no versionado `PROMPT_SPEC_KIT.md` se conserva íntegro.

## Dictamen

C4A tiene una base reutilizable de auditoría estática con evidencia, triaje y reportes. No está acreditada todavía como plataforma de evaluación de controles mediante pruebas sobre Metasploitable. El MVP debe cerrar la trazabilidad y la separación entre resultado técnico y dictamen del auditor antes de ampliar detectores o desarrollar una plataforma SaaS.

El objetivo es una herramienta del auditor: organiza alcance, registro de hechos e incertidumbres, enunciado de riesgo, cita normativa, perfil, lista de controles, encargo técnico, comunicación ejecutiva/técnica, borrador y cierre. Las cuatro fases existentes son la estructura de almacenamiento. No sustituyen esos productos del trabajo del auditor.

## Evidencia y hallazgos de esta revisión

### A01 — Alto: conclusión automática de cumplimiento

`platform/c4a/correlation.py::controls_matrix` asigna `no-cumple` a controles con hallazgos de severidad alta/crítica y `parcial` al resto. No exige decisión firmada ni verifica la aplicabilidad del requisito antes de concluir. Tampoco filtra por estado: los falsos positivos y riesgos aceptados pueden seguir alimentando la matriz después del triaje que aplica `orchestrator.py`.

Esto puede producir un dictamen incorrecto, aunque la detección técnica sea válida. Corrección propuesta: guardar observación y evaluación separadas; falso positivo descartado no acredita incumplimiento; riesgo aceptado no significa cumplimiento. Toda conclusión exige criterio, aplicabilidad, evidencia y revisión humana. Sin evidencia suficiente: `no-evaluado` o `pendiente-validacion`. Relación con backlog existente: #24, #29, #31 y #33.

### A02 — Alto: el objetivo técnico no coincide con el motor disponible

`scope/alcance.md` declara Metasploitable2. `platform/README.md` y el código implementan análisis estático de repositorios y SCA. El módulo de red está pendiente en `platform/ROADMAP.md`. Los informes bajo `04_informe/` corresponden a autoauditoría estática, no a una ejecución acreditada contra Metasploitable. `scope/autorizacion.md` está marcada NO FIRMADA — COMPUERTA CERRADA. No reutilizar resultados de VT o de la demo SCA como evidencia del laboratorio. Issues #3, #34–#37.

### A03 — Medio: cobertura normativa parcial

`platform/c4a/knowledge/controls_iso27001.json` contiene 12 controles, declarados explícitamente como subconjunto de ISO/IEC 27001:2022. `config.py` carga ese catálogo; no existe catálogo CIS ni evaluación de safeguards CIS. `PROMPT_SPEC_KIT.md` menciona CIS en S06: prueba de intención, no de implementación. La denominación correcta del estándar es ISO/IEC 27001:2022; ISO 27000 es una familia y no el identificador usado por este catálogo.

El catálogo `normativas.json` también declara ISO 27002, NIST CSF 2.0, SP 800-53 Rev.5, SSDF, leyes chilenas, SOC 2, PCI DSS y GDPR; ser seleccionable no acredita cobertura. NIST CSF 2.0 tiene seis funciones, mientras el prompt local habla de cinco: requiere corregir esa contradicción al especificar. Para CIS se propone v8.1, pendiente de contrastar con las guías académicas antes de fijarla como versión del encargo. Fuentes oficiales: [ISO](https://www.iso.org/standard/27001), [CIS](https://www.cisecurity.org/controls), [NIST](https://www.nist.gov/news-events/news/2024/02/nist-releases-version-20-landmark-cybersecurity-framework). Backlog #8–#11; CIS requiere refinamiento explícito.

Las afirmaciones legales históricas de `LINEA_ORIGEN.md` y `scope/alcance.md` son antecedentes, no una validación jurídica actual. Este trabajo no concluye vigencia, aplicabilidad, plazos de reporte ni artículos infringidos. El MVP debe registrar fuente oficial, fecha de consulta, artículo y fundamento de aplicabilidad; si faltan, `VALIDAR`. Una vulnerabilidad de una VM no demuestra por sí sola incumplimiento de una ley de una organización. Issues #10 y #25.

### A04 — Medio: reporte sin vínculo estructurado con issues

Existe un formato ejecutable en `platform/c4a/report.py`: resumen ejecutivo, informe técnico, riesgos, remediación, matrices y registros de evidencia/reproducción/triaje. `04_informe/README.md` es un índice de una ejecución, no una plantilla vacía. `Finding` en `model.py` no tiene enlace tipado a issue o Project, y `ControlResult` carece de revisión firmada y versión explícita del marco. Debe añadirse trazabilidad estructurada sin reemplazar el generador actual. Issues #28, #30, #31 y #33.

### A05 — Medio: seguimiento remoto sin planificación activa

Consultas autenticadas con `gh` bajo `cherrera0001`: Project privado #7, ID `PVT_kwHOASvtSs4BnGu9`, abierto, 18 campos y 40 elementos. Se consultó con límite 200; total 40, sin elementos pendientes de paginar. Sus elementos son las issues #1–#40 de este repositorio; las 40 issues siguen abiertas. Todos los elementos están en `Todo`, sin Sprint ni Assignees informados en el listado del Project. Existen los campos Prioridad, Talla, Fase C4A, Tipo de trabajo y Sprint previstos en `AGILE_PROJECT.md`.

El tablero sí registra el backlog, pero no acredita avance ni un compromiso de sprint. Las issues #38 (auto-add) y #39 (vistas) siguen abiertas; la existencia del tablero no prueba que esas configuraciones estén activas. No se verificaron workflows ni vistas en la interfaz.

La issue #40 conserva la afirmación histórica «remoto vacío / sin origin». Hoy existe origin y la API entrega `README.md` (blob `e94df8aa8980183807f288a2dade3f915ec9941d`); el remoto registra push el 15-10-2026 UTC. Debe reconciliarse esa issue con la evidencia antes de actualizarla o cerrarla. No se modificó el tablero. [Project oficial](https://github.com/users/cherrera0001/projects/7).

### A06 — Medio: Spec Kit aún no inicializado

No se encontró `.specify/` en esta raíz. El prompt existente es un insumo de trabajo, no ejecución de Spec Kit. Sus invocaciones, `feature.json` y `converge` deben contrastarse con la versión realmente instalada; no se presuponen capacidades. Este lineamiento no inicializa Spec Kit ni simula que se ejecutaron sus comandos.

Se respeta la instrucción del prompt local de detener la secuencia si falta `.specify/`. Las guías externas S00/S01–S10 no se auditaron en esta revisión: sus descripciones se conocen por el prompt, no por lectura de los DOCX originales. La fuente normativa y la plantilla académica definitiva requieren ese contraste.

### A07 — Alto: hash publicado no coincide con archivo de evidencia de comando

`platform/c4a/evidence.py::from_command` calcula SHA-256 del texto de salida, pero guarda un archivo con encabezados adicionales de comando/fecha. `write_manifest` publica ese hash junto al nombre del archivo en `SHA256SUMS.txt`. La verificación directa del archivo difiere, incluso sin alteración. Comprobado con salida sintética: `command_evidence_file_matches_manifest_hash=False`. Además, las evidencias `from_file` referencian rutas del objetivo, no copias bajo la carpeta del manifiesto; el procedimiento de verificación debe distinguir ambos casos.

La corrección propuesta es separar hash del contenido original y hash del artefacto persistido, registrar qué bytes acredita cada uno y verificar la integridad de forma independiente de la reproducción del detector. No asumir cifrado por disponer de hashes: el método escribe texto UTF-8 y el cifrado de custodia requiere decisión explícita (#23, #30). El caso de prueba y sus límites están en `VERIFICACION_C4A.md`. Incorporar esta corrección en el incremento 3 del Sprint 1 antes de usar evidencia importada para acreditar controles.

## Producto y límite del MVP

Usuario principal: auditor que necesita un expediente recorrible por un tercero y un borrador de informe revisable. Operación local con Python 3.10+, CLI existente y HTML existente como interfaz de consulta. Sin nueva base de datos, autenticación multiusuario, SaaS, agentes autónomos de explotación ni catálogo completo de todos los marcos.

El mínimo es una auditoría de un activo Metasploitable 2, con tres pruebas documentadas y sus controles aplicables revisados. Selección propuesta: exposición de servicios, configuración de autenticación y protección de comunicaciones. Son categorías de evidencia, no procedimientos ni resultados. Un control que necesite políticas, personas o procesos organizacionales no se acredita mediante una prueba de red: queda pendiente con solicitud documental.

Ruta de un sprint: importar evidencia sanitizada ya disponible y autorizada, o fixtures identificados como sintéticos, evaluar controles y generar informe borrador trazable. Si solo hay fixtures, la salida es una demostración de la herramienta y no una auditoría real del objetivo. Ruta de dos sprints: añadir importador de resultados técnicos y reevaluación del laboratorio; ejecutar contra el activo solo tras la compuerta vigente. La duración de los sprints y la capacidad no están definidas; son propuesta de alcance, no promesa de calendario.

## Modelo de evaluación

Conservar `Run`, `Evidence`, `Finding` y los identificadores deterministas. Añadir por evaluación: `assessment_id`, activo, `framework_id`, `framework_version`, `control_id`, requisito/fuente, aplicabilidad y motivo, criterio de éxito, tipo de prueba, `test_id`, resultado técnico, IDs de evidencia, hallazgos, limitaciones, fecha, auditor/revisor, decisión y justificación, estado de aprobación y links a issues.

Relación muchos-a-muchos: un hallazgo puede afectar varios controles y un control necesitar varias pruebas. CWE→control es una sugerencia explicada, nunca prueba de incumplimiento. El CVSS conserva versión y vector; el motor actual calcula v3.1. La discrepancia con v4.0 solicitada por el contrato se resuelve en #27 antes de declarar conformidad; no se cambia el nombre de la versión al exportar.

Separar tres dimensiones: resultado técnico (`positivo`, `negativo`, `inconcluso`, `no-ejecutado`); cumplimiento (`cumple`, `parcial`, `no-cumple`, `no-evaluado`, `no-aplica`); aprobación (`borrador`, `revisado`, `firmado`). `No-aplica` necesita motivo aprobado. «Sin hallazgos» no implica «cumple». Un estado «cumple» requiere pruebas suficientes del criterio y aprobación del auditor. La aceptación de riesgo se registra por separado y no convierte un incumplimiento en cumplimiento.

Para mostrar nivel de control, usar una rúbrica propuesta y explícitamente propia de C4A: 0 sin evidencia; 1 diseño documentado; 2 implementación evidenciada; 3 eficacia comprobada para el alcance/fecha. No presentarla como escala oficial ISO o CIS. Un fallo técnico conserva el nivel de implementación y registra eficacia fallida; la escala no debe ocultar el resultado ni el riesgo residual. Si se calcula cobertura: controles aplicables evaluados / controles aplicables seleccionados, mostrando numerador, denominador y pendientes. No extrapolar al SGSI ni a los 93 controles ISO.

## Secuencia Spec Kit propuesta

Usar [Spec Kit oficial](https://github.com/github/spec-kit) y su [quickstart](https://github.com/github/spec-kit/blob/main/docs/quickstart.md). Al inicializar, consultar la ayuda de la versión instalada para repositorio existente e integración de agente; revisar archivos generados y preservar el código y prompt existentes. No inventar flags ni sobrescribirlos silenciosamente.

Tras inicializar y revisar la salida: constitución → especificación → aclaraciones → plan → checklist → tareas → análisis de coherencia → implementación y validación. Usar los nombres de comandos que provea esa versión. La constitución recoge trazabilidad, criterio humano, control versionado y compuerta del objetivo. La especificación describe necesidades y aceptación; el plan define cómo extender el motor. Las tareas se vinculan después a issues existentes. No declarar una fase ejecutada por haber redactado este documento.

Mantener el ciclo secuencial por producto del prompt local S01–S10: cada funcionalidad debe converger antes de avanzar a la siguiente. Agrupar sus incrementos en los dos sprints siguientes no autoriza construir diez épicas en paralelo. Si la versión instalada no incluye convergencia automatizada, documentar una revisión de aceptación equivalente sin afirmar que se invocó un comando inexistente.

## Incrementos y backlog propuesto

Sprint 1, base demostrable:

1. Cerrar especificación de alcance, registro de hechos y riesgo; resolver criterio de cumplimiento y discrepancia CVSS (#19–#21, #24, #26–#29). Aceptación: no existe conclusión final a partir de CVSS solamente y la ausencia de datos se conserva.
2. Incorporar cita versionada, perfil y lista mínima ISO/CIS con justificación humana (#8–#11; refinamiento CIS aún sin issue). Tres controles relevantes como máximo inicial, IDs y equivalencias sujetos a validación; no prometer completar todos los catálogos de #9 en este sprint.
3. Definir encargo/importación de tres pruebas, integridad de evidencia y vínculo a hallazgos (#22, #23, #30). Aceptación: hash alterado se detecta; evidencia de otro activo o corrida no acredita esta evaluación; fixture queda rotulado.
4. Producir comunicación ejecutiva/técnica y borrador de cierre usando formato existente (#31–#33). Aceptación: navegación control → evaluación → prueba → evidencia → hallazgo → issue, con pendientes y revisión explícitos.

Sprint 2, integración y cierre:

5. Refinar compuerta y adaptador de importación de resultados del laboratorio (#34–#36). Aceptación: autorización ausente, incompleta, vencida o activo fuera de alcance bloquean ejecución; se prueba con fixtures, sin tocar red.
6. Si se abre la compuerta, recopilar las tres evidencias del activo (#37); si no, conservar el resultado `no-ejecutado` y no sustituirlo por un resultado simulado. Registrar herramientas/versiones y condiciones de repetición.
7. Reevaluar, revisar y emitir cierre con riesgos residuales y firmas (#31, #33; aprovechar #5/#6 solo para comparación mínima necesaria, difiriendo tendencia #7).
8. Reconciliar Project y evidencias (#4, #38–#40): decidir responsable/sprint, actualizar estado cuando corresponda y verificar incorporación de issues. No cerrar por existencia de código previo.

Prioridad propuesta: corregir dictamen y trazabilidad antes de agregar ejecución activa. Responsables, tallas, duración y fechas requieren capacidad del equipo; no fueron asignados. La lista anterior agrupa issues existentes, no compromete completarlas íntegramente. Dividirlas si su alcance supera este MVP. Diferir catálogos completos, IaC/SAST/cloud, empaquetado y comparativas históricas amplias. No crear otra épica o Project duplicado.

## Informe final y aceptación

Reutilizar `platform/c4a/report.py` y `04_informe/` para índice, resumen ejecutivo, informe técnico, riesgos, plan de remediación, matrices y registros. [PLANTILLA_CIERRE_C4A.md](04_informe/PLANTILLA_CIERRE_C4A.md) explicita los campos nuevos y no altera los resultados históricos.

Cada ficha debe incluir marco/versión/control y fuente, requisito aplicable, activo y alcance, prueba y resultado, evidencia/hash, hallazgo/CWE/CVE solo si consta, CVSS con versión, confianza/limitaciones, issue URL/estado, responsable acordado, acción, reevaluación y dictamen humano. Para un control sin hallazgo se conserva la fila y la evidencia; sin prueba suficiente se mantiene pendiente.

DoD del MVP: pruebas pertinentes pasan; se verifican falso positivo, riesgo aceptado, control sin evidencia, control no aplicable, hash alterado, importación duplicada, fuente desconocida y enlace a issue; el HTML no interpreta como código el texto importado; no se exportan secretos; ninguna conclusión excede el activo/fecha evaluados. Una issue Done exige criterio demostrado y vínculo a evidencia revisada; no equivale a control cumplido. El informe final exige aprobación registrada y entrega de pendientes al auditor.

## Comparativa de mercado

Revisión de documentación pública oficial del 19-10-2026. Capacidades declaradas por proveedores; no es prueba de producto, benchmark ni verificación de disponibilidad contractual. No se comparan precios sin cotización.

- **Drata**: su documentación vincula controles, evidencias, responsables y monitorización automatizada. Referente para biblioteca de evidencia y estado de preparación. Implicación para C4A: tomar ese vínculo explícito y su historial; el MVP local no debe intentar reproducir su amplitud de conectores. [Producto](https://drata.com/products/compliance-automation), [Evidence Overview](https://help.drata.com/en/articles/13404035-evidence-overview).
- **eramba**: documenta requisitos, controles, auditorías y evidencia, con pruebas manuales y automatizadas; indica que no es herramienta de gestión de vulnerabilidades. Referente para distinguir diseño del control y auditoría de eficacia. Implicación: C4A debe unir evaluación de cumplimiento con evidencia técnica importada. [Compliance Management](https://www.eramba.org/compliance-management), [Controles y auditorías](https://www.eramba.org/learning/courses/82).
- **DefectDojo**: documenta importación, deduplicación y triaje de hallazgos, y conectores a seguimiento de issues. Referente para normalización, deduplicación y remediación. Implicación: C4A debe añadir identidad de prueba y links estables a issues, sin construir un catálogo equivalente de conectores. [Documentación](https://docs.defectdojo.com/), [Issue Tracking](https://docs.defectdojo.com/connectors/issue_tracking/).
- **C4A hoy**: CLI local, seis detectores estáticos, evidencia con hash, CVSS v3.1, mapa CWE→ISO, triaje, SARIF e informe HTML. Faltan CIS implementado, evaluación humana estructurada, evidencia del objetivo y correlación con issues. Evidencia: código y documentos locales citados arriba; capacidades no medidas en producción.

Posicionamiento propuesto, por inferencia: expediente local del auditor que une requisito, control, prueba reproducible y reporte con issue; complemento a GRC y gestión de vulnerabilidades. Es una hipótesis de producto para validar con un auditor y una corrida completa, no una ventaja de mercado ya demostrada.

## REA y verificaciones operativas

Clonado `morluto/rea` en `.audit-tools/rea`, SHA `833136507dd79d959340b09862a53af344e4f1b3`; versión declarada 6.7.0. El directorio se excluye de Git. REA se presenta como MCP de ingeniería inversa; no es una base de datos de mercado. [Fuente oficial](https://github.com/morluto/rea).

El resultado de la sesión MCP y de las pruebas se registra en [VERIFICACION_C4A.md](VERIFICACION_C4A.md). Las afirmaciones comerciales anteriores provienen de documentación oficial, no se atribuyen a REA si este no observó esas funcionalidades. No se eluden autenticación, licencias ni protecciones para inspeccionar soluciones.
