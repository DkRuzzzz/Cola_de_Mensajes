## 1. Introducción

Los sistemas modernos de comercio electrónico requieren arquitecturas distribuidas capaces de procesar grandes volúmenes de solicitudes de manera eficiente, escalable y tolerante a fallos. En entornos de alta concurrencia, los modelos de comunicación síncrona entre servicios pueden generar acoplamiento fuerte, bloqueos ante fallos parciales y limitaciones en la escalabilidad horizontal.

Con el objetivo de superar estas limitaciones, el presente trabajo propone el diseño de un sistema distribuido para el procesamiento de pedidos basado en una arquitectura orientada a eventos (Event-Driven Architecture), en la cual los distintos módulos del sistema se comunican de manera indirecta mediante colas de mensajes. Este enfoque permite el desacoplamiento temporal y estructural entre los servicios, favoreciendo la resiliencia del sistema ante fallos individuales.

La solución planteada utiliza Oracle Open Message Queue como broker de mensajería, implementando el estándar JMS (Java Message Service) para garantizar comunicación asíncrona, persistencia de mensajes y entrega confiable. El sistema está compuesto por múltiples servicios independientes encargados de la recepción de pedidos, procesamiento de pagos, gestión de inventario y notificación al cliente.

Las principales consideraciones de diseño incluyen:

- Comunicación asíncrona basada en colas.
- Escalabilidad horizontal de consumidores.
- Persistencia de mensajes para evitar pérdida de información.
- Garantía de procesamiento bajo el modelo at-least-once delivery.
- Implementación de mecanismos de idempotencia para prevenir efectos duplicados.

Este diseño busca asegurar continuidad operativa, confiabilidad en la entrega de mensajes y capacidad de adaptación ante incrementos de carga o fallos parciales en alguno de los módulos del sistema.

---

## 2. Arquitectura General del Sistema

El sistema propuesto sigue un modelo de arquitectura distribuida basada en eventos, donde los distintos servicios interactúan mediante un broker de mensajería en lugar de realizar llamadas directas entre sí. Este enfoque permite desacoplar los módulos, reducir dependencias y facilitar la escalabilidad independiente de cada componente.

La arquitectura está compuesta por los siguientes elementos principales:

- Cliente: Usuario final que realiza pedidos a través de la tienda en línea.
- Servicio de Recepción de Pedidos: Encargado de recibir las solicitudes de compra y publicarlas en la cola de mensajes correspondiente.
- Servicio de Procesamiento de Pagos: Consume los mensajes de la cola de pedidos, valida y procesa el pago, y en caso de éxito publica un nuevo evento de confirmación.
- Servicio de Gestión de Inventario: Consume los eventos de confirmación de pago y actualiza el stock disponible.
- Servicio de Notificación al Cliente: Escucha los eventos relevantes del sistema y envía notificaciones sobre el estado del pedido.
- Broker de Mensajes: Implementado mediante Oracle Open Message Queue, encargado de gestionar las colas, almacenar los mensajes y garantizar su entrega confiable.

El flujo general del sistema es el siguiente:

1. El cliente genera un pedido.
2. El Servicio de Recepción publica el pedido en la cola pedidos.
3. El Servicio de Procesamiento de Pagos consume el mensaje, procesa la transacción y publica un nuevo mensaje en la cola confirmacion_pago.
4. El Servicio de Inventario consume la confirmación y actualiza el stock.
5. En caso de inconsistencias o falta de stock, se publica un mensaje en la cola alertas.
6. El Servicio de Notificaciones consume los eventos de confirmación y alertas para informar al cliente.

Este modelo permite que cada servicio funcione de manera autónoma, pudiendo escalar horizontalmente sin afectar a los demás módulos. Asimismo, la arquitectura garantiza que los mensajes permanezcan en las colas hasta ser procesados exitosamente, evitando pérdidas de información ante fallos temporales.

### 2.1 Representación Arquitectónica

El diagrama arquitectónico sitúa al broker de mensajería en el núcleo del sistema, representando el punto central de comunicación entre los servicios. Las colas de mensajes (`pedidos`, `confirmacion_pago` y `alertas`) se encuentran definidas dentro del broker, enfatizando que el intercambio de información se realiza exclusivamente a través de este componente.

No existen comunicaciones directas entre los servicios, lo cual refuerza el desacoplamiento estructural del sistema. Cada módulo interactúa únicamente con las colas correspondientes, ya sea publicando o consumiendo mensajes, lo que permite escalabilidad independiente y tolerancia a fallos parciales.
