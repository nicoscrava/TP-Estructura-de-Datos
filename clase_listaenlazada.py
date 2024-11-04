
class Nodo:
    def __init__(self,dato):
        self.dato = dato
        self.siguiente = None
        
    def __str__(self):
        return f'{self.dato}'
    

class ListaEnlazada():
    def __init__(self,inicio=None):
        self.inicio=inicio

    def esVacia(self):
        return self.inicio==None
    
    def agregarInicio(self,nodo:Nodo):
        if self.esVacia():
            self.inicio=nodo
        else:
            nodo.siguiente=self.inicio
            self.inicio=nodo
            
    def agregarFinal(self,nodo:Nodo):
        if self.esVacia():
            self.inicio=nodo
        else:
            aux=self.inicio
            while aux.siguiente!=None:
                aux=aux.siguiente
            aux.siguiente=nodo
    
    def pop(self):
        if self.esVacia():
            return 'No se puede eliminar el primer dato'
        else:
            dato=self.inicio.dato
            self.inicio=self.inicio.siguiente
            return f'se elimino {dato}'
        
    def __str__(self):
        cadena=''
        aux=self.inicio
        while aux!=None:
            cadena+=str(aux.dato)+' '
            aux=aux.siguiente
        return cadena
    
    def eliminarPosicion(self, posicion):
        """Elimina el nodo en la posición indicada"""
        if self.inicio is None:  # Lista vacía
            return
            
        if posicion == 0:  # Eliminar el primer elemento
            self.inicio = self.inicio.siguiente
            return
            
        actual = self.inicio
        for i in range(posicion - 1):  # Nos movemos hasta el nodo anterior al que queremos eliminar
            if actual is None:
                return
            actual = actual.siguiente
            
        if actual is None or actual.siguiente is None:  # Si llegamos al final
            return
            
        actual.siguiente = actual.siguiente.siguiente  # "Saltamos" el nodo a eliminar