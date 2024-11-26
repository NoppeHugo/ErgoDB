import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import ttk
from tkinter import PhotoImage
from database import delete_objectif, init_db, fetch_objectifs, fetch_activites_by_objectif, add_objectif, add_activite, update_activite, delete_activite_by_id, fetch_activity_by_id
from PIL import Image, ImageTk

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
        listbox.insert(tk.END, f"{activite[0]} - {activite[1]}")  # Afficher l'ID et le nom

def view_activity_details(event):
    selected_activity_index = listbox.curselection()
    if not selected_activity_index:
        return
    selected_activity = listbox.get(selected_activity_index)
    activite_id = int(selected_activity.split(" - ")[0])  # Récupérer l'ID de l'activité
    activity = fetch_activity_by_id(activite_id)  # Récupérer les détails de l'activité
    open_activity_window(activity)

def open_activity_window(activity):
    def toggle_edit():
        state = "normal" if name_entry["state"] == "disabled" else "disabled"
        name_entry.config(state=state)
        desc_entry.config(state=state)
        link_entry.config(state=state)
        save_button.config(state=state)

    def save_changes():
        new_name = name_var.get()
        new_desc = desc_var.get()
        new_link = link_var.get()
        if not new_name:
            messagebox.showerror("Erreur", "Le nom de l'activité est requis.")
            return
        update_activite(activity['id'], new_name, new_desc, new_link)  # ID de l'activité
        messagebox.showinfo("Succès", "Modifications enregistrées.")
        display_activities()  # Rafraîchit la liste des activités
        activity_window.destroy()

    # Création de la fenêtre
    activity_window = tk.Toplevel(app)
    activity_window.title("Détails de l'activité")

    # Widgets
    tk.Label(activity_window, text="Nom de l'activité :").pack(pady=5)
    name_var = tk.StringVar(value=activity['nom'])
    name_entry = tk.Entry(activity_window, textvariable=name_var, state="disabled", width=50)
    name_entry.pack(pady=5)

    tk.Label(activity_window, text="Description :").pack(pady=5)
    desc_var = tk.StringVar(value=activity['description'])
    desc_entry = tk.Entry(activity_window, textvariable=desc_var, state="disabled", width=50)
    desc_entry.pack(pady=5)

    tk.Label(activity_window, text="Lien :").pack(pady=5)
    link_var = tk.StringVar(value=activity['lien'])
    link_entry = tk.Entry(activity_window, textvariable=link_var, state="disabled", width=50)
    link_entry.pack(pady=5)

    edit_button = tk.Button(activity_window, text="Modifier", command=toggle_edit)
    edit_button.pack(pady=10)

    save_button = tk.Button(activity_window, text="Enregistrer", command=save_changes, state="disabled")
    save_button.pack(pady=10)

    # Ajuster la taille de la fenêtre selon son contenu
    activity_window.update_idletasks()  # S'assurer que les widgets ont été ajoutés et mis à jour
    width = activity_window.winfo_width()
    height = activity_window.winfo_height()
    activity_window.geometry(f"{width}x{height}")  # Définir la taille de la fenêtre

    # Lancer la fenêtre
    activity_window.mainloop()

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

def save_activity():
    nom = activite_name.get()
    description = activite_desc.get()
    lien = activite_link.get()
    objectif_id = objectif_var.get().split(" - ")[0]
    if not nom or not objectif_id:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        return
    add_activite(nom, description, lien, int(objectif_id))
    messagebox.showinfo("Succès", "Activité ajoutée avec succès.")
    display_activities()  # Met à jour la liste d'activités automatiquement
    activite_window.destroy()


def add_new_activity():
    global activite_name, activite_desc, activite_link, activite_window

    activite_window = tk.Toplevel(app)
    activite_window.title("Ajouter une Activité")

    tk.Label(activite_window, text="Nom de l'activité :").pack(pady=5)
    activite_name = tk.Entry(activite_window)
    activite_name.pack(pady=5)

    tk.Label(activite_window, text="Description :").pack(pady=5)
    activite_desc = tk.Entry(activite_window)
    activite_desc.pack(pady=5)

    tk.Label(activite_window, text="Lien :").pack(pady=5)
    activite_link = tk.Entry(activite_window)
    activite_link.pack(pady=5)

    tk.Button(activite_window, text="Enregistrer", command=save_activity).pack(pady=10)
  
def delete_activity():
    selected_activity_index = listbox.curselection()
    if not selected_activity_index:
        messagebox.showerror("Erreur", "Veuillez sélectionner une activité à supprimer.")
        return
    selected_activity = listbox.get(selected_activity_index)
    activite_id = int(selected_activity.split(" - ")[0])  # Récupérer l'ID de l'activité
    delete_activite_by_id(activite_id)  # Passez l'ID de l'activité à la fonction
    listbox.delete(selected_activity_index)
    messagebox.showinfo("Succès", "Activité supprimée avec succès.")


