import javax.jms.*;
import com.sun.messaging.ConnectionFactory;
import com.sun.messaging.ConnectionConfiguration;

import java.util.Random;

public class ProcesamientoDePagos {

    public static void main(String[] args) {

        Connection connection = null;

        try {

            System.out.println("Iniciando módulo Procesamiento de Pagos...");

            ConnectionFactory factory = new ConnectionFactory();
            factory.setProperty(ConnectionConfiguration.imqAddressList, "localhost:7676");

            connection = factory.createConnection();

            // AUTO_ACKNOWLEDGE para mantenerlo simple en la demo
            Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

            Queue pedidosQueue = session.createQueue("pedidos");
            Queue confirmacionQueue = session.createQueue("confirmacion_pago");

            MessageConsumer consumer = session.createConsumer(pedidosQueue);
            MessageProducer producer = session.createProducer(confirmacionQueue);

            connection.start();

            System.out.println("Esperando pedidos para procesar pagos...");

            consumer.setMessageListener(message -> {
                try {
                    if (message instanceof TextMessage) {

                        String pedidoJson = ((TextMessage) message).getText();
                        System.out.println("Pedido recibido: " + pedidoJson);

                        boolean pagoExitoso = simularPago();

                        if (pagoExitoso) {

                            TextMessage confirmacion = session.createTextMessage(
                                    "{ \"estado\":\"PagoConfirmado\", \"detalle\":" + pedidoJson + " }"
                            );

                            producer.send(confirmacion);

                            System.out.println("Pago procesado correctamente. Confirmación enviada.");

                        } else {
                            System.out.println("Pago fallido. Se podría implementar reintento.");
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Error procesando pago:");
                    e.printStackTrace();
                }
            });

        } catch (Exception e) {
            System.err.println("Error inicializando Procesamiento de Pagos:");
            e.printStackTrace();
        }
    }

    private static boolean simularPago() {
        Random random = new Random();
        return random.nextBoolean(); // 50% éxito / 50% fallo
    }
}