from typing import TYPE_CHECKING
from datetime import datetime
if TYPE_CHECKING:
    from clase_celular import Celular
    


class Comunicacion:
    """
    Clase base para representar una comunicación entre dos dispositivos celulares.

    Attributes:
        emisor (Celular): Dispositivo que inicia la comunicación
        receptor (Celular): Dispositivo que recibe la comunicación
    """
    def __init__(self, emisor: 'Celular', receptor: 'Celular'):
        self.emisor = emisor
        self.receptor = receptor
    

class SMS(Comunicacion):
    """
    Clase que representa un mensaje de texto entre dos dispositivos.

    Attributes:
        emisor (Celular): Dispositivo que envía el mensaje
        receptor (Celular): Dispositivo que recibe el mensaje
        contenido (str): Contenido del mensaje
    """
    def __init__(self, emisor: 'Celular', receptor: 'Celular', contenido: str):
        super().__init__(emisor, receptor)
        self.contenido = contenido

    
    def __str__(self, vista_emisor=False):
        if vista_emisor:
            return f'Mensaje enviado a: {self.emisor.apps["sms"].obtener_nombre_contacto(self.receptor.num_telefonico)}\n Mensaje: {self.contenido}'
        return f'Mensaje de: {self.receptor.apps["sms"].obtener_nombre_contacto(self.emisor.num_telefonico)}\n Mensaje: {self.contenido}'

class Llamada(Comunicacion):
    """
    Clase que representa una llamada telefónica entre dos dispositivos.

    Attributes:
        emisor (Celular): Dispositivo que inicia la llamada
        receptor (Celular): Dispositivo que recibe la llamada
        llamada_aceptada (bool): Indica si la llamada fue aceptada
        llamada_en_transcurso (bool): Indica si la llamada está activa
        fecha_inicio (datetime): Momento en que se inició la llamada
    """
    def __init__(self, emisor: 'Celular', receptor: 'Celular'):
        super().__init__(emisor, receptor)
        self.llamada_aceptada = False
        self.llamada_en_transcurso = False
        self.fecha_inicio = datetime.now()
    
    def __str__(self, vista_emisor=False):
        estado = 'aceptada' if self.llamada_aceptada else 'perdida'
        if vista_emisor:
            return f'Llamada {estado} a {self.receptor.num_telefonico}'
        return f'Llamada {estado} de {self.receptor.apps["telefono"].obtener_nombre_contacto(self.emisor.num_telefonico)}'
    