def delete_selected_objectif():
    """Supprime l'objectif sélectionné avec confirmation, affichant d'abord les activités associées."""
    objectif = objectif_var.get()
    if not objectif:
        messagebox.showerror("Erreur", "Veuillez sélectionner un objectif à supprimer.")
        return

    objectif_id = int(objectif.split(" - ")[0])  # Récupérer l'ID de l'objectif
    activites = fetch_activites_by_objectif(objectif_id)

    if activites:
        activites_text = "\n".join([f"{act[0]} - {act[1]}" for act in activites])
        confirmation_text = (
            f"L'objectif sélectionné contient les activités suivantes :\n\n{activites_text}\n\n"
            "Êtes-vous sûr de vouloir supprimer cet objectif et toutes ses activités associées ?"
        )
    else:
        confirmation_text = (
            "L'objectif sélectionné ne contient aucune activité.\n\n"
            "Êtes-vous sûr de vouloir le supprimer ?"
        )

    if messagebox.askyesno("Confirmation", confirmation_text):
        delete_objectif(objectif_id)  # Supprimer l'objectif et ses activités associées
        refresh_objectifs()  # Mettre à jour la liste des objectifs
        listbox.delete(0, tk.END)  # Vider la liste des activités
        messagebox.showinfo("Succès", "Objectif et ses activités supprimés avec succès.")




# Configuration de l'interface utilisateur
app = tk.Tk()
app.title("Ergothérapie - Gestion des Activités")
app.geometry("800x600")
app.configure(bg="#E8F5E9")  # Blanc cassé vert

# Appliquer un thème
style = ttk.Style(app)
style.theme_use('clam')

# Définir les couleurs
primary_color = "#4CAF50"  # Vert
secondary_color = "#FFFFFF"  # Blanc
accent_color = "#388E3C"  # Vert foncé
background_color = "#E8F5E9"  # Blanc cassé vert

# Créer des styles personnalisés
style.configure('TFrame', background=background_color)
style.configure('TButton', background=primary_color, foreground=secondary_color, font=('Helvetica', 10, 'bold'), borderwidth=0, focuscolor=accent_color)
style.configure('TCombobox', background=secondary_color, foreground='black', font=('Helvetica', 10))
style.configure('TLabel', background=background_color, foreground='black', font=('Helvetica', 12))
style.configure('TListbox', background=secondary_color, foreground='black', font=('Helvetica', 10))

# Frame pour le texte en haut
header_frame = ttk.Frame(app, style='TFrame')
header_frame.pack(pady=20)

# Ajouter un texte en haut
header_label = ttk.Label(header_frame, text="Carla DB", style='TLabel', font=('Helvetica', 24, 'bold'))
header_label.pack()

# Frame pour le menu déroulant et le bouton
top_frame = ttk.Frame(app, style='TFrame')
top_frame.pack(pady=20)

# Menu déroulant pour les objectifs
objectif_var = tk.StringVar()
objectif_combobox = ttk.Combobox(top_frame, textvariable=objectif_var, state="readonly", width=40, style='TCombobox')
objectif_combobox.pack(side=tk.LEFT, padx=10)

# Bouton pour supprimer un objectif
delete_objectif_button = ttk.Button(top_frame, text="Supprimer l'Objectif", command=delete_selected_objectif, style='TButton')
delete_objectif_button.pack(side=tk.LEFT, padx=10)

# Bouton "Ajouter un Objectif"
add_objectif_button = ttk.Button(top_frame, text="Ajouter un Objectif", command=add_new_objectif, style='TButton')
add_objectif_button.pack(side=tk.LEFT, padx=10)

# Lier l'événement de sélection d'un objectif à la mise à jour des activités
objectif_combobox.bind("<<ComboboxSelected>>", lambda e: display_activities())

# Liste des activités
listbox = tk.Listbox(app, width=80, height=10, bg=secondary_color, fg='black', font=('Helvetica', 10))
listbox.pack(pady=20)
listbox.bind("<Double-1>", view_activity_details)

# Créer un frame pour les boutons d'activité
activity_button_frame = tk.Frame(app, bg=background_color)
activity_button_frame.pack(pady=20)

# Bouton pour ajouter une activité
ttk.Button(activity_button_frame, text="Ajouter une Activité", command=add_new_activity, style='TButton').pack(side=tk.LEFT, padx=10)

# Bouton pour supprimer une activité
ttk.Button(activity_button_frame, text="Supprimer une Activité", command=delete_activity, style='TButton').pack(side=tk.LEFT, padx=10)

# Initialiser la base de données et rafraîchir les objectifs
init_db()
refresh_objectifs()

# Lancer l'application
app.mainloop()