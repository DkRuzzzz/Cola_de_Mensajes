import javax.jms.*;
import com.sun.messaging.ConnectionFactory;
import com.sun.messaging.ConnectionConfiguration;

public class NotificacionAlCliente {

    public static void main(String[] args) {

        Connection connection = null;

        try {

            System.out.println("Iniciando módulo Notificación al Cliente...");

            ConnectionFactory factory = new ConnectionFactory();
            factory.setProperty(ConnectionConfiguration.imqAddressList, "localhost:7676");

            connection = factory.createConnection();
            Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

            Queue confirmacionQueue = session.createQueue("confirmacion_pago");
            Queue alertasQueue = session.createQueue("alertas");

            MessageConsumer confirmacionConsumer = session.createConsumer(confirmacionQueue);
            MessageConsumer alertasConsumer = session.createConsumer(alertasQueue);

            connection.start();

            System.out.println("Esperando eventos para notificar...");

            // Listener para confirmaciones de pago
            confirmacionConsumer.setMessageListener(message -> {
                try {
                    if (message instanceof TextMessage) {
                        String contenido = ((TextMessage) message).getText();
                        System.out.println("Notificación enviada al cliente: Pago confirmado.");
                        System.out.println("Detalle: " + contenido);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });

            // Listener para alertas
            alertasConsumer.setMessageListener(message -> {
                try {
                    if (message instanceof TextMessage) {
                        String contenido = ((TextMessage) message).getText();
                        System.out.println("Notificación enviada al cliente: Problema con inventario.");
                        System.out.println("Detalle: " + contenido);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });

        } catch (Exception e) {
            System.err.println("Error inicializando Notificación al Cliente:");
            e.printStackTrace();
        }
    }
}