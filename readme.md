Explicaciones:
- Explicar por que se se eligio un diccionario para cada instancia de celular
para guardar las aplicaciones donde el key es el nombre de la app y el value es el objeto (aplicacion) especifico
a ese celular
- Lo mismo para los contactos dentro de la app Contactos donde el key es el nombre y el value es el objeto
- Explicar que agendar y actualizar un contacto usan el mismo metodo por como funcionan los diccionarios
- Explicar que la bandeja de entrada de sms es una pila
- La validacion del celular emisor se hace al intentar comunicar con la central desde el mismo celular.
- celular.red_movil indica si un celular tiene datos moviles, puede o no estar en la red. 
- celular (self) ya entra en la red una vez que tiene datos moviles pero la central puede dar de baja, asi como darlo de alta denuevo
- el celular.disponible indica si esta en llamada

A revisar:
- Revisar si el sistema de cambio de codigo funciona asi o si es con 'while' 
- Preguntar si la clase apps deberia tener atributos 
- Preguntar si esta bien que la app de config y store tengan acceso al objeto celular 
- Preguntar si esta bien usar dos listas separadas para los mails: leidos y no leidos 
- Hacer clase de central de mails
- Preguntar si esta mal el metodo validar_emisor que sea de la clase Aplicacion y que lo hereden todas como por ejemplo Contacto. 
- Preguntar si se puede estar en llamada y hacer otras cosas al mismo tiempo


Chiche para agregar: 
- Sistema de almacenamiento en base al tamanio de las apps 
- Sistema de requerimiento minimo de RAM para descargar ciertas aplicaciones

