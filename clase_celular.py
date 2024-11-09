from clase_central import Central, Comunicacion
from collections import deque
from clase_listaenlazada import ListaEnlazada, Nodo
from clase_email import Email, CentralGmail
import random
from abc import ABC, abstractmethod


class Celular:
    """
    Representa un dispositivo celular con sus aplicaciones y funcionalidades.
    
    Attributes:

        VALID_RAM_VALUES (list): Lista de valores válidos para la RAM
        VALID_OS_VALUES (list): Lista de valores válidos para el sistema operativo
        VALID_STORAGE_VALUES (list): Lista de valores válidos para el almacenamiento
        central (Central): Central de comunicaciones compartida
        central_gmail (CentralGmail): Central de emails compartida
        celulares_registrados (list): Lista de celulares registrados
    """
    VALID_RAM_VALUES = [2, 4, 8, 16, 32]
    VALID_OS_VALUES = ['android', 'ios']
    VALID_STORAGE_VALUES = [32, 64, 128, 256, 512]
    central = Central()
    central_gmail = CentralGmail()
    celulares_registrados = []

    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico):
        """
        Inicializa un nuevo dispositivo celular.
        
        Args:
            identificacion: Identificador único de 8 caracteres sin espacios
            nombre: Nombre del dispositivo (no vacío)
            modelo: Modelo del dispositivo
            sistema_operativo: Sistema operativo ('Android' o 'iOS')
            version: Versión del sistema operativo (formato: X.Y.Z)
            RAM: Memoria RAM en GB (valores válidos: 2, 4, 8, 16, 32)
            almacenamiento: Almacenamiento en GB (valores válidos: 32, 64, 128, 256, 512)
            num_telefonico: Número telefónico de 8 dígitos
            
        Raises:
            ValueError: Si algún parámetro no cumple con los requisitos de formato o valor
        """
        # Validación de identificación
        if len(identificacion) != 8:
            raise ValueError("La identificación debe tener exactamente 8 caracteres.")
        if " " in identificacion:
            raise ValueError("La identificación no puede contener espacios.")
        if identificacion in [celular.identificacion for celular in Celular.celulares_registrados]:
            raise ValueError("Esta identificación ya está registrada en otro celular.")
        self.identificacion = identificacion

        # Validación de nombre
        nombre = nombre.strip()
        if len(nombre) == 0:
            raise ValueError("El nombre no puede estar vacío.")
        self.nombre = nombre
        
        # El modelo puede ser cualquier string no vacío
        modelo = modelo.strip()
        if len(modelo) == 0:
            raise ValueError("El modelo no puede estar vacío.")
        self.modelo = modelo

        # Validación de sistema operativo
        sistema_operativo = sistema_operativo.strip().lower()
        if sistema_operativo not in self.VALID_OS_VALUES:
            raise ValueError(f"Sistema operativo debe ser uno de: {', '.join(self.VALID_OS_VALUES)}")
        self.sistema_operativo = sistema_operativo

        # Validación de número telefónico
        num_telefonico = num_telefonico.strip()
        if not num_telefonico.isdigit() or len(num_telefonico) != 8:
            raise ValueError("El número telefónico debe ser una cadena con 8 dígitos")
        if num_telefonico in [celular.num_telefonico for celular in Celular.celulares_registrados]:
            raise ValueError("Este número telefónico ya está registrado")
        self.num_telefonico = num_telefonico
        
        # Validación de versión
        try:
            # Validamos que sea un formato de versión válido (ej: "1", "1.0", "1.1.2")
            partes = str(version).split('.')
            for parte in partes:
                if not parte.isdigit() or int(parte) < 0:
                    raise ValueError
            self.version = version
        except ValueError:
            raise ValueError("La versión debe tener un formato válido (ej: 1, 1.0, 1.1.2)")

        # Validación de RAM
        try:
            ram_int = int(RAM)
            if ram_int not in self.VALID_RAM_VALUES:
                raise ValueError
            self.RAM = ram_int
        except ValueError:
            raise ValueError(f"La RAM debe ser uno de estos valores: {', '.join(str(x) for x in self.VALID_RAM_VALUES)} GB")

        # Validación de almacenamiento
        try:
            almacenamiento_int = int(almacenamiento)
            if almacenamiento_int not in self.VALID_STORAGE_VALUES:
                raise ValueError
            self.almacenamiento = float(almacenamiento_int) #se convierte a float para trabajar mejor 
        except ValueError:
            raise ValueError(f"El almacenamiento debe ser uno de estos valores: {', '.join(str(x) for x in self.VALID_STORAGE_VALUES)} GB")


        #para poder usar EMAIl
        self.datos_moviles=False

        #atributos adicionales
        self.encendido = False #indica si esta encendido o apagado
        self.desbloqueado=False #indica si esta desbloqueado el celular
        self.codigo=None
        self.red_movil=False


        # se da de alta automaticamente al crear el celular
        self.central.alta_dispositivo(self)

        # Se encuentra disponible para la llamada
        self.disponible = True

        # Contiene el numero con el cual se esta en llamada
        self.llamada_actual = None
        
        #aca se crea esta instancia para trabajar con las apps y su almacenamiento
        self.almacenamiento_ocupado=0

        #primero se inicializa la app de contactos
        contactos = Contactos(self)
        
        
        #creamos un diccionario para reflejar cada aplicacion y poder identificarla por su nombre
        #la app contactos ya fue creada para poder ser pasada como argumento
        self.apps={"contactos": contactos,
                   "sms": SMS(self, contactos), 
                   "email": AppEmail(self),
                   "telefono": Telefono(self, contactos),
                   'app store': App_Store(self), #accede al celular para modificar las apps dentro
                    'configuracion': Configuracion(self) #accede a toda la configuracion del celular
                   }
        
        # se agrega a la lista de celulares registrados para poder acceder a ellos desde el menu principal
        Celular.celulares_registrados.append(self)
    
    def encender_apagar(self):
        """
        Alterna el estado de encendido/apagado del celular.
        Cuando se enciende, activa la red móvil.
        Cuando se apaga, desconecta de la central y termina llamadas activas.
        """
        self.encendido = not self.encendido
        if self.encendido:
            self.apps['configuracion'].activar_red_movil()
            print("\nEl celular se ha prendido")

        else:
            self.red_movil = False
            self.desbloqueado = False
            if self.llamada_actual is not None:
                self.apps['telefono'].terminar_llamada() # Se termina la llamada en curso en el caso de existir
            print("\nHas apagado el celular")

    def menu_celular(self):
        """
        Muestra el menú principal del celular y maneja la navegación entre opciones.
        Permite encender/apagar el dispositivo, bloquear/desbloquear y acceder a aplicaciones.
        """
        while True:
            if not self.encendido:
                opcion = input("""
CELULAR APAGADO
1. Encender celular
2. Volver al menú principal

Ingrese una opci��n: """)
                
                if opcion == "1":
                    self.encender_apagar()
                elif opcion == "2":
                    break
                else:
                    print("Opción inválida")
                
            elif not self.desbloqueado:
                opcion = input("""
CELULAR BLOQUEADO
1. Desbloquear celular
2. Apagar celular
3. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    self.bloq_desbloq()
                elif opcion == "2":
                    self.encender_apagar()
                elif opcion == "3":
                    break
                else:
                    print("Opción inválida")
                        
            else:
                opcion = input("""
MENU CELULAR
1. Abrir aplicación
2. Bloquear celular
3. Apagar celular
4. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    try:
                        self.abrir_app()
                    except Exception as e:
                        print(f"Error al abrir la aplicación: {str(e)}")
                elif opcion == "2":
                    self.bloq_desbloq()
                elif opcion == "3":
                    self.encender_apagar()
                elif opcion == "4":
                    break
                else:
                    print("Opción inválida")

    def abrir_app(self):
        """
        Permite al usuario abrir una aplicación instalada en el celular.
        Muestra la lista de aplicaciones disponibles y permite seleccionar una.
        
        Raises:
            Exception: Si hay un error al abrir la aplicación
        """
        print(f"\nAplicaciones disponibles: {', '.join(list(self.apps.keys()))}")
        
        app_nombre = input("\nIngrese el nombre de la aplicación: ").lower()
        if app_nombre in self.apps:
            self.apps[app_nombre].menu()
        else:
            print("\nAplicación no encontrada")


    #agregar contrasenia    
    def bloq_desbloq(self):
        """
        Maneja el bloqueo y desbloqueo del celular.
        Si tiene código configurado, solicita la verificación.
        Permite hasta 3 intentos de desbloqueo.
        """
        if self.desbloqueado:
            self.desbloqueado = False
            print("\nHas bloqueado el celular")
            return
        
        if self.codigo is None:
            self.desbloqueado = True
            print("\nEl celular se ha desbloqueado")
            return
        
        # Si tiene código, pedimos que lo ingrese
        intentos = 3
        while intentos > 0:
            try:
                codigo_ingresado = int(input('\nIngrese el código de desbloqueo: '))
                if codigo_ingresado == self.codigo:
                    self.desbloqueado = True
                    print("\nEl celular se ha desbloqueado")
                    return
                else:
                    intentos -= 1
                    if intentos > 0:
                        print(f"\nCódigo incorrecto. Te quedan {intentos} intentos")
                    else:
                        print("\nDemasiados intentos fallidos. Vuelva a intentarlo.")
            except ValueError:
                print("\nEl código debe ser un número")
                intentos -= 1

    def validar_estado_emisor(self) -> bool:
        """
        Valida si el celular puede enviar mensajes o realizar llamadas.
        
        Returns:
            bool: True si el celular está habilitado para comunicarse, False en caso contrario
        """
        if not self.red_movil:
            print('Tu celular no puede enviar mensajes. Activa la red móvil.')
            return False
        
        if self.num_telefonico not in self.central.dispositivos_registrados:
            print('Tu celular no se encuentra en la red.')
            return False
        
        return True

    def __str__(self):
        estado_red = "Activada" if self.red_movil else "Desactivada"
        estado_datos = "Activados" if self.datos_moviles else "Desactivados"
        
        return f"""
        Celular {self.nombre}
        ID: {self.identificacion}
        Modelo: {self.modelo}
        SO: {self.sistema_operativo} v{self.version}
        RAM: {self.RAM}GB
        Almacenamiento: {self.almacenamiento}GB
        Número: {self.num_telefonico}
        Red móvil: {estado_red}
        Datos móviles: {estado_datos}
        """
    @classmethod
    def generar_informe_csv(cls):
        """Genera un archivo CSV con información básica de todos los celulares registrados"""
        try:
            with open('informe_celulares.csv', 'w') as archivo:
                # Escribir encabezados
                archivo.write("Nombre,Numero,Red Movil\n")
                
                # Escribir datos de cada celular
                for celular in cls.celulares_registrados:
                    estado_red = "Activada" if celular.red_movil else "Desactivada"
                    
                    linea = f"{celular.nombre},{celular.num_telefonico},{estado_red}\n"
                    archivo.write(linea)
                    
            print("Informe generado exitosamente en 'informe_celulares.csv'")
            
        except Exception as e:
            print(f"Error al generar el informe: {str(e)}")
    
        


class Aplicacion:
    """
    Clase base para todas las aplicaciones del celular.
    
    Attributes:
        celular (Celular): Referencia al celular que contiene la aplicación
        almacenamiento (float): Espacio que ocupa la aplicación en GB
        necesaria (bool): Indica si la aplicación es del sistema y no puede eliminarse
    """
    def __init__(self, celular: 'Celular'):
        """
        Inicializa una nueva aplicación.
        
        Args:
            celular: Referencia al celular que contendrá la aplicación
        """
        self.celular = celular
        self.almacenamiento= None
        self.necesaria = False

    def menu(self):
        """
        Muestra el menú principal de la aplicación.
        Cada aplicación debe sobrescribir este método con su propia implementación.
        """
        print("Esta aplicación no tiene menú implementado")

    def obtener_nombre_contacto(self, numero):
        """
        Busca el nombre del contacto por su número.
        
        Args:
            numero: Número telefónico a buscar
                
        Returns:
            str: Nombre del contacto si existe, número en caso contrario
        """
        for nombre, num in self.celular.apps['contactos'].lista_de_contactos.items():
            if num == numero:
                return nombre
        return numero

class Contactos(Aplicacion):
    """
    Aplicación para gestionar contactos del celular.
    
    Attributes:
        lista_de_contactos (dict): Diccionario que almacena nombre y número de contactos
    """
    
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.lista_de_contactos={}
        self.almacenamiento=1 #ocupa 1 gb
        celular.almacenamiento_ocupado +=self.almacenamiento
        self.necesaria = True
    
    def ver_contactos(self):
        if not self.lista_de_contactos:
            print("No hay contactos guardados")
        else:
            print("\nLista de contactos:")
            for nombre, numero in self.lista_de_contactos.items():
                print(f"{nombre}: {numero}")

    def agregar_contacto(self):
        while True:
            numero = input("Ingrese número: ")
            if not numero.isdigit():
                print("El número debe contener solo dígitos")
            elif len(numero) != 8:
                print("El n��mero debe tener 8 dígitos")
            elif numero in self.lista_de_contactos.values():
                print("Este número ya existe en contactos")
            else:
                break
        
        while True:
            nombre_base = input("Ingrese nombre: ")
            nombre = nombre_base
            contador = 1
            
            # Si el nombre ya existe, agregar (1), (2), etc.
            while nombre in self.lista_de_contactos:
                nombre = f"{nombre_base}({contador})"
                contador += 1
            
            # Preguntar si está de acuerdo con el nombre
            if nombre != nombre_base:
                opcion = input(f"El nombre '{nombre_base}' ya existe. ¿Desea guardarlo como '{nombre}'? (si/no): ").lower()
                if opcion == 'no':
                    continue
            
            self.lista_de_contactos[nombre] = numero
            print(f"Contacto agregado: {nombre} - {numero}")
            break

    def modificar_contacto(self):
        """
        Permite modificar el nombre o número de un contacto existente.
        Valida que los nuevos datos no estén duplicados.
        """
        if not self.lista_de_contactos:
            print("No hay contactos guardados para modificar")
            return
            
        self.ver_contactos()
        nombre = input("\nIngrese el nombre del contacto a modificar: ")
        
        if nombre not in self.lista_de_contactos:
            print("El contacto no existe")
            return
            
        print(f"\nModificando contacto: {nombre} - {self.lista_de_contactos[nombre]}")
        self._mostrar_menu_modificacion(nombre)

    def _mostrar_menu_modificacion(self, nombre: str):
        """
        Método privado que maneja el menú de modificación de contactos.
        
        Args:
            nombre: Nombre del contacto a modificar
        """
        opcion = input("¿Qué desea modificar?\n1. Nombre\n2. Número\nIngrese opción: ")
        
        if opcion == "1":
            self._modificar_nombre_contacto(nombre)
        elif opcion == "2":
            self._modificar_numero_contacto(nombre)
        else:
            print("Opción inválida")

    def _modificar_nombre_contacto(self, nombre: str):
        """
        Método privado que maneja la lógica de modificación del nombre de un contacto.
        
        Args:
            nombre: Nombre del contacto a modificar
        """
        while True:
            nuevo_nombre = input("Ingrese el nuevo nombre: ")
            if nuevo_nombre in self.lista_de_contactos:
                print("Ya existe un contacto con ese nombre")
                if input("¿Desea intentar con otro nombre? (si/no): ").lower() != 'si':
                    return
            else:
                numero = self.lista_de_contactos[nombre]
                del self.lista_de_contactos[nombre]
                self.lista_de_contactos[nuevo_nombre] = numero
                print(f"Nombre modificado: {nuevo_nombre} - {numero}")
                break

    def _modificar_numero_contacto(self, nombre: str):
        """
        Método privado que maneja la lógica de modificación del número de un contacto.
        
        Args:
            nombre: Nombre del contacto a modificar
        """
        while True:
            nuevo_numero = input("Ingrese el nuevo número: ")
            if not nuevo_numero.isdigit():
                print("El número debe contener solo dígitos")
            elif len(nuevo_numero) != 8:
                print("El número debe tener 8 dígitos")
            elif nuevo_numero in self.lista_de_contactos.values():
                print("Este número ya existe en contactos")
            else:
                self.lista_de_contactos[nombre] = nuevo_numero
                print(f"Número modificado: {nombre} - {nuevo_numero}")
                break

    def menu(self):
        while True:
            opcion = input("""
CONTACTOS
1. Ver contactos
2. Agregar contacto
3. Modificar contacto
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.ver_contactos()
            elif opcion == "2":
                self.agregar_contacto()
            elif opcion == "3":
                self.modificar_contacto()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")


class SMS(Aplicacion):
    """
    Aplicación para enviar y recibir mensajes SMS.
    
    Attributes:
        bandeja (ListaEnlazada): Lista de mensajes recibidos
        contactos (Contactos): Referencia a la app de contactos
        en_espera (deque): Cola de mensajes recibidos cuando la red está inactiva
    """
    def __init__(self, celular: Celular, contactos: Contactos):
        super().__init__(celular)
        self.almacenamiento=1 #ocupa 1 gb
        celular.almacenamiento_ocupado+=self.almacenamiento
        self.bandeja= ListaEnlazada() #lista enlazada 
        self.contactos=contactos
        self.en_espera = deque() # COLA Mensajes que te llegaron cuando no tenias la red movil activa
        self.necesaria = True

    def enviar_mensaje(self):
        """
        Permite enviar un mensaje SMS a otro dispositivo.
        
        Raises:
            ValueError: Si el receptor no es válido
        """
        try:
            self.contactos.ver_contactos()
            receptor = input("\nIngrese un numero o un nombre de contacto: ")
            
            if receptor in self.contactos.lista_de_contactos:
                receptor = self.contactos.lista_de_contactos[receptor]
            elif not receptor.isdigit() or len(receptor) != 8:
                raise ValueError("Número inválido. Debe contener 8 dígitos.")
                
            mensaje = input("\nEscriba su mensaje: ")
            if not mensaje.strip():
                raise ValueError("El mensaje no puede estar vacío")
                
            self.celular.central.comunicacion_sms(self.celular, receptor, mensaje)
            
        except ValueError as e:
            print(f"\nError al enviar mensaje: {str(e)}")

    def recibir_mensaje(self, mensaje):
        self.bandeja.agregarInicio(Nodo(mensaje))
   
    def ver_bandeja(self):
        if self.bandeja.esVacia():
            print("No hay mensajes en la bandeja")
            return False
            
        print("\nBandeja de mensajes:")
        actual = self.bandeja.inicio
        contador = 1
        
        while actual:
            vista_emisor = actual.dato.emisor == self.celular
            print(f"{contador}. {actual.dato.__str__(vista_emisor)}")
            actual = actual.siguiente
            contador += 1
        return True
       
    def actualizar_bandeja(self):
        cantidad_mensajes = len(self.en_espera) 
        if cantidad_mensajes > 0:
            print(f'\nTenes {cantidad_mensajes} mensaje/s nuevos. Revisa tu bandeja. ')
            while self.en_espera:
                mensaje = self.en_espera.popleft()
                self.bandeja.agregarInicio(Nodo(mensaje))
        else:
            print('\nNo hay mensajes nuevos.')

    def eliminar_mensajes(self):
        """
        Permite al usuario eliminar mensajes específicos de la bandeja.
        Muestra los mensajes numerados y permite seleccionar cuál eliminar.
        """
        if not self.ver_bandeja():
            return
            
        seleccion = input("\nIngrese el número del mensaje a eliminar (0 para cancelar): ")
        if not seleccion.isdigit():
            print("Por favor ingrese un número válido")
            return
            
        seleccion = int(seleccion)
        if seleccion == 0:
            return
            
        if 1 <= seleccion <= self.bandeja.tamanio:
            self.bandeja.eliminarPosicion(seleccion - 1)
            print("Mensaje eliminado exitosamente")
        else:
            print("Número de mensaje inválido")
   
    def actualizar_bandeja(self):
        cantidad_mensajes = len(self.en_espera) 
        if cantidad_mensajes > 0:
            print(f'\nTenes {cantidad_mensajes} mensaje/s nuevos')
            while self.en_espera:
                mensaje = self.en_espera.popleft()
                print(mensaje)
                self.bandeja.agregarInicio(Nodo(mensaje))
        else:
            print('\nNo hay mensajes nuevos.')

    def menu(self):
        while True:
            opcion = input("""
SMS
1. Ver bandeja de mensajes
2. Enviar mensaje
3. Eliminar mensajes
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.ver_bandeja()
            elif opcion == "2":
                if self.celular.validar_estado_emisor():
                    self.enviar_mensaje()
            elif opcion == "3":
                self.eliminar_mensajes()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
   
class Telefono(Aplicacion):
    def __init__(self, celular: Celular, contactos):
        super().__init__(celular)
        self.almacenamiento=1 #ocupa 1 gb
        celular.almacenamiento_ocupado+=self.almacenamiento
        self.historial_llamadas=deque() #Pila para ver cual llega primero
        self.contactos=contactos
        self.necesaria = True
    
    def llamar(self):
        if self.celular.llamada_actual is None:
            # Primero mostramos los contactos disponibles
            self.contactos.ver_contactos()
            
            # Pedimos el destinatario (puede ser un número directo o nombre de contacto)
            receptor = input("\nIngrese un numero o un nombre de contacto: ")
            
            # Si el receptor está en las claves (nombres) de contactos, obtenemos su número
            if receptor in self.contactos.lista_de_contactos:
                receptor = self.contactos.lista_de_contactos[receptor]
            else:
                # Si no es un contacto, verificamos que sea un número válido
                if not receptor.isdigit() or len(receptor) != 8:
                    print("Número inválido. Debe contener 8 dígitos.")
                    return
            

            self.celular.central.comunicacion_telefonica(self.celular, receptor)
        else:
            print('\nYa tienes una llamada en curso.')
    
    def recibir_llamada(self, comunicacion: Comunicacion):

        """
        Maneja una llamada entrante.
        
        Args:
            comunicacion: Objeto que contiene los datos de la llamada
        
        Returns:
            bool: True si la llamada fue aceptada, False en caso contrario
        """
        
        if self.celular.disponible:
            # Buscamos si el número que llama está en los contactos
            nombre_contacto = self.obtener_nombre_contacto(comunicacion.emisor.num_telefonico)
    
                    
            # Mostramos el nombre si existe, sino el número
            if nombre_contacto != comunicacion.emisor.num_telefonico:
                eleccion = input(f'{nombre_contacto} te está llamando. ¿Desea aceptar la llamada? (si/no)')
            else:
                eleccion = input(f'El numero {comunicacion.emisor.num_telefonico} te esta llamando. Desea aceptar la llamada? (si/no)')
                
            if eleccion.lower() == 'si':
                self.celular.disponible = False
                self.celular.llamada_actual = comunicacion
                return True
            else:
                return False
        # Se agrega al historial de llamadas como llamada perdida
        else:
            self.agregar_historial_llamadas(comunicacion)
            return False

    def terminar_llamada(self):
        if not self.celular.disponible:
            self.celular.central.terminar_comunicacion_telefonica(self.celular.llamada_actual)
            print('Llamada finalizada. ')
        else:
            print('No hay una llamada en curso. ')

    
    def ver_historial_llamadas(self):
        """
        Muestra el historial de llamadas ordenado cronológicamente.
        Las llamadas más recientes aparecen primero.
        """
        if not self.historial_llamadas:
            print("No hay llamadas en el historial")
            return
            
        print("\nHistorial de llamadas:")
        for i, llamada in enumerate(self.historial_llamadas, 1):
            # True si el emisor de la llamada es este celular
            es_llamada_saliente = llamada.emisor == self.celular
            emisor = self.obtener_nombre_contacto(llamada.emisor.num_telefonico)
            receptor = self.obtener_nombre_contacto(llamada.receptor.num_telefonico)
            
            if es_llamada_saliente:
                print(f"{i}. [SALIENTE] a: {receptor} - {llamada.fecha_inicio}")
            else:
                print(f"{i}. [ENTRANTE] de: {emisor} - {llamada.fecha_inicio}")

    def agregar_historial_llamadas(self, comunicacion: Comunicacion):
        self.historial_llamadas.appendleft(comunicacion)

    def menu(self):
        while True:
            opcion = input("""
TELÉFONO
1. Realizar llamada
2. Ver historial de llamadas
3. Terminar llamada actual
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                if self.celular.validar_estado_emisor():
                    self.llamar()
            elif opcion == "2":
                self.ver_historial_llamadas()
            elif opcion == "3":
                self.terminar_llamada()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
    
    
class AppEmail(Aplicacion):
    """
    Aplicación de correo electrónico.
    
    Attributes:
        mail (str): Dirección de email del usuario
        bandeja (ListaEnlazada): Lista de emails recibidos
        bandeja_enviados (list): Lista de emails enviados
        casillas_bloqueadas (set): Conjunto de direcciones bloqueadas
    """
    
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.almacenamiento=3 #ocupa 3gb
        celular.almacenamiento_ocupado+=self.almacenamiento
        self.mail = f"{celular.nombre.lower().replace(' ', '')}@gmail.com"
        celular.central_gmail.usuarios_registrados[self.mail]=celular
        self.bandeja= ListaEnlazada() #lista enlazada 
        self.en_espera = deque() # Mensajes que te llegaron cuando no tenias la red movil activa
        self.bandeja_enviados = deque()  # pila para los emails enviados
        self.necesaria = True
        self.casillas_bloqueadas=set()

    def actualizar_bandeja(self):
        cantidad_mensajes = len(self.en_espera)
        if cantidad_mensajes > 0:
            print(f'\nTenes {cantidad_mensajes} mensaje/s nuevos')
            while self.en_espera:
                mensaje = self.en_espera.popleft()
                print(mensaje)
                self.bandeja.agregarInicio(Nodo(mensaje))
        else:
            print('\nNo hay mensajes nuevos.')
            
    def recibir_mensaje(self, mensaje):
        self.bandeja.agregarInicio(Nodo(mensaje))
        
    def ver_bandeja(self, mostrar_no_leidos=False):
        if self.bandeja.esVacia():
            print("No hay mensajes en la bandeja")
            return False
            
        actual = self.bandeja.inicio
        contador = 1
        hay_mensajes = False
        
        print("\nBandeja de mensajes:")
        while actual:
            if not mostrar_no_leidos or not actual.dato.leido:
                hay_mensajes = True
                vista_emisor = actual.dato.emisor == self.mail
                print(f"{contador}. {actual.dato.__str__(vista_emisor)}\nCuerpo: {actual.dato.cuerpo}\n")
                actual.dato.leido = True
            actual = actual.siguiente
            contador += 1
            
        if mostrar_no_leidos and not hay_mensajes:
            print("No hay mensajes sin leer")
        return True

    def enviar_mail(self):
        if not self.celular.datos_moviles:
            print("Error: Necesita activar los datos móviles para enviar emails")
            return
        
        destinatario = input("Ingrese email del destinatario: ")
        if destinatario in self.casillas_bloqueadas:
            print("Has bloqueado esta casilla de correo. No se puede enviar el email. ")
            return
        
        asunto = input("Ingrese asunto: ")
        cuerpo = input("Escriba su mensaje: ")
        
        nuevo_email = Email(
            self.mail,
            destinatario,
            asunto,
            cuerpo
        )
        
        if self.celular.central_gmail.enviar_mail(nuevo_email):
            print("Email enviado exitosamente")
        else:
            print("Error al enviar el email")   
   
    def reenviar_mail(self):
        """
        Permite reenviar un email existente a otro destinatario.
        Mantiene la información del email original.
        
        Returns:
            bool: True si el email fue reenviado exitosamente, False en caso contrario
        """
        if not self.ver_bandeja():
            print("No hay emails para reenviar")
            return False
            
        opcion = int(input("\nIngrese el número del email a reenviar (0 para volver): "))
        if opcion == 0 or opcion > self.bandeja.tamanio:
            return False
            
        email = self.bandeja.obtener_nodo(opcion - 1).dato
        destinatario = input("Ingrese email del nuevo destinatario: ").strip()
        
        nuevo_email = Email(
            self.mail,
            destinatario,
            f"FWD: {email.asunto}",
            f"---------- Email reenviado ----------\nDe: {email.emisor}\nPara: {email.destinatario}\nFecha original: {email.fecha}\n{email.cuerpo}"
        )
            
        if self.celular.central_gmail.enviar_mail(nuevo_email):
            print("Email reenviado exitosamente")
            return True
        return False
           
    def bloquear_casillas(self):
        """
        Permite bloquear múltiples casillas de correo.
        Las casillas bloqueadas no podrán enviar emails a este usuario.
        """
        while True:
            casilla = input("ingrese la casilla que desea bloquear (No podra interactuar al estar bloqueada): ")
            try:
                if casilla in self.celular.central_gmail.usuarios_registrados:
                    self.casillas_bloqueadas.add(casilla)
                    print(f"Casilla {casilla} bloqueada exitosamente")
                else:
                    print("Esa casilla es inexistente")
            except Exception as e:
                print(f"Error al bloquear la casilla: {str(e)}")
            finally:
                opcion = input("¿Desea bloquear otra casilla? (si/no): ")
                if opcion.lower() == 'no':
                    break
                elif opcion.lower() != 'si':
                    print("Esa opción es inexistente")
                    break

    def desbloquear_casilla(self):
        """
        Permite desbloquear una casilla de correo previamente bloqueada.
        
        Returns:
            bool: True si se desbloqueó exitosamente, False en caso contrario
        """
        if not self.casillas_bloqueadas:
            print("No hay casillas bloqueadas")
            return False
            
        print("\nCasillas bloqueadas:")
        for casilla in sorted(self.casillas_bloqueadas):
            print(f"- {casilla}")
            
        casilla = input("\nIngrese el email que desea desbloquear: (ingrese . para desbloquear todas las casillas bloqueadas)").strip()
        if not casilla:
            print("El email no puede estar vacío")
            return False    
            
        if casilla == '.':
            self.casillas_bloqueadas.clear()
            print("Todas las casillas han sido desbloqueadas")
            return True
            
        if casilla in self.casillas_bloqueadas:
            self.casillas_bloqueadas.remove(casilla)
            print(f"La casilla {casilla} ha sido desbloqueada")
            return True
            
        print("La casilla ingresada no está bloqueada")
        return False

    def ver_bandeja_enviados(self):
        if not self.bandeja_enviados:
            print("No hay emails enviados")
            return
            
        print("\nEmails enviados:")
        for email in self.bandeja_enviados:
            print(email.__str__(True))

   
    def menu(self):
        while True:
            opcion = input(f"""
EMAIL - {self.mail}
1. Ver todos los emails
2. Ver emails no leídos
3. Ver emails enviados
4. Enviar email
5. Bloquear casilla
6. Desbloquear casilla
7. Reenviar email
8. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.ver_bandeja()
            elif opcion == "2":
                self.ver_bandeja(True)
            elif opcion == "3":
                self.ver_bandeja_enviados()
            elif opcion == "4":
                self.enviar_mail()
            elif opcion == "5":
                self.bloquear_casillas()
            elif opcion == "6":
                self.desbloquear_casilla()
            elif opcion == "7":
                self.reenviar_mail()
            elif opcion == "8":
                break
            else:
                print("Opción inválida")


class App_Store(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.almacenamiento= 2 #ocupa 2gb
        celular.almacenamiento_ocupado+=self.almacenamiento
        self.necesaria = True
        
    def descargar_app(self):
        if not self.celular.datos_moviles:
            print("Error: Necesita activar los datos móviles para descargar apps")
            return
            
        app = input("¿Qué app quiere descargar?: ")
        if app in self.celular.apps:
            print("Esta aplicación ya está instalada")
            return
            
        # Se crea un almacenamiento random  entre 0 y 2
        almacenamiento_de_nueva_app=random.uniform(0,2)
        #si pasa la verificacion este almacenamiento, se le pasa como atributo a la nueva app
        if self.celular.apps['configuracion'].validar_almacenamiento(almacenamiento_de_nueva_app):
            self.celular.apps[app] = Aplicacion(self.celular)
            self.celular.apps[app].almacenamiento=almacenamiento_de_nueva_app #se le pasa como atributo el almacenamiento ya verificado
            print(f"App '{app}' descargada exitosamente")
        

    def borrar_app(self):
        """
        Permite borrar una aplicación no esencial y liberar su espacio.
        Muestra la lista de apps instaladas y permite seleccionar cuál borrar.
        """
        apps_borrables = {nombre: app for nombre, app in self.celular.apps.items() 
                         if not app.necesaria}
        
        if not apps_borrables:
            print("No hay apps que se puedan borrar")
            return
            
        print("\nApps que se pueden borrar:")
        for nombre in apps_borrables:
            print(f"- {nombre}")
                
        app = input("\n¿Qué app quiere borrar?: ").lower().strip()
        if app not in apps_borrables:
            print("App no encontrada o no se puede borrar")
            return
            
        espacio_liberado = apps_borrables[app].almacenamiento
        del self.celular.apps[app]
        self.celular.almacenamiento_ocupado -= espacio_liberado
        print(f"App '{app}' borrada exitosamente. Se liberaron {espacio_liberado:.1f}GB")
        
        
    
    def menu(self):
        while True:
            opcion = input("""
APP STORE
1. Descargar app
2. Borrar app
3. Ver apps instaladas
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.descargar_app()
            elif opcion == "2":
                self.borrar_app()
            elif opcion == "3":
                print("\nApps instaladas:", list(self.celular.apps.keys()))
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
    

class Configuracion(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.almacenamiento=1.5 #ocupa gb
        celular.almacenamiento+=self.almacenamiento
        self.necesaria = True
        
    def cambiar_codigo(self):
        """Cambia el código de desbloqueo del celular"""
        
        # Si no hay código previo, simplemente pide el nuevo
        if self.celular.codigo is None:
            while True:
                try:
                    nuevo_codigo = int(input('Ingrese el nuevo código: '))
                    self.celular.codigo = nuevo_codigo
                    print("Código establecido exitosamente")
                    return
                except ValueError:
                    print("El código debe ser un número")
                
        # Si hay código previo, pide verificación
        if self.celular.codigo == int(input('Ingrese el código actual: ')):
            while True:
                try:
                    nuevo_codigo = int(input('Ingrese el nuevo código: '))
                    self.celular.codigo = nuevo_codigo
                    print("Código cambiado exitosamente")
                    return
                except ValueError:
                    print("El código debe ser un número")
        else:
            print("Código incorrecto")
        
    def activar_red_movil(self):
        #desactiva la red movil y manda la actualizacion a la central
        if self.celular.red_movil:
            print('La red movil ya esta activada')
        else:   
            if self.celular.num_telefonico in self.celular.central.dispositivos_registrados:
                self.celular.red_movil = True
                self.celular.apps['sms'].actualizar_bandeja()
                print("Red móvil activada")
            else:
                print('Tu celular no esta registrado en la central. No podes activar la red movil')
    
    def desactivar_red_movil(self):
        if self.celular.llamada_actual:
            self.celular.apps['telefono'].terminar_llamada()
        self.celular.red_movil = False
        print("Red móvil desactivada")
        
        
    def toggle_disponibilidad(self):
        self.celular.disponible = not self.celular.disponible
        estado = "disponible" if self.celular.disponible else "no disponible"
        print(f"El celular ahora está {estado} para recibir llamadas")

    def toggle_datos_moviles(self):
        if not self.celular.red_movil:
            print("Error: Primero debe activar la red móvil")
            return
            
        self.celular.datos_moviles = not self.celular.datos_moviles
        estado = "activados" if self.celular.datos_moviles else "desactivados"
        #se actualiza la bandeja del mail cuando se prenden los datos
        if self.celular.datos_moviles:
            self.celular.apps['email'].actualizar_bandeja()
        print(f"Datos móviles {estado}")
        
    def validar_almacenamiento(self, almacenamiento_requerido: float):
        """
        Valida si hay suficiente almacenamiento disponible para instalar una nueva aplicación.
        El método actualiza el almacenamiento_ocupado del celular si hay espacio suficiente.
        Si no hay espacio suficiente, muestra un mensaje de error.

        Args:
            almacenamiento_requerido (float): Cantidad de almacenamiento en GB que requiere la aplicación

        Returns:
            bool: True si hay suficiente espacio disponible, False en caso contrario
        """
        
        
        espacio_disponible = self.celular.almacenamiento - self.celular.almacenamiento_ocupado  
        if espacio_disponible >= almacenamiento_requerido:
            self.celular.almacenamiento_ocupado += almacenamiento_requerido
            return True
        else: 
            print("No se puede descargar esta aplicacion debido a que ocupa mas del espacio que tiene disponible")
            return False

    def menu(self):
        while True:
            opcion = input("""
CONFIGURACIÓN
1. Cambiar código de desbloqueo
2. Activar red móvil
3. Desactivar red móvil
4. Cambiar disponibilidad para llamadas
5. Activar/Desactivar datos móviles
6. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.cambiar_codigo()
            elif opcion == "2":
                self.activar_red_movil()
            elif opcion == "3":
                self.desactivar_red_movil()
            elif opcion == "4":
                self.toggle_disponibilidad()
            elif opcion == "5":
                self.toggle_datos_moviles()
            elif opcion == "6":
                break
            else:
                print("Opción inválida")
