---
name: "net-compuerta"
description: "Verifica si la compuerta de autorización permite una actividad de red, leyendo scope/autorizacion.md y scope/alcance.md. Usar antes de cualquier diagnóstico o prueba de red."
argument-hint: "Actividad y activo a verificar"
user-invocable: true
disable-model-invocation: false
---

## Entrada

```text
$ARGUMENTS
```

## Pasos

1. Si la entrada no dice qué actividad y sobre qué activo, pregúntalo.
2. Delega en el agente `guardian-alcance` con la actividad y el activo.
3. Muestra su respuesta tal cual (COMPUERTA, Actividad, Activo, Motivo).
4. Si es CERRADA, lista los campos faltantes de `scope/autorizacion.md` y termina.
   No ofrezcas formas de saltarse la compuerta.
5. Si es ESTACIÓN LOCAL, recuerda que el resultado no es evidencia de la auditoría
   y sugiere `/net-diagnostico`.
