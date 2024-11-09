class Nodo:
    def __init__(self,dato):
        self.dato = dato
        self.siguiente = None
        
    def __str__(self):
        return f'{self.dato}'
    

class ListaEnlazada():
    def __init__(self,inicio=None):
        self.inicio=inicio
        self.tamanio = 0

    def esVacia(self):
        return self.inicio==None
    
    def agregarInicio(self,nodo:Nodo):
        if self.esVacia():
            self.inicio=nodo
        else:
            nodo.siguiente=self.inicio
            self.inicio=nodo
        self.tamanio += 1
            
    def agregarFinal(self,nodo:Nodo):
        if self.esVacia():
            self.inicio=nodo
        else:
            aux=self.inicio
            while aux.siguiente!=None:
                aux=aux.siguiente
            aux.siguiente=nodo
        self.tamanio += 1
    
    def pop(self):
        if self.esVacia():
            return 'No se puede eliminar el primer dato'
        else:
            dato=self.inicio.dato
            self.inicio=self.inicio.siguiente
            self.tamanio -= 1
            return f'se elimino {dato}'
        
    def __str__(self):
        cadena=''
        aux=self.inicio
        while aux!=None:
            cadena+=str(aux.dato)+' '
            aux=aux.siguiente
        return cadena
    
    def eliminarPosicion(self, posicion):
        if posicion < 0 or posicion >= self.tamanio:
            return "Posición inválida"
            
        if self.inicio is None:
            return
            
        if posicion == 0:
            self.inicio = self.inicio.siguiente
            self.tamanio -= 1
            return
            
        actual = self.inicio
        for i in range(posicion - 1):
            if actual is None:
                return
            actual = actual.siguiente
            
        if actual is None or actual.siguiente is None:
            return
            
        actual.siguiente = actual.siguiente.siguiente
        self.tamanio -= 1

    def obtener_nodo(self, posicion):
        if posicion < 0 or posicion >= self.tamanio:
            return "Posición inválida"
        actual = self.inicio
        for i in range(posicion):
            actual = actual.siguiente
        return actual   
