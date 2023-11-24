# main.py
import os
from database import init_db, create_admin_user, update_admin_password,add_user
import gui  # Asegúrate de que el archivo gui.py esté en el mismo directorio

def main():
    # Inicializa la base de datos y crea el usuario admin si no existe
    init_db()

    # add_user('','')
    #create_admin_user()
    
    #update_admin_password() #Si quieres modificar la contraseña primero tendras que acceder a database.py y actualizarla ahi en la funcion.
    
    # Luego, la interfaz gráfica de usuario (GUI) se inicia
    gui.root.mainloop()

if __name__ == "__main__":
    main()  