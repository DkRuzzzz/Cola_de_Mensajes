## 1. Introducción

El presente repositorio describe el diseño de un sistema distribuido para el procesamiento de pedidos de una tienda en línea, basado en comunicación indirecta mediante colas de mensajes. Este enfoque permite que los distintos módulos del sistema operen de manera independiente, intercambiando información de forma asíncrona a través de un broker de mensajería.

El objetivo principal del diseño es garantizar confiabilidad en la entrega de mensajes, escalabilidad horizontal de los servicios y tolerancia ante fallos parciales del sistema, evitando la pérdida de información y manteniendo la continuidad operativa.
