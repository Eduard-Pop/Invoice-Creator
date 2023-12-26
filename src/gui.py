import tkinter as tk
import PySimpleGUI as sg
from tkinter import messagebox, font, ttk
from database import get_db_connection, hash_password,insert_concepto,insert_factura,insert_concepto_presupuesto, insert_presupuesto
from tkinter import simpledialog
import pdfkit
from jinja2 import Environment, FileSystemLoader
from urllib.parse import quote




current_user_id = 1

def login(username, password):
    hashed_password = hash_password(password)
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password)).fetchone()
    conn.close()
    if user:
        return True
    else:
        return False

def attempt_login():
    username = username_entry.get()
    password = password_entry.get()
    if login(username, password):
        open_menu_window()  # Abre la ventana del menú después de un inicio de sesión exitoso
    else:
        messagebox.showerror("Failed", "Usuario/contraseña incorrectos")

def on_enter_key(event):
    attempt_login()
# Configuración de la ventana de inicio de sesión
root = tk.Tk()
root.title("Python: Simple Login Application")
root.geometry("1200x750")  # Tamaño fijo de la ventana
root.bind('<Return>', on_enter_key)

# Configura la imagen de fondo
background_image = tk.PhotoImage(file='images/background.png')
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Configura la fuente
custom_font = font.Font(family="Helvetica", size=16)

# Centrar los campos de usuario y contraseña
frame = tk.Frame(root, bg='white', bd=5)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=200)

# Etiquetas y entradas dentro del frame centrado
username_label = tk.Label(frame, text="Usuario:", font=custom_font)
username_label.grid(row=0, column=0, pady=10)
username_entry = tk.Entry(frame, font=custom_font)
username_entry.grid(row=0, column=1, pady=10)

password_label = tk.Label(frame, text="Contraseña:", font=custom_font)
password_label.grid(row=1, column=0, pady=10)
password_entry = tk.Entry(frame, show="*", font=custom_font)
password_entry.grid(row=1, column=1, pady=10)

# Botón de inicio de sesión
login_button = tk.Button(frame, text="Login", command=attempt_login, font=custom_font)
login_button.grid(row=2, column=1, pady=10)

