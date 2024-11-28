import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage
from tkinterdnd2 import DND_FILES, TkinterDnD
from database import delete_objectif, init_db, fetch_objectifs, fetch_activites_by_objectifs, add_objectif, add_activite, update_activite, delete_activite_by_id, fetch_activity_by_id, fetch_objectif_by_id, update_activity_images, update_activity_objectifs, fetch_all_activites
from PIL import Image, ImageTk
import os
import shutil
import webbrowser


# Initialisation de la base de données
init_db()
activity_name_to_id = {}
objectif_name_to_id = {}
objectif_vars = []
objectif_comboboxes = []

def add_objectif_combobox():
    """Ajoute un menu déroulant pour sélectionner un objectif."""
    # Enregistrer les sélections actuelles
    current_selections = [var.get() for var in objectif_vars]

    objectif_var = tk.StringVar()
    objectif_combobox = ttk.Combobox(objectifs_frame, textvariable=objectif_var, state="readonly", width=40, style='TCombobox')
    objectif_combobox.pack(pady=5)
    objectif_combobox.bind("<<ComboboxSelected>>", lambda e: display_activities())
    objectif_vars.append(objectif_var)
    objectif_comboboxes.append(objectif_combobox)
    refresh_objectifs()  # Met à jour les valeurs des menus déroulants

    # Restaurer les sélections
    for var, selection in zip(objectif_vars, current_selections):
        var.set(selection)

    # Lier l'événement <<ComboboxSelected>> à la fonction display_activities pour chaque combobox
    for combobox in objectif_comboboxes:
        combobox.bind("<<ComboboxSelected>>", lambda e: display_activities())


def remove_objectif_combobox():
    """Enlève le dernier menu déroulant ajouté pour sélectionner un objectif."""
    if objectif_comboboxes:
        combobox = objectif_comboboxes.pop()
        combobox.destroy()
        objectif_vars.pop()
        display_activities()  # Met à jour les activités affichées

def refresh_objectifs():
    """Met à jour la liste des objectifs dans les menus déroulants."""
    objectifs = fetch_objectifs()
    objectif_name_to_id.clear()  # Vider le dictionnaire avant de le remplir
    for obj in objectifs:
        objectif_name_to_id[f"{obj[0]} - {obj[1]}"] = obj[0]
    for objectif_var in objectif_vars:
        objectif_var.set("")
    for objectif_combobox in objectif_comboboxes:
        objectif_combobox['values'] = ["Toutes les activités"] + [f"{obj[0]} - {obj[1]}" for obj in objectifs]



def display_activities():
    """Affiche les activités correspondant aux objectifs sélectionnés."""
    if not objectif_vars:
        return

    objectif_ids = []
    for objectif_var in objectif_vars:
        objectif = objectif_var.get()
        if objectif == "Toutes les activités":
            activites = fetch_all_activites()
            break
        if objectif:
            try:
                objectif_id = objectif_name_to_id[objectif]  # Récupérer l'ID de l'objectif à partir du dictionnaire
                objectif_ids.append(objectif_id)
            except KeyError:
                messagebox.showerror("Erreur", "L'objectif sélectionné est invalide.")
                return

    if not objectif_ids and objectif != "Toutes les activités":
        listbox.delete(0, tk.END)
        return

    if objectif != "Toutes les activités":
        activites = fetch_activites_by_objectifs(objectif_ids)

    activity_name_to_id.clear()  # Vider le dictionnaire avant de le remplir

    # Afficher les noms des activités
    listbox.delete(0, tk.END)
    for activite in activites:
        activity_name_to_id[f"{activite[0]} - {activite[1]}"] = activite[0]
        listbox.insert(tk.END, f"{activite[0]} - {activite[1]}")  # Afficher l'ID et le nom

def view_activity_details(event):
    selected_activity_index = listbox.curselection()
    if not selected_activity_index:
        return
    selected_activity_name = listbox.get(selected_activity_index)
    try:
        activite_id = activity_name_to_id[selected_activity_name]  # Récupérer l'ID de l'activité à partir du dictionnaire
    except KeyError:
        messagebox.showerror("Erreur", "L'activité sélectionnée est invalide.")
        return
    activity = fetch_activity_by_id(activite_id)  # Récupérer les détails de l'activité
    open_activity_window(activity)


        
