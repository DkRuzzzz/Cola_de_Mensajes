## Módulo de Procesamiento de Pagos

Consume eventos de la cola pedidos y simula el procesamiento de pagos asociados a cada orden.

Rol Arquitectónico

- Tipo: Consumidor y Productor
- Consume: `pedidos`
- Publica en: `confirmacion_pago`

Flujo de Operación

1. Recibe un evento de tipo "PedidoCreado".
2. Simula validación de pago.
3. Si el pago es exitoso, publica un evento "PagoConfirmado".
4. En caso de fallo, registra el evento y podría aplicar política de reintento.

Consideraciones de Diseño

- Opera bajo modelo at-least-once.
- Puede escalar horizontalmente.
- No tiene dependencia directa con Inventario.
- Representa la transición de estado financiero del pedido.
