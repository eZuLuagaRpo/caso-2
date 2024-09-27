class Authentication:
    def __init__(self, userDataBase):
        self.dataBaseObject = userDataBase
        self.session = False
    
    def login (self, user, password):

        if not(isinstance(user,str)) or not(isinstance(password,str)):
            raise ValueError("El usuario y/o la contraseña deben ser str.")

        if self.dataBaseObject.connection() != "Success":
            print("Error al conectar la base de datos.")
            return False
        
        if self.session == True:
            print("Ya hay una sesión activa.")
            return True
        
        db = self.dataBaseObject.db()

        if user in db and db[user] == password:
            self.session = True
            return True
        else:
            print("Usuario y/o contraseña inválidos.")
            return False
    
    def logout (self):
        self.session = False
        print("Sesión cerrada con éxito.")
    
    def getSession(self):
        return self.session

        

        