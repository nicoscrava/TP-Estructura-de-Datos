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
        
    def validar_usuario(self, emisor: str, receptor: str):
        if receptor not in self.usuarios_registrados:
            print (f"La direccion de mail {receptor} no se encuentra registrada.")
            return False 
        
        elif receptor in self.usuarios_registrados[emisor].celular.apps["email"].casillas_bloqueadas:
            print ("El celular al que intentas enviarle un mensaje se encuentra bloqueado por ti.")
            return False 
        
        elif emisor in self.usuarios_registrados[receptor].celular.apps["email"].casillas_bloqueadas:
            print ("La casilla a la que le intentas enviar un email te ha bloqueado.")
            
        else: 
            return True
    
    def enviar_mail(self, mail: Email) :
        if self.validar_usuario(mail.emisor, mail.destinatario):
            self.usuarios_registrados[mail.destinatario].celular.apps["email"].recibir_mail(mail)
            self.registro_mails.append(mail)
            print("Email enviado exitosamente")
            
                