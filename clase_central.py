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
    
    def validar_estado_receptor(self, receptor: Celular, es_llamada=False):

        # la validacion para la emision del mensaje se realiza desde el ceular emisor mismo
        
        # Si el dispositivo receptor no esta registrado en la red se avisa que esta fuera de servicio y devuelve False
        if not (receptor.num_telefonico in self.dispositivos_registrados):
            print(f'El numero {receptor.num_telefonico} esta fuera de servicio.')
            return False
        
        # Si se trata de una llamada y no esta disponible el receptor se avisa y devuelve False
        elif es_llamada and receptor.disponible == False:
            print(f'El numero {receptor.num_telefonico} no se encuentra disponible.')
            return False
        
        # Devuelve True si se puede realizar la comunicacion
        else:
            return True

    def comunicacion_sms(self, emisor: Celular, receptor: str, mensaje: str):

        # Se halla en el diccionario de la red el celular receptor en base a su num telefonico
        celular_receptor = self.dispositivos_registrados[receptor]
        
        # Si el receptor se puede comunicar, el receptor recibe el mensaje y se crea el registro
        if self.validar_estado_receptor(celular_receptor):
            celular_receptor.recibir_mensaje(emisor.num_telefonico, mensaje)
            self.registro_comunicaciones.append(Comunicacion('sms', emisor, receptor, mensaje))

    def comunicacion_telefonica(self, emisor: Celular, receptor: str):

        # Se halla en el diccionario de la red el celular receptor en base a su num telefonico
        celular_receptor = self.dispositivos_registrados[receptor]

        # Si el receptor se puede comunicar se crea la comunicacion 
        if self.validar_estado_receptor(celular_receptor, True):
            comunicacion = Comunicacion('llamada', emisor, receptor)

            # Si se acepta la llamada, se le cambia el atributo llamada_aceptada de la comunicacion
            if celular_receptor.apps['telefono'].recibir_llamada(emisor.num_telefonico):
                comunicacion.llamada_aceptada = True

            # Si rechaza la llamada el atributo llamada_aceptada queda como False
            else:
                print('Llamada rechazada.')

            # Se agrega la comunicacion al registro
            self.registro_comunicaciones.append(comunicacion)
        
class Comunicacion:
    def __init__(self, tipo: str, emisor: Celular, receptor: Celular, contenido=None):
        self.tipo = tipo
        self.emisor = emisor
        self.receptor = receptor
        self.contenido = contenido
        if self.tipo == 'llamada':
            self.llamada_aceptada=False