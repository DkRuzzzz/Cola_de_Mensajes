## Módulo de Notificación al Cliente

Consume eventos relevantes del sistema y simula el envío de notificaciones al cliente sobre el estado de su pedido.

Rol Arquitectónico

- Tipo: Consumidor
- Consume: `confirmacion_pago`
- Consume: `alertas`
- No publica mensajes

Flujo de Operación

1. Si recibe un evento "PagoConfirmado", informa al cliente que su pago fue procesado exitosamente.
2. Si recibe un evento "AlertaInventario", notifica al cliente sobre la falta de disponibilidad del producto.

Consideraciones de Diseño

- Funciona como consumidor transversal.
- No afecta el flujo principal del sistema.
- Puede escalarse independientemente.
- Representa la capa de interacción con el usuario final.
