---
name: "correlacion-cumplimiento"
description: "Lleva un hecho verificado a su encuadre: enunciado de riesgo (S03), cita con marco+versión+identificador (S04), perfil NIST CSF 2.0 (S05) y lista CIS v8.1 (S06). Las correspondencias son sugerencias explicadas que el auditor firma; nunca pruebas automáticas de incumplimiento."
metadata:
  author: "c4a"
  scope: "project"
  version: "1.0.0"
---

# correlacion-cumplimiento

Fase 4 del proceso (`docs/INSTRUCCION_AUDITORIA_CURSO.md`): consume los hechos firmados
del registro (S02) y propone la cadena S03–S06. Es el puente del proceso híbrido: el
hallazgo técnico gana encuadre normativo (y al revés) sin que ninguno se confunda con
el otro (principio II de la constitución).

## Cuándo usarla

- Hay hechos vigentes (`registro entregar`) que hay que enunciar, citar, perfilar y
  listar.
- Se necesita la matriz de cumplimiento del informe (hallazgo → control ISO →
  obligación legal → brecha → acción).

## Cómo correrla

```bash
cd platform
python3 -m c4a enunciado abrir --raiz ..   # S03: un riesgo por hecho (condición, consecuencia, criterio, lo que falta)
python3 -m c4a cita abrir --raiz ..        # S04: marco, versión e identificador por riesgo
python3 -m c4a perfil abrir --raiz ..      # S05: seis funciones NIST CSF 2.0
python3 -m c4a lista abrir --raiz ..       # S06: CIS Controls v8.1 anclados en hechos
python3 -m c4a cita corregir ...           # el auditor corrige; luego revisar y firmar
```

Fuentes de verdad: `platform/c4a/knowledge/` (`cwe_map.json`, `controls_iso27001.json`,
`controls_cis.json`, `normativas.json`). La spec viva de cada sprint está en
`specs/003-enunciado-riesgo/` a `specs/006-lista-cis/`.

## Reglas que no se negocian

- **Cita completa o nada.** Todo control se cita con marco, versión e identificador
  (principio IV). Si el identificador no consta en la fuente, queda «pendiente de
  confirmar»: no se inventa.
- **Sugerencia ≠ prueba.** Una correspondencia CWE→control es una sugerencia explicada;
  el triaje y la firma son del auditor. La severidad CVSS no produce por sí sola un
  «no-cumple» (principio II).
- **Obligaciones legales con ficha.** Ley 21.663 (exigible) y Ley 21.719 (en
  preparación) se registran con fuente oficial, fecha de consulta, artículo y
  fundamento de aplicabilidad; si falta alguno, «VALIDAR». Una vulnerabilidad no
  demuestra por sí sola incumplimiento legal de una organización.
- **Marco mencionado ≠ marco implementado.** ISO 27001:2022, NIST CSF 2.0 y CIS v8.1
  están implementados como bases de conocimiento; seleccionarlos no acredita cobertura.
- **Un control que pide políticas, personas o procesos** no se acredita con una prueba
  técnica: queda «pendiente-documental» con solicitud al cliente.
