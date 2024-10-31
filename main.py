from clase_central import Central, Comunicacion
from collections import deque
from listaenlazada import *


class Celular:
    
    central = Central()

    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico) :
        
        #atributos bases
        #falta agregar validadores
        self.identificacion=identificacion 
        self.nombre=nombre
        self.modelo=modelo
        self.sistema_operativo=sistema_operativo
        self.version=version
        self.RAM=RAM
        self.almacenamiento=almacenamiento
        self.num_telefonico=num_telefonico

        #atributos adicionales
        self.encendido = False #indica si esta encendido o apagado
        self.desbloqueado=False #indica si esta desbloqueado el celular
        self.codigo=None
        self.red_movil=False

        # Se encuentra disponible para la llamada
        self.disponible = True

        # Contiene el numero con el cual se esta en llamada
        self.llamada_actual = None
        
        #primero se inicializa la app de contactos
        contactos = Contactos(self)
        
        #creamos un diccionario para reflejar cada aplicacion y poder identificarla por su nombre
        #la app contactos ya fue creada para poder ser pasada como argumento
        self.apps={"contactos": contactos,
                   "sms": SMS(self, contactos), 
                   "email": Email(self),
                   "telefono": Telefono(self, contactos),
                   'app store': App_Store(self), #accede al celular para modificar las apps dentro
                    'configuracion': Configuracion(self) #accede a toda la configuracion del celular
                   }
    
    def encender_apagar(self):

        self.encendido = not self.encendido
        if self.encendido:
            self.apps['configuracion'].activar_red_movil()
            print("El celular se ha prendido")

        else:
            #ACA deberia DESCONECTAR CON LA CENTRAL
            self.red_movil = False
            self.desbloqueado = False
            if self.llamada_actual != None:
                
                self.apps['telefono'].terminar_llamada() # Se termina la llamada en curso en el caso de existir
            print("Has apagado el celular")

    #agregar contrasenia    
    def bloq_desbloq(self):
        self.desbloqueado= not self.desbloqueado
        if self.desbloqueado:
            print("El celular se ha desbloqueado")
        else:
            print("Has bloqueado el celular")
               
    def abrir_app(self):
        aplicacion=input(f"Que aplicacicion desea abrir: {self.apps.keys()}")
        self.apps[aplicacion].menu()

    def validar_estado_emisor(self):

        if self.red_movil == False:
            print('Tu celular no puede enviar mensajes. Activa la red movil.')
            return False
        
        # Verifica que el celular emisor este registrado en la red
        elif self.num_telefonico not in self.central.dispositivos_registrados:
            print('Tu celular no se encuentra en la red.')
            return False
        
        else:
            return True


class Aplicacion():

    def __init__ (self, celular: Celular):
        self.celular = celular


class Contactos(Aplicacion):

    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.lista_de_contactos={}
    
    def agendar(self, numero: str, nombre: str):
        #tanto para modificar como para agregar contactos, se usa el mismo key por ende es la misma funcionalidad que reemplaza el value
        self.lista_de_contactos[numero]=nombre
        

class SMS(Aplicacion):
    def __init__(self, celular: Celular, contactos: Contactos):
        super().__init__(celular)
        self.bandeja_sms= ListaEnlazada() #lista enlazada 
        self.contactos=contactos
        self.mensajes_en_espera = deque() # Mensajes que te llegaron cuando no tenias la red movil activa
        
        
    def enviar_mensaje(self, receptor: str, mensaje: str):

        # Si el argumento esta en el diccionario de contactos, se extrae el numero.
        # En otro caso, se le puede pasar como argumento el numero telefonico directamente
        if receptor in self.celular.apps['contactos'].lista_de_contactos:
            receptor = self.celular.apps['contactos'].lista_de_contactos[receptor]
        
        # Valida el estado desde la central
        self.celular.central.comunicacion_sms(self.celular, receptor, mensaje)
        
    def recibir_mensaje(self, mensaje: Comunicacion):
        self.bandeja_sms.agregarInicio(Nodo(mensaje))
        

    def actualizar_bandeja(self):
        print(f'Tenes {len(self.mensajes_en_espera)} mensajes nuevos. ')
        while self.mensajes_en_espera:
            self.bandeja_sms.agregarInicio(Nodo(self.mensajes_en_espera.popleft()))

    def ver_bandeja_sms(self):
        print(self.bandeja_sms)
    
    def eliminar_mensajes(self):
        pass

   
class Telefono(Aplicacion):
    def __init__(self, celular: Celular, contactos):
        super().__init__(celular)
        self.historial_llamadas=deque() #Pila para ver cual llega primero 
        self.en_llamada=False #se activa si estas en llamada, no podes estar en dos llamadas al mismo tiempo
        self.contactos=contactos
    
    def llamar(self, receptor: str):

        # Si el argumento esta en el diccionario de contactos, se extrae el numero.
        # En otro caso, se le puede pasar como argumento el numero telefonico directamente
        if receptor in self.celular.apps['contactos'].lista_de_contactos:
            receptor = self.celular.apps['contactos'].lista_de_contactos[receptor]

        self.celular.central.comunicacion_telefonica(self, receptor)
    
    def recibir_llamada(self, comunicacion: Comunicacion):

        # Si el celular no esta en llamada se le pide aceptar o rechazar la llamada
        
        if self.celular.disponible:
            eleccion = input(f'El numero {comunicacion.emisor.num_telefonico} te esta llamando. Desea aceptar la llamada? (si/no)')
            if eleccion == 'si':
                self.celular.disponible = False
                self.celular.llamada_actual = comunicacion
                return True
            else:
                return False
        # Se agrega al historial de llamadas como llamada perdida
        else:
            self.agregar_historial_llamadas(Comunicacion())

    def terminar_llamada(self):
        if self.disponible == False:
            self.celular.central.terminar_comunicacion_telefonica(self.celular.llamada_actual)

            print('Llamada finalizada. ')

    
    def ver_historial_llamadas(self):
        pass

    def agregar_historial_llamadas(self):
        pass
    
    
class Email(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)

        self.bandeja_email=[] #pila
        
    def ver_bandeja_mails(self, filtrar_leido=False):
        pass

     
class App_Store(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        
    def descargar_app(self):
        self.celular.apps[input("Que app quiere descargar?")] = Aplicacion() 
        #faltan validaciones
    

class Configuracion(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)

    def cambiar_nombre(self,nuevo_nombre: str):
        self.celular.nombre=nuevo_nombre
        
    def cambiar_codigo(self,nuevo_codigo: int):
        if self.celular.codigo == None or self.celular.codigo == int(input('ingrese el codigo actual: ')): #chequear
            self.celular.codigo=nuevo_codigo
        
    def activar_red_movil(self):
        #desactiva la red movil y manda la actualizacion a la central
        if self.celular.num_telefonico in self.celular.central.dispositivos_registrados:
            self.celular.red_movil = True
            self.celular.apps['sms'].actualizar_bandeja()
        else:
            print('Tu celular no esta registrado en la central. No podes activar datos')
    
    def desactivar_red_movil(self):
        self.celular.apps['telefono'].terminar_llamada()
        self.celular.red_movil = False
        
        
    def toggle_disponibilidad(self):
        self.celular.disponible = not self.celular.disponible

    #datos moviles: wifi para el mail
    def datos(self):
        pass

