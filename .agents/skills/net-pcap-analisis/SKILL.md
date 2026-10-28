---
name: "net-pcap-analisis"
description: "Analiza un archivo pcap/pcapng ya capturado con tshark y resume DNS, retransmisiones, resets, fallos de handshake TLS y QUIC sin respuesta. No captura tráfico."
argument-hint: "Ruta al archivo .pcap/.pcapng"
user-invocable: true
disable-model-invocation: false
---

## Entrada

```text
$ARGUMENTS
```

## Pasos

1. Confirma que el archivo existe y que `tshark` está instalado. Si no, indica
   `sudo apt install tshark` y espera.
2. Calcula el SHA-256 del archivo antes de leerlo y repórtalo.
3. Lee solo el archivo (`tshark -r`); no captures en vivo. Obtén:
   - resumen: `-q -z io,phs` y `-q -z conv,tcp`;
   - avisos del análisis experto: `-q -z expert`;
   - DNS: consultas, respuestas, NXDOMAIN, respuestas 0.0.0.0 y tiempos (`dns.time`);
   - TCP: `tcp.analysis.retransmission`, `tcp.flags.reset==1`, `tcp.analysis.zero_window`;
   - TLS: Client Hello sin Server Hello y alertas (`tls.alert_message`), con su SNI;
   - QUIC: `udp.port==443` con tráfico solo de salida;
   - ICMP: `icmp.type==3 && icmp.code==4` (fragmentación necesaria).
4. Agrupa por destino (SNI o nombre DNS), no por IP sola.
5. Reporta cada señal con su filtro, el número de paquetes y un número de frame de
   ejemplo. Separa hechos e hipótesis.
6. No copies cargas útiles ni datos personales en la salida. Si el pcap corresponde a
   un activo en alcance con la compuerta abierta, ofrece registrarlo con
   `custodio-evidencia`.