def open_menu_window():
    # Cierra la ventana de inicio de sesión
    root.destroy()

    # Crea una nueva ventana que sirva como menú principal
    menu_window = tk.Tk()
    menu_window.title("Menú")
    menu_window.geometry("1200x750")  # Tamaño de la ventana del menú

    # Configura la imagen de fondo
    background_image = tk.PhotoImage(file='images/background.png')
    # Importante: Guardar una referencia de la imagen para evitar que sea recolectada por el recolector de basura
    menu_window.background_image = background_image
    background_label = tk.Label(menu_window, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    # Frame para contener y centrar los botones en la pantalla
    button_frame = tk.Frame(menu_window, bg='white', bd=5)
    button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Estilos personalizados
    style = ttk.Style(menu_window)
    style.theme_use('clam')  # Puedes elegir otro tema que se ajuste a tu diseño general
    style.configure('TButton', font=('Helvetica', 12), width=20, padding=10)
    style.map('TButton', foreground=[('active', '!disabled', 'black')], background=[('active', 'grey')])

    # Botones del menú con estilo personalizado
    ttk.Button(button_frame, text="Crear nueva factura", command=lambda: create_invoice(menu_window)).pack(pady=20)
    ttk.Button(button_frame, text="Crear nuevo presupuesto", command=lambda: create_presupuesto(menu_window)).pack(pady=20)
    ttk.Button(button_frame, text="Ver/editar", command=lambda: show_invoices(menu_window)).pack(pady=20)


def create_invoice(menu_window):

    menu_window.withdraw()
    temp_conceptos = []
    
    def add_concepto():
        descripcion = descripcion_entry.get()
        cantidad = cantidad_entry.get()
        precio = precio_entry.get()
        tecnico = tecnico_entry.get()

        if invoice_type.get() == 0:
            tecnico = "1"
        try:
        # Ensure that cantidad and precio can be converted to float for calculation
            total = float(cantidad) * float(precio) * float(tecnico)
        except ValueError:
        # Handle the error if cantidad or precio is not a valid number
            messagebox.showerror("Error", "Cantidad, Precio y Nº Tecnicos deben ser números válidos.")
            return
        temp_conceptos.append((descripcion, cantidad, precio,tecnico, total))

        descripcion_entry.delete(0, tk.END)
        cantidad_entry.delete(0, tk.END)
        precio_entry.delete(0, tk.END)
        if invoice_type.get() == 1:
            tecnico_entry.delete(0, tk.END)

        update_conceptos_treeview()

    def update_conceptos_treeview():
        for i in conceptos_treeview.get_children():
            conceptos_treeview.delete(i)
        for concepto in temp_conceptos:
            formatted_concepto = concepto[:-1] + (f"{concepto[-1]:.2f}",)
            conceptos_treeview.insert('', tk.END, values=formatted_concepto)

    def delete_selected_concepto():
        selected_item = conceptos_treeview.selection()
        if selected_item:  # Verifica si hay algo seleccionado
            selected_index = conceptos_treeview.index(selected_item[0])
            conceptos_treeview.delete(selected_item[0])
            del temp_conceptos[selected_index]  # Elimina usando el índice en temp_conceptos
            update_conceptos_treeview()  # Actualiza el Treeview

    def save_factura():
        nombre_cliente = nombre_cliente_entry.get()
        dni_cliente = dni_cliente_entry.get()
        direccion_cliente = direccion_cliente_entry.get()
        referencia = referencia_entry.get()
        if invoice_type.get() == -1:
            messagebox.showerror("Error", "Por favor, seleccione el tipo de factura antes de guardar.", parent=invoice_window)
            return
        tipo_factura = invoice_type.get()
        id_factura = insert_factura(current_user_id, nombre_cliente, dni_cliente, direccion_cliente,tipo_factura,referencia)
        for concepto in temp_conceptos:
            insert_concepto(id_factura, *concepto[:4])
        # Aquí deberías insertar la lógica para guardar los datos en tu base de datos o archivo
        temp_conceptos.clear()
        messagebox.showinfo("Éxito", "Factura Generada correctamente", parent=invoice_window)
        invoice_window.destroy()
        menu_window.deiconify()
    def handle_invoice_type_change():
        # If 'Factura para Clientes' is selected
        if invoice_type.get() == 0:
            tecnico_entry.delete(0, tk.END)  # Clear the entry
            tecnico_entry.insert(0, "1")  # Set value to 1
            tecnico_entry.pack_forget()
            conceptos_treeview.column('Tecnico', width=0, stretch=False)  # Hide the entry widget
        # If 'Factura para Empresas' is selected
        elif invoice_type.get() == 1:
            tecnico_entry.pack(fill='x')
            conceptos_treeview.column('Tecnico', width=100, stretch=True)

    def return_to_menu():
        menu_window.deiconify()
        invoice_window.destroy()

    invoice_window = tk.Toplevel()
    invoice_window.title("Crear Nueva Factura")
    invoice_window.geometry("900x700")

    style = ttk.Style(invoice_window)
    style.theme_use('clam')

    main_frame = ttk.Frame(invoice_window, padding="10")
    main_frame.pack(expand=True, fill='both')

    left_frame = ttk.Frame(main_frame, padding="10")
    left_frame.pack(side='left', fill='y')

    right_frame = ttk.Frame(main_frame, padding="10")
    right_frame.pack(side='left', fill='both', expand=True)

    # Campos del formulario
    ttk.Label(left_frame, text="Nombre cliente:").pack(fill='x', padx=5, pady=2)
    nombre_cliente_entry = ttk.Entry(left_frame)
    nombre_cliente_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="DNI/NIF:").pack(fill='x', padx=5, pady=2)
    dni_cliente_entry = ttk.Entry(left_frame)
    dni_cliente_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Dirección:").pack(fill='x', padx=5, pady=2)
    direccion_cliente_entry = ttk.Entry(left_frame)
    direccion_cliente_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Referencia(En caso de que sea para empresa):").pack(fill='x', padx=5, pady=2)
    referencia_entry = ttk.Entry(left_frame)
    referencia_entry.pack(fill='x', padx=5, pady=2)


    ttk.Label(left_frame, text="Concepto:").pack(fill='x', padx=5, pady=2)
    descripcion_entry = ttk.Entry(left_frame)
    descripcion_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Cantidad:").pack(fill='x', padx=5, pady=2)
    cantidad_entry = ttk.Entry(left_frame)
    cantidad_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Precio:").pack(fill='x', padx=5, pady=2)
    precio_entry = ttk.Entry(left_frame)
    precio_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Nº Tecnicos (Si la factura es para empresas):").pack(fill='x', padx=5, pady=2)
    tecnico_entry_frame = ttk.Frame(left_frame)
    tecnico_entry_frame.pack(fill='x', padx=5, pady=2)
    tecnico_entry = ttk.Entry(tecnico_entry_frame)


    ttk.Label(left_frame, text="Tipo de Factura:").pack(fill='x', padx=5, pady=2)
    invoice_type = tk.IntVar(value=-1)
    # Radio button for Clients
    ttk.Radiobutton(left_frame, text="Factura para Clientes", variable=invoice_type, value=0, command=handle_invoice_type_change).pack(fill='x', padx=5, pady=2)
    # Radio button for Companies
    ttk.Radiobutton(left_frame, text="Factura para Empresas", variable=invoice_type, value=1, command=handle_invoice_type_change).pack(fill='x', padx=5, pady=2)

    ttk.Button(left_frame, text="Agregar Concepto", command=add_concepto).pack(fill='x', padx=5, pady=2)
    ttk.Button(left_frame, text="Guardar Factura", command=save_factura).pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame).pack(fill='x', padx=5, pady=20)  # Espaciador
    ttk.Button(left_frame, text="Volver al Menú", command=return_to_menu).pack(fill='x', padx=5, pady=2)

    # Lista de conceptos con Treeview
    columns = ('Concepto', 'Cantidad','Precio', 'Tecnico','total')
    conceptos_treeview = ttk.Treeview(right_frame, columns=columns, show='headings')
    for col in columns:
        conceptos_treeview.heading(col, text=col)
        conceptos_treeview.column(col, width=100)
    conceptos_treeview.pack(expand=True, fill='both', padx=8, pady=8)

    ttk.Button(right_frame, text="Eliminar concepto", command=delete_selected_concepto).pack(pady=5)

    invoice_window.protocol("WM_DELETE_WINDOW", lambda: (menu_window.deiconify(), invoice_window.destroy()))

