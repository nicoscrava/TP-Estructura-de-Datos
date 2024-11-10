INFORME


Este sistema simula las funcionalidades de dispositivos móviles, incluyendo la comunicación a través de SMS, llamada y correo electrónico, la gestión de aplicaciones y la configuración del dispositivo. El código está estructurado en varias clases, cada una responsable de diferentes aspectos de la simulación.


Estructuras de Datos Utilizadas:


Lista Enlazada
Clase: ListaEnlazada
- Operaciones:
  - agregarInicio(): Añade un nodo al inicio. 
  - agregarFinal(): Añade un nodo al final. 
  - pop(): Elimina el primer nodo.
  - eliminarPosicion(): Elimina un nodo en una posición específica. 
  - obtener_nodo(i): Devuelve el i-esimo nodo


Se elige una lista enlazada para la bandeja de SMS y Email para gestionar eficientemente datos dinámicos donde se esperan inserciones y eliminaciones frecuentes. Permite una fácil expansión y contracción de la lista sin necesidad de asignación de memoria contigua. Tambien utilizamos esta estructura para el almacenamiento de notas. 


Cola (Deque)
Librería: collections
Se utiliza para gestionar mensajes y correos electrónicos que están pendientes debido a la falta de conectividad. Un deque es ideal para manejar operaciones de primero en entrar, primero en salir (FIFO), lo cual es adecuado para gestionar mensajes pendientes que necesitan ser procesados en el orden en que fueron recibidos. Se utiliza para gestionar mensajes y correos electrónicos que están pendientes debido a la falta de conectividad.


