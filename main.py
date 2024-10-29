from clase_central import Central, Comunicacion

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
        #self.en_red = False
        self.red_movil=False

        # Se encuentra disponible para la llamada
        self.disponible = True
        
        #primero se inicializa la app de contactos
        contactos = Contactos()
        
        #creamos un diccionario para reflejar cada aplicacion y poder identificarla por su nombre
        #la app contactos ya fue creada para poder ser pasada como argumento
        self.apps={"contactos": contactos,
                   "sms": SMS(contactos, self), 
                   "email": Email(),
                   "telefono": Telefono(contactos, self),
                   'app store': App_Store(self), #accede al celular para modificar las apps dentro
                    'configuracion': Configuracion(self) #accede a toda la configuracion del celular
                   }

    @classmethod    
    def enceder_apagar(self, cls):

        self.encendido = not self.encendido
        if self.encendido:
            print("El celular se ha prendido")

        else:
            #ACA deberia DESCONECTAR CON LA CENTRAL
            cls.central.baja_dispositivo(self)
            self.red_movil = False
            self.desbloqueado = False
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
        aplicacion=input(f"Que aplicacicion desea abrir: {self.apps.keys}")
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
    def __init__ (self):
        pass

    


class Contactos(Aplicacion):
    def __init__(self):
        self.lista_de_contactos={}
    
    def agendar(self,celular: Celular):
        #tanto para modificar como para agregar contactos, se usa el mismo key por ende es la misma funcionalidad que reemplaza el value
        self.lista_de_contactos[celular.nombre]=celular
        

class SMS(Aplicacion):
    def __init__(self, contactos: Contactos, celular: Celular):
        self.bandeja_sms=[] #pila para ver cual llega primero 
        self.contactos=contactos
        self.celular = celular
        pass
        
    def enviar_mensaje(self, receptor: str, mensaje: str):

        # Valida el estado desde el propio celular emisor
        if self.celular.validar_estado_emisor():
            self.celular.central.comunicacion_sms(self, receptor, mensaje)
        
    def recibir_mensaje(self, emisor: str, mensaje: str):
        #agregar mensaje a pila
        pass

    def ver_bandeja_sms(self):
        pass 
    
    def eliminar_mensajes(self):
        pass

    
    


    
class Telefono(Aplicacion):
    def __init__(self, contactos, celular: Celular):
        self.historial_llamadas=[] #Cola para ver cual llega primero 
        self.en_llamada=False #se activa si estas en llamada, no podes estar en dos llamadas al mismo tiempo
        self.contactos=contactos
        self.celular = celular
    

    def llamar(self):
        pass
    
    def recibir_llamada(self, emisor: str):

        # Si el celular no esta en llamada se le pide aceptar o rechazar la llamada
        if self.celular.disponible:
            eleccion = input(f'El numero {emisor} te esta llamando. Desea aceptar la llamada? (si/no)')
            if eleccion == 'si':
                return True
            else:
                return False
        # Se agrega al historial de llamadas como llamada perdida
        else:
            self.agregar_historial_llamadas(Comunicacion())


    def terminar_llamada(self):
        pass 
    
    def ver_historial_llamadas(self):
        pass

    def agregar_historial_llamadas(self):
        pass
    
    

class Email(Aplicacion):
    def __init__(self):
        self.bandeja_email=[] #pila
        
    def ver_bandeja_mails(self,filtrar_leido=False):
        pass
        
class App_Store(Aplicacion):
    def __init__(self,celular):
        self.celular=celular
        
    def descargar_app(self):
        self.celular.apps[input("Que app quiere descargar?")] = Aplicacion() 
        #faltan validaciones
    

class Configuracion(Aplicacion):
    def __init__(self, celular: Celular):
        self.celular=celular

    def cambiar_nombre(self,nuevo_nombre: str):
        self.celular.nombre=nuevo_nombre
        
    def cambiar_codigo(self,nuevo_codigo: int):
        if self.celular.codigo == None or self.celular.codigo == int(input('ingrese el codigo actual: ')): #chequear
            self.celular.codigo=nuevo_codigo
        
    def activar_red_movil(self):
        #desactiva la red movil y manda la actualizacion a la central
        self.celular.central.alta_dispositivo(self)
        self.celular.red_movil = False
    
    def desactivar_red_movil(self):
        self.celular.central.baja_dispositivo(self)
        self.celular.red_movil = False
        
    def toggle_disponibilidad(self):
        self.celular.disponible = not self.celular.disponible

    #datos moviles: wifi para el mail
    def datos(self):
        pass

