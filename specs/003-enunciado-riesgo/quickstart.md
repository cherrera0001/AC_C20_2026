# Quickstart: S03 — El enunciado

Validación de punta a punta con fixtures sintéticos (rotulados como tales) y con el producto real.

## 1. Línea base

```bash
cd platform && python -m unittest discover -s tests
```

129 pruebas en verde (78 de S01/plataforma + 51 de S02). Si algo falla, detenerse y reportar.

## 2. Abrir el enunciado sobre el producto real de S02

```bash
cd platform
python -m c4a registro abrir --raiz ..        # idempotente: regenera la entrega de S02
python -m c4a enunciado abrir --raiz ..
```

Hoy el registro tiene 0 hechos y 8 «no consta»: el producto tiene 0 enunciados y lista 8 vacíos
heredados, estado «borrador». No contiene estados de cumplimiento ni extractos de evidencia.

## 3. Ciclo completo con fixture sintético (pasos con evidencia)

```bash
# en un directorio temporal creado por los tests; a mano:
python -m c4a alcance proponer --raiz <tmp>          # alcance sintético
python -m c4a registro abrir --raiz <tmp>
python -m c4a registro aportar --raiz <tmp> --activo <A> --dominio <A-…> \
    --afirmacion "…" --resultado positivo --evidencia <archivo> \
    --tipo documental --fecha-recoleccion 2026-10-26 --autor "…" --origen "…"
python -m c4a registro firmar --raiz <tmp> --firmante "…" --motivo "…"   # tras revisar
python -m c4a enunciado abrir --raiz <tmp>
python -m c4a enunciado corregir --raiz <tmp> --enunciado R-… --campo impacto \
    --valor "…" --motivo "…" --autor "…"
python -m c4a enunciado revisar --raiz <tmp> --autor "…" --motivo "…"
python -m c4a enunciado firmar --raiz <tmp> --firmante "…" --motivo "…"
python -m c4a enunciado verificar --raiz <tmp>
python -m c4a enunciado entregar --raiz <tmp> --json
```

## 4. Qué comprobar

- `enunciados_s03.json` valida contra `contracts/enunciados_s03.schema.json`.
- Los enunciados citan hecho y evidencias con huellas; los vacíos heredados no tienen enunciado.
- `03_hallazgos/README.md` y `matriz_cumplimiento.csv` no cambian (huellas antes/después).
- Dos `abrir` seguidos producen bytes idénticos.
- Alterar un byte de una copia en `evidence/registro_s02/` hace que `verificar` informe
  «evidencia alterada» y la entrega excluya ese enunciado.

## 5. Resultado de la validación

Validación de punta a punta sobre la raíz del repositorio (2026-10-26): suite completa
`python -m unittest discover -s tests` → 239 pruebas en verde (línea base 129 + 110 de
S03 y los sprints S04–S10 construidos en la misma jornada, por orden del dueño). Con el
registro real vigente (0 hechos, 8 «no consta» por compuerta cerrada): `enunciado abrir`
produjo 0 enunciados y 8 vacíos heredados, con aviso de registro no firmado; los archivos
previos de `03_hallazgos/` quedaron con huella idéntica (SC-010) y una búsqueda sobre los
archivos generados no encontró estados de cumplimiento ni direcciones de red (SC-003).
No se corrigió ni firmó nada: eso es del auditor (T033 pendiente, acción humana).
