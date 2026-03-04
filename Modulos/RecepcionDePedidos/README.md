## Módulo de Recepción de Pedidos

Actúa como punto de entrada del sistema. Su responsabilidad es recibir las órdenes generadas por los clientes y transformarlas en eventos publicados en la cola pedidos del broker.

Rol Arquitectónico

- Tipo: Productor
- Publica en: pedidos
- No consume mensajes
- No depende de otros servicios

Flujo de Operación

1. Se recibe un pedido (simulado en la demo).
2. Se genera un mensaje estructurado con ID único.
3. Se publica el evento en la cola pedidos.
4. El broker almacena el mensaje de manera persistente.

Consideraciones

- Los pedidos incluyen identificadores únicos para permitir trazabilidad.
- El módulo es completamente independiente del procesamiento posterior.
- Puede escalarse horizontalmente si la carga de pedidos aumenta.
