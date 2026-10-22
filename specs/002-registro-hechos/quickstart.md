# Quickstart: validar S02 — El registro

Todo local, sin red y sin leer `.env`. Contrato: [contracts/cli-registro.md](contracts/cli-registro.md).
Forma de los archivos: [data-model.md](data-model.md).

## 1. Pruebas automáticas

```text
python -m unittest discover -s tests
```

Esperado: la suite existente (78) y las pruebas de S02 en verde. Usan fixtures sintéticos rotulados.

## 2. Abrir el registro del ejercicio

```text
python -m c4a registro abrir --raiz ..
```

Esperado: `02_evidencia/registro_s02.json` y `.md`. Con el alcance en borrador, una entrada «no consta»
por el activo y por cada dominio dentro o pendiente; el registro declara que el alcance no está
firmado. `02_evidencia/inventario.json` y `scope/` no cambian.

## 3. Aportar una evidencia documental

```text
python -m c4a registro aportar --raiz .. --activo "<activo del alcance>" --dominio <A-…> --afirmacion "<lo que el documento muestra>" --resultado positivo --evidencia <ruta> --tipo documental --origen "<de dónde viene>" --fecha-recoleccion <AAAA-MM-DD> --autor "<auditor>"
```

Esperado: una entrada «hecho» con la huella del original y de la copia en `evidence/registro_s02/`; la
entrada «no consta» de ese dominio queda «superada».

## 4. Rechazos

- Evidencia técnica con la compuerta cerrada → rechazo «sin autorización vigente».
- Aporte con `--corrida` de una corrida del análisis estático → rechazo «otro objetivo».
- Activo distinto del alcance → rechazo con la fila que lo decide.

## 5. Corregir, firmar y verificar

```text
python -m c4a registro corregir --raiz .. --entrada <H-…> --campo resultado --valor inconcluso --motivo "<motivo>" --autor "<auditor>"
python -m c4a registro firmar   --raiz .. --firmante "<auditor>" --motivo "<justificación>"
python -m c4a registro verificar --raiz ..
```

## 6. Verificación manual

- SC-008: cronometrar la identificación de todo lo que no consta en `02_evidencia/registro_s02.md`.
- SC-009: recorrer una entrada por dominio hasta su evidencia y comprobar la huella.
