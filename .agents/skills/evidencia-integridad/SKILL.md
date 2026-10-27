---
name: "evidencia-integridad"
description: "Cadena de custodia verificable: hash SHA-256 sobre los bytes realmente persistidos, distinción entre hash del original y del artefacto guardado, manifiesto, verificación independiente del detector y detección de alteraciones."
metadata:
  author: "c4a"
  scope: "project"
  version: "1.0.0"
---

# evidencia-integridad

Custodia de la evidencia del proceso C4A (principio III de la constitución): todo hash
publicado corresponde exactamente a los bytes persistidos que acredita, y la integridad
se verifica de forma independiente de la reproducción del detector.

## Cuándo usarla

- Al cerrar cualquier corrida que escriba en `evidence/<run>/`.
- Antes de citar una evidencia en una ficha de hallazgo, en el registro (S02) o en el
  informe (S09/S10).
- Periódicamente en frío: re-verificar `SHA256SUMS.txt` de corridas históricas.
- Siempre que se copie evidencia de un medio a otro (original → copia guardada).

## Cómo correrla

```bash
cd platform
python3 -m c4a verify --config <cfg> --run <RUN-ID>     # por hallazgo: re-lee, re-hash, marca reproduced/external
python3 -m c4a reproduce --config <cfg> --run <RUN-ID>  # por ciclo: result_hash por contenido
# Verificación en frío de una corrida histórica:
cd evidence/<run> && sha256sum -c SHA256SUMS.txt
```

## Qué se exige de cada evidencia

- **Dos hashes cuando hay copia**: el del contenido original y el del artefacto guardado,
  declarando qué bytes acredita cada uno. Referenciar un archivo del objetivo sin copiarlo
  se declara explícitamente (nunca se deja implícito).
- **Manifiesto + sumas**: `MANIFEST.json` con identificador, tipo, fuente, fecha,
  responsable y estado; `SHA256SUMS.txt` calculado **sobre los archivos ya escritos**
  (no hashear antes de añadir encabezados: la suma debe verificar el archivo tal como
  quedó en disco).
- **Independencia**: la verificación no re-corre el detector; solo re-lee bytes y compara.
- **Prohibido mezclar corridas**: evidencia de otro activo o de otra corrida no acredita
  una evaluación y se rechaza en el registro con su motivo.
- **Fixtures rotulados**: un fixture sintético se marca como tal; su resultado es
  demostración de la herramienta, no auditoría del objetivo.
- **Hash ≠ cifrado**: tener hashes no implica cifrado de custodia; el cifrado es decisión
  explícita del dueño y se registra aparte.
- **Alteración detectable**: si una suma no calza, la evidencia queda invalidada y el
  hecho que la citaba retrocede a «pendiente de validación» — no se «corrige» el hash.