def show_invoices(menu_window):
    menu_window.withdraw()

    # Crear una ventana para mostrar las facturas y presupuestos
    invoices_window = tk.Toplevel()
    invoices_window.title("Facturas y Presupuestos")
    invoices_window.geometry("1400x800")

    # Crear pestañas para Facturas y Presupuestos
    tab_control = ttk.Notebook(invoices_window)
    tab_facturas = ttk.Frame(tab_control)
    tab_presupuestos = ttk.Frame(tab_control)
    tab_control.add(tab_facturas, text='Facturas')
    tab_control.add(tab_presupuestos, text='Presupuestos')
    tab_control.pack(expand=1, fill="both")

    # Función para cargar datos de la base de datos
    def return_to_menu():
        menu_window.deiconify()
        invoices_window.destroy()

    def load_data(view_name):
        conn = get_db_connection()
        cursor = conn.execute(f"SELECT * FROM {view_name}")
        data = cursor.fetchall()
        conn.close()
        return data
    
    def load_data_by_id(view_name, id_value):
        conn = get_db_connection()
        query = f"SELECT * FROM {view_name} WHERE ID_factura = ?"
        cursor = conn.execute(query, (id_value,))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def load_data_by_id_presupuesto(view_name, id_value):
        conn = get_db_connection()
        query = f"SELECT * FROM {view_name} WHERE ID_presupuesto = ?"
        cursor = conn.execute(query, (id_value,))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def on_id_select(event):
        selected_item = treeview_ids_facturas.focus()
        if selected_item:
            id_factura = treeview_ids_facturas.item(selected_item, 'values')[0]
            data_facturas = load_data_by_id('ResumenFactura', id_factura)
            update_treeview_grouped_by_factura(treeview_facturas, data_facturas)

    def on_id_select_presupuesto(event):
        selected_item = treeview_ids_presupuestos.focus()  # Obtener el ítem seleccionado
        if selected_item:  # Verificar si hay algo seleccionado
            id_presupuesto = treeview_ids_presupuestos.item(selected_item, 'values')[0]
            data_presupuestos = load_data_by_id_presupuesto('Resumenpresupuesto', id_presupuesto)
            update_treeview_grouped_by_presupuesto(treeview_presupuestos, data_presupuestos)

    # Función para actualizar Treeview
    def update_treeview(treeview, data, id_only=False):
        treeview.delete(*treeview.get_children())
        inserted_ids = set()  # Un conjunto para recordar los IDs que ya se han insertado
        for row in data:
            if id_only:
                row_data = (row[0],)  # Solo el ID
                if row_data[0] not in inserted_ids:
                    treeview.insert('', tk.END, values=row_data)
                    inserted_ids.add(row_data[0])  # Recordar que este ID ya se ha insertado
            else:
                row_data = tuple(row)
                treeview.insert('', tk.END, values=row_data)

    def filter_facturas():
        nombre_cliente = nombre_cliente_entry_facturas.get()
        dni_cliente = dni_cliente_entry_facturas.get()
        data_facturas = load_data('ResumenFactura', nombre_cliente, dni_cliente)
        update_treeview_grouped_by_factura(treeview_facturas, data_facturas)
        update_treeview_grouped_by_factura(treeview_ids_facturas, data_facturas, id_only=True)
    
    def filter_presupuesto():
        nombre_cliente = nombre_cliente_entry_presupuestos.get()
        dni_cliente = dni_cliente_entry_presupuestos.get()
        data_presupuestos = load_data('Resumenpresupuesto', nombre_cliente, dni_cliente)
        update_treeview_grouped_by_presupuesto(treeview_presupuestos, data_presupuestos)
        update_treeview_grouped_by_presupuesto(treeview_ids_presupuestos, data_presupuestos, id_only=True)

    def load_data(view_name, nombre_cliente='', dni_cliente=''):
        conn = get_db_connection()
        query = f"SELECT * FROM {view_name} WHERE 1=1"
        params = []
        if nombre_cliente:
            query += " AND nombre_cliente LIKE ?"
            params.append(f'%{nombre_cliente}%')
        if dni_cliente:
            query += " AND dni_cliente LIKE ?"
            params.append(f'%{dni_cliente}%')
        cursor = conn.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data
    
    def update_treeview_grouped_by_factura(treeview, data):
        treeview.delete(*treeview.get_children())  # Clear the current treeview entries
        factura_data = {}
        # Group data by id_factura
        for row in data:
            id_factura = row[0]  # Assuming this is the first element of the row
            if id_factura not in factura_data:
                factura_data[id_factura] = {
                    'fecha': row[1],
                    'nombre_cliente': row[2],
                    'dni_cliente': row[3],
                    'direccion_cliente': row[4],
                    'conceptos': []
                }
            # Append concept details to the conceptos list
            factura_data[id_factura]['conceptos'].append(row[5:])
        # Insert grouped data into treeview
        for id_factura, details in factura_data.items():
            for i, concept in enumerate(details['conceptos']):
                if i == 0:  # First concept for this factura, include the factura details
                    treeview.insert('', tk.END, values=(id_factura,
                                                        details['fecha'],
                                                        details['nombre_cliente'],
                                                        details['dni_cliente'],
                                                        details['direccion_cliente'],
                                                        *concept))
                else:  # Subsequent concepts for this factura, only include the concept details
                    treeview.insert('', tk.END, values=('',  # Empty value for id_factura
                                                        '',  # Empty value for fecha
                                                        '',  # Empty value for nombre_cliente
                                                        '',  # Empty value for dni_cliente
                                                        '',  # Empty value for direccion_cliente
                                                        *concept))
    def update_treeview_grouped_by_presupuesto(treeview, data):
            treeview.delete(*treeview.get_children())  # Clear the current treeview entries
            presupuesto_data = {}
            # Group data by id_presupuesto
            for row in data:
                id_presupuesto = row[0]  # Assuming this is the first element of the row
                if id_presupuesto not in presupuesto_data:
                    presupuesto_data[id_presupuesto] = {
                        'fecha': row[1],
                        'nombre_cliente': row[2],
                        'dni_cliente': row[3],
                        'direccion_cliente': row[4],
                        'conceptos': []
                    }
                # Append concept details to the conceptos list
                presupuesto_data[id_presupuesto]['conceptos'].append(row[5:])
            # Insert grouped data into treeview
            for id_presupuesto, details in presupuesto_data.items():
                for i, concept in enumerate(details['conceptos']):
                    if i == 0:  # First concept for this factura, include the factura details
                        treeview.insert('', tk.END, values=(id_presupuesto,
                                                            details['fecha'],
                                                            details['nombre_cliente'],
                                                            details['dni_cliente'],
                                                            details['direccion_cliente'],
                                                            *concept))
                    else:  # Subsequent concepts for this factura, only include the concept details
                        treeview.insert('', tk.END, values=('',  # Empty value for id_factura
                                                            '',  # Empty value for fecha
                                                            '',  # Empty value for nombre_cliente
                                                            '',  # Empty value for dni_cliente
                                                            '',  # Empty value for direccion_cliente
                                                            *concept))            
    column_mapping = {
        'Fecha': 'fecha',
        'Nombre cliente': 'nombre_cliente',
        'DNI cliente': 'dni_cliente',
        'Direccion cliente': 'direccion_cliente',
        'Descripcion': 'descripcion',
        'Cantidad': 'cantidad',
        'Precio': 'precio',
        'Referencia': 'referencia',
        'Tecnico': 'tecnico',
        # Add more mappings as necessary
    }
    column_mapping_presupuesto = {
        'Fecha': 'fecha',
        'Nombre cliente': 'nombre_cliente',
        'DNI cliente': 'dni_cliente',
        'Direccion cliente': 'direccion_cliente',
        'Descripcion': 'descripcion',
        'Cantidad': 'cantidad',
        'Precio': 'precio',
        'Tecnico': 'tecnico',
        # Add more mappings as necessary
    }

    def on_double_click(event):
        # Get the column id and item id at the event x and y coordinates
        column_id = treeview_facturas.identify_column(event.x)
        item_id = treeview_facturas.identify_row(event.y)
        if item_id:  # Check if a valid item is selected
            column = column_id.replace('#', '')  # Convert '#1' to '1'

        # Check if the column is editable ('ID Factura' and 'ID Concepto' are not editable)
        if treeview_facturas.heading(column_id, 'text') not in ['ID Factura', 'ID Concepto']:
            edit_item(item_id, column)

    def on_double_click_presupuesto(event):
        # Get the column id and item id at the event x and y coordinates
        column_id = treeview_presupuestos.identify_column(event.x)
        item_id = treeview_presupuestos.identify_row(event.y)
        if item_id:  # Check if a valid item is selected
            column = column_id.replace('#', '')  # Convert '#1' to '1'

        # Check if the column is editable ('ID Factura' and 'ID Concepto' are not editable)
        if treeview_presupuestos.heading(column_id, 'text') not in ['ID Presupuesto', 'ID Concepto']:
            edit_item_presupuesto(item_id, column)

    def edit_item(item_id, column):
        # Get the bounding box of the cell
        column_num = int(column) - 1
        x, y, width, height = treeview_facturas.bbox(item_id, column_num)

        # Create an entry widget
        entry = tk.Entry(treeview_facturas)
        entry.place(x=x, y=y, width=width, height=height, anchor='nw')

        def save_edit(event):
            # Get the new value from the entry widget
            new_value = entry.get()
            # Get the record from the Treeview
            record = treeview_facturas.item(item_id, 'values')
            # Get the Treeview heading name
            column_name = treeview_facturas.heading('#' + column, 'text')

            # Map the Treeview heading name to the database field name
            db_field_name = column_mapping.get(column_name)

            if db_field_name:
                # Determine which table and field to update based on the column
                
                if db_field_name in ['fecha','tipo_factura', 'nombre_cliente', 'dni_cliente', 'direccion_cliente','referencia']:
                    table = 'factura'
                    key = record[0]  # Assuming 'ID Factura' is the first field in the Treeview
                else:
                    table = 'concepto'
                    key = record[7]  # Assuming 'ID Concepto' is the sixth field in the Treeview
                # Update the database
                column_num = int(column) - 1  # Adjust for 1-indexing in Treeview
                new_record = list(record)
                new_record[column_num] = new_value
                treeview_facturas.item(item_id, values=new_record)
                update_database(table, db_field_name, new_value, key)
            # Destroy the entry widget
            entry.destroy()

        # Bind the Return key to save the edited value
        entry.bind('<Return>', save_edit)
        # Set focus on the entry widget
        entry.focus()
        # Bind the Escape key to destroy the entry widget
        entry.bind('<Escape>', lambda e: entry.destroy())

    def edit_item_presupuesto(item_id, column):
        # Get the bounding box of the cell
        column_num = int(column) - 1
        x, y, width, height = treeview_presupuestos.bbox(item_id, column_num)

        # Create an entry widget
        entry = tk.Entry(treeview_presupuestos)
        entry.place(x=x, y=y, width=width, height=height, anchor='nw')

        def save_edit_presupuesto(event):
            # Get the new value from the entry widget
            new_value = entry.get()
            # Get the record from the Treeview
            record = treeview_presupuestos.item(item_id, 'values')
            # Get the Treeview heading name
            column_name = treeview_presupuestos.heading('#' + column, 'text')

            # Map the Treeview heading name to the database field name
            db_field_name = column_mapping_presupuesto.get(column_name)

            if db_field_name:
                # Determine which table and field to update based on the column
                
                if db_field_name in ['fecha','tipo_presupuesto', 'nombre_cliente', 'dni_cliente', 'direccion_cliente','referencia']:
                    table = 'presupuesto'
                    key = record[0]  # Assuming 'ID factura' is the first field in the Treeview
                else:
                    table = 'Concepto_presupuesto'
                    key = record[6]  # Assuming 'ID Concepto' is the sixth field in the Treeview
                # Update the database
                column_num = int(column) - 1  # Adjust for 1-indexing in Treeview
                new_record = list(record)
                new_record[column_num] = new_value
                treeview_presupuestos.item(item_id, values=new_record)
                update_database_presupuesto(table, db_field_name, new_value, key)
            # Destroy the entry widget
            entry.destroy()

        # Bind the Return key to save the edited value
        entry.bind('<Return>', save_edit_presupuesto)
        # Set focus on the entry widget
        entry.focus()
        # Bind the Escape key to destroy the entry widget
        entry.bind('<Escape>', lambda e: entry.destroy())

    def update_database(table, field, new_value, key):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Determine the correct key field name for the table
            key_field = 'id_factura' if table == 'factura' else 'id_concepto'
            sql = f"UPDATE {table} SET {field} = ? WHERE {key_field} = ?"
            cursor.execute(sql, (new_value, key))

            # Commit the changes
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the connection whether or not an error occurred
            if conn:
                conn.close()
    def update_database_presupuesto(table, field, new_value, key):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Determine the correct key field name for the table
            key_field = 'id_presupuesto' if table == 'presupuesto' else 'id_concepto_p'
            sql = f"UPDATE {table} SET {field} = ? WHERE {key_field} = ?"
            cursor.execute(sql, (new_value, key))

            # Commit the changes
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the connection whether or not an error occurred
            if conn:
                conn.close()

    def delete_invoice():
    # Prompt the user to enter the ID of the invoice to be deleted
        id_factura = simpledialog.askstring("Borrar factura", "Selecciona el id de la factura que quieres borrar:")

        if id_factura and ask_yes_no_confirmation(f"Estas seguro de que quieres borrar la factura {id_factura}?"):
        # Proceed with deletion if ID is provided
            delete_invoice_from_database(id_factura)
            update_treeview(treeview_ids_facturas, data_facturas, id_only=True)
            update_treeview_grouped_by_factura(treeview_facturas, data_facturas)

    def delete_concepto():
        id_concepto = simpledialog.askstring("Borrar concepto", "Selecciona el id del concepto que quieres borrar:")
        if id_concepto and ask_yes_no_confirmation(f"Estas seguro de que quieres borrar el concepto {id_concepto}?"):
            delete_concepto_from_database(id_concepto)
            #update_treeview(treeview_ids_facturas, data_facturas, id_only=True)
            #update_treeview_grouped_by_factura(treeview_facturas, data_facturas)

    def delete_concepto_presupuesto():
        id_concepto = simpledialog.askstring("Borrar concepto", "Selecciona el id del concepto que quieres borrar:")
        if id_concepto and ask_yes_no_confirmation(f"Estas seguro de que quieres borrar el concepto {id_concepto}?"):
            delete_concepto_from_database_presupuesto(id_concepto)
            #update_treeview(treeview_ids_presupuestos, data_presupuestos, id_only=True)
            #update_treeview_grouped_by_presupuesto(treeview_presupuestos, data_presupuestos)

    def delete_invoice_presupuesto():
    # Prompt the user to enter the ID of the invoice to be deleted
        id_presupuesto = simpledialog.askstring("Borrar presupuesto", "Selecciona el id del presupuesto que quieres borrar:")

        if id_presupuesto and ask_yes_no_confirmation(f"Estas seguro de que quieres borrar el presupuesto {id_presupuesto}?"):
        # Proceed with deletion if ID is provided
            delete_invoice_from_database_presupuesto(id_presupuesto)
            update_treeview(treeview_ids_presupuestos, data_presupuestos, id_only=True)
            update_treeview_grouped_by_presupuesto(treeview_presupuestos, data_presupuestos)

        # Refresh your Treeview or update your GUI as needed
    def delete_invoice_from_database(id_factura):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # First, delete the associated 'conceptos'
            cursor.execute("DELETE FROM concepto WHERE id_factura = ?", (id_factura,))

            # Then, delete the invoice
            cursor.execute("DELETE FROM factura WHERE id_factura = ?", (id_factura,))

            # Commit the changes
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()
    def delete_concepto_from_database(id_concepto):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # First, delete the associated 'conceptos'
            cursor.execute("DELETE FROM concepto WHERE id_concepto = ?", (id_concepto,))
            # Commit the changes
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()
    def delete_concepto_from_database_presupuesto(id_concepto):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # First, delete the associated 'conceptos'
            cursor.execute("DELETE FROM concepto_presupuesto WHERE id_concepto_p = ?", (id_concepto,))
            # Commit the changes
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()    
    def ask_yes_no_confirmation(message):
        return messagebox.askyesno("Confirmation", message)
    def get_selected_invoice_id():
    # Getting the currently focused item in the treeview
        focused_item = treeview_ids_facturas.focus()
        # If there's a focused item, retrieve its values
        if focused_item:
            item = treeview_ids_facturas.item(focused_item)
            # Assuming the ID is the first value in the 'values' tuple
            selected_invoice_id = item['values'][0] 
            return selected_invoice_id
        else:
            # Handle the case when no item is selected, maybe return None or raise an error
            return None
        
    def delete_invoice_from_database_presupuesto(id_presupuesto):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # First, delete the associated 'conceptos'
            cursor.execute("DELETE FROM concepto_presupuesto WHERE id_presupuesto = ?", (id_presupuesto,))

            # Then, delete the invoice
            cursor.execute("DELETE FROM presupuesto WHERE id_presupuesto = ?", (id_presupuesto,))

            # Commit the changes
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()
    def ask_yes_no_confirmation(message):
        return messagebox.askyesno("Confirmation", message)
    def get_selected_invoice_id_presupuesto():
    # Getting the currently focused item in the treeview
        focused_item = treeview_ids_presupuestos.focus()
        # If there's a focused item, retrieve its values
        if focused_item:
            item = treeview_ids_presupuestos.item(focused_item)
            # Assuming the ID is the first value in the 'values' tuple
            selected_invoice_id = item['values'][0] 
            return selected_invoice_id
        else:
            # Handle the case when no item is selected, maybe return None or raise an error
            return None
    def get_tipo_factura(id_factura):
        conn = get_db_connection()
        tipo_factura = None
        with conn:
            tipo_factura = conn.execute("SELECT tipo_factura FROM factura WHERE id_factura = ?", (id_factura,)).fetchone()
        return tipo_factura[0] if tipo_factura else None
    
    def get_tipo_presupuesto(id_presupuesto):
        conn = get_db_connection()
        tipo_presupuesto = None
        with conn:
            tipo_presupuesto = conn.execute("SELECT tipo_presupuesto FROM presupuesto WHERE id_presupuesto = ?", (id_presupuesto,)).fetchone()
        return tipo_presupuesto[0] if tipo_presupuesto else None

    def add_concepto():
        id_factura = sg.popup_get_text("En que factura quieres insertar un concepto ?", "Insertar factura")
        if id_factura:
            tipo_factura = get_tipo_factura(id_factura)
            fields = ['Concepto', 'Cantidad', 'Precio']
            if tipo_factura == 1:
                fields.append('Tecnicos')
            values = sg.Window('Insertar datos', [[sg.Text(f'{field}:'), sg.Input(key=field)] for field in fields] + [[sg.Button('Aceptar')]]).read(close=True)[1]
            if values:
                tecnico = values.get('Tecnicos', 1)
                insert_concepto(id_factura, values['Concepto'], values['Cantidad'], values['Precio'], tecnico)

    def add_concepto_presupuesto():
        id_presupuesto = sg.popup_get_text("En que presupuesto quieres insertar un concepto ?", "Insertar presupuesto")
        if id_presupuesto:
            tipo_presupuesto = get_tipo_presupuesto(id_presupuesto)
            fields = ['Concepto', 'Cantidad', 'Precio']
            if tipo_presupuesto == 1:
                fields.append('Tecnicos')
            values = sg.Window('Insertar datos', [[sg.Text(f'{field}:'), sg.Input(key=field)] for field in fields] + [[sg.Button('Aceptar')]]).read(close=True)[1]
            if values:
                tecnico = values.get('Tecnicos', 1)
                insert_concepto_presupuesto(id_presupuesto, values['Concepto'], values['Cantidad'], values['Precio'], tecnico)      
            
    def generate_pdf():
        selected_invoice_id = get_selected_invoice_id()
        if selected_invoice_id is None:
            print("No invoice selected.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ResumenFactura WHERE id_factura = ?", (selected_invoice_id,))
        factura_details = cursor.fetchone()
        cursor.execute("SELECT * FROM ResumenFactura WHERE id_factura = ?", (selected_invoice_id,))
        conceptos = cursor.fetchall()  # Use fetchone() if you expect a single row
        conn.close()

        if not factura_details:
            print(f"No data found for invoice ID {selected_invoice_id}")
            return
        
        invoice_context = {
            'factura_details': factura_details,
            'conceptos': conceptos,
                # Add the rest of the fields...
        }
        # Load the Jinja template
        env = Environment(loader=FileSystemLoader('../template'))
        template = env.get_template('invoice_template.html')
        ruta_original = 'C:/Users/Edi/Desktop/Proyectos/Aplicaccion python/proyecto_final/template/logo.png'
        ruta_formateada = quote(ruta_original)
        logo_path = f'file:///{ruta_formateada}'
    

        # Render the template with the invoice data
        html = template.render(invoice_data=invoice_context, logo=logo_path)
        print(html)
        config = pdfkit.configuration(wkhtmltopdf=r'C:\wkhtmltopdf\wkhtmltopdf.exe')
        options = {'enable-local-file-access': ''}

        output_filename = f'factura_{selected_invoice_id}.pdf'
        pdfkit.from_string(html, output_filename, options=options, configuration=config)

    def generate_pdf_presupuesto():
        selected_presupuesto_id = get_selected_invoice_id_presupuesto()
        if selected_presupuesto_id is None:
            print("No invoice selected.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resumenpresupuesto WHERE id_presupuesto = ?", (selected_presupuesto_id,))
        presupuesto_details = cursor.fetchone()
        cursor.execute("SELECT * FROM resumenpresupuesto WHERE id_presupuesto = ?", (selected_presupuesto_id,))
        conceptos = cursor.fetchall()  # Use fetchone() if you expect a single row
        conn.close()

        if not presupuesto_details:
            print(f"No data found for invoice ID {selected_presupuesto_id}")
            return
        
        presupuesto_context = {
            'presupuesto_details': presupuesto_details,
            'conceptos': conceptos,
                # Add the rest of the fields...
        }
        # Load the Jinja template
        env = Environment(loader=FileSystemLoader('../template'))
        template = env.get_template('invoice_template_presupuesto.html')
        logo_path = 'file:///C:/Users/Edi/Desktop/Proyectos/Aplicaccion python/proyecto_final/template/logo.png'
    

        # Render the template with the invoice data
        html = template.render(presupuesto_data=presupuesto_context, logo=logo_path)
        print(html)
        config = pdfkit.configuration(wkhtmltopdf=r'C:\wkhtmltopdf\wkhtmltopdf.exe')
        options = {'enable-local-file-access': ''}

        output_filename = f'presupuesto_{selected_presupuesto_id}.pdf'
        pdfkit.from_string(html, output_filename, options=options, configuration=config)


        # Convert the rendered HTML to a PDF
    
    # Treeview para mostrar solo IDs (Facturas)
    style = ttk.Style()
    style.configure("filter_frame_facturas", background="#E8E8E8", foreground="black", rowheight=25)
    style.map("filter_frame_facturas", background=[('selected', '#3498db')])
    style.configure("TButton", font=('Helvetica', 10), borderwidth='1')
    style.map("TButton", foreground=[('pressed', 'red'), ('active', 'blue')], background=[('pressed', '!disabled', 'black'), ('active', 'white')])
    label_font = ('Helvetica', 10, 'bold')
    button_width = 25

    left_frame_facturas = ttk.Frame(tab_facturas)
    left_frame_facturas.pack(side='left', fill='y')

    treeview_ids_facturas = ttk.Treeview(left_frame_facturas, columns=('ID Factura',), show='headings')
    treeview_ids_facturas.heading('ID Factura', text='ID Factura')
    treeview_ids_facturas.column('ID Factura', width=100, stretch=True)  # Adjust the width as needed
    treeview_ids_facturas.pack(side='top', fill='both', expand=True)
    treeview_ids_facturas.bind('<<TreeviewSelect>>', on_id_select)
    ############ CAMPOS PARA FILTRAR
    filter_frame_facturas = ttk.Frame(left_frame_facturas)
    filter_frame_facturas.pack(side='top', fill='x', padx=8, pady=8)
    
    #campo para filitrar por nombre
    nombre_cliente_label = ttk.Label(filter_frame_facturas, text="Nombre Cliente", font=label_font)
    nombre_cliente_label.pack(side='top', fill='x')
    nombre_cliente_entry_facturas = ttk.Entry(filter_frame_facturas)
    nombre_cliente_entry_facturas.pack(side='top', fill='x')

    #campo para filtrar por DNI
    dni_cliente_label = ttk.Label(filter_frame_facturas, text="DNI Cliente", font=label_font)
    dni_cliente_label.pack(side='top', fill='x')
    dni_cliente_entry_facturas = ttk.Entry(filter_frame_facturas)
    dni_cliente_entry_facturas.pack(side='top', fill='x')
   

    # Boton para filtrar

    filter_button_facturas = ttk.Button(filter_frame_facturas, text="Filtrar", command=filter_facturas, style='TButton', width=button_width)
    filter_button_facturas.pack(pady=(15, 0))

    filter_button_facturas = ttk.Button(filter_frame_facturas, text="Añadir Concepto", command=add_concepto, style='TButton', width=button_width)
    filter_button_facturas.pack(pady=(15, 0))

    delete_button = ttk.Button(filter_frame_facturas, text='Borrar Concepto', command=delete_concepto, style="TButton", width=button_width)
    delete_button.pack(pady=(15, 0))

    delete_button = ttk.Button(filter_frame_facturas, text='Borrar Factura', command=delete_invoice, style="TButton", width=button_width)
    delete_button.pack(pady=(15, 0))   # Adjust this according to your layout needs

    generate_pdf_button = ttk.Button(filter_frame_facturas, text='Generar PDF', command=generate_pdf, style="TButton", width=button_width)
    generate_pdf_button.pack(pady=(15, 0)) 

    
    return_button = ttk.Button(filter_frame_facturas, text="Volver al Menú", command=return_to_menu, style="TButton", width=button_width)
    return_button.pack(side='left', anchor='w', pady=(80, 10))
    ##########################################################################################################################################
    # Treeview para mostrar solo IDs (Presupuestos)
    style = ttk.Style()
    style.configure("filter_frame_presupuestos", background="#E8E8E8", foreground="black", rowheight=25)
    style.map("ffilter_frame_presupuestos", background=[('selected', '#3498db')])
    style.configure("TButton", font=('Helvetica', 10), borderwidth='1')
    style.map("TButton", foreground=[('pressed', 'red'), ('active', 'blue')], background=[('pressed', '!disabled', 'black'), ('active', 'white')])
    label_font = ('Helvetica', 10, 'bold')
    button_width = 25


    left_frame_presupuestos = ttk.Frame(tab_presupuestos)
    left_frame_presupuestos.pack(side='left', fill='y')

    treeview_ids_presupuestos = ttk.Treeview(left_frame_presupuestos, columns=('ID Presupuesto',), show='headings')
    treeview_ids_presupuestos.heading('ID Presupuesto', text='ID Presupuesto')
    treeview_ids_presupuestos.column('ID Presupuesto', width=100, stretch=True)
    treeview_ids_presupuestos.pack(side='top', fill='both',expand=True)
    treeview_ids_presupuestos.bind('<<TreeviewSelect>>', on_id_select_presupuesto)

    ############ CAMPOS PARA FILTRAR
    filter_frame_presupuestos = ttk.Frame(left_frame_presupuestos)
    filter_frame_presupuestos.pack(side='top', fill='x', padx=8, pady=8)


    #campo para filitrar por nombre
    nombre_cliente_label = ttk.Label(filter_frame_presupuestos, text="Nombre Cliente", font=label_font)
    nombre_cliente_label.pack(side='top', fill='x')
    nombre_cliente_entry_presupuestos = ttk.Entry(filter_frame_presupuestos)
    nombre_cliente_entry_presupuestos.pack(side='top', fill='x')

    #campo para filtrar por DNI
    dni_cliente_label = ttk.Label(filter_frame_presupuestos, text="DNI Cliente",font=label_font)
    dni_cliente_label.pack(side='top', fill='x')
    dni_cliente_entry_presupuestos = ttk.Entry(filter_frame_presupuestos)
    dni_cliente_entry_presupuestos.pack(side='top', fill='x')



   

    # Boton para filtrar
    filter_button_presupuestos = ttk.Button(filter_frame_presupuestos, text="Filtrar", command=filter_presupuesto, style='TButton', width=button_width)
    filter_button_presupuestos.pack(pady=(15, 0))

    filter_button_facturas = ttk.Button(filter_frame_presupuestos, text="Añadir Concepto", command=add_concepto_presupuesto, style='TButton', width=button_width)
    filter_button_facturas.pack(pady=(15, 0))

    delete_button = ttk.Button(filter_frame_presupuestos, text='Borrar Concepto', command=delete_concepto_presupuesto, style="TButton", width=button_width)
    delete_button.pack(pady=(15, 0))

    delete_button = ttk.Button(filter_frame_presupuestos, text='Borrar Factura', command=delete_invoice_presupuesto, style="TButton", width=button_width)
    delete_button.pack(pady=(15, 0))   # Adjust this according to your layout needs

    generate_pdf_button = ttk.Button(filter_frame_presupuestos, text='Generar PDF', command=generate_pdf_presupuesto, style="TButton", width=button_width)
    generate_pdf_button.pack(pady=(15, 0)) 

    return_button = ttk.Button(filter_frame_presupuestos, text="Volver al Menú", command=return_to_menu, style="TButton", width=button_width)
    return_button.pack(side='left', anchor='w', pady=(80, 10))
    




    # Configuración del Treeview para Facturas
    columns_facturas = ('ID Factura', 'Fecha','tipo de factura', 'Nombre cliente', 'DNI cliente', 'Direccion cliente','Referencia', 'ID Concepto', 'Descripcion', 'Cantidad', 'Precio','Tecnico')
    treeview_facturas = ttk.Treeview(tab_facturas, columns=columns_facturas, show='headings')
    for col in columns_facturas:
        treeview_facturas.heading(col, text=col)
        treeview_facturas.column(col, minwidth=0, width=80, stretch=True)
    treeview_facturas.pack(expand=True, fill='both', padx=8, pady=8)
    treeview_facturas.bind('<Double-1>', on_double_click)



    # Cargar y mostrar datos de facturas
    data_facturas = load_data('ResumenFactura')
    update_treeview(treeview_facturas, data_facturas)
    update_treeview(treeview_ids_facturas, data_facturas, id_only=True)
    treeview_facturas.delete(*treeview_facturas.get_children())

    # Configuración del Treeview para Presupuestos
    columns_presupuestos = ('ID Presupuesto', 'Fecha','tipo de presupuesto', 'Nombre cliente', 'DNI cliente', 'Direccion cliente', 'ID Concepto', 'Descripcion', 'Cantidad', 'Precio','Tecnico')
    treeview_presupuestos = ttk.Treeview(tab_presupuestos, columns=columns_presupuestos, show='headings')
    for col in columns_presupuestos:
        treeview_presupuestos.heading(col, text=col)
        treeview_presupuestos.column(col, minwidth=0, width=80, stretch=True)
    treeview_presupuestos.pack(expand=True, fill='both', padx=8, pady=8)
    treeview_presupuestos.bind('<Double-1>', on_double_click_presupuesto)

    # Cargar y mostrar datos de presupuestos
    data_presupuestos = load_data('ResumenPresupuesto')
    update_treeview(treeview_presupuestos, data_presupuestos)
    update_treeview(treeview_ids_presupuestos, data_presupuestos, id_only=True)
    treeview_presupuestos.delete(*treeview_presupuestos.get_children())
    

    invoices_window.protocol("WM_DELETE_WINDOW", lambda: (menu_window.deiconify(), invoices_window.destroy()))

