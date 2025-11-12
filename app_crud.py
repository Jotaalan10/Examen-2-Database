import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

# Conexión local (Docker)
URI = "mongodb://root:secret@localhost:27017/?authSource=admin"
DB_NAME = "social_crud"
COLL_NAME = "personas"

client = MongoClient(URI)
db = client[DB_NAME]
col = db[COLL_NAME]

def cargar_tabla():
    for i in tree.get_children():
        tree.delete(i)
    for doc in col.find().sort("id", 1):
        tree.insert("", "end", iid=str(doc["id"]), values=(
            doc.get("id",""),
            doc.get("nombre",""),
            doc.get("apellido1",""),
            doc.get("apellido2",""),
            doc.get("marca_o_modelo",""),
            doc.get("edad",""),
            doc.get("correo",""),
            doc.get("telefono",""),
            doc.get("ciudad",""),
            doc.get("estado",""),
            doc.get("activo",""),
        ))

def limpiar_form():
    for v in entradas.values():
        v.set("")

def on_select(event):
    sel = tree.focus()
    if not sel:
        return
    vals = tree.item(sel, "values")
    keys = ["id","nombre","apellido1","apellido2","marca_o_modelo","edad","correo","telefono","ciudad","estado","activo"]
    for k, v in zip(keys, vals):
        entradas[k].set(v)

def siguiente_id():
    doc = col.find_one(sort=[("id", -1)])
    return (doc["id"] + 1) if doc else 1

def agregar():
    try:
        _id = entradas["id"].get().strip()
        _id = int(_id) if _id else siguiente_id()
        doc = {
            "id": _id,
            "nombre": entradas["nombre"].get().strip(),
            "apellido1": entradas["apellido1"].get().strip(),
            "apellido2": entradas["apellido2"].get().strip(),
            "marca_o_modelo": entradas["marca_o_modelo"].get().strip() or None,
            "edad": int(entradas["edad"].get().strip() or 0),
            "correo": entradas["correo"].get().strip(),
            "telefono": entradas["telefono"].get().strip(),
            "ciudad": entradas["ciudad"].get().strip(),
            "estado": entradas["estado"].get().strip(),
            "activo": entradas["activo"].get().strip().lower() in ("1","true","si","sí","yes","y")
        }
        col.insert_one(doc)
        cargar_tabla()
        limpiar_form()
    except Exception as e:
        messagebox.showerror("Error al agregar", str(e))

def editar():
    try:
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un registro en la tabla.")
            return
        _id = int(entradas["id"].get().strip() or sel)
        updates = {
            "nombre": entradas["nombre"].get().strip(),
            "apellido1": entradas["apellido1"].get().strip(),
            "apellido2": entradas["apellido2"].get().strip(),
            "marca_o_modelo": entradas["marca_o_modelo"].get().strip() or None,
            "edad": int(entradas["edad"].get().strip() or 0),
            "correo": entradas["correo"].get().strip(),
            "telefono": entradas["telefono"].get().strip(),
            "ciudad": entradas["ciudad"].get().strip(),
            "estado": entradas["estado"].get().strip(),
            "activo": entradas["activo"].get().strip().lower() in ("1","true","si","sí","yes","y")
        }
        col.update_one({"id": _id}, {"$set": updates})
        cargar_tabla()
    except Exception as e:
        messagebox.showerror("Error al editar", str(e))

def eliminar():
    try:
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un registro en la tabla.")
            return
        _id = int(tree.item(sel,"values")[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar ID {_id}?"):
            col.delete_one({"id": _id})
            cargar_tabla()
            limpiar_form()
    except Exception as e:
        messagebox.showerror("Error al eliminar", str(e))

root = tk.Tk()
root.title("CRUD MongoDB - Personas")

frm = ttk.Frame(root, padding=10)
frm.pack(fill="both", expand=True)

# Formulario con etiquetas arriba (requisito)
labels = ["id","nombre","apellido1","apellido2","marca_o_modelo","edad","correo","telefono","ciudad","estado","activo"]
entradas = {k: tk.StringVar() for k in labels}

grid_form = ttk.Frame(frm)
grid_form.pack(fill="x", pady=5)

for i, k in enumerate(labels):
    ttk.Label(grid_form, text=k.capitalize()).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)
    ttk.Entry(grid_form, textvariable=entradas[k], width=30).grid(row=i//2, column=(i%2)*2+1, padx=5, pady=3)

# Botones identificables (Agregar, Editar, Eliminar)
btns = ttk.Frame(frm)
btns.pack(fill="x", pady=10)
ttk.Button(btns, text="Agregar", command=agregar).pack(side="left", padx=5)
ttk.Button(btns, text="Editar", command=editar).pack(side="left", padx=5)
ttk.Button(btns, text="Eliminar", command=eliminar).pack(side="left", padx=5)

# Tabla / Vista de datos (requisito)
cols = labels
tree = ttk.Treeview(frm, columns=cols, show="headings", height=12)
for c in cols:
    tree.heading(c, text=c.capitalize())
    tree.column(c, width=120, anchor="center")
tree.pack(fill="both", expand=True)
tree.bind("<<TreeviewSelect>>", on_select)

cargar_tabla()
root.mainloop()
