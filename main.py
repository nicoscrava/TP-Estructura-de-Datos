class Telefono:
    red_telefonos={}
    
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
        self.desbloqueado=False #indica si esta desbloqueado el telefono
        self.red_movil=False #indica si esta en la red
        self.datos_moviles= True #el telefono viene con datos moviles
        
    def enceder_apagar(self,cls):
        self.encendido = not self.encendido
        if self.encendido:
            #una vez encendido, se agrega el telefono a la red
            self.red_movil=True
            cls.red_telefonos[self.num_telefonico]=self #su key va a ser el numero telefonico
            print("El celular se ha prendido")
        else:
            #una vez apagado, se elimina de la red
            self.red_movil=False
            cls.red_telefonos.pop(self.num_telefonico)
            print("Has apagado el celular")
        
    def bloq_desbloq(self):
        self.desbloqueado= not self.desbloqueado
        #
        if self.desbloqueado:
            print("El celular se ha desbloqueado")
        else:
            print("Has bloqueado el celular")
        
    
    def app_telefono(self):
        pass
    
    def app_contactos(self):
        pass
    
    def app_mensajes(self):
        pass
    
    def app_mail(self):
        pass
    
    def app_store(self):
        pass
    
    # hay que agregar la funcionalidad de desactivar la red movil 
    def app_configuracion(self):
        pass
    
    
    
        