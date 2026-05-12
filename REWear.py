#import all libraries needed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from PIL import Image, ImageTk
import io

#form the database
class database:
    def __init__(self, db_name='Wardrobe.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    #base wardrobe databse
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wardrobe (
                clothes_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL,
                image BLOB NOT NULL,
                color VARCHAR(20) NOT NULL,
                clothing_type VARCHAR(20) NOT NULL DEFAULT 'Other',
                fit VARCHAR(20),
                length VARCHAR(20),
                neckline VARCHAR(20),
                sleeve VARCHAR(20),
                rise VARCHAR(20), 
                style VARCHAR(20),
                closure VARCHAR(20)
            )
        """)

    #database for clothes user isn't keeping
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS discarded_wardrobe (
                clothes_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL,
                image BLOB NOT NULL,
                color VARCHAR(20) NOT NULL,
                clothing_type VARCHAR(20) NOT NULL DEFAULT 'Other',
                fit VARCHAR(20),
                length VARCHAR(20),
                neckline VARCHAR(20),
                sleeve VARCHAR(20),
                rise VARCHAR(20), 
                style VARCHAR(20),
                closure VARCHAR(20)
            )
       """)
        
        self.conn.commit()

    #takes user input and puts it in wardrobe database
    def clothes_entry(self, name, image_path, color, clothing_type, fit= None, length = None, neckline = None, sleeve = None, rise = None, style = None, closure = None):
        try:
            with open(image_path, 'rb') as file:
                blob_data = file.read()
                
            self.cursor.execute(
                "INSERT INTO wardrobe (name, clothing_type, image, color, fit, length, neckline, sleeve, rise, style, closure) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, clothing_type, blob_data, color, fit, length, neckline, sleeve, rise, style, closure)
                )
            
            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"Error adding clothes: {e}")
            return False

    #outputs all clothes entries in wardrobe database
    def get_clothes(self):
        self.cursor.execute("""
            SELECT clothes_id, name, image, color, clothing_type,
            fit, length, neckline, sleeve, rise, style, closure
            FROM wardrobe
        """)
        return self.cursor.fetchall()

    #takes entry from wardrobe database and inserts it into the discarded wardrobe
    def discard_item(self, clothes_id):
        self.cursor.execute("SELECT name, image, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure FROM wardrobe WHERE clothes_id = ?", (clothes_id,))
        item = self.cursor.fetchone()
        if item:
            self.cursor.execute(
                "INSERT INTO discarded_wardrobe (name, image, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                item
            )
            self.cursor.execute("DELETE FROM wardrobe WHERE clothes_id = ?", (clothes_id,))
            self.conn.commit()
            return True
        return False
    
    #outputs all clothes entries in discarded wardrobe database
    def get_discarded_clothes(self):
        self.cursor.execute("SELECT clothes_id, name, image, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure FROM discarded_wardrobe")
        return self.cursor.fetchall()
    
    #outputs the images from the discarded wardrobe database based on the clothes_id
    def get_discarded_clothes_image(self, clothes_id):
        self.cursor.execute("SELECT image FROM discarded_wardrobe WHERE clothes_id = ?", (clothes_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    #comepletely clears the database and resets clothes_id counter
    def clear_database(self):
        self.cursor.execute("DELETE FROM wardrobe")
        self.cursor.execute("DELETE FROM discarded_wardrobe")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='wardrobe'")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='discarded_wardrobe'")
        self.conn.commit()
        print("Wardrobe cleared")   
    
class REWearApp:
    def __init__(self, root):
        self.root = root
        self.root.title("REWear")
        self.root.geometry("1280x720")
        self.root.configure(bg="#FFE6ED")
        self.db = database()
        style = ttk.Style()

        style.configure("TFrame", background="#FFE6ED")

        #menu
        opt_frame = tk.Frame(root, bg="#FFE6ED")
        opt_frame.pack(fill="x", padx=10, pady=(10, 0))

        #menu button
        self.opt_menubutton = tk.Menubutton(opt_frame, text="Menu", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED")
        self.opt_menubutton.pack(side=tk.LEFT, padx=5)

        #menu options
        self.opt_menu = tk.Menu(self.opt_menubutton, tearoff=0, font=("UD Digi Kyokasho NP-B", 12), bg ="#FFE6ED", fg="#3E2723", activebackground="#CF7486", activeforeground="#FFE6ED")
        self.opt_menubutton.config(menu=self.opt_menu)
        self.opt_menu.add_command(label="Wardrobe", command=self.show_wardrobe)
        self.opt_menu.add_command(label="Discarded", command=self.show_discarded)
        self.opt_menu.add_command(label="Clear Wardrobe", command=self.clear_wardrobe)

        tab_frame = tk.Frame(root, bg="#FFE6ED")
        tab_frame.pack(fill="both", expand=True, padx=15, pady=15)
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)
        
        self.wardrobe_frame = ttk.Frame(tab_frame, style="TFrame")
        self.discarded_clothes_frame = ttk.Frame(tab_frame, style="TFrame")

        self.wardrobe_frame.pack()

        self.wardrobe_frame.grid(row=0, column=0, sticky="nsew")
        self.discarded_clothes_frame.grid(row=0, column=0, sticky="nsew")

        #creates tabs
        self.create_wardrobe_tab()
        self.create_discarded_tab()

        #makes the wardrobe the first screen you see
        self.show_wardrobe()

        #makes the wardrobe and discarded updated
        self.load_wardrobe()
        self.load_discarded()

    def show_wardrobe(self):
        self.wardrobe_frame.tkraise()

    def show_discarded(self):
        self.discarded_clothes_frame.tkraise()

    #creates the wardrobe tab
    def create_wardrobe_tab(self): 
        frame = self.wardrobe_frame
        style = ttk.Style()
        style.configure("TCombobox", foreground="#3E2723")
        
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        #all the entry fields for clothinh
        tk.Label(frame, text="Add Clothing", font=("UD Digi Kyokasho NP-B", 14), bg="#FFE6ED", fg="#3E2723").grid(row=0, column=0, sticky="w")

        tk.Label(frame, text="Name:", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723").grid(row=1, column=0, sticky="w", padx=0, pady=5)
        self.name_entry = tk.Entry(frame, font=("UD Digi Kyokasho NP-B", 12), fg="#3E2723")
        self.name_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame, text="Image:", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723").grid(row=2, column=0, sticky="w", padx=0, pady=5)
        self.image_path_var = tk.StringVar()
        self.image_entry = tk.Entry(frame, textvariable=self.image_path_var, state='readonly', font=("UD Digi Kyokasho NP-B", 12), fg="#3E2723")
        self.image_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        tk.Button(frame, text="Browse", command=self.select_image, font=("UD Digi Kyokasho NP-B", 12), bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED").grid(row=2, column=2, sticky="w", padx=5, pady=5)

        tk.Label(frame, text="Color:", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723").grid(row=3, column=0, sticky="w", padx=0, pady=5)
        self.color_combo = ttk.Combobox(frame, style="TCombobox", font=("UD Digi Kyokasho NP-B", 12), values=["Red", "Yellow", "Blue", "Green", "Purple", "Orange", "Pink", "Brown", "Gray", "Black", "White"])
        self.color_combo.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame, text="Type:", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723").grid(row=4, column=0, sticky="w", padx=0, pady=5)
        self.clothing_type_combobox = ttk.Combobox(frame, style="TCombobox", font=("UD Digi Kyokasho NP-B", 12), values=["Top", "Pants", "Skirt", "Outerwear", "Dress"])
        self.clothing_type_combobox.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.clothing_type_combobox.bind("<<ComboboxSelected>>", self.clothing_type_options)

        self.clothing_type_options_frame = tk.Frame(frame, bg="#FFE6ED")
        self.clothing_type_options_frame.grid(row=5, column=0, sticky="w", columnspan=3, padx=5, pady=5)

        self.clothing_type_options_vars = {}
        self.clothing_type_options_widgets = {}

        tk.Button(frame, text="Save Clothing", command=self.save_entry, font=("UD Digi Kyokasho NP-B", 12), bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED").grid(row=6, column=0, sticky="w", padx=5, pady=10)

        #gallery for wardrobe
        frame.grid_rowconfigure(10, weight=1)
        tk.Label(frame, text="Your Wardrobe", font=("UD Digi Kyokasho NP-B", 14), bg="#FFE6ED", fg="#3E2723").grid(row=10, column=0, sticky="w", padx=5, pady=10)
        self.wardrobe_canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        wardrobe_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.wardrobe_canvas.yview)
        self.wardrobe_scrollframe = tk.Frame(self.wardrobe_canvas, bg="white")
        
        self.wardrobe_scrollframe.bind("<Configure>",lambda e: self.wardrobe_canvas.configure(scrollregion=self.wardrobe_canvas.bbox("all")))
        
        self.wardrobe_canvas.create_window((0, 0), window=self.wardrobe_scrollframe, anchor="nw")
        self.wardrobe_canvas.configure(yscrollcommand=wardrobe_scrollbar.set)
        
        self.wardrobe_canvas.grid(row=10, column=1, columnspan=2, sticky="nsew", padx=10, pady=5)
        wardrobe_scrollbar.grid(row=10, column=3, sticky="ns", padx=(0, 10), pady=5)

    #extra fields based on the clothing type
    def clothing_type_options(self, event=None):
        for widget in self.clothing_type_options_frame.winfo_children():
            widget.destroy()
        self.clothing_type_vars = {}
        self.clothing_type_widget = {}

        clothing_type = self.clothing_type_combobox.get()
        row = 0
 
        options_config = {
            "Top": [
                ("Fit", "fit", ["Fitted", "Regular", "Oversized"]),
                ("Neckline", "neckline", ["Crew Neck", "V Neck", "Scoop Neck", "Turtleneck", "Off The Shoulder", "Halter", "Collar", "Strappless"]),
                ("Length", "length", ["Cropped", "Regular", "Long"]),
                ("Sleeve", "sleeve", ["Sleeveless", "Short Sleeve", "3/4 Sleeve", "Long Sleeve"])
            ],
            "Pants": [
                ("Fit", "fit", ["Skinny", "Straight", "Tappered", "Wide", "Baggy", "Bootcut", "Flared"]),
                ("Rise", "rise", ["Low Rise", "Mid Rise", "High Rise"]),
                ("Length", "length", ["Short", "Long Shorts", "Mid Calf", "Ankle", "Full Length"])
            ],
            "Skirt": [
                ("Fit", "fit", ["Pleated", "Tiered", "Straight", "Pencil", "Mermaid"]),
                ("Length", "length", ["Mini", "Above Knee", "Knee", "Midi", "Maxi", "Floor Length"])
            ],
            "Outerwear": [
                ("Fit", "fit", ["Cropped", "Slim Fit", "Relaxed", "Long", "Oversized"]),
                ("Style", "style", ["Jacket", "Cardigan", "Vest", "Coat"]),
                ("Closure", "closure", ["Zipper", "Buttons", "Open Front", "Snaps"]),
            ],
            "Dress": [
                ("Fit", "fit", ["Fitted", "A-Line", "Fit and Flare", "Shift", "Oversized", "Mermaid"]),
                ("Neckline", "neckline", ["Crew Neck", "V Neck", "Scoop Neck", "Turtleneck", "Off The Shoulder", "Halter", "Collar", "Strappless"]),
                ("Sleeve", "sleeve", ["Sleeveless", "Short Sleeve", "3/4 Sleeve", "Long Sleeve"]),
                ("Length", "length", ["Mini", "Above Knee", "Knee", "Midi", "Maxi", "Floor Length"])
            ],
            "Other": []

        }
        
        options = options_config.get(clothing_type, [])

        self.clothing_type_options_frame.grid()

        for label_text, option_key, choices in options:
            tk.Label(self.clothing_type_options_frame, text=label_text + ":", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723").grid(row=row, column=0, sticky="w", padx=10, pady=5)
            var = tk.StringVar()
            self.clothing_type_vars[option_key] = var
            combo = ttk.Combobox(self.clothing_type_options_frame, textvariable=var, values=choices, state="readonly", font=("UD Digi Kyokasho NP-B", 12), background="#F5F1E6", foreground="#3E2723")
            combo.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
            self.clothing_type_options_widgets[option_key] = combo
            row += 1

    #creates tab for discarded clothes
    def create_discarded_tab(self):
        frame = self.discarded_clothes_frame
        style = ttk.Style()
        frame.grid_columnconfigure(1, weight=1)

        self.next_button = tk.Button(frame, text="What Next?", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, command=self.next_steps, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED").grid(row=0, column=2, sticky="e", padx=10)

        style.configure("Treeview.Heading", font=("UD Digi Kyokasho NP-B", 12), foreground="#3E2723")

        tk.Label(frame, text="Discarded Clothes", font=("UD Digi Kyokasho NP-B", 14), bg="#FFE6ED", fg="#3E2723").grid(row=1, column=0, columnspan=2, pady=5)

        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        
        #table of discarded clothes
        tk.Label(frame, font=("UD Digi Kyokasho NP-B", 14), text="Selected Image: ", bg="#FFE6ED").grid(row=1, column=2, pady=10)
        
        self.discarded_tree = ttk.Treeview(frame, columns=("Clothes ID", "Name", "Color", "Type", "Fit", "Length"), show="headings", height=10)
        self.discarded_tree.heading("Clothes ID", text="Clothes ID")
        self.discarded_tree.column("Clothes ID", width=80)      

        self.discarded_tree.heading("Name", text="Name")
        self.discarded_tree.column("Name", width=100)

        self.discarded_tree.heading("Color", text="Color")
        self.discarded_tree.column("Color", width=80)

        self.discarded_tree.heading("Type", text="Type")
        self.discarded_tree.column("Type", width=80)

        self.discarded_tree.heading("Fit", text="Fit")
        self.discarded_tree.column("Fit", width=80)

        self.discarded_tree.heading("Length", text="Length")
        self.discarded_tree.column("Length", width=80)

       
        tree_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.discarded_tree.yview)
        self.discarded_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.discarded_tree.grid(row=2, column=0, columnspan=2, padx=(10, 0), pady=5, sticky="nsew")
        tree_scrollbar.grid(row=2, column=2, sticky="nsw", pady=5)

        self.discarded_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.discarded_tree.bind("<<TreeviewSelect>>", self.display_discarded_image)

        #image display
        self.discarded_image_label = tk.Label(frame, font=("UD Digi Kyokasho NP-B", 12), bg="white", relief=tk.SUNKEN, bd=2, width=30, height=20)
        self.discarded_image_label.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")

        #buttons moving and clearing entries
        button_frame = tk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="Load Discarded", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED",command=self.load_discarded).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Restore Item", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED",command=self.restore_item).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Discarded", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED",command=self.clear_discarded).pack(side=tk.LEFT, padx=5)

    #selects images for wardrobe gallery
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.image_path_var.set(file_path)

    #saves user input
    def save_entry(self):
        name = self.name_entry.get()
        image_path = self.image_path_var.get()
        color = self.color_combo.get()
        clothing_type = self.clothing_type_combobox.get()

        if not all([name,image_path, color, clothing_type]):
            messagebox.showerror("Error", "Please fill in all boxes!")
            return
        
        #gets the values for the fields based on clothing_type
        fit = self.clothing_type_vars.get("fit", tk.StringVar(value=None)).get()
        length = self.clothing_type_vars.get("length", tk.StringVar(value=None)).get()
        neckline = self.clothing_type_vars.get("neckline", tk.StringVar(value=None)).get()
        sleeve = self.clothing_type_vars.get("sleeve", tk.StringVar(value=None)).get()
        rise = self.clothing_type_vars.get("rise", tk.StringVar(value=None)).get()
        style = self.clothing_type_vars.get("style", tk.StringVar(value=None)).get()
        closure = self.clothing_type_vars.get("closure", tk.StringVar(value=None)).get()

        #empty fields turn into none
        fit = fit or None
        length = length or None
        neckline = neckline or None
        sleeve = sleeve or None
        rise = rise or None
        style = style or None
        closure = closure or None

        #resets entry fields and readies it for the next item to be entered
        if self.db.clothes_entry(name, image_path, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure):
            messagebox.showinfo("Success", "Clothing item added to wardrobe!")
            self.name_entry.delete(0, tk.END)
            self.image_path_var.set("")
            self.color_combo.set("")
            self.clothing_type_combobox.set("")
            for var in self.clothing_type_vars.values():
                var.set("")
            for widget in self.clothing_type_options_frame.winfo_children():
                widget.destroy()
            self.clothing_type_vars = {}
            self.load_wardrobe()
        else:
            messagebox.showerror("Error", "Clothing item could not be added. Please try again!")

    #shows all the details of clothes after clicking on its image in the gallery
    def show_item_details(self, clothes_id):
        self.db.cursor.execute(
            "SELECT clothes_id, name, image, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure FROM wardrobe WHERE clothes_id = ?",
            (clothes_id,)
        )
        item = self.db.cursor.fetchone()
        
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        
        clothes_id, name, blob_data, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure = item
        
        #creates the pop up
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Details - {name}")
        details_window.geometry("520x850")
        details_window.configure(bg="#FFE6ED")
        
        #image for the popup
        if blob_data:
            try:
                image = Image.open(io.BytesIO(blob_data))
                image = image.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                img_label = tk.Label(details_window, image=photo)
                img_label.image = photo
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Error displaying image: {e}")
        
        #shows all details that are filled. If not, it wont show
        details_frame = tk.Frame(details_window, bg="#FFE6ED")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        details = [
            ("ID", clothes_id),
            ("Name", name),
            ("Color", color),
            ("Clothing Type", clothing_type),
            ("Fit", fit),
            ("Length", length),
            ("Neckline", neckline),
            ("Sleeve", sleeve),
            ("Rise", rise),
            ("Style", style),
            ("Closure", closure)
        ]
        
        for label, value in details:
            if value is None:
                continue
            detail_frame = tk.Frame(details_frame, bg="#FFE6ED")
            detail_frame.pack(fill="x", pady=5)
            
            tk.Label(detail_frame, text=f"{label}:", font=("UD Digi Kyokasho NP-B", 12), width=15, anchor="w", bg="#FFE6ED").pack(side="left")
            tk.Label(detail_frame, text=str(value), font=("UD Digi Kyokasho NP-R", 12), bg="#FFE6ED").pack(side="left", fill="x", expand=True)

        tips_frame = tk.LabelFrame(details_window, text="Styling Tips", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723", padx=10, pady=10)
        tips_frame.pack(fill="both", expand=True, padx=20, pady=10)

        #based on clothing type and details, a styling tip will be shown
        tips = []
        if clothing_type == "Top":
            if fit == "Fitted":
                tips.append("Pair with wide/baggy bottoms for a balanced and trendy silhouette.")
            if fit == "Oversized":
                tips.append("Pair with baggy pants for a streetwear-inspired look.")
                tips.append("Tuck in the front and pair with jeans or shorts for a casual look.")
            if neckline == "Collar":
                tips.append("Pair with dress pants or a skirt for a polished and professional look.")
            if length == "Cropped":
                tips.append("Pair with low waisted bottoms for a Y2K-inspired look.")
            if length == "Long":
                tips.append("Wear with a jacket or sweater for a cool and casual layered look.")
            if sleeve == "Short Sleeve":
                tips.append("Wear over a long sleeve shirt if you want to cover more skin.")
                tips.append("Wear over a dress for a 90s-inspired look.")
        elif clothing_type == "Pants":
            if fit == "Wide" or fit == "Baggy":
                tips.append("Pair with a fitted top for a balanced and trendy silhouette.")
            if fit == "Flared":
                tips.append("Pair with a fitted top to emphasize the flare of the pants and your waistline.")
            if fit == "Bootcut":
                tips.append("Wear with heels or boots to enlongate your legs.")
            if rise == "Low Rise":
                tips.append("Pair with a cropped shirt for a Y2K-inspired look.")
            if rise == "High Rise":
                tips.append("Consider wearing a voluminous top to highlight the high waist.")
            if length == "Ankle":
                tips.append("Pair with a stylish pair of shoes like loafers or sneakers to show them off.")
        elif clothing_type == "Skirt":
            if fit == "Pleated":
                tips.append("Pair with a sweater for a cute and cozy look.")
            if fit == "Pencil":
                tips.append("Wear with a fitted top and heels for a polished and professional look.")
            if length == "Mini":
                tips.append("Add a cropped jacket or sweater for a structured look, perfect for any occassion.")
            if length == "Maxi":
                tips.append("Throw on a sweater or pair with a flowy blouse to use the skirt year-round.")
        elif clothing_type == "Outerwear":
            if style == "Jacket":
                tips.append("Utilize the jacket to add shape wherever you need, the most versatile item you can have!")
            if style == "Cardigan":
                tips.append("Layer of a collared shirt or a crew neck, perfect for dressing up or down.")    
            if fit == "Cropped":
                tips.append("Wear on top of slim fit pants to emphasize the shape of the jacket")
            if fit == "Long":
                tips.append("Add a belt to cinch the waist and create a more defined silhouette.")   
        elif clothing_type == "Dress":    
            if fit == "Fitted":
                tips.append("Wear a long coat over your shoulders for a classy, sophisticated look.")
            if fit == "Oversized":
                tips.append("Add a belt around your waist to add some shape to your outfit and get a second look out of one dress.")
            if length == "Mini":
                tips.append("Pair with knee high boots for a modern look.")
            if length == "Midi":
                tips.append("Add a belt or a corset seperate the bodice and skirt of the dress and give a more defined waistline, especially if there's none.")

        #if no tip is set, this will show
        if not tips:
            tips.append("The only one who knows your style best is you! Feel free to experiment!")

        for tip in tips:
            tk.Label(tips_frame, text=tip, font=("UD Digi Kyokasho NP-R", 12), bg="#FFE6ED", wraplength=450, justify="left").pack(anchor="w", pady=5)

        
        #discard and delete button is in pop up
        button_frame = tk.Frame(details_window, bg="#FFE6ED")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Discard Item", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED", command=lambda: self.discard_entry(clothes_id, details_window)).pack(side=tk.LEFT, pady=10)
        tk.Button(button_frame, text="Delete Entry", font=("UD Digi Kyokasho NP-B", 12), relief=tk.RAISED, bg = "#CF7486", fg = "#FFE6ED", activebackground = "#EFA8AC", activeforeground = "#FFE6ED",  command=lambda : self.delete_entry(clothes_id, details_window)).pack(side=tk.LEFT, padx=10)

    #puts clothing in the discarded database
    def discard_entry(self, clothes_id, popup_window):
        result = messagebox.askyesno("Discard", "Are you sure you want to discard this item? (You can switch it back later!)")

        if result:
            if self.db.discard_item(clothes_id):
                messagebox.showinfo("Discarded", "Item has been discarded.")
                popup_window.destroy()
                self.load_wardrobe()
                self.load_discarded()
            else:
                messagebox.showerror("Error", "Could not discard item. Please try again!")

    #delete a clothing entry
    def delete_entry(self, clothes_id, popup_window):  
        result = messagebox.askyesno("Delete Item", "Are you sure you want to delete this item? (You will have to reenter the item!)")

        if result:
            try:
               self.db.cursor.execute(
                   "DELETE FROM wardrobe WHERE clothes_id = ?", (clothes_id,)
               )
               
               self.db.conn.commit()
               popup_window.destroy()
               self.load_wardrobe()
               messagebox.showinfo("Deleted", "Item has been deleted.")
            
            except Exception as e:
                print(f"Error deleting item: {e}")
                
                messagebox.showerror("Error", "Could not delete item. Please try again!")
   
    #details for after sorting your real clothes
    def next_steps(self):
        details_window = tk.Toplevel(self.root)
        details_window.title("Next Steps!")
        details_window.geometry("600x600")
        details_window.configure(bg="#FFE6ED")

        steps_frame = tk.LabelFrame(details_window, text="What Now?", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", fg="#3E2723", padx=10, pady=10)
        steps_frame.pack(fill="both", expand=True, padx=20, pady=10)

        texts = [
            "So now you have a bunch of clothes you don't want? What now?!",
            "Here are your options: "
            ]

        for text in texts:
            tk.Label(steps_frame, text=text, font=("UD Digi Kyokasho NP-R", 12), bg="#FFE6ED", wraplength=500, justify="left").pack(anchor="w", pady=2)

        tk.Label(steps_frame, text="Donation!", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", justify="left").pack(anchor="w", pady=5)

        texts2 = [
            "- Goodwill/Salvation Army. The most common place to donate used clothes.",
            "- Clothes Stores. Many clothes stores have recycle programs where they reuse donated products to make new ones.",
            "- Homeless Shelters. Give clothes directly to those who need it.",
            "- UNIQLO. Similar to the previous options but they are very transparent on where each donation goes. HIGHLY RECOMMEND!!"
            ]

        for text2 in texts2:
            tk.Label(steps_frame, text=text2, font=("UD Digi Kyokasho NP-R", 12), bg="#FFE6ED", wraplength=500, justify="left").pack(anchor="w", pady=2)

        tk.Label(steps_frame, text="Repurpose!", font=("UD Digi Kyokasho NP-B", 12), bg="#FFE6ED", justify="left").pack(anchor="w", pady=5)

        texts2 = [
            "- Upcycle your own clothes. Like a color or pattern but not the actual item? There's countless tutorials on how to transform your own clothes. Turn sweats into skirts! Shirts to accessories!", 
            "- Give your old clothes to family members. Your old style could be a family member's style now. Saves money for them and you know exactly where your old clothes end up.",
            "\n\nPick an option that's the most convienient for you and gives you the most peace of mind. Let's help save the enviroment one article of clothing at a time!"
            ]

        for text2 in texts2:
            tk.Label(steps_frame, text=text2, font=("UD Digi Kyokasho NP-R", 12), bg="#FFE6ED", wraplength=500, justify="left").pack(anchor="w", pady=2)  

    #loads wardrobe in tab
    def load_wardrobe(self):
        for widget in self.wardrobe_scrollframe.winfo_children():
            widget.destroy()

        clothes = self.db.get_clothes()
        if not clothes:
            tk.Label(self.wardrobe_scrollframe, bg="white").pack(pady=20)
            return

        row = 0
        col = 0
        max_cols = 4

        #thumbnail in gallery
        for clothing_item in clothes:
            clothes_id, name, blob_data, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure = clothing_item

            try:
                image = Image.open(io.BytesIO(blob_data))
                image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                thumb_frame = tk.Frame(self.wardrobe_scrollframe, relief=tk.RAISED, bd=2)
                thumb_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                btn = tk.Button(thumb_frame,image=photo,command=lambda cid=clothes_id: self.show_item_details(cid),bd=0)
                btn.image = photo
                btn.pack()

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except Exception as e:
                    print(f"Error creating thumbnail: {e}")

    #loads discarded into tab and sorts into table
    def load_discarded(self):
        for item in self.discarded_tree.get_children():
            self.discarded_tree.delete(item)

        discarded_clothes = self.db.get_discarded_clothes()

        for cloth in discarded_clothes:
            clothes_id = cloth[0]
            name = cloth[1]
            color = cloth[3]
            fit = cloth[4]
            clothing_type = cloth[5]
            length = cloth[6]

            self.discarded_tree.insert(
                "",
                tk.END,
                values=(clothes_id, name, color, fit, clothing_type, length)
            )

    #displays the image of the discarded item
    def display_discarded_image(self, event):
        try:
            selected_item = self.discarded_tree.selection()
            if not selected_item:
                return

            item = self.discarded_tree.item(selected_item[0])
            values = item.get("values", [])

            if not values:
                return

            clothes_id = values[0]

            image_data = self.db.get_discarded_clothes_image(clothes_id)

            if image_data:
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((400, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                self.discarded_image_label.config(image=photo)
                self.discarded_image_label.image = photo

        except Exception as e:
            print("Error displaying discarded image:", e)

    #switches discarded clothes back into the wardrobe
    def restore_item(self):
        selected_item = self.discarded_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an item to restore.")
            return
        
        item = self.discarded_tree.item(selected_item)
        clothes_id = item['values'][0]
        item_name = item['values'][1]
        
        result = messagebox.askyesno("Restore Item", f"Are you sure you want to restore '{item_name}' to your wardrobe?")
        if result:
            self.db.cursor.execute("SELECT name, image, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure FROM discarded_wardrobe WHERE clothes_id = ?", (clothes_id,))
            item_data = self.db.cursor.fetchone()
            if item_data:
                self.db.cursor.execute(
                    "INSERT INTO wardrobe (name, image, color, clothing_type, fit, length, neckline, sleeve, rise, style, closure) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    item_data
                )
                self.db.cursor.execute("DELETE FROM discarded_wardrobe WHERE clothes_id = ?", (clothes_id,))
                self.db.conn.commit()
                
                self.discarded_tree.delete(selected_item)

                self.discarded_image_label.config(image='')
                self.discarded_image_label.image = None

                self.load_wardrobe()
                messagebox.showinfo("Success", f"'{item_name}' has been restored to your wardrobe.")
            else:
                messagebox.showerror("Error", "Failed to restore item.")
    
    #clears wardrobe
    def clear_wardrobe(self):
        result = messagebox.askyesno("Clear Wardrobe", "Are you sure you want to clear your wardrobe and discarded items? This action cannot be undone.")
        if result:
            self.db.clear_database()
            self.load_wardrobe()
            self.load_discarded()

    #clears discarded tab
    def clear_discarded(self):
        result = messagebox.askyesno("Clear Discarded", "Are you sure you want to clear all discarded items? This action cannot be undone.")
        if result:
            self.db.cursor.execute("DELETE FROM discarded_wardrobe")
            self.db.conn.commit()

            for item in self.discarded_tree.get_children():
                self.discarded_tree.delete(item)

            self.discarded_image_label.config(image='')
            self.discarded_image_label.image = None
            messagebox.showinfo("Success", "All discarded items have been permanently deleted.")


if __name__ == "__main__":
    root = tk.Tk()
    app = REWearApp(root)
    root.mainloop()