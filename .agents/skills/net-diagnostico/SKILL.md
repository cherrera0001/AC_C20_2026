---
name: "net-diagnostico"
description: "Diagnostica fallos de conectividad de la estación del auditor (p. ej. un servicio como Instagram que no carga): DNS, latencia, MTU, IPv4/IPv6, rutas y Tailscale. Solo lectura y medición."
argument-hint: "Síntoma y servicio afectado"
user-invocable: true
disable-model-invocation: false
---

## Entrada

```text
$ARGUMENTS
```

## Pasos

1. Ejecuta `/net-compuerta` con la actividad «diagnóstico de conectividad» y el
   activo afectado. Si la respuesta es CERRADA, detente.
2. Pregunta lo que falte y cambie el diagnóstico: dispositivo afectado (PC, teléfono),
   tipo de conexión (WiFi, cable), desde cuándo y si falla todo el servicio o solo
   parte (imágenes, video, mensajes).
3. Delega en el agente `diagnostico-red` con el síntoma y esas respuestas.
4. Para un servicio de Meta (Instagram), pídele revisar al menos:
   - resolución de los dominios del servicio y de su CDN con el resolvedor local
     frente a uno público;
   - IPv6 frente a IPv4 (tiempos de `curl -4` y `curl -6`);
   - PMTU, sobre todo si Tailscale está activo;
   - si UDP 443 (QUIC) obtiene respuesta o solo funciona TCP 443.
5. Si el usuario puede reproducir el fallo, indícale cómo capturar en el dispositivo
   afectado (Wireshark/`pktmon` en Windows; app de captura local en el teléfono) y
   entregar el archivo; luego usa `/net-pcap-analisis`.
6. Entrega el informe de `diagnostico-red` sin agregar conclusiones no medidas.
