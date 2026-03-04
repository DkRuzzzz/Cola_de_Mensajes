import javax.jms.*;
import com.sun.messaging.ConnectionFactory;
import com.sun.messaging.ConnectionConfiguration;

import java.util.UUID;
import java.time.LocalDateTime;

public class RecepcionDePedidos {

    public static void main(String[] args) {

        Connection connection = null;

        try {

            System.out.println("Iniciando módulo Recepción de Pedidos...");

            ConnectionFactory factory = new ConnectionFactory();
            factory.setProperty(ConnectionConfiguration.imqAddressList, "localhost:7676");

            connection = factory.createConnection();
            Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

            Queue queue = session.createQueue("pedidos");
            MessageProducer producer = session.createProducer(queue);

            // Simulación de múltiples pedidos
            for (int i = 0; i < 3; i++) {

                String pedidoId = UUID.randomUUID().toString();
                String timestamp = LocalDateTime.now().toString();

                String jsonPedido = String.format(
                        "{ \"pedidoId\":\"%s\", \"producto\":\"Laptop\", \"cliente\":\"Jesus\", \"fecha\":\"%s\" }",
                        pedidoId, timestamp
                );

                TextMessage message = session.createTextMessage(jsonPedido);

                producer.send(message);

                System.out.println("Pedido enviado: " + pedidoId);
                Thread.sleep(1000); // Simula llegada gradual de pedidos
            }

            System.out.println("Todos los pedidos fueron enviados correctamente.");

        } catch (Exception e) {
            System.err.println("Error en Recepción de Pedidos:");
            e.printStackTrace();
        } finally {
            try {
                if (connection != null) {
                    connection.close();
                }
            } catch (JMSException e) {
                e.printStackTrace();
            }
        }
    }
}