Diccionario:
Los diccionarios nos permiten búsquedas, inserciones y eliminaciones, lo que los hace perfectos para un acceso rápido a dispositivos registrados en la Central, aplicaciones instaladas en cada celular instanciado, lista de contactos en cada celular instanciado, la lista de emails registrados en la central de Gmai y las notas de cada dispositivo.
En la clase Central () se utiliza el diccionario `self.dispositivos_registrados` que guarda en par key-value números de teléfono (key) e instancias de `Celular` (value).
En la clase Celular() se utiliza el diccionario `self.apps` que guarda en par key-value nombre de las aplicaciones en minúscula (key) e instancias de cada aplicación particular (value). Se eligió hacer un diccionario donde el key sea el nombre en minúscula de cada aplicación y el value asociado a esa key sea el una instancia de la app propia de ese celular para tener un fácil acceso desde los métodos que lo requieran. 
En la clase Contactos() se utiliza el diccionario `self.lista_de_contactos’ que guarda en par key-value nombre del contacto (key) y número telefónico del contacto que se agrega (value).
En la clase CentralGmail ()  se utiliza el diccionario ‘self.usuarios_registrados’ que guarda en par key-value direcciones de correo (key) y usuarios (value).
En la clase Notas () se utiliza el diccionario ‘???’ que guarda en par key-value “Titulo” (key) y el titulo escrito por el usuario (value) y por otro lado, “Cuerpo” (key) y el contenido escrito por el usuario (value). Pero esto se guarda en un nodo de una lista enlazada. 


Tupla: 
Las tuplas se utilizan en la clase `Email` para almacenar el asunto y el cuerpo del correo electrónico como un único elemento. Esto permite una gestión más sencilla y estructurada del contenido del email, asegurando que el asunto y el cuerpo estén siempre asociados.




Jerarquía de Clases y Funcionalidad
Clase Celular
La funcionalidad de la clase es gestionar el estado del dispositivo (encendido/apagado, bloqueado/desbloqueado), manejar la conectividad de red y el uso de datos. Además, proporciona un menú para la interacción del usuario con el dispositivo. El mismo celular realiza las validaciones de red móvil necesarias previas a comunicarse. En el caso de no tener red móvil, no podría existir la comunicación propia con la central de comunicaciones. 
Atributos por defecto: 
‘encendido’: Tipo Bool. Indica si el dispositivo está encendido. Se inicializa como False, lo que significa que el dispositivo está apagado. Se cambia a True cuando el dispositivo se enciende.
‘desbloqueado’: Tipo Bool. Indica si el dispositivo está desbloqueado. Inicialmente, el dispositivo está bloqueado (False). Se cambia a True cuando el usuario ingresa el código de desbloqueo correcto si lo fuera necesario.
‘codigo’: Tipo int o None. Representa el código de desbloqueo del dispositivo. Si es None, significa que no se ha establecido un código. Si se establece, debe ser un número entero.
‘red_movil’: Tipo Bool. Indica si la red móvil está activada. Inicialmente, está desactivada (False). Se activa (True) cuando el usuario activa la red móvil. Este atributo va a estar en True únicamente si está registrado en la central.
‘datos_moviles’: Tipo Bool. Indica si los datos móviles están activados. Inicialmente, están desactivados (False). Se activan (True) cuando el usuario habilita los datos móviles.
‘llamada_actual’: Tipo Llamada() o None. Este atributo indica si el celular esta en llamada, es decir que si es None por default cuando se instancia celular, significa que no está en llamada.
‘apps’: Un diccionario que contiene instancias de aplicaciones instaladas.






Clases de Aplicación


Las clases SMS, Email, Configuración, Teléfono, AppStore, Contactos y Notas heredan de la clase Aplicación. Cada clase hija representa una aplicación específica con sus propias funcionalidades y características (métodos y atributos).


Central de Comunicaciones


Clase Central:
Gestiona el registro de dispositivos y las comunicaciones entre ellos. Además proporciona un menú de administración para gestionar dispositivos y generar informes. Al ser una central independiente, se puede acceder a la central por fuera de los celulares debido a que se maneja de forma propia con sus propios métodos y no depende del celular. Al ser instanciada como atributo de clase en clase Celular, no requiere de que se instancien celulares. 


Funcionalidades Principales:
Sistema de Mensajería
Gestión de envío de SMS que valida el estado del emisor (si está registrado en la central) y receptor. También envía el mensaje si el receptor está disponible, o lo deja en espera (cola) si no lo está.


Sistema de Llamadas:
Gestión de Llamadas que valida dispositivos antes de establecer una llamada y registra llamadas aceptadas o pérdidas.


Central de Gmail
Clase: CentralGmail
La clase CentralGmail centraliza la gestión de correos electrónicos, asegurando que los correos se envíen y reciban de manera eficiente, y que se respeten las configuraciones de bloqueo de usuarios.
Atributos: 
usuarios_registrados: Diccionario que mapea direcciones de correo a usuarios.
registro_mails: Lista que almacena todos los correos enviados.

Funcionalidad:
Verifica si el receptor está registrado y si el emisor no está bloqueado. Gestiona el envío de correos electrónicos, almacenando los correos en la bandeja de enviados del emisor y en la bandeja de entrada del receptor si los datos móviles están activos. Si el receptor no tiene datos móviles activados, el correo se almacena en espera (cola). 
Clase Agregada: Notas

La clase Notas permite a los usuarios crear, editar, y gestionar notas en su dispositivo móvil. Esta aplicación es parte del conjunto de aplicaciones disponibles en cada instancia de Celular.

Estructura de Datos Utilizada:
- Lista Enlazada: Se utiliza para almacenar las notas, permitiendo una gestión eficiente de inserciones y eliminaciones. Cada nota se almacena como un nodo en la lista enlazada, donde el título y el contenido de la nota se guardan en un diccionario dentro del nodo.

Funcionalidades Principales:
- Agregar Nota: Permite al usuario crear una nueva nota, que se añade al inicio de la lista enlazada.
- Ver Notas: Muestra todas las notas almacenadas, listando el título y una vista previa del contenido.
- Editar Nota: Permite al usuario modificar una nota existente. El usuario puede elegir entre continuar escribiendo al final del contenido actual o sobrescribirlo completamente. La nota editada se mueve al inicio de la lista.
- Imprimir Nota: Exporta el contenido de una nota seleccionada a un archivo de texto.

La clase ‘Notas’ se integra en el sistema de aplicaciones del `Celular`, permitiendo a los usuarios gestionar sus notas de manera similar a otras aplicaciones como SMS y Email.
