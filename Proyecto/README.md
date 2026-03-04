## Messages Queue

### Diseño de Aplicación con Cola de Mensajes

Oracle Open MQ no ha sido actualizado desde 2017 por lo que fue necesario compilar el proyecto con un JDK compatible, en este caso fue con JDK 8

Descargamos Oracle Open MQ y agregamos las siguientes librerías al proyecto:
- imq.jar
- imqbroker.jar
- jms.jar

Posteriormente construimos el proyecto para asegurarnos de no tener ningún error

Una vez todo preparado seguimos los siguiente pasos para comprobar el funcionamiento:

1. Abrimos el cmd y nos dirigimos nos dirigimos a la carpeta bin que descargamos de Oracle Open MQ

```
cd Downloads/mq/bin
```

2. Dentro de la carpeta ejecutamos el archivo imqbrokerd con la versión de Java correspondiente

```
imqbrokerd -javahome "C:\Program Files\Eclipse Adoptium\jdk-8.0.482.8-hotspot"
```

3. Ahora nos dirigimos al IDE en el que estamos trabajando y ejecutamos las clases:

- ProcesamientoDePagos
- GestionDeInventario
- NotificacionAlCliente

4. Por último ejecutamos la clase `RecepcionDePedidos` para comprobar el total funcionamiento de la aplicación


