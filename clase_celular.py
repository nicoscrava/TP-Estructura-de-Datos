from clase_central import Central, Comunicacion
from collections import deque
from clase_listaenlazada import ListaEnlazada, Nodo
from clase_email import Email, CentralGmail
import random

class Dispositivo:
    
    VALID_RAM_VALUES = [2, 4, 8, 16, 32]
    VALID_OS_VALUES = ['android', 'ios']
    VALID_STORAGE_VALUES = [32, 64, 128, 256, 512]
    central_gmail = CentralGmail()
    dispositivos_instanciados = []

    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento):
        """
        Inicializa un nuevo dispositivo.
        
        Args:
            identificacion: Identificador único de 8 caracteres sin espacios
            nombre: Nombre del dispositivo (no vacío)
            modelo: Modelo del dispositivo
            sistema_operativo: Sistema operativo ('Android' o 'iOS')
            version: Versión del sistema operativo (formato: X.Y.Z)
            RAM: Memoria RAM en GB (valores válidos: 2, 4, 8, 16, 32)
            almacenamiento: Almacenamiento en GB (valores válidos: 32, 64, 128, 256, 512)
            
        Raises:
            ValueError: Si algún parámetro no cumple con los requisitos de formato o valor
        """
        
        if len(identificacion) != 8:
            raise ValueError("La identificación debe tener exactamente 8 caracteres.")
        if " " in identificacion:
            raise ValueError("La identificación no puede contener espacios.")
        if identificacion in [dispositivo.identificacion for dispositivo in Dispositivo.dispositivos_instanciados]:
            raise ValueError("Esta identificación ya está registrada en otro dispositivo.")
        self.identificacion = identificacion

        nombre = nombre.strip()
        if len(nombre) == 0:
            raise ValueError("El nombre no puede estar vacío.")
        self.nombre = nombre
        
        modelo = modelo.strip()
        if len(modelo) == 0:
            raise ValueError("El modelo no puede estar vacío.")
        self.modelo = modelo

        sistema_operativo = sistema_operativo.strip().lower()
        if sistema_operativo not in self.VALID_OS_VALUES:
            raise ValueError(f"Sistema operativo debe ser uno de: {', '.join(self.VALID_OS_VALUES)}")
        self.sistema_operativo = sistema_operativo
        
        try:
            partes = str(version).split('.')
            for parte in partes:
                if not parte.isdigit() or int(parte) < 0:
                    raise ValueError
            self.version = version
        except ValueError:
            raise ValueError("La versión debe tener un formato válido (ej: 1, 1.0, 1.1.2)")

        try:
            ram_int = int(RAM)
            if ram_int not in self.VALID_RAM_VALUES:
                raise ValueError
            self.RAM = ram_int
        except ValueError:
            raise ValueError(f"La RAM debe ser uno de estos valores: {', '.join(str(x) for x in self.VALID_RAM_VALUES)} GB")

        try:
            almacenamiento_int = int(almacenamiento)
            if almacenamiento_int not in self.VALID_STORAGE_VALUES:
                raise ValueError
            self.almacenamiento = float(almacenamiento_int) 
        except ValueError:
            raise ValueError(f"El almacenamiento debe ser uno de estos valores: {', '.join(str(x) for x in self.VALID_STORAGE_VALUES)} GB")

        # variables de estado
        self.encendido = False 
        self.desbloqueado=False 
        self.codigo=None
        self.almacenamiento_ocupado=0
        
        contactos = Contactos(self)
        self.apps={"contactos": contactos,
                    'configuracion': Configuracion(self), 
                    'notas': Notas(self)
                    }
        
    def abrir_app(self):
        """
        Permite al usuario abrir una aplicación instalada en el dispositivo.
        Muestra la lista de aplicaciones disponibles y permite seleccionar una.
        """
        print(f"\nAplicaciones disponibles: {', '.join(list(self.apps.keys()))}")
        
        app_nombre = input("\nIngrese el nombre de la aplicación: ").lower()
        if app_nombre in self.apps:
            self.apps[app_nombre].menu()
        else:
            print("\nAplicación no encontrada")
            
    def bloq_desbloq(self):
        """
        Maneja el bloqueo y desbloqueo del dispositivo.
        Si tiene código configurado, solicita la verificación.
        Permite hasta 3 intentos de desbloqueo.
        """
        if self.desbloqueado:
            self.desbloqueado = False
            print("\nHas bloqueado el dispositivo")
            return
        
        if self.codigo is None:
            self.desbloqueado = True
            print("\nEl dispositivo se ha desbloqueado")
            return
        
        intentos = 3
        while intentos > 0:
            try:
                codigo_ingresado = int(input('\nIngrese el código de desbloqueo: '))
                if codigo_ingresado == self.codigo:
                    self.desbloqueado = True
                    print("\nEl dispositivo se ha desbloqueado")
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
        
    def encender_apagar(self):
        """
        Alterna el estado de encendido/apagado del dispositivo.
        """
        self.encendido = not self.encendido
        if self.encendido:
            print("\nEl dispositivo se ha prendido")

        else:
            self.desbloqueado = False
            print("\nHas apagado el dispositivo")
    
    @classmethod
    def generar_informe_txt(cls):
        """Genera un archivo TXT con información detallada de todos los dispositivoes instanciados"""
        try:
            with open('informe_dispositivos.txt', 'w') as archivo:
                for dispositivo in cls.dispositivos_instanciados:
                    archivo.write(dispositivo.__str__())
                    archivo.write("\n" + "-"*50 + "\n") 
                    
            print("Informe generado exitosamente en 'informe_dispositivos.txt'")
            
        except Exception as e:
            print(f"Error al generar el informe: {str(e)}")
            
    def menu_dispositivo(self):
        """
        Muestra el menú principal del dispositivo y maneja la navegación entre opciones.
        Permite encender/apagar el dispositivo, bloquear/desbloquear y acceder a aplicaciones.
        """
        encendido = False
        desbloqueado = False
        while not encendido:
                opcion = input("""
dispositivo APAGADO
1. Encender dispositivo
2. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    self.encender_apagar()
                    encendido=True
                elif opcion == "2":
                    return
                else:
                    print("Opción inválida")
                
        while not desbloqueado:
                opcion = input("""
dispositivo BLOQUEADO
1. Desbloquear dispositivo
2. Apagar dispositivo
3. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    self.bloq_desbloq()
                    desbloqueado=True
                elif opcion == "2":
                    self.encender_apagar() 
                    return
                elif opcion == "3":
                    return
                else:
                    print("Opción inválida")
                        
        while desbloqueado:
                opcion = input("""
MENU dispositivo
1. Abrir aplicación
2. Bloquear dispositivo
3. Apagar dispositivo
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
                    return
                else:
                    print("Opción inválida")


class Tablet(Dispositivo):
    
    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento):
        super().__init__(identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento)
        self.datos_moviles=False
        
        #se agregan estas apps a tablet
        self.apps["email"]= AppEmail(self)
        self.apps['app store']= App_Store(self)
        
        Tablet.dispositivos_instanciados.append(self)
        
    def __str__(self):
        return f"""
        Tablet {self.nombre}
        ID: {self.identificacion}
        Modelo: {self.modelo}
        SO: {self.sistema_operativo} v{self.version}
        RAM: {self.RAM}GB
        Almacenamiento: {self.almacenamiento}GB
        """


class Celular(Dispositivo):
    """
    Representa un dispositivo Celular con sus aplicaciones y funcionalidades.
    
    Attributes:
        central (Central): Central de comunicaciones compartida
    """
    central = Central()

    def __init__(self,identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico):
        
        """
        Inicializa un nuevo dispositivo celular.
        
        Args:
            num_telefonico: Número telefónico de 8 dígitos
            
        Raises:
            ValueError: Si algún parámetro no cumple con los requisitos de formato o valor
        """
        super().__init__(identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento)
        num_telefonico = num_telefonico.strip()
        if not num_telefonico.isdigit() or len(num_telefonico) != 8:
            raise ValueError("El número telefónico debe ser una cadena con 8 dígitos")
        if num_telefonico in [dispositivo.num_telefonico for dispositivo in Celular.dispositivos_instanciados if isinstance(dispositivo,Celular)]: 
            raise ValueError("Este número telefónico ya está registrado")
        self.num_telefonico = num_telefonico
        
        # variables de estado
        self.red_movil=False
        self.disponible = True
        self.llamada_actual = None



        self.apps["sms"] = SMS(self, self.apps['contactos'])
        self.apps['telefono'] = Telefono(self, self.apps['contactos'])

        
        Celular.dispositivos_instanciados.append(self)
    
    def encender_apagar(self):
        """
        Alterna el estado de encendido/apagado del dispositivo.
        Cuando se enciende, activa la red móvil.
        Cuando se apaga, desconecta de la central y termina llamadas activas.
        """
        self.encendido = not self.encendido
        if self.encendido:
            self.apps['configuracion'].activar_red_movil()
            print("\nEl dispositivo se ha prendido")

        else:
            self.red_movil = False
            self.desbloqueado = False
            if self.llamada_actual is not None:
                self.apps['telefono'].terminar_llamada()
            print("\nHas apagado el dispositivo")



    def validar_estado_emisor(self):
        """
        Valida si el dispositivo puede emitir comunicaciones.
        
        Returns:
            bool: True si el dispositivo está habilitado para emitir comunicaciones, False en caso contrario
        """
        if not self.red_movil:
            print('Tu dispositivo no se puede comunicar. Activa la red móvil. ')
            return False
        
        if self.num_telefonico not in self.central.dispositivos_registrados:
            print('Tu dispositivo no se encuentra en la red.')
            return False
        
        return True


class Celular_Viejo(Celular):
    def __init__(self,identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico):
        
        """
        Inicializa un nuevo dispositivo celular.
        
        Args:
            num_telefonico: Número telefónico de 8 dígitos
            
        Raises:
            ValueError: Si algún parámetro no cumple con los requisitos de formato o valor
        """
        super().__init__(identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico)
        self.apps['configuracion']=Configuracion_Celular_Viejo()
    
    def __str__(self):
        estado_red = "Activada" if self.red_movil else "Desactivada"
        
        return f"""
        dispositivo {self.nombre}
        ID: {self.identificacion}
        Modelo: {self.modelo}
        SO: {self.sistema_operativo} v{self.version}
        RAM: {self.RAM}GB
        Almacenamiento: {self.almacenamiento}GB
        Numero: {self.num_telefonico}
        Red movil: {estado_red}
        """
        
class Celular_Nuevo(Celular):
    def __init__(self,identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico):
        
        """
        Inicializa un nuevo dispositivo celular.
        
        Args:
            num_telefonico: Número telefónico de 8 dígitos
            
        Raises:
            ValueError: Si algún parámetro no cumple con los requisitos de formato o valor
        """
        super().__init__(identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico)
        self.datos_moviles=False
    
        #solo el celular nuevo tiene estas apps
        self.apps['configuracion']=Configuracion_Celular()
        self.apps["email"]= AppEmail(self)
        self.apps['app store']= App_Store(self)
        
    def __str__(self):
        estado_red = "Activada" if self.red_movil else "Desactivada"
        estado_datos = "Activados" if self.datos_moviles else "Desactivados"
        
        return f"""
        dispositivo {self.nombre}
        ID: {self.identificacion}
        Modelo: {self.modelo}
        SO: {self.sistema_operativo} v{self.version}
        RAM: {self.RAM}GB
        Almacenamiento: {self.almacenamiento}GB
        Numero: {self.num_telefonico}
        Red movil: {estado_red}
        Datos moviles: {estado_datos}
        """
         
class Aplicacion:
    """
    Clase base para todas las aplicaciones del dispositivo.
    
    Attributes:
        dispositivo (dispositivo): Referencia al dispositivo que contiene la aplicación
        almacenamiento (float): Espacio que ocupa la aplicación en GB
        necesaria (bool): Indica si la aplicación es del sistema y no puede eliminarse
    """
    def __init__(self, dispositivo: 'Dispositivo'):
        """
        Inicializa una nueva aplicación.
        
        Args:
            dispositivo: Referencia al dispositivo que contendrá la aplicación
        """
        self.dispositivo = dispositivo
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
        Se utiliza para apps de mensajeria.
        
        Args:
            numero: Número telefónico a buscar
                
        Returns:
            str: Nombre del contacto si existe, número en caso contrario
        """
        for nombre, num in self.dispositivo.apps['contactos'].lista_de_contactos.items():
            if num == numero:
                return nombre
        return numero


class Contactos(Aplicacion):
    """
    Aplicación para gestionar contactos del dispositivo.
    
    Attributes:
        lista_de_contactos (dict): Diccionario que almacena nombre y número de contactos
    """
    
    def __init__(self, dispositivo: dispositivo):
        super().__init__(dispositivo)
        self.lista_de_contactos={}
        self.almacenamiento=1
        dispositivo.almacenamiento_ocupado +=self.almacenamiento
        self.necesaria = True
    
    def ver_contactos(self):
        """
        Muestra la lista de contactos guardados.
        
        Si no hay contactos guardados, muestra un mensaje indicándolo.
        Si hay contactos, muestra el nombre y número de cada uno.
        """
        if not self.lista_de_contactos:
            print("No hay contactos guardados")
        else:
            print("\nLista de contactos:")
            for nombre, numero in self.lista_de_contactos.items():
                print(f"{nombre}: {numero}")

    def agregar_contacto(self):
        """
        Permite agregar un nuevo contacto a la lista.
        
        Solicita al usuario ingresar un número telefónico y un nombre.
        Valida que:
        - El número contenga solo dígitos
        - El número tenga exactamente 8 dígitos 
        - El número no esté duplicado
        - El nombre no esté duplicado (agrega sufijo si es necesario)
        
        Si el nombre ya existe, sugiere una alternativa agregando un número
        entre paréntesis y consulta al usuario si acepta.
        """
        agrego_contacto=True
        while agrego_contacto:
            numero = input("\nIngrese el número del contacto (8 dígitos) o 'cancelar' para volver: ").strip()
            if numero.lower() == "cancelar":
                print("\nOperación cancelada")
                return
            if not numero.isdigit():
                print("El número debe contener solo dígitos")
            elif len(numero) != 8:
                print("El numero debe tener 8 dígitos")
            elif numero in self.lista_de_contactos.values():
                print("Este número ya existe en contactos")
            elif numero==self.dispositivo.num_telefonico:
                print("No puedes agregar un contacto con tu mismo número")
            else:
                agrego_contacto=False
        
        agrego_contacto_dos=True
        while agrego_contacto_dos:
            nombre_base = input("Ingrese nombre: ")
            
            nombre = self.revisar_repeticiones_nombre(nombre_base)
            
            if nombre != nombre_base:
                opcion = input(f"El nombre '{nombre_base}' ya existe. ¿Desea guardarlo como '{nombre}'? (si/no): ").lower()
                if opcion != 'si' and opcion != 'no':
                    print("Opción inválida")
                elif opcion == 'no':
                    print("Contacto no agregado. ")
                    agrego_contacto_dos=False
            
            self.lista_de_contactos[nombre] = numero
            print(f"Contacto agregado: {nombre} - {numero}")
            agrego_contacto_dos=False
            
    def modificar_contacto(self):
        """
        Permite modificar el nombre o número de un contacto existente.
        
        Muestra la lista de contactos y solicita el nombre del contacto a modificar.
        Permite elegir entre modificar el nombre o el número.
        
        Para modificar el nombre:
        - Valida que el nuevo nombre no esté duplicado
        - Si está duplicado, sugiere alternativa con sufijo numérico
        - Consulta al usuario si acepta el nombre alternativo
        
        Para modificar el número:
        - Valida que contenga solo dígitos
        - Valida que tenga 8 dígitos exactos
        - Valida que no esté duplicado en otros contactos
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
        
        opcion = input("¿Qué desea modificar?\n1. Nombre\n2. Número\nIngrese opción: ")
        
        if opcion == "1":
            opcion_uno=True
            while opcion_uno:
                nombre_base = input("Ingrese el nuevo nombre: ")
                
                if nombre_base in self.lista_de_contactos and nombre_base != nombre:
                    nombre_nuevo = self.revisar_repeticiones_nombre(nombre_base)
                    opcion = input(f"El nombre '{nombre_base}' ya existe. ¿Desea guardarlo como '{nombre_nuevo}'? (si/no): ").lower()
                    if opcion != 'si' and opcion != 'no':
                        print("Opción inválida")
                        continue
                    elif opcion == 'no':
                        print("Contacto no modificado.")
                        opcion_uno=False
                    else:
                        nombre_base = nombre_nuevo
                
                numero = self.lista_de_contactos[nombre]
                del self.lista_de_contactos[nombre]
                self.lista_de_contactos[nombre_base] = numero
                print(f"Nombre modificado: {nombre_base} - {numero}")
                opcion_uno=False
                    
        elif opcion == "2":
            opcion_dos=True
            while opcion_dos:
                nuevo_numero = input("Ingrese el nuevo número: ")
                if not nuevo_numero.isdigit():
                    print("El número debe contener solo dígitos")
                elif len(nuevo_numero) != 8:
                    print("El número debe tener 8 dígitos")
                elif nuevo_numero in self.lista_de_contactos.values() and nuevo_numero != self.lista_de_contactos[nombre]:
                    print("Este número ya existe en contactos")
                else:
                    self.lista_de_contactos[nombre] = nuevo_numero
                    print(f"Número modificado: {nombre} - {nuevo_numero}")
                    opcion_dos=False
        else:
            print("Opción inválida")

    def revisar_repeticiones_nombre(self, nombre_base):
        """
        Revisa si un nombre ya existe en la lista de contactos y genera uno nuevo agregando un número entre paréntesis.

        Args:
            nombre_base (str): El nombre base a revisar

        Returns:
            str: El nombre modificado si había repetición, o el original si no había conflicto
        """
        nombre_actual = nombre_base
        contador = 1
        while nombre_actual in self.lista_de_contactos:
            nombre_actual = f"{nombre_base}({contador})"
            contador += 1
        return nombre_actual

    def menu(self):
        menu_contactos=True
        while menu_contactos:
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
                menu_contactos=False
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
    def __init__(self, dispositivo: dispositivo, contactos: Contactos):
        super().__init__(dispositivo)
        self.almacenamiento=1 
        dispositivo.almacenamiento_ocupado+=self.almacenamiento
        self.bandeja= ListaEnlazada() 
        self.contactos=contactos
        self.en_espera = deque() # cola
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
            elif receptor==self.dispositivo.num_telefonico:
                print("No puedes enviar un mensaje a ti mismo")
                raise ValueError("No puedes enviar un mensaje a ti mismo")
                
            mensaje = input("\nEscriba su mensaje: ")
            if not mensaje.strip():
                raise ValueError("El mensaje no puede estar vacío")
                
            self.dispositivo.central.comunicacion_sms(self.dispositivo, receptor, mensaje)
            
        except ValueError as e:
            print(f"\nError al enviar mensaje: {str(e)}")

    def recibir_mensaje(self, mensaje):
        self.bandeja.agregarInicio(Nodo(mensaje))
   
    def ver_bandeja(self):
        """
        Muestra todos los mensajes almacenados en la bandeja.
        
        Imprime cada mensaje numerado, mostrando el emisor/receptor y contenido.
        Si la bandeja está vacía, muestra un mensaje indicándolo.
        
        Returns:
            bool: True si hay mensajes, False si la bandeja está vacía
        """
        if self.bandeja.esVacia():
            print("No hay mensajes en la bandeja")
            return False
            
        print("\nBandeja de mensajes:")
        actual = self.bandeja.inicio
        contador = 1
        
        while actual:
            vista_emisor = actual.dato.emisor == self.dispositivo
            print(f"{contador}. {actual.dato.__str__(vista_emisor)}")
            actual = actual.siguiente
            contador += 1
        return True
       
    def actualizar_bandeja(self):
        """
        Actualiza la bandeja de mensajes con los mensajes en espera.
        
        Verifica si hay mensajes nuevos en la cola de espera y los agrega
        al inicio de la bandeja de mensajes. Muestra la cantidad de mensajes
        nuevos si los hay.
        """
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
   
    def menu(self):
        menu_sms=True
        while menu_sms:
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
                if self.dispositivo.validar_estado_emisor():
                    self.enviar_mensaje()
            elif opcion == "3":
                self.eliminar_mensajes()
            elif opcion == "4":
                menu_sms=False
            else:
                print("Opción inválida")


class Telefono(Aplicacion):
    """
    Aplicación para realizar y recibir llamadas telefónicas.
    
    Attributes:
        historial_llamadas (deque): Cola que almacena el historial de llamadas
        contactos (Contactos): Referencia a la aplicación de contactos
    """
    def __init__(self, dispositivo: dispositivo, contactos):
        super().__init__(dispositivo)
        self.almacenamiento=1 
        dispositivo.almacenamiento_ocupado+=self.almacenamiento
        self.historial_llamadas=deque() #Pila para ver cual llega primero
        self.contactos=contactos
        self.necesaria = True
    
    def llamar(self):
        """
        Inicia una llamada telefónica a otro dispositivo.
        
        Muestra la lista de contactos y permite ingresar un número o nombre.
        Si se ingresa un nombre, busca el número asociado en contactos.
        Valida que el número tenga 8 dígitos.
        No permite iniciar una llamada si ya hay una en curso.
        
        La llamada se realiza a través de la central telefónica.
        """
        if self.dispositivo.llamada_actual is None:
            
            self.contactos.ver_contactos()
            
            receptor = input("\nIngrese un numero o un nombre de contacto: ")
            
            if receptor in self.contactos.lista_de_contactos:
                receptor = self.contactos.lista_de_contactos[receptor]
            elif receptor==self.dispositivo.num_telefonico:
                print("No puedes llamar a ti mismo")
                return
            elif not receptor.isdigit() or len(receptor) != 8:
                print("Número inválido. Debe contener 8 dígitos.")
                return
            
            self.dispositivo.central.comunicacion_telefonica(self.dispositivo, receptor)
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
        
        if self.dispositivo.disponible:
            nombre_contacto = self.obtener_nombre_contacto(comunicacion.emisor.num_telefonico)
            
            if nombre_contacto != comunicacion.emisor.num_telefonico:
                eleccion = input(f'{self.dispositivo.nombre}, {nombre_contacto} te está llamando. ¿Desea aceptar la llamada? (si/no)')
            else:
                eleccion = input(f'{self.dispositivo.nombre}, el numero {comunicacion.emisor.num_telefonico} te esta llamando. Desea aceptar la llamada? (si/no)')
                
            if eleccion.lower() == 'si':
                self.dispositivo.disponible = False
                self.dispositivo.llamada_actual = comunicacion
                return True
            else:
                return False
        else:
            self.agregar_historial_llamadas(comunicacion)
            return False

    def terminar_llamada(self):
        """
        Termina una llamada telefónica.
        
        Si hay una llamada en curso, la termina a través de la central telefónica.
        Muestra un mensaje indicando que la llamada ha finalizado.
        """
        if not self.dispositivo.disponible:
            self.dispositivo.central.terminar_comunicacion_telefonica(self.dispositivo.llamada_actual)
            print('Llamada finalizada. ')
        else:
            print('No hay una llamada en curso. ')

    def ver_historial_llamadas(self):
        """
        Muestra el historial de llamadas ordenado cronológicamente.
        Las llamadas más recientes aparecen primero.

        El historial muestra:
        - Número secuencial de la llamada
        - Tipo de llamada (ENTRANTE/SALIENTE) 
        - Nombre del contacto o número telefónico del emisor/receptor
        - Fecha y hora de inicio de la llamada

        Si el historial está vacío, muestra un mensaje indicándolo.
        """
        if not self.historial_llamadas:
            print("No hay llamadas en el historial")
            return
            
        print("\nHistorial de llamadas:")
        for i, llamada in enumerate(reversed(self.historial_llamadas), 1):
            es_llamada_saliente = llamada.emisor == self.dispositivo
            emisor = self.obtener_nombre_contacto(llamada.emisor.num_telefonico)
            receptor = self.obtener_nombre_contacto(llamada.receptor.num_telefonico)
            
            if es_llamada_saliente:
                print(f"{i}. [SALIENTE] a: {receptor} - {llamada.fecha_inicio}")
            else:
                print(f"{i}. [ENTRANTE] de: {emisor} - {llamada.fecha_inicio}")

    def agregar_historial_llamadas(self, comunicacion: Comunicacion):
        """
        Agrega una llamada al historial de llamadas.
        
        La llamada se agrega al principio de la cola para mantener el orden cronológico.
        """
        self.historial_llamadas.appendleft(comunicacion)

    def menu(self):
        menu_llamada=True
        while menu_llamada:
            opcion = input("""
TELÉFONO
1. Realizar llamada
2. Ver historial de llamadas
3. Terminar llamada actual
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                if self.dispositivo.validar_estado_emisor():
                    self.llamar()
            elif opcion == "2":
                self.ver_historial_llamadas()
            elif opcion == "3":
                self.terminar_llamada()
            elif opcion == "4":
                menu_llamada==False
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
    
    def __init__(self, dispositivo: dispositivo):
        super().__init__(dispositivo)
        self.almacenamiento=3 
        dispositivo.almacenamiento_ocupado+=self.almacenamiento
        self.mail = f"{dispositivo.nombre.lower().replace(' ', '')}@gmail.com"
        dispositivo.central_gmail.usuarios_registrados[self.mail]=dispositivo
        self.bandeja= ListaEnlazada() #lista enlazada 
        self.en_espera = deque() # cola
        self.bandeja_enviados = deque()  # pila 
        self.necesaria = True
        self.casillas_bloqueadas=set()

    def actualizar_bandeja(self):
        """
        Actualiza la bandeja de entrada con los mensajes en espera.
        
        Si hay mensajes en la cola de espera, los muestra y los mueve a la bandeja de entrada.
        Si no hay mensajes nuevos, muestra un mensaje indicándolo.
        """
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
        """
        Recibe un mensaje y lo agrega a la bandeja de entrada.
        
        Args:
            mensaje (Email): El mensaje de correo electrónico a recibir
        """
        self.bandeja.agregarInicio(Nodo(mensaje))
        
    def ver_bandeja(self, mostrar_no_leidos=False):
        """
        Muestra los mensajes en la bandeja de entrada.
        
        Args:
            mostrar_no_leidos (bool): Si es True, muestra solo mensajes no leídos. Por defecto False.
            
        Returns:
            bool: True si hay mensajes para mostrar, False si la bandeja está vacía
        """
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
                print(f"{contador}. {actual.dato.__str__(vista_emisor)}\nCuerpo: {actual.dato.contenido[1]}\n")
                actual.dato.leido = True
            actual = actual.siguiente
            contador += 1
            
        if mostrar_no_leidos and not hay_mensajes:
            print("No hay mensajes sin leer")
        return True

    def enviar_mail(self):
        """
        Permite enviar un nuevo email a un destinatario.
        
        Verifica que los datos móviles estén activos antes de enviar.
        Solicita al usuario ingresar:
        - Email del destinatario
        - Asunto del correo
        - Cuerpo del mensaje
        
        Si el destinatario está bloqueado, no permite enviar el email.
        """
        if not self.dispositivo.datos_moviles:
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
        
        if self.dispositivo.central_gmail.enviar_mail(nuevo_email):
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
                
        try:
            opcion = input("\nIngrese el número del email a reenviar (0 para volver): ").strip()
            
            if opcion == "0":
                return False
                
            opcion = int(opcion)
            
            if opcion < 0 or opcion > self.bandeja.tamanio:
                print("El número ingresado no es válido")
                return False
                
            email = self.bandeja.obtener_nodo(opcion - 1).dato
            destinatario = input("Ingrese email del nuevo destinatario: ").strip()
            if destinatario in self.casillas_bloqueadas:
                print("Has bloqueado esta casilla de correo. No se puede reenviar el email. ")
                return False
            nuevo_email = Email(
                self.mail,
                destinatario,
                f"FWD: {email.contenido[0]}",
                f"---------- Email reenviado ----------\nDe: {email.emisor}\nPara: {email.destinatario}\nFecha original: {email.fecha}\n{email.contenido[1]}"
            )
                
            if self.dispositivo.central_gmail.enviar_mail(nuevo_email):
                print("Email reenviado exitosamente")
                return True
                
            print("No se pudo reenviar el email")
            return False
            
        except ValueError:
            print("Debe ingresar un número válido")
            return False
            
    def bloquear_casillas(self):
        """
        Permite bloquear múltiples casillas de correo.
        Las casillas bloqueadas no podrán enviar emails a este usuario.
        """
        condicion= True
        while condicion:
            casilla = input("ingrese la casilla que desea bloquear (No podra interactuar al estar bloqueada): ")
            try:
                if casilla == self.mail:
                    print('No te podes bloquear a vos mismo. ')
                elif casilla in self.casillas_bloqueadas:
                    print('Esta casilla ya esta bloqueada. ')
                elif casilla in self.dispositivo.central_gmail.usuarios_registrados:
                    self.casillas_bloqueadas.add(casilla)
                    print(f"Casilla {casilla} bloqueada exitosamente")
                else:
                    print("Esa casilla es inexistente")
            except Exception as e:
                print(f"Error al bloquear la casilla: {str(e)}")
            finally:
                opcion = input("¿Desea bloquear otra casilla? (si/no): ")
                if opcion.lower() == 'no':
                    condicion=False
                elif opcion.lower() != 'si':
                    print("Esa opción es inexistente")
                    condicion=False

    def desbloquear_casilla(self):
        """
        Permite desbloquear una casilla de correo previamente bloqueada.
        Tambien permite desbloquear todas las casillas bloqueadas si se ingresa '.'
        
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
        """
        Muestra los emails enviados.
        """
        if not self.bandeja_enviados:
            print("No hay emails enviados")
            return
            
        print("\nEmails enviados:")
        for email in self.bandeja_enviados:
            print(email.__str__(True))

    def menu(self):
        menu_email=True
        while menu_email:
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
                menu_email=False
            else:
                print("Opción inválida")


class App_Store(Aplicacion):
    """
    Aplicación para gestionar la instalación y eliminación de apps.
    
    Permite descargar nuevas aplicaciones y eliminar las existentes que no sean del sistema.
    """
    def __init__(self, dispositivo: dispositivo):
        super().__init__(dispositivo)
        self.almacenamiento= 2
        self.dispositivo.almacenamiento_ocupado+=self.almacenamiento
        self.necesaria = True
        
    def descargar_app(self):
        """
        Permite descargar una nueva aplicación al dispositivo.
        
        Verifica que:
        - Los datos móviles estén activados
        - La app no esté ya instalada 
        - Haya suficiente espacio de almacenamiento
        
        La app descargada ocupará un espacio aleatorio entre 0 y 2 GB.
        """
        if not self.dispositivo.datos_moviles:
            print("Error: Necesita activar los datos móviles para descargar apps")
            return
            
        app = input("¿Qué app quiere descargar?: ")
        if app in self.dispositivo.apps:
            print("Esta aplicación ya está instalada")
            return
            
        
        almacenamiento_de_nueva_app=random.uniform(0,2)
        if self.dispositivo.apps['configuracion'].validar_almacenamiento(almacenamiento_de_nueva_app):
            self.dispositivo.almacenamiento_ocupado += almacenamiento_de_nueva_app
            self.dispositivo.apps[app.lower()] = Aplicacion(self.dispositivo)
            self.dispositivo.apps[app.lower()].almacenamiento=almacenamiento_de_nueva_app
            print(f"App '{app}' descargada exitosamente")
        else:
            print("No hay espacio suficiente para descargar la app")
        
    def borrar_app(self):
        """
        Permite borrar una aplicación no esencial y liberar su espacio.
        Muestra la lista de apps instaladas y permite seleccionar cuál borrar.
        """
        apps_borrables = {nombre: app for nombre, app in self.dispositivo.apps.items() 
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
        del self.dispositivo.apps[app]
        self.dispositivo.almacenamiento_ocupado -= espacio_liberado
        print(f"App '{app}' borrada exitosamente. Se liberaron {espacio_liberado:.1f}GB")
        
    def menu(self):
        menu_appstore=True
        while menu_appstore:
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
                print("\nApps instaladas: " + ", ".join(self.dispositivo.apps.keys()) + ".")
            elif opcion == "4":
                menu_appstore=False
            else:
                print("Opción inválida")
    

class Configuracion(Aplicacion):
    """
    Aplicación para configurar aspectos del sistema del dispositivo.
    
    Permite gestionar configuraciones básicas como el código de desbloqueo,
    la red móvil y otras opciones del sistema.

    Attributes:
        dispositivo (dispositivo): Referencia al dispositivo que contiene la aplicación
    """
    def __init__(self, dispositivo: Dispositivo):
        super().__init__(dispositivo)
        self.almacenamiento=1.5
        self.dispositivo.almacenamiento_ocupado+=self.almacenamiento
        self.necesaria = True
        
    def cambiar_codigo(self):
        """Cambia el código de desbloqueo del dispositivo"""
        if self.dispositivo.codigo is None:
            try:
                nuevo_codigo = int(input('Ingrese el nuevo código: '))
                self.dispositivo.codigo = nuevo_codigo
                print("Código establecido exitosamente")
                return
            except ValueError:
                print("El código debe ser un número")
                
        if self.dispositivo.codigo == int(input('Ingrese el código actual: ')):
            try:
                nuevo_codigo = int(input('Ingrese el nuevo código: '))
                self.dispositivo.codigo = nuevo_codigo
                print("Código cambiado exitosamente")
                return
            except ValueError:
                print("El código debe ser un número")
        else:
            print("Código incorrecto")
        

    def validar_almacenamiento(self, almacenamiento_requerido: float):
        """
        Valida si hay suficiente almacenamiento disponible para instalar una nueva aplicación.
        Si no hay espacio suficiente, muestra un mensaje de error.

        Args:
            almacenamiento_requerido (float): Cantidad de almacenamiento en GB que requiere la aplicación

        Returns:
            bool: True si hay suficiente espacio disponible, False en caso contrario
        """
        return self.dispositivo.almacenamiento - self.dispositivo.almacenamiento_ocupado >= almacenamiento_requerido
    
    def toggle_datos_moviles(self):
        """
        Alterna el estado de los datos móviles del dispositivo.
        Si se activan los datos, actualiza la bandeja de email.
        Muestra un mensaje indicando el nuevo estado.
        """
        self.dispositivo.datos_moviles = not self.dispositivo.datos_moviles
        estado = "activados" if self.dispositivo.datos_moviles else "desactivados"
        if self.dispositivo.datos_moviles:
            self.dispositivo.apps['email'].actualizar_bandeja()
        print(f"Datos móviles {estado}")

    def menu(self):
        menu_configuracion=True
        while menu_configuracion:
            opcion = input("""
CONFIGURACIÓN
1. Cambiar código de desbloqueo
2. Activar/Desactivar datos móviles
3. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.cambiar_codigo()
            elif opcion == "2":
                self.toggle_datos_moviles()            
            elif opcion == "3":
                menu_configuracion=False
            else:
                print("Opción inválida")

class Configuracion_Celular(Configuracion):
    def __init__(self, dispositivo: Dispositivo):
        super().__init__(dispositivo)
        
    def activar_red_movil(self):
        """
        Activa la red móvil del dispositivo y actualiza la bandeja de SMS.
        
        Si la red ya está activada, muestra un mensaje.
        Si el dispositivo no está registrado en la central, muestra un error.
        """
        if self.dispositivo.red_movil:
            print('La red movil ya esta activada')
        else:   
            if self.dispositivo.num_telefonico in self.dispositivo.central.dispositivos_registrados:
                self.dispositivo.red_movil = True
                self.dispositivo.apps['sms'].actualizar_bandeja()
                print("Red móvil activada")
            else:
                print('Tu dispositivo no esta registrado en la central. No podes activar la red movil')
                
    def desactivar_red_movil(self):
        """
        Desactiva la red móvil del dispositivo.
        
        Si hay una llamada activa, la termina antes de desactivar la red.
        Establece el estado de red_movil en False y muestra un mensaje de confirmación.
        """
        if self.dispositivo.llamada_actual:
            self.dispositivo.apps['telefono'].terminar_llamada()
        self.dispositivo.red_movil = False
        print("Red móvil desactivada")
        
    def toggle_disponibilidad(self):
        """
        Alterna el estado de disponibilidad del dispositivo para recibir llamadas.
        
        Cambia el estado de disponible a no disponible o viceversa.
        Muestra un mensaje indicando el nuevo estado.
        """
        self.dispositivo.disponible = not self.dispositivo.disponible
        estado = "disponible" if self.dispositivo.disponible else "no disponible"
        print(f"El dispositivo ahora está {estado} para recibir llamadas")

    def toggle_datos_moviles(self):
        """
        Alterna el estado de los datos móviles del dispositivo.
        
        Si la red móvil está desactivada, muestra un error.
        De lo contrario, cambia el estado de datos_moviles a su opuesto.
        Si se activan los datos, actualiza la bandeja de email.
        Muestra un mensaje indicando el nuevo estado.
        """
        if not self.dispositivo.red_movil:
            print("Error: Primero debe activar la red móvil")
            return
            
        self.dispositivo.datos_moviles = not self.dispositivo.datos_moviles
        estado = "activados" if self.dispositivo.datos_moviles else "desactivados"
        if self.dispositivo.datos_moviles:
            self.dispositivo.apps['email'].actualizar_bandeja()
        print(f"Datos móviles {estado}")
        
    def menu(self):
        menu_configuracion=True
        while menu_configuracion:
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
                menu_configuracion=False
            else:
                print("Opción inválida")
                
                
class Configuracion_Celular_Viejo(Configuracion):
    def __init__(self, dispositivo: Dispositivo):
        super().__init__(dispositivo)
        
    def activar_red_movil(self):
        """
        Activa la red móvil del dispositivo y actualiza la bandeja de SMS.
        
        Si la red ya está activada, muestra un mensaje.
        Si el dispositivo no está registrado en la central, muestra un error.
        """
        if self.dispositivo.red_movil:
            print('La red movil ya esta activada')
        else:   
            if self.dispositivo.num_telefonico in self.dispositivo.central.dispositivos_registrados:
                self.dispositivo.red_movil = True
                self.dispositivo.apps['sms'].actualizar_bandeja()
                print("Red móvil activada")
            else:
                print('Tu dispositivo no esta registrado en la central. No podes activar la red movil')
                
    def desactivar_red_movil(self):
        """
        Desactiva la red móvil del dispositivo.
        
        Si hay una llamada activa, la termina antes de desactivar la red.
        Establece el estado de red_movil en False y muestra un mensaje de confirmación.
        """
        if self.dispositivo.llamada_actual:
            self.dispositivo.apps['telefono'].terminar_llamada()
        self.dispositivo.red_movil = False
        print("Red móvil desactivada")
        
    def toggle_disponibilidad(self):
        """
        Alterna el estado de disponibilidad del dispositivo para recibir llamadas.
        
        Cambia el estado de disponible a no disponible o viceversa.
        Muestra un mensaje indicando el nuevo estado.
        """
        self.dispositivo.disponible = not self.dispositivo.disponible
        estado = "disponible" if self.dispositivo.disponible else "no disponible"
        print(f"El dispositivo ahora está {estado} para recibir llamadas")

        
    def menu(self):
        menu_configuracion=True
        while menu_configuracion:
            opcion = input("""
CONFIGURACIÓN
1. Cambiar código de desbloqueo
2. Activar red móvil
3. Desactivar red móvil
4. Cambiar disponibilidad para llamadas
5. Volver

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
                menu_configuracion=False
            else:
                print("Opción inválida")

class Notas(Aplicacion):
    """
    Aplicación para gestionar notas usando una Lista Enlazada.
    Las notas editadas se mueven al inicio de la lista.
    """
    def __init__(self, dispositivo):
        super().__init__(dispositivo)
        self.notas = ListaEnlazada() # Lista de notas
        self.almacenamiento = 0.3
        self.dispositivo.almacenamiento_ocupado += self.almacenamiento 
        self.necesaria = True
        
    def agregar_nota(self):
        """Agrega una nueva nota al inicio de la lista"""
        titulo = input("\nIngrese título de la nota: ").strip() 
        contenido = input("Ingrese contenido de la nota: ").strip()
        
        if not titulo or not contenido:
            print("\nEl título y contenido no pueden estar vacíos")
            return
            
        # Crea una nota con el título y contenido ingresados en formato diccionario
        nota = {"titulo": titulo, "contenido": contenido}
        nuevo_nodo = Nodo(nota) # Crea un nodo con la nota
        self.notas.agregarInicio(nuevo_nodo) # Agrega la nota al inicio de la lista
        print("\nNota agregada exitosamente")
        
    def ver_notas(self):
        """Muestra todas las notas almacenadas"""
        if self.notas.esVacia():
            print("\nNo hay notas guardadas")
            return False
            
        print("\nNotas guardadas:")
        actual = self.notas.inicio
        i = 1
        while actual:
            nota = actual.dato
            print(f"\n{i}. {nota['titulo']}")
            # Muestra el contenido de la nota, limitado a 50 caracteres para que no se vea muy largo
            print(f"   {nota['contenido'][:50]}...")
            actual = actual.siguiente
            i += 1
        return True
        
    def editar_nota(self):
        """Edita una nota existente y la mueve al inicio"""
        if not self.ver_notas(): # Si no hay notas, muestra un mensaje y termina la función
            return
            
        try:
            # Solicita al usuario que ingrese el número de la nota a editar
            opcion = int(input("\nIngrese el número de la nota a editar: "))
            if opcion < 1 or opcion > self.notas.tamanio:
                print("\nNúmero de nota inválido")
                return
                
            nodo = self.notas.obtener_nodo(opcion - 1)
            if nodo == "Posición inválida": # Si el nodo no existe, muestra un mensaje y termina la función
                print("\nError al acceder a la nota")
                return
                
            print(f"\nEditando nota: {nodo.dato['titulo']}")
            print(f"Contenido actual:\n{nodo.dato['contenido']}\n")
            
            modo_edicion = input("¿Desea continuar escribiendo (c) o sobrescribir (s)? ").lower()
            
            if modo_edicion == 'c':
                # Continuar escribiendo
                nuevo_contenido = input("Ingrese el texto adicional: ").strip()
                if nuevo_contenido:
                    contenido_actualizado = f"{nodo.dato['contenido']}\n{nuevo_contenido}"
                    nota_actualizada = {
                        "titulo": nodo.dato['titulo'],
                        "contenido": contenido_actualizado
                    }
                    self.notas.eliminarPosicion(opcion - 1)
                    self.notas.agregarInicio(Nodo(nota_actualizada))
                    print("\nNota actualizada y movida al inicio")
                else:
                    print("\nNota sin cambios")
                    
            elif modo_edicion == 's':
                # Sobrescribir
                nuevo_contenido = input("Ingrese nuevo contenido: ").strip()
                if nuevo_contenido:
                    nota_actualizada = {
                        "titulo": nodo.dato['titulo'],
                        "contenido": nuevo_contenido
                    }
                    self.notas.eliminarPosicion(opcion - 1)
                    self.notas.agregarInicio(Nodo(nota_actualizada))
                    print("\nNota editada y movida al inicio")
                else:
                    print("\nNota sin cambios")
            else:
                print("\nOpción inválida")
            
        except ValueError:
            print("\nDebe ingresar un número válido")
            
    def imprimir_nota(self):
        """Exporta una nota a un archivo txt"""
        if not self.ver_notas():
            return
            
        try:
            opcion = int(input("\nIngrese el número de la nota a imprimir: "))
            if opcion < 1 or opcion > self.notas.tamanio:
                print("\nNúmero de nota inválido")
                return
                
            nodo = self.notas.obtener_nodo(opcion - 1)
            if nodo == "Posición inválida":
                print("\nError al acceder a la nota")
                return
                
            nota = nodo.dato
            nombre_archivo = f"nota_{nota['titulo']}.txt"
            
            with open(nombre_archivo, 'w') as f:
                f.write(f"Título: {nota['titulo']}\n\n")
                f.write(nota['contenido'])
                
            print(f"\nNota exportada a {nombre_archivo}")
            
        except ValueError:
            print("\nDebe ingresar un número válido")
        except Exception as e:
            print(f"\nError al exportar la nota: {str(e)}")
            
    def menu(self):
        """Menú principal de la aplicación"""
        menu_notas=True
        while menu_notas:
            opcion = input("""
NOTAS
1. Ver notas
2. Agregar nota
3. Editar nota
4. Imprimir nota
5. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.ver_notas()
            elif opcion == "2":
                self.agregar_nota()
            elif opcion == "3":
                self.editar_nota()
            elif opcion == "4":
                self.imprimir_nota()
            elif opcion == "5":
                menu_notas=False
            else:
                print("Opción inválida")