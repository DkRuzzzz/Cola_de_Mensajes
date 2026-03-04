import javax.jms.*;
import com.sun.messaging.ConnectionFactory;
import com.sun.messaging.ConnectionConfiguration;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class GestionDeInventario {

    private static Map<String, Integer> inventario = new HashMap<>();

    public static void main(String[] args) {

        Connection connection = null;

        try {

            System.out.println("Iniciando módulo Gestión de Inventario...");

            // Stock inicial simulado
            inventario.put("Laptop", 2);

            ConnectionFactory factory = new ConnectionFactory();
            factory.setProperty(ConnectionConfiguration.imqAddressList, "localhost:7676");

            connection = factory.createConnection();
            Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

            Queue confirmacionQueue = session.createQueue("confirmacion_pago");
            Queue alertasQueue = session.createQueue("alertas");

            MessageConsumer consumer = session.createConsumer(confirmacionQueue);
            MessageProducer producer = session.createProducer(alertasQueue);

            connection.start();

            System.out.println("Esperando confirmaciones de pago...");

            consumer.setMessageListener(message -> {
                try {
                    if (message instanceof TextMessage) {

                        String contenido = ((TextMessage) message).getText();
                        System.out.println("Confirmación recibida: " + contenido);

                        String producto = "Laptop"; // simplificado para demo

                        if (inventario.get(producto) > 0) {
                            inventario.put(producto, inventario.get(producto) - 1);
                            System.out.println("Stock actualizado. Restantes: " + inventario.get(producto));
                        } else {

                            TextMessage alerta = session.createTextMessage(
                                    "{ \"tipo\":\"AlertaInventario\", \"detalle\":\"Producto sin stock\" }"
                            );

                            producer.send(alerta);

                            System.out.println("Sin stock. Alerta enviada.");
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Error en inventario:");
                    e.printStackTrace();
                }
            });

        } catch (Exception e) {
            System.err.println("Error inicializando Gestión de Inventario:");
            e.printStackTrace();
        }
    }
}