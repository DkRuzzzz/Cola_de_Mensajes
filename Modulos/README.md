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

---

## 3. Diseño de Colas y Flujo de Mensajes

El sistema utiliza un modelo de comunicación basado en eventos, donde cada acción relevante genera un mensaje que es publicado en una cola específica dentro del broker. Las colas actúan como mecanismos de desacoplamiento entre productores y consumidores, permitiendo que los servicios operen de manera independiente.

### 3.1 Cola `pedidos`

Esta cola almacena los eventos generados cuando un cliente realiza una compra.
El Servicio de Recepción de Pedidos actúa como productor, mientras que el Servicio de Procesamiento de Pagos actúa como consumidor.

Cada mensaje contiene información estructurada del pedido, incluyendo:

- Identificador único del pedido
- Identificador del cliente
- Lista de productos
- Cantidades solicitadas
- Fecha y hora de creación

Este evento representa la intención inicial de compra y marca el inicio del flujo de procesamiento.

### 3.2 Cola `confirmacion_pago`

Esta cola almacena los eventos generados tras el procesamiento exitoso de un pago.

El Servicio de Procesamiento de Pagos publica el mensaje, y el Servicio de Gestión de Inventario lo consume.

El mensaje incluye:

- Identificador del pedido
- Estado del pago (aprobado)
- Referencia de transacción
- Marca de tiempo de confirmación

Este evento indica que el pedido ha superado la validación financiera y puede continuar su flujo dentro del sistema.

### 3.3 Cola `alertas`

Esta cola contiene eventos relacionados con incidencias, como falta de stock o inconsistencias detectadas durante el procesamiento.

El Servicio de Gestión de Inventario publica mensajes en esta cola cuando detecta que un producto no está disponible en la cantidad solicitada.

El Servicio de Notificaciones consume estos eventos para informar al cliente sobre la situación del pedido.

### 3.4 Flujo General de Eventos

El flujo del sistema sigue la siguiente secuencia:

1. Se genera un evento de tipo "PedidoCreado".
2. Tras su procesamiento, se genera un evento "PagoConfirmado".
3. En caso de inconsistencias, se genera un evento "AlertaInventario".
4. El Servicio de Notificaciones actúa como consumidor transversal de eventos relevantes.

Este modelo permite que cada transición de estado del pedido esté representada como un evento independiente, facilitando trazabilidad, auditoría y extensibilidad futura del sistema.

---

## 4. Escalabilidad y Tolerancia a Fallos

Uno de los principales objetivos del diseño es garantizar que el sistema pueda adaptarse a incrementos en la carga de trabajo y mantener su operación ante fallos parciales. Para ello, la arquitectura basada en colas de mensajes ofrece mecanismos naturales de escalabilidad horizontal y resiliencia.

### 4.1 Escalabilidad Horizontal

Cada servicio consumidor puede escalarse de manera independiente mediante la ejecución de múltiples instancias que escuchen la misma cola.

Por ejemplo:

- Varias instancias del Servicio de Procesamiento de Pagos pueden consumir simultáneamente mensajes de la cola `pedidos`.
- Múltiples instancias del Servicio de Inventario pueden procesar eventos de `confirmacion_pago`.

El broker, implementado con Oracle Open Message Queue, distribuye los mensajes entre los consumidores disponibles, equilibrando la carga de manera automática.

Este modelo permite aumentar la capacidad del sistema sin modificar su arquitectura interna, simplemente desplegando más instancias de los servicios.

### 4.2 Desacoplamiento y Tolerancia a Fallos

La comunicación asíncrona garantiza desacoplamiento temporal entre los servicios. Esto implica que los productores y consumidores no necesitan estar activos simultáneamente.

Si un servicio consumidor se encuentra temporalmente fuera de operación:

- Los mensajes permanecen almacenados en la cola correspondiente.
- El sistema continúa aceptando y publicando nuevos eventos.
- Una vez restablecido el servicio, este puede procesar los mensajes acumulados.

Este comportamiento evita la propagación de fallos y permite que el sistema mantenga continuidad operativa ante caídas parciales.

### 4.3 Persistencia y Entrega Confiable

El sistema opera bajo el modelo de entrega at-least-once, donde los mensajes permanecen en la cola hasta que el consumidor confirma explícitamente su procesamiento.

En caso de que un servicio falle antes de completar la operación, el mensaje no confirmado podrá ser reprocesado, evitando la pérdida de información.

### 4.4 Idempotencia y Consistencia

Dado que el modelo at-least-once puede implicar la reprocesamiento de mensajes, el diseño contempla mecanismos de idempotencia basados en identificadores únicos de pedido.

Cada servicio verifica si un evento ya fue procesado previamente antes de aplicar cambios persistentes (por ejemplo, descuento de inventario o actualización de estado). Esto previene efectos secundarios duplicados y mantiene la consistencia del sistema.

---

## 5. Alta Disponibilidad y Monitoreo

Además de la escalabilidad horizontal y la tolerancia a fallos a nivel de servicios, el diseño contempla consideraciones adicionales orientadas a mantener la disponibilidad del sistema y facilitar su supervisión en entornos productivos.

### 5.1 Alta Disponibilidad del Broker

Dado que el broker de mensajería constituye el núcleo de comunicación del sistema, su disponibilidad es crítica para la operación general.

El sistema puede fortalecerse mediante:

- Configuración del broker con almacenamiento persistente en disco.
- Replicación o configuración en clúster del broker.
- Implementación de mecanismos de respaldo y recuperación ante fallos.

El uso de Oracle Open Message Queue permite habilitar almacenamiento persistente de mensajes, asegurando que los eventos no se pierdan ante reinicios o fallos temporales del servidor.

En un entorno productivo, podría implementarse una arquitectura con nodos redundantes del broker para evitar un único punto de fallo.

### 5.2 Monitoreo y Registro de Eventos

La observabilidad del sistema es esencial para detectar anomalías, medir desempeño y garantizar trazabilidad de los pedidos.

Se recomienda la implementación de:

- Registro de logs estructurados en cada servicio.
- Identificadores únicos de correlación por pedido.
- Métricas como:
  - Tiempo promedio de procesamiento.
  - Número de mensajes pendientes por cola.
  - Tasa de fallos en pagos.
  - Retrasos en actualización de inventario.

El monitoreo de la longitud de las colas permite identificar cuellos de botella y escalar servicios de manera preventiva.

### 5.3 Gestión de Errores y Reintentos

El Servicio de Procesamiento de Pagos puede implementar políticas de reintento controlado en caso de fallos temporales de transacción.

Asimismo, el sistema puede incorporar una cola adicional de tipo Dead Letter Queue para almacenar mensajes que no puedan procesarse tras múltiples intentos, permitiendo su análisis posterior sin bloquear el flujo general del sistema.