class Central:
    """
    Clase que gestiona la red de comunicaciones entre dispositivos celulares.

    Attributes:
        dispositivos_registrados (dict): Diccionario de dispositivos registrados. Clave: número de teléfono, valor: objeto Celular
        registro_comunicaciones (list): Historial de todas las comunicaciones
    """

    def __init__(self):
        self.dispositivos_registrados = {}
        self.registro_comunicaciones = []

    
    def generar_informe(self):
        """
        Genera un informe legible de las comunicaciones en informe_comunicaciones.txt
        """
        try:
            with open('informe_comunicaciones.txt', 'w') as archivo:
                if not self.registro_comunicaciones:
                    archivo.write("No hay comunicaciones registradas\n")
                    return
                for comunicacion in self.registro_comunicaciones:
                    if isinstance(comunicacion, SMS):
                        archivo.write(f"SMS de {comunicacion.emisor.num_telefonico} a {comunicacion.receptor.num_telefonico}.\n")
                    elif isinstance(comunicacion, Llamada):
                        estado = "aceptada" if comunicacion.llamada_aceptada else "rechazada"
                        archivo.write(f"Llamada {estado} de {comunicacion.emisor.num_telefonico} a {comunicacion.receptor.num_telefonico}\n")
        except Exception as e:
            print(f"Error al generar el informe: {e}")

    def alta_dispositivo(self, celular: 'Celular'):
        """
        Registra un nuevo dispositivo celular en la central.

        Args:
            celular (Celular): Dispositivo a registrar
        """
        self.dispositivos_registrados[celular.num_telefonico] = celular

    def validar_estado_celular(self, celular: 'Celular', es_emisor, es_llamada=False):
        """
        Valida si un celular está en condiciones de comunicarse.

        Args:
            celular (Celular): Dispositivo a validar
            es_emisor (bool): Indica si el celular es el emisor
            es_llamada (bool): Indica si es una llamada telefónica

        Returns:
            bool: True si el celular está disponible, False en caso contrario
        """
        
        if not celular.red_movil:
            if es_emisor:
                print('Tu celular esta fuera de servicio') 
            return False
        
        
        if es_llamada and not celular.disponible:
            print(f'El numero {celular.num_telefonico} no se encuentra disponible.')
            return False
        
        return True

    def comunicacion_sms(self, celular_emisor: 'Celular', receptor: str, mensaje: str):
        """
        Gestiona el envío de un mensaje SMS entre dos celulares.
        
        Args:
            celular_emisor (Celular): Celular que envía el mensaje
            receptor (str): Número telefónico del receptor
            mensaje (str): Contenido del mensaje a enviar
            
        La función verifica que:
        - El receptor esté registrado en la central
        - Ambos celulares tengan red móvil activa
        
        Si el envío es exitoso:
        - Se crea un objeto SMS y se agrega al historial del receptor
        - Se agrega al registro de comunicaciones de la central
        
        Si el receptor no tiene red móvil:
        - El mensaje queda en espera hasta que active su red
        """
        if receptor not in self.dispositivos_registrados:
            print(f'El número {receptor} no se encuentra registrado en la red.')
            return
        celular_receptor = self.dispositivos_registrados[receptor]
    

        if self.validar_estado_celular(celular_emisor, True):

            comunicacion = SMS(celular_emisor, celular_receptor, mensaje)
            
            if self.validar_estado_celular(celular_receptor, False):
                celular_receptor.apps['sms'].recibir_mensaje(comunicacion)
                self.registro_comunicaciones.append(comunicacion)
                print("\nMensaje enviado exitosamente")
            else:
                celular_receptor.apps['sms'].en_espera.append(comunicacion)
                print(f"\nEl número {receptor} está fuera de servicio.")
                print("Mensaje enviado. El destinatario lo recibirá cuando active su red móvil")

    def comunicacion_telefonica(self, celular_emisor: 'Celular', receptor: str):
        """
        Gestiona una llamada telefónica entre dos celulares.
        
        Args:
            celular_emisor (Celular): Celular que inicia la llamada
            receptor (str): Número telefónico del receptor
            
        La función verifica que:
        - El receptor esté registrado en la central
        - Ambos celulares tengan red móvil activa y estén disponibles
        - El receptor acepte la llamada
        
        Si la llamada es exitosa:
        - Se crea un objeto Llamada y se agrega al historial de ambos celulares
        - Se marca a ambos celulares como no disponibles
        - Se establece la llamada actual en ambos celulares
        
        Si la llamada falla:
        - Se notifica el motivo del fallo
        - Se agrega al registro de comunicaciones
        """
        if receptor not in self.dispositivos_registrados:
            print(f'\nEl número {receptor} no se encuentra registrado en la red.')
            return
            
        celular_receptor = self.dispositivos_registrados[receptor]
        
        
        if not (self.validar_estado_celular(celular_emisor, True, True) and 
                self.validar_estado_celular(celular_receptor, False, True)):
            return
        
        comunicacion = Llamada(celular_emisor, celular_receptor)
        
        
        celular_receptor.apps['telefono'].historial_llamadas.append(comunicacion)
        celular_emisor.apps['telefono'].historial_llamadas.append(comunicacion)

       
        if celular_receptor.apps['telefono'].recibir_llamada(comunicacion):
            comunicacion.llamada_aceptada = True
            comunicacion.llamada_en_transcurso = True
            celular_emisor.disponible = False
            celular_emisor.llamada_actual = comunicacion
            print(f'\nEstas en llamada con {receptor}')
        else:
            print('\nLlamada rechazada.')

        self.registro_comunicaciones.append(comunicacion)

    def terminar_comunicacion_telefonica(self, comunicacion: Llamada):
        """
        Finaliza una llamada telefónica en curso.

        Args:
            comunicacion (Llamada): Objeto de la llamada a terminar
        """
        comunicacion.llamada_en_transcurso = False
        comunicacion.emisor.disponible = True
        comunicacion.receptor.disponible = True
        comunicacion.emisor.llamada_actual = None
        comunicacion.receptor.llamada_actual = None
        
    def ver_dispositivos(self):
        """
        Muestra la lista de dispositivos registrados en la central.

        Returns:
            bool: True si hay dispositivos registrados, False en caso contrario
        """
        
        if not self.dispositivos_registrados:
            print("No hay dispositivos registrados")
            return False
            
        
        print("\nDispositivos registrados:")
        for i, (numero, celular) in enumerate(self.dispositivos_registrados.items(), 1):
            estado_red = "Activada" if celular.red_movil else "Desactivada"
            print(f"{i}. Número: {numero} - Nombre: {celular.nombre} - Red móvil: {estado_red}")
        return True

    def dar_baja_dispositivo(self):
        """
        Permite dar de baja un dispositivo seleccionado por el usuario.
        Muestra la lista de dispositivos y solicita seleccionar uno para eliminar.
        """
        
        if not self.ver_dispositivos():
            return
            
        
        seleccion = input("\nSeleccione el número del dispositivo a dar de baja (0 para cancelar): ")
        if not seleccion.isdigit():
            print("Por favor ingrese un número válido")
            return
        seleccion = int(seleccion)  
        if seleccion == 0:
            return
            
        
        if 1 <= seleccion <= len(self.dispositivos_registrados):
            dispositivo = list(self.dispositivos_registrados.values())[seleccion-1]
            dispositivo.red_movil = False
            del self.dispositivos_registrados[dispositivo.num_telefonico]
            print(f"Dispositivo de {dispositivo.nombre} con numero {dispositivo.num_telefonico} dado de baja exitosamente")
        else:
            print("Selección inválida")

    def menu_admin(self):
        """
        Muestra y gestiona el menú de administración de la central.
        Permite ver dispositivos, generar informes y dar de baja dispositivos.
        """
        while True:
            opcion = input("""
            MENU ADMINISTRADOR
            1. Ver dispositivos registrados
            2. Generar informe de comunicaciones
            3. Dar de baja dispositivo
            4. Volver
            Ingrese una opción: """)

            
            if opcion == "1":
                self.ver_dispositivos()
            elif opcion == "2":
                self.generar_informe()
            elif opcion == "3":
                self.dar_baja_dispositivo()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
