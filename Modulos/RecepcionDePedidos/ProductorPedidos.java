import javax.jms.*;
import com.sun.messaging.ConnectionFactory;
import com.sun.messaging.ConnectionConfiguration;

public class RecepcionDePedidos {

    public static void main(String[] args) {
        try {

            ConnectionFactory factory = new ConnectionFactory();
            factory.setProperty(ConnectionConfiguration.imqAddressList, "localhost:7676");

            Connection connection = factory.createConnection();
            Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

            Queue queue = session.createQueue("pedidos");
            MessageProducer producer = session.createProducer(queue);

            TextMessage message = session.createTextMessage(
                    "{\"pedidoId\":1,\"producto\":\"Laptop\",\"cliente\":\"Jesus\"}"
            );

            producer.send(message);

            System.out.println("Mensaje enviado correctamente.");

            connection.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