def create_presupuesto(menu_window):

    menu_window.withdraw()
    temp_conceptos = []

    def add_concepto():
        descripcion = descripcion_entry.get()
        cantidad = cantidad_entry.get()
        precio = precio_entry.get()
        tecnico = tecnico_entry.get()

        if invoice_type.get() == 0:
            tecnico = "1"
        try:
        # Ensure that cantidad and precio can be converted to float for calculation
            total = float(cantidad) * float(precio) * float(tecnico)
        except ValueError:
        # Handle the error if cantidad or precio is not a valid number
            messagebox.showerror("Error", "Cantidad, Precio y Nº Tecnicos deben ser números válidos.")
            return
        temp_conceptos.append((descripcion, cantidad, precio, tecnico, total))

        descripcion_entry.delete(0, tk.END)
        cantidad_entry.delete(0, tk.END)
        precio_entry.delete(0, tk.END)
        if invoice_type.get() == 1:
            tecnico_entry.delete(0, tk.END)

        update_conceptos_treeview()

    def update_conceptos_treeview():
        for i in conceptos_treeview.get_children():
            conceptos_treeview.delete(i)
        for concepto in temp_conceptos:
            formatted_concepto = concepto[:-1] + (f"{concepto[-1]:.2f}",)
            conceptos_treeview.insert('', tk.END, values=formatted_concepto)

    def delete_selected_concepto():
        selected_item = conceptos_treeview.selection()
        if selected_item:  # Verifica si hay algo seleccionado
            selected_index = conceptos_treeview.index(selected_item[0])
            conceptos_treeview.delete(selected_item[0])
            del temp_conceptos[selected_index]  # Elimina usando el índice en temp_conceptos
            update_conceptos_treeview()  # Actualiza el Treeview

    def save_presupuesto():
        nombre_cliente = nombre_cliente_entry.get()
        dni_cliente = dni_cliente_entry.get()
        direccion_cliente = direccion_cliente_entry.get()
        if invoice_type.get() == -1:
            messagebox.showerror("Error", "Por favor, seleccione el tipo de factura antes de guardar.", parent=invoice_window)
            return
        tipo_presupuesto = invoice_type.get()
        id_presupuesto = insert_presupuesto(current_user_id, nombre_cliente, dni_cliente, direccion_cliente,tipo_presupuesto)
        for concepto in temp_conceptos:
            insert_concepto_presupuesto(id_presupuesto, *concepto[:4])
        # Aquí deberías insertar la lógica para guardar los datos en tu base de datos o archivo
        temp_conceptos.clear()
        messagebox.showinfo("Éxito", "Presupuesto generado correctamente", parent=invoice_window)
        invoice_window.destroy()
        menu_window.deiconify()
    def handle_invoice_type_change():
        # If 'Factura para Clientes' is selected
        if invoice_type.get() == 0:
            tecnico_entry.delete(0, tk.END)  # Clear the entry
            tecnico_entry.insert(0, "1")  # Set value to 1
            tecnico_entry.pack_forget()
            conceptos_treeview.column('Tecnico', width=0, stretch=False)  # Hide the entry widget
        # If 'Factura para Empresas' is selected
        elif invoice_type.get() == 1:
            tecnico_entry.pack(fill='x')
            conceptos_treeview.column('Tecnico', width=100, stretch=True)

    def return_to_menu():
        menu_window.deiconify()
        invoice_window.destroy()

    invoice_window = tk.Toplevel()
    invoice_window.title("Crear nuevo presupuesto")
    invoice_window.geometry("900x700")

    style = ttk.Style(invoice_window)
    style.theme_use('clam')

    main_frame = ttk.Frame(invoice_window, padding="10")
    main_frame.pack(expand=True, fill='both')

    left_frame = ttk.Frame(main_frame, padding="10")
    left_frame.pack(side='left', fill='y')

    right_frame = ttk.Frame(main_frame, padding="10")
    right_frame.pack(side='left', fill='both', expand=True)

    # Campos del formulario
    ttk.Label(left_frame, text="Nombre cliente:").pack(fill='x', padx=5, pady=2)
    nombre_cliente_entry = ttk.Entry(left_frame)
    nombre_cliente_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="DNI/NIF:").pack(fill='x', padx=5, pady=2)
    dni_cliente_entry = ttk.Entry(left_frame)
    dni_cliente_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Dirección:").pack(fill='x', padx=5, pady=2)
    direccion_cliente_entry = ttk.Entry(left_frame)
    direccion_cliente_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Concepto:").pack(fill='x', padx=5, pady=2)
    descripcion_entry = ttk.Entry(left_frame)
    descripcion_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Cantidad:").pack(fill='x', padx=5, pady=2)
    cantidad_entry = ttk.Entry(left_frame)
    cantidad_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Precio:").pack(fill='x', padx=5, pady=2)
    precio_entry = ttk.Entry(left_frame)
    precio_entry.pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame, text="Nº Tecnicos (Si el presupuesto es para empresas):").pack(fill='x', padx=5, pady=2)
    tecnico_entry_frame = ttk.Frame(left_frame)
    tecnico_entry_frame.pack(fill='x', padx=5, pady=2)
    tecnico_entry = ttk.Entry(tecnico_entry_frame)

    ttk.Label(left_frame, text="Tipo de Presupuesto:").pack(fill='x', padx=5, pady=2)
    invoice_type = tk.IntVar(value=-1)
    # Radio button for Clients
    ttk.Radiobutton(left_frame, text="Presupuesto para Clientes", variable=invoice_type, value=0, command=handle_invoice_type_change).pack(fill='x', padx=5, pady=2)
    # Radio button for Companies
    ttk.Radiobutton(left_frame, text="Presupuesto para Empresas", variable=invoice_type, value=1, command=handle_invoice_type_change).pack(fill='x', padx=5, pady=2)

    ttk.Button(left_frame, text="Agregar Concepto", command=add_concepto).pack(fill='x', padx=5, pady=2)
    ttk.Button(left_frame, text="Guardar presupuesto", command=save_presupuesto).pack(fill='x', padx=5, pady=2)

    ttk.Label(left_frame).pack(fill='x', padx=5, pady=20)  # Espaciador
    ttk.Button(left_frame, text="Volver al Menú", command=return_to_menu).pack(fill='x', padx=5, pady=2)

    # Lista de conceptos con Treeview
    columns = ('Concepto', 'Cantidad', 'Precio','Tecnico','Total')
    conceptos_treeview = ttk.Treeview(right_frame, columns=columns, show='headings')
    for col in columns:
        conceptos_treeview.heading(col, text=col)
        conceptos_treeview.column(col, width=100)
    conceptos_treeview.pack(expand=True, fill='both', padx=8, pady=8)

    ttk.Button(right_frame, text="Eliminar concepto", command=delete_selected_concepto).pack(pady=5)

    invoice_window.protocol("WM_DELETE_WINDOW", lambda: (menu_window.deiconify(), invoice_window.destroy()))

# Ejemplo de uso
# menu_window = tk.Tk()
# create_invoice(menu_window)
# create_presupuesto(menu_window)
    

# Ejecutar la GUI
root.mainloop()