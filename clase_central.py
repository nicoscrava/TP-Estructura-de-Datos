from main import Celular

class Central:

    def __init__(self):
        self.dispositivos_registrados = {}
        self.registro_comunicaciones = [] #revisar tipo de dato

    def alta_dispositivo(self, celular: Celular):
        self.dispositivos_registrados[celular.num_telefonico] = celular

    def baja_dispositivo(self, celular: Celular):
        try:
            del self.dispositivos_registrados[celular.num_telefonico]
        except KeyError:
            print(f'El telefono con numero {celular.num_telefonico} no se encuentra en la red.')
    
    def comunicacion_sms(self, emisor: Celular, receptor: Celular):
        # la validacion para la emision del mensaje se realiza desde el ceular emisor mismo
        if not (receptor.num_telefonico in self.dispositivos_registrados):
            print(f'El numero {receptor.num_telefonico} esta fuera de servicio.')
        if receptor.disponible == False:
            print(f'El numero {receptor.num_telefonico} no se encuentra disponible.')
        