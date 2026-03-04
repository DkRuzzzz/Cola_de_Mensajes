## Módulo de Gestión de Inventario

Consume eventos de la cola confirmacion_pago y actualiza el stock de productos disponibles.

Rol Arquitectónico

- Tipo: Consumidor y Productor condicional
- Consume: `confirmacion_pago`
- Publica en: `alertas` (solo en caso de falta de stock)

Flujo de Operación

1. Recibe evento "PagoConfirmado".
2. Verifica disponibilidad de producto.
3. Si hay stock, lo descuenta.
4. Si no hay disponibilidad, publica un evento de tipo "AlertaInventario".

Consideraciones de Diseño

- Puede escalar horizontalmente.
- Opera bajo modelo at-least-once.
- Requiere idempotencia en entornos reales.
- Representa la validación física del pedido.
