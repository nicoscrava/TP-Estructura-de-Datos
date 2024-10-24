class Celular:
    
    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico) :
        #falta agregar validadores
        self.identificacion=identificacion 
        self.nombre=nombre
        self.modelo=modelo
        self.sistema_operativo=sistema_operativo
        self.version=version
        self.RAM=RAM
        self.almacenamiento=almacenamiento
        self.num_telefonico=num_telefonico
        self.encendido = False #indica si esta encendido o apagado
        self.desbloqueado=False #indica si esta desbloqueado el celular
        self.codigo=None
        
        contactos = Contactos()
        
        #creamos un diccionario para reflejar cada aplicacion y poder identificarla por su nombre
        self.apps={"contactos": contactos,
                   "sms": SMS(contactos), 
                   "email": Email(),
                   "telefono": Telefono(contactos),
                   'app store': App_Store(self), #accede al celular para modificar las apps dentro
                    'configuracion': Configuracion(self) #accede a toda la configuracion del celular
                   }
        
    def enceder_apagar(self,cls):
        self.encendido = not self.encendido
        if self.encendido:
            #una vez encendido, se agrega el celular a la red
            self.red_movil=True
            #ACA deberia CONECTAR CON LA CENTRAL
            print("El celular se ha prendido")
        else:
            #una vez apagado, se elimina de la red
            self.red_movil=False
            #ACA deberia CONECTAR CON LA CENTRAL
            print("Has apagado el celular")
        
    def bloq_desbloq(self):
        self.desbloqueado= not self.desbloqueado
        #
        if self.desbloqueado:
            print("El celular se ha desbloqueado")
        else:
            print("Has bloqueado el celular")
            
        
    def abrir_app(self):
        aplicacion=input(f"Que aplicacicion desea abrir: {self.apps.keys}")
        self.apps[aplicacion].abrir()
        
    
        
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
    def __init__(self,contactos):
        self.bandeja_sms=[] #pila para ver cual llega primero 
        self.contactos=contactos
        pass
    
   
        
    def enviar_mensaje(self,receptor: str):
        pass 
    
    def ver_bandeja_sms(self):
        pass 
    
    def eliminar_mensajes(self):
        pass
    
        
    
    
class Telefono(Aplicacion):
    def __init__(self,contactos):
        self.historial_llamadas=[] #Cola para ver cual llega primero 
        self.en_llamada=False #se activa si estas en llamada, no podes estar en dos llamadas al mismo tiempo
        self.contactos=contactos
    

    def llamar(self):
        pass
    
    def recibir_llamado(self):
        pass
    
    def terminar_llamada(self):
        pass 
    
    def ver_historial_llamadas(self):
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
    def __init__(self,celular):
        self.celular=celular

    def cambiar_nombre(self,nuevo_nombre: str):
        self.celular.nombre=nuevo_nombre
        
    def cambiar_codigo(self,nuevo_codigo: int):
        if self.celular.codigo == None or self.celular.codigo == int(input('ingrese el codigo actual: ')): #chequear
            self.celular.codigo=nuevo_codigo
            
    def activar_red_movil(self):
        pass 
    
    def desactivar_red_movil(self):
        pass
    
    def datos(self):
        pass