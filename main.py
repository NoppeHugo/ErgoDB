import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import ttk
from database import init_db, fetch_objectifs, fetch_activites_by_objectif, add_objectif, add_activite, update_activite

# Initialisation de la base de données
init_db()

def refresh_objectifs():
    """Met à jour la liste des objectifs dans le menu déroulant."""
    objectifs = fetch_objectifs()
    objectif_combobox['values'] = [f"{obj[0]} - {obj[1]}" for obj in objectifs]
    objectif_var.set("")  # Réinitialise la sélection actuelle

def display_activities():
    """Affiche les activités correspondant à l'objectif sélectionné."""
    objectif = objectif_var.get()
    if not objectif:
        listbox.delete(0, tk.END)
        return

    objectif_id = int(objectif.split(" - ")[0])  # Récupérer l'ID de l'objectif
    activites = fetch_activites_by_objectif(objectif_id)

    # Afficher les noms des activités
    listbox.delete(0, tk.END)
    for activite in activites:
        listbox.insert(tk.END, activite[0])  # Seuls les noms sont affichés

def view_activity_details(event):
    """Affiche les détails d'une activité dans une fenêtre dédiée."""
    selected = listbox.curselection()
    if not selected:
        return

    activity_name = listbox.get(selected[0])
    objectif_id = int(objectif_var.get().split(" - ")[0])
    activites = fetch_activites_by_objectif(objectif_id)

    # Trouver l'activité sélectionnée
    for activite in activites:
        if activite[0] == activity_name:
            open_activity_window(activite)
            break

def open_activity_window(activity):
    """Ouvre une fenêtre avec les détails d'une activité et permet de modifier ses informations."""
    def toggle_edit():
        """Active/Désactive les champs pour modifier les informations."""
        if edit_button['text'] == "Modifier":
            edit_button['text'] = "Enregistrer"
            name_entry.config(state="normal")
            desc_entry.config(state="normal")
            link_entry.config(state="normal")
        else:
            edit_button['text'] = "Modifier"
            name_entry.config(state="disabled")
            desc_entry.config(state="disabled")
            link_entry.config(state="disabled")
            save_changes()

    def save_changes():
        """Enregistre les modifications dans la base de données."""
        new_name = name_var.get()
        new_desc = desc_var.get()
        new_link = link_var.get()
        if not new_name:
            messagebox.showerror("Erreur", "Le nom de l'activité est requis.")
            return
        update_activite(activity[4], new_name, new_desc, new_link)  # ID de l'activité
        messagebox.showinfo("Succès", "Modifications enregistrées.")
        display_activities()  # Rafraîchit la liste des activités

    activity_window = tk.Toplevel(app)
    activity_window.title("Détails de l'activité")
    activity_window.geometry("400x300")

    tk.Label(activity_window, text="Nom de l'activité :").pack(pady=5)
    name_var = tk.StringVar(value=activity[0])
    name_entry = tk.Entry(activity_window, textvariable=name_var, state="disabled", width=50)
    name_entry.pack(pady=5)

    tk.Label(activity_window, text="Description :").pack(pady=5)
    desc_var = tk.StringVar(value=activity[1])
    desc_entry = tk.Entry(activity_window, textvariable=desc_var, state="disabled", width=50)
    desc_entry.pack(pady=5)

    tk.Label(activity_window, text="Lien :").pack(pady=5)
    link_var = tk.StringVar(value=activity[3])
    link_entry = tk.Entry(activity_window, textvariable=link_var, state="disabled", width=50)
    link_entry.pack(pady=5)

    edit_button = tk.Button(activity_window, text="Modifier", command=toggle_edit)
    edit_button.pack(pady=10)

def add_new_objectif():
    """Ajoute un nouvel objectif dans la base de données."""
    def save_objectif():
        nom = objectif_name.get()
        if not nom:
            messagebox.showerror("Erreur", "Le nom de l'objectif est requis.")
            return
        add_objectif(nom)
        messagebox.showinfo("Succès", "Objectif ajouté avec succès.")
        refresh_objectifs()  # Met à jour la combobox
        objectif_window.destroy()

    objectif_window = tk.Toplevel(app)
    objectif_window.title("Ajouter un Objectif")

    tk.Label(objectif_window, text="Nom de l'objectif :").pack(pady=5)
    objectif_name = tk.Entry(objectif_window)
    objectif_name.pack(pady=5)

    tk.Button(objectif_window, text="Enregistrer", command=save_objectif).pack(pady=10)

def add_new_activity():
    """Ajoute une nouvelle activité dans la base de données."""
    def save_activity():
        nom = activite_name.get()
        description = activite_desc.get()
        objectif_id = objectif_var.get().split(" - ")[0]
        if not nom or not objectif_id:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        add_activite(nom, description, "", "", int(objectif_id))
        messagebox.showinfo("Succès", "Activité ajoutée avec succès.")
        display_activities()  # Met à jour la liste d'activités automatiquement
        activite_window.destroy()

    activite_window = tk.Toplevel(app)
    activite_window.title("Ajouter une Activité")

    tk.Label(activite_window, text="Nom de l'activité :").pack(pady=5)
    activite_name = tk.Entry(activite_window)
    activite_name.pack(pady=5)

    tk.Label(activite_window, text="Description :").pack(pady=5)
    activite_desc = tk.Entry(activite_window)
    activite_desc.pack(pady=5)

    tk.Button(activite_window, text="Enregistrer", command=save_activity).pack(pady=10)
    
def delete_selected_activity():
    selected_activity_index = listbox.curselection()
    if selected_activity_index:
        listbox.delete(selected_activity_index)

# Interface principale
app = tk.Tk()
app.title("Ergothérapie - Gestion des Activités")
app.geometry("600x400")

# Appliquer un thème
style = ttk.Style(app)
style.theme_use('clam')

# Définir les couleurs
primary_color = "#4CAF50"  # Vert
secondary_color = "#FFFFFF"  # Blanc

# Créer des styles personnalisés
style.configure('TFrame', background=secondary_color)
style.configure('TButton', background=primary_color, foreground=secondary_color, font=('Helvetica', 10, 'bold'))
style.configure('TCombobox', background=secondary_color, foreground='black')
style.configure('TLabel', background=secondary_color, foreground='black')
style.configure('TListbox', background=secondary_color, foreground='black')

# Frame pour le menu déroulant et le bouton
top_frame = ttk.Frame(app, style='TFrame')
top_frame.pack(pady=10)

# Menu déroulant pour les objectifs
objectif_var = tk.StringVar()
objectif_combobox = ttk.Combobox(top_frame, textvariable=objectif_var, state="readonly", width=40, style='TCombobox')
objectif_combobox.pack(side=tk.LEFT, padx=5)
refresh_objectifs()

# Bouton "Ajouter un Objectif"
ttk.Button(top_frame, text="Ajouter un Objectif", command=add_new_objectif, style='TButton').pack(side=tk.LEFT)

# Lier l'événement de sélection d'un objectif à la mise à jour des activités
objectif_combobox.bind("<<ComboboxSelected>>", lambda e: display_activities())

# Bouton pour ajouter une activité
ttk.Button(app, text="Ajouter une Activité", command=add_new_activity, style='TButton').pack(pady=10)

# Bouton pour supprimer une activité
ttk.Button(app, text="Supprimer une Activité", command=delete_selected_activity, style='TButton').pack(pady=10)

# Liste des activités
listbox = tk.Listbox(app, width=80, height=10, bg=secondary_color, fg='black')
listbox.pack(pady=10)
listbox.bind("<Double-1>", view_activity_details)

app.mainloop()