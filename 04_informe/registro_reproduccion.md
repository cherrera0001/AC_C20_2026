# Registro de reproducción

Ejecución RUN-20261006T110708Z-aad4 · hash de resultado `e3b0c44298fc1c14…`

Cómo reproducir la auditoría completa:

```
python3 -m c4a run --config audit.example.json
python3 -m c4a reproduce --run RUN-20261006T110708Z-aad4
```

La reproducción re-ejecuta la auditoría y compara cada hallazgo por id determinista y por hash de evidencia. Estados posibles: reproducido, parcial, no reproducido.

| ID | Estado | Comando de verificación |
|---|---|---|
| - | - | - |