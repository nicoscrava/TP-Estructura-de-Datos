from datetime import datetime
from clase_celular import Celular

class Email:
    def __init__(self, emisor, destinatario, asunto, cuerpo):
        self.emisor = emisor
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.fecha = datetime.now()
        self.leido = False
        
    def __str__(self):
        estado = "No leído" if not self.leido else "Leído"
        return f"[{estado}] De: {self.emisor} - Asunto: {self.asunto} - Fecha: {self.fecha}"
    

class CentralGmail:
    def __init__(self):
        self.usuarios_registrados={}
        self.registro_mails=[] 
        
    #validar si el usuario existe
    def validar_usuario(self, emisor: str, receptor: str):
        if receptor not in self.usuarios_registrados:
            print (f"La direccion de mail {receptor} no se encuentra registrada.")
            return False 
        #validar si el receptor esta bloqueado por el emisor
        elif receptor in self.usuarios_registrados[emisor].celular.apps["email"].casillas_bloqueadas:
            print ("El celular al que intentas enviarle un mensaje se encuentra bloqueado por ti.")
            return False 
        
        #validar si el emisor esta bloqueado por el receptor
        elif emisor in self.usuarios_registrados[receptor].celular.apps["email"].casillas_bloqueadas:
            print ("La casilla a la que le intentas enviar un email te ha bloqueado.")
            return False
            
        else: 
            return True
    
    def enviar_mail(self, mail: Email) :
        #validar si el usuario existe y si el mail se puede enviar
        if self.validar_usuario(mail.emisor, mail.destinatario):
            #enviar mail
            self.usuarios_registrados[mail.destinatario].celular.apps["email"].recibir_mail(mail)
            #registrar mail enviado
            self.usuarios_registrados[mail.emisor].celular.apps["email"].bandeja_enviados.append(mail)
            #registrar mail
            self.registro_mails.append(mail)
            print("Email enviado exitosamente")
            
                
    def enviar_mail(self, mail: Email):
        try:
            #validar si el usuario existe y si el mail se puede enviar
            if self.validar_usuario(mail.emisor, mail.destinatario):
                #cambio los numeros a objetos
                receptor = self.usuarios_registrados[mail.destinatario]
                emisor = self.usuarios_registrados[mail.emisor]
                
                #enviar mail al receptor
                receptor.celular.apps["email"].recibir_mail(mail)
                #registrar mail enviado en el emisor
                emisor.celular.apps["email"].bandeja_enviados.append(mail)
                #registrar mail en el registro de la central de gmail
                self.registro_mails.append(mail)
                print("Email enviado exitosamente")
                return True
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            return False
