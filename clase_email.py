from datetime import datetime

class Email:
    def __init__(self, emisor, destinatario, asunto, cuerpo):
        self.emisor = emisor
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.fecha = datetime.now()
        self.leido = False
        
    def __str__(self, vista_emisor=False):
        if not vista_emisor:
            estado = "No leído" if not self.leido else "Leído"
            return f"[{estado}] De: {self.emisor} - Asunto: {self.asunto} - Fecha: {self.fecha}"
        else:
            return f"Para: {self.destinatario} - Asunto: {self.asunto} - Fecha: {self.fecha}"
    

class CentralGmail:
    def __init__(self):
        self.usuarios_registrados = {}
        self.registro_mails = [] 
        
    def validar_usuario(self, emisor: str, receptor: str):
        if receptor not in self.usuarios_registrados:
            print(f"La direccion de mail {receptor} no se encuentra registrada.")
            return False  
        
        elif emisor in self.usuarios_registrados[receptor].apps["email"].casillas_bloqueadas:
            print("La casilla a la que le intentas enviar un email te ha bloqueado.")
            return False
            
        return True

    def enviar_mail(self, mail: Email):
        try:
            if self.validar_usuario(mail.emisor, mail.destinatario):
                receptor = self.usuarios_registrados[mail.destinatario]
                emisor = self.usuarios_registrados[mail.emisor]
                
                if receptor.datos_moviles:
                    receptor.apps["email"].recibir_mensaje(mail)
                else:
                    receptor.apps["email"].en_espera.append(mail)
                
                emisor.apps["email"].bandeja_enviados.append(mail)
                self.registro_mails.append(mail)
                return True
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            return False