def open_activity_window(activity):
    def toggle_edit():
        state = "normal" if name_entry["state"] == "disabled" else "disabled"
        name_entry.config(state=state)
        desc_entry.config(state=state)
        link_entry.config(state=state)
        save_button.config(state=state)
        add_image_button.config(state=state)
        remove_image_button.config(state=state)
        objectifs_listbox.config(state=state)
        
        if state == "normal":
            link_entry.pack(pady=5)  # Afficher la case pour écrire le lien
            if link_label.winfo_ismapped():
                link_label.pack_forget()  # Masquer le label du lien
            # Afficher tous les objectifs dans la liste
            objectifs_listbox.delete(0, tk.END)
            objectifs = fetch_objectifs()
            for obj in objectifs:
                objectifs_listbox.insert(tk.END, f"{obj[0]} - {obj[1]}")
                if obj[0] in activity['objectifs']:
                    objectifs_listbox.selection_set(tk.END)
        else:
            link_entry.pack_forget()  # Masquer la case pour écrire le lien
            if activity['lien']:
                link_label.pack(pady=5)  # Afficher le label du lien
            # Afficher uniquement les objectifs de l'activité
            objectifs_listbox.delete(0, tk.END)
            for objectif_id in activity['objectifs']:
                objectif = fetch_objectif_by_id(objectif_id)
                objectifs_listbox.insert(tk.END, f"{objectif_id} - {objectif['nom']}")
                objectifs_listbox.selection_set(tk.END)

    def save_changes():
        new_name = name_var.get()
        new_desc = desc_entry.get("1.0", tk.END).strip()  # Récupérer le texte du widget Text
        new_link = link_var.get()
        new_images = [img_label.cget("text") for img_label in image_labels]
        selected_objectifs = objectifs_listbox.curselection()
        objectif_ids = [int(objectifs_listbox.get(i).split(" - ")[0]) for i in selected_objectifs]
        if not new_name:
            messagebox.showerror("Erreur", "Le nom de l'activité est requis.")
            return
        update_activite(activity['id'], new_name, new_desc, new_link)  # ID de l'activité
        update_activity_images(activity['id'], new_images)  # Mettre à jour les images
        update_activity_objectifs(activity['id'], objectif_ids)  # Mettre à jour les objectifs
        messagebox.showinfo("Succès", "Modifications enregistrées.")
        display_activities()  # Rafraîchit la liste des activités
        activity_window.destroy()

    def add_images():
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_paths:
            for file_path in file_paths:
                img = Image.open(file_path)
                img.thumbnail((225, 225), Image.Resampling.LANCZOS)  # Augmenter la taille de 50%
                img = ImageTk.PhotoImage(img)
                img_label = tk.Label(images_frame, image=img, text=file_path, bg=background_color)
                img_label.image = img  # Keep a reference to avoid garbage collection
                img_label.pack(side=tk.LEFT, padx=5)
                img_label.bind("<Button-1>", lambda e, label=img_label: select_image(label))
                image_labels.append(img_label)

    def remove_selected_images():
        for img_label in selected_images:
            img_label.destroy()
            image_labels.remove(img_label)
        selected_images.clear()

    def select_image(label):
        if label in selected_images:
            selected_images.remove(label)
            label.config(bg=background_color)
        else:
            selected_images.append(label)
            label.config(bg="red")

    def open_link(event, url):
        webbrowser.open_new(url)

    # Création de la fenêtre
    activity_window = tk.Toplevel(app)
    activity_window.title("Détails de l'activité")
    activity_window.geometry("1100x850")
    activity_window.configure(bg=background_color)

    # Widgets
    tk.Label(activity_window, text="Nom de l'activité :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    name_var = tk.StringVar(value=activity['nom'])
    name_entry = tk.Entry(activity_window, textvariable=name_var, state="disabled", width=70, bg=secondary_color, fg='black', font=('Helvetica', 10))
    name_entry.pack(pady=5)

    tk.Label(activity_window, text="Objectifs :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    objectifs_frame = tk.Frame(activity_window, bg=background_color)
    objectifs_frame.pack(pady=5)
    objectifs_listbox = tk.Listbox(objectifs_frame, selectmode=tk.MULTIPLE, bg=secondary_color, fg='black', font=('Helvetica', 10), width=70, height=5)
    for objectif_id in activity['objectifs']:
        objectif = fetch_objectif_by_id(objectif_id)
        objectifs_listbox.insert(tk.END, f"{objectif_id} - {objectif['nom']}")
        objectifs_listbox.selection_set(tk.END)
    objectifs_listbox.pack(pady=5)

    # Frame pour les images
    images_frame = tk.Frame(activity_window, bg=background_color)
    images_frame.pack(pady=5)

    tk.Label(activity_window, text="Images :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    image_labels = []
    selected_images = []
    for image_path in activity['images']:
        img = Image.open(image_path)
        img.thumbnail((225, 225), Image.Resampling.LANCZOS)  # Augmenter la taille de 50%
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(images_frame, image=img, text=image_path, bg=background_color)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(side=tk.LEFT, padx=5)
        img_label.bind("<Button-1>", lambda e, label=img_label: select_image(label))
        image_labels.append(img_label)

    # Frame pour les boutons d'images
    buttons_frame = tk.Frame(activity_window, bg=background_color)
    buttons_frame.pack(pady=5)

    add_image_button = tk.Button(buttons_frame, text="Ajouter", command=add_images, state="disabled", bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold'))
    add_image_button.pack(side=tk.LEFT, padx=3)

    remove_image_button = tk.Button(buttons_frame, text="Supprimer", command=remove_selected_images, state="disabled", bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold'))
    remove_image_button.pack(side=tk.LEFT, padx=3)

    tk.Label(activity_window, text="Description :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    desc_entry = tk.Text(activity_window, height=7, width=100, bg=secondary_color, fg='black', font=('Helvetica', 10))
    desc_entry.insert(tk.END, activity['description'])
    desc_entry.config(state="disabled")
    desc_entry.pack(pady=5)

    # Frame pour le lien
    link_frame = tk.Frame(activity_window, bg=background_color)
    link_frame.pack(pady=5)

    tk.Label(link_frame, text="Lien :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    link_var = tk.StringVar(value=activity['lien'])
    link_entry = tk.Entry(link_frame, textvariable=link_var, state="disabled", width=70, bg=secondary_color, fg='black', font=('Helvetica', 10))

    if activity['lien']:
        link_label = tk.Label(link_frame, text=activity['lien'], bg=background_color, fg='blue', font=('Helvetica', 10), cursor="hand2")
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda event: open_link(event, activity['lien']))

    # Frame pour les boutons de modification et d'enregistrement
    edit_save_frame = tk.Frame(activity_window, bg=background_color)
    edit_save_frame.pack(pady=10)

    edit_button = tk.Button(edit_save_frame, text="Modifier", command=toggle_edit, bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold'))
    edit_button.pack(side=tk.LEFT, padx=3)

    save_button = tk.Button(edit_save_frame, text="Enregistrer", command=save_changes, state="disabled", bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold'))
    save_button.pack(side=tk.LEFT, padx=3)

    # Lancer la fenêtre
    activity_window.mainloop()

def add_new_objectif():
    """Ajoute un nouvel objectif dans la base de données."""
    def save_objectif():
        nom = objectif_name.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom de l'objectif est requis.")
            return
        add_objectif(nom)
        refresh_objectifs()
        objectif_window.destroy()

    objectif_window = tk.Toplevel(app)
    objectif_window.title("Ajouter un Objectif")
    objectif_window.configure(bg=background_color)  # Appliquer la couleur de fond

    tk.Label(objectif_window, text="Nom de l'objectif :", bg=background_color, fg='black', font=('Helvetica', 12), height=3, width=50).pack(pady=5)
    objectif_name = tk.Entry(objectif_window, bg=secondary_color, fg='black', font=('Helvetica', 10), width=50)
    objectif_name.pack(pady=5)

    # Lier l'événement <Return> à la fonction save_objectif
    objectif_name.bind("<Return>", lambda event: save_objectif())

    tk.Button(objectif_window, text="Enregistrer", command=save_objectif, bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold')).pack(pady=10)

def save_activity():
    nom = activite_name.get().strip()
    description = activite_desc.get("1.0", tk.END).strip()  # Récupérer le texte du widget Text
    lien = activite_link.get().strip()
    image_paths = activite_image_paths.get().strip().split(";")
    selected_objectifs = objectifs_listbox.curselection()
    objectif_ids = [int(objectifs_listbox.get(i).split(" - ")[0]) for i in selected_objectifs]
    
    if not nom or not description or not objectif_ids:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
        return
    
    # Vérifier si des images ont été fournies
    if image_paths == ['']:
        image_paths = []

    add_activite(nom, description, lien, objectif_ids, image_paths)
    messagebox.showinfo("Succès", "Activité ajoutée avec succès.")
    display_activities()  # Met à jour la liste d'activités automatiquement
    activite_window.destroy()


def add_new_activity():
    global activite_name, activite_desc, activite_link, activite_image_paths, activite_window, image_text, objectifs_listbox

    def select_images():
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_paths:
            local_image_paths = []
            for file_path in file_paths:
                # Créer le dossier local pour les images s'il n'existe pas
                local_image_dir = os.path.join(os.getcwd(), "images")
                os.makedirs(local_image_dir, exist_ok=True)

                # Générer un nom de fichier incrémenté
                base_name = os.path.basename(file_path)
                name, ext = os.path.splitext(base_name)
                counter = 1
                new_name = f"{name}_{counter}{ext}"
                new_path = os.path.join(local_image_dir, new_name)
                while os.path.exists(new_path):
                    counter += 1
                    new_name = f"{name}_{counter}{ext}"
                    new_path = os.path.join(local_image_dir, new_name)

                # Copier l'image dans le dossier local
                shutil.copy(file_path, new_path)
                local_image_paths.append(new_path)

            activite_image_paths.set(";".join(local_image_paths))
            image_text.delete("1.0", tk.END)
            image_text.insert(tk.END, "\n".join(local_image_paths))

    def drop(event):
        file_paths = event.data.split()
        activite_image_paths.set(";".join(file_paths))
        image_text.delete("1.0", tk.END)
        image_text.insert(tk.END, "\n".join(file_paths))

    activite_window = tk.Toplevel(app)
    activite_window.title("Ajouter une Activité")
    activite_window.geometry("1100x850")
    activite_window.configure(bg=background_color)

    tk.Label(activite_window, text="Nom de l'activité :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    activite_name = tk.Entry(activite_window, bg=secondary_color, fg='black', font=('Helvetica', 10), width=70)
    activite_name.pack(pady=5)

    tk.Label(activite_window, text="Description :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    activite_desc = tk.Text(activite_window, height=10, width=100, bg=secondary_color, fg='black', font=('Helvetica', 10))
    activite_desc.pack(pady=5)

    tk.Label(activite_window, text="Lien :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    activite_link = tk.Entry(activite_window, bg=secondary_color, fg='black', font=('Helvetica', 10), width=70)
    activite_link.pack(pady=5)

    tk.Label(activite_window, text="Objectifs :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    objectifs_listbox = tk.Listbox(activite_window, selectmode=tk.MULTIPLE, bg=secondary_color, fg='black', font=('Helvetica', 10), width=70, height=5)
    objectifs = fetch_objectifs()
    for obj in objectifs:
        objectifs_listbox.insert(tk.END, f"{obj[0]} - {obj[1]}")
    objectifs_listbox.pack(pady=5)

    tk.Label(activite_window, text="Images :", bg=background_color, fg='black', font=('Helvetica', 12)).pack(pady=5)
    activite_image_paths = tk.StringVar()
    image_text = tk.Text(activite_window, height=5, width=70, bg=secondary_color, fg='black', font=('Helvetica', 10))
    image_text.pack(pady=5)
    image_text.drop_target_register(DND_FILES)
    image_text.dnd_bind('<<Drop>>', drop)
    tk.Button(activite_window, text="Sélectionner des images", command=select_images, bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold')).pack(pady=5)

    tk.Button(activite_window, text="Enregistrer", command=save_activity, bg=primary_color, fg=secondary_color, font=('Helvetica', 10, 'bold')).pack(pady=10)

    # Configurer les poids des colonnes et des lignes
    activite_window.grid_columnconfigure(0, weight=1)
  
def delete_activity():
    """Supprime l'activité sélectionnée."""
    selected_activity_index = listbox.curselection()
    if not selected_activity_index:
        messagebox.showerror("Erreur", "Veuillez sélectionner une activité à supprimer.")
        return
    selected_activity_name = listbox.get(selected_activity_index)
    try:
        activite_id = activity_name_to_id[selected_activity_name]  # Récupérer l'ID de l'activité à partir du dictionnaire
    except KeyError:
        messagebox.showerror("Erreur", "L'activité sélectionnée est invalide.")
        return

    if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette activité ?"):
        delete_activite_by_id(activite_id)  # Supprimer l'activité et ses images associées
        display_activities()  # Rafraîchir la liste des activités
        messagebox.showinfo("Succès", "L'activité a été supprimée avec succès.")

def delete_selected_objectif():
    """Supprime l'objectif sélectionné et ses activités associées."""
    if not objectif_vars:
        messagebox.showerror("Erreur", "Veuillez sélectionner un objectif à supprimer.")
        return
    objectif = objectif_vars[0].get()
    if not objectif:
        messagebox.showerror("Erreur", "Veuillez sélectionner un objectif à supprimer.")
        return
    try:
        objectif_id = objectif_name_to_id[objectif]  # Récupérer l'ID de l'objectif
    except KeyError:
        messagebox.showerror("Erreur", "L'objectif sélectionné est invalide.")
        return

    # Récupérer les activités associées à l'objectif
    activites = fetch_activites_by_objectifs([objectif_id])
    activites_list = "\n".join([f"{activite[0]} - {activite[1]}" for activite in activites])

    if not activites_list:
        activites_list = "Aucune activité associée."

    confirmation_message = (
        f"Êtes-vous sûr de vouloir supprimer l'objectif suivant et toutes ses activités associées ?\n\n"
        f"Objectif : {objectif}\n\n"
        f"Activités associées :\n{activites_list}"
    )

    if messagebox.askyesno("Confirmation", confirmation_message):
        delete_objectif(objectif_id)  # Supprimer l'objectif et ses activités associées
        refresh_objectifs()  # Mettre à jour la liste des objectifs
        listbox.delete(0, tk.END)  # Vider la liste des activités

def search_activities(search_term):
    """Recherche les activités par titre."""
    if not search_term:
        messagebox.showerror("Erreur", "Veuillez entrer un terme de recherche.")
        return

    activites = fetch_all_activites()
    activity_name_to_id.clear()  # Vider le dictionnaire avant de le remplir

    # Filtrer les activités par titre
    filtered_activites = [activite for activite in activites if search_term.lower() in activite[1].lower()]

    # Afficher les noms des activités filtrées
    listbox.delete(0, tk.END)
    for activite in filtered_activites:
        activity_name_to_id[f"{activite[0]} - {activite[1]}"] = activite[0]
        listbox.insert(tk.END, f"{activite[0]} - {activite[1]}")  # Afficher l'ID et le nom

# Configuration de l'interface utilisateur
app = TkinterDnD.Tk()
app.title("Ergothérapie - Gestion des Activités")
app.geometry("1100x850")
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
header_label = ttk.Label(header_frame, text="love you DB", style='TLabel', font=('Helvetica', 24, 'bold'))
header_label.pack()

# Frame pour les menus déroulants et les boutons
top_frame = ttk.Frame(app, style='TFrame')
top_frame.pack(pady=20)

# Frame pour les menus déroulants des objectifs
objectifs_frame = ttk.Frame(top_frame, style='TFrame')
objectifs_frame.pack(side=tk.LEFT, padx=10)

# Ajouter le premier menu déroulant pour les objectifs
add_objectif_combobox()

# Bouton pour ajouter un menu déroulant
add_objectif_button = ttk.Button(top_frame, text="Plus", command=add_objectif_combobox, style='TButton')
add_objectif_button.pack(side=tk.LEFT, padx=5)

# Bouton pour enlever un menu déroulant
remove_objectif_button = ttk.Button(top_frame, text="Moins", command=remove_objectif_combobox, style='TButton')
remove_objectif_button.pack(side=tk.LEFT, padx=5)

# Bouton pour supprimer un objectif
delete_objectif_button = ttk.Button(top_frame, text="Supprimer l'Objectif", command=delete_selected_objectif, style='TButton')
delete_objectif_button.pack(side=tk.LEFT, padx=10)

# Bouton "Ajouter un Objectif"
add_new_objectif_button = ttk.Button(top_frame, text="Ajouter un Objectif", command=add_new_objectif, style='TButton')
add_new_objectif_button.pack(side=tk.LEFT, padx=10)

# Barre de recherche
search_frame = ttk.Frame(app, style='TFrame')
search_frame.pack(pady=10)

search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
search_entry.pack(side=tk.LEFT, padx=10)

# Lier l'événement <Return> à la fonction search_activities
search_entry.bind("<Return>", lambda event: search_activities(search_var.get()))

search_button = ttk.Button(search_frame, text="Rechercher", command=lambda: search_activities(search_var.get()), style='TButton')
search_button.pack(side=tk.LEFT, padx=10)
# Liste des activités
listbox = tk.Listbox(app, width=80, height=10, bg=secondary_color, fg='black', font=('Helvetica', 10))
listbox.pack(pady=20)
listbox.bind("<Double-1>", view_activity_details)

# Créer un frame pour les boutons d'activité
activity_button_frame = tk.Frame(app, bg=background_color)
activity_button_frame.pack(pady=20)

icon_image = PhotoImage(file="icon.png")
app.iconphoto(True, icon_image)
# Bouton pour ajouter une activité
ttk.Button(activity_button_frame, text="Ajouter une Activité", command=add_new_activity, style='TButton').pack(side=tk.LEFT, padx=10)

# Bouton pour supprimer une activité
ttk.Button(activity_button_frame, text="Supprimer une Activité", command=delete_activity, style='TButton').pack(side=tk.LEFT, padx=10)

# Initialiser la base de données et rafraîchir les objectifs
init_db()
refresh_objectifs()

# Lancer l'application
app.mainloop()