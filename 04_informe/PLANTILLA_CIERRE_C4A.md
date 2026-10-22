# Plantilla complementaria de cierre C4A

Estado: BORRADOR / REVISADO / FIRMADO. Plantilla de diseño; no contiene resultados acreditados.

## Identificación y autorización

Encargo, organización confirmada, auditor, revisor, fecha/zona horaria, activo, alcance, exclusiones, versión del informe, run_id, SHA del código y autorización/ventana referenciada. No publicar detalles sensibles del laboratorio.

## Resumen ejecutivo

Objetivo, alcance realmente probado, resultado sustentado, riesgos prioritarios, decisiones solicitadas y limitaciones. Distinguir ejecución real, análisis documental y demostración con fixtures. No equiparar ausencia de hallazgos con cumplimiento.

## Criterios y cobertura

Marco, versión, identificadores y fuentes; aplicabilidad justificada; criterios de éxito y limitaciones por control. Informar controles aplicables seleccionados, evaluados y pendientes con denominadores explícitos. Separar prueba técnica y evidencia organizacional. Citas legales sin artículo/fuente vigente: VALIDAR.

## Evaluación por control — repetir para cada control seleccionado

- Identidad: assessment_id, activo, framework_id/version, control_id y requisito/fuente.
- Aplicabilidad y motivo; criterio de éxito, tipo de evidencia requerida.
- test_id, fecha, herramienta/versión, resultado técnico y condiciones de repetición.
- Evidence IDs, ubicación protegida, SHA-256 y verificación de integridad.
- Finding IDs, CWE/CVE si constan, CVSS/versión/vector, confianza y limitaciones.
- Cumplimiento propuesto y razonamiento; evidencia faltante; nivel C4A y fundamento, sin atribuirlo al estándar.
- Decisión humana, auditor/revisor, fecha y estado de aprobación.
- Issue URL/ID, estado de consulta, acción, responsable y plazo acordados.
- Reevaluación: corrida/prueba, evidencia, resultado y riesgo residual.

La relación entre controles, pruebas, evidencias, hallazgos e issues es muchos-a-muchos. Conservar también controles sin hallazgo o sin prueba. Un falso positivo no prueba incumplimiento; riesgo aceptado no prueba cumplimiento.

## Remediación y seguimiento

Priorizar por riesgo técnico y contexto/aplicabilidad fundamentados. Referenciar issues existentes y Project #7. Separar estado de desarrollo de estado de cumplimiento. Registrar datos desconocidos como pendientes, sin inventar responsables o fechas.

## Cierre y anexos

Dictamen limitado al alcance y fecha, pendientes, riesgos residuales, aprobación/firma humana y control de versiones. Anexar matriz de cumplimiento, mapa CWE/CVE/CVSS, registros de evidencia, reproducción y triaje; referencia al índice generado por `report.py`. Un borrador no se presenta como informe firmado.
