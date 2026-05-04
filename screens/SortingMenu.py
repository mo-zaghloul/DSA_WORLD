import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import importlib.util
import pygame
import traceback


class SortingMenuScreen:
    def __init__(self, master, go_back_callback):
        self.master = master
        self.go_back_callback = go_back_callback
        self.master.title("DSA World - Sorting & Searching Menu")
        self.master.geometry("800x800")
        self.master.resizable(False, False)

        # Load background
        bg_path = os.path.join("assets", "background", "menu_bg.png")
        bg_image = Image.open(bg_path).resize((800, 800), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        self.canvas = tk.Canvas(self.master, width=800, height=800)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Initialize button sound
        self.button_sound = pygame.mixer.Sound(os.path.join("assets", "music", "menu_button.mp3"))

        self.create_buttons()

        # Back to home button (top left)
        self.top_back_button = tk.Button(
            self.master,
            text="← Back",
            font=("Consolas", 12, "bold"),
            bg="#333333",
            fg="white",
            command=self.go_to_mainMenu
        )
        self.canvas.create_window(60, 30, window=self.top_back_button)

    def create_buttons(self):
        button_font = ("Pixel", 20, "bold")

        # Sorting Algorithms
        self.insertion_sort_button = tk.Button(
            self.master,
            text="Insertion Sort",
            font=button_font,
            bg="#FFD93D",
            fg="black",
            command=lambda: self.select_option("Insertion Sort")
        )

        self.merge_sort_button = tk.Button(
            self.master,
            text="Merge Sort",
            font=button_font,
            bg="#6BCB77",
            fg="black",
            command=lambda: self.select_option("Merge Sort")
        )

        self.hybrid_sort_button = tk.Button(
            self.master,
            text="Hybrid Sort",
            font=button_font,
            bg="#FF6B9D",
            fg="white",
            command=lambda: self.select_option("Hybrid Sort")
        )

        # Searching Algorithms
        self.binary_search_button = tk.Button(
            self.master,
            text="Binary Search",
            font=button_font,
            bg="#6BD8FF",
            fg="white",
            command=lambda: self.select_option("Binary Search")
        )

        # Back button
        self.back_button = tk.Button(
            self.master,
            text="Back",
            font=button_font,
            bg="#333333",
            fg="white",
            command=self.go_to_mainMenu
        )

        center_x = 400
        start_y = 250

        self.canvas.create_window(center_x, start_y, window=self.insertion_sort_button, width=220, height=50)
        self.canvas.create_window(center_x, start_y + 80, window=self.merge_sort_button, width=220, height=50)
        self.canvas.create_window(center_x, start_y + 160, window=self.hybrid_sort_button, width=220, height=50)
        self.canvas.create_window(center_x, start_y + 240, window=self.binary_search_button, width=220, height=50)
        self.canvas.create_window(center_x, start_y + 340, window=self.back_button, width=220, height=50)

    def play_sound(self):
        if self.button_sound:
            self.button_sound.play()

    def select_option(self, option):
        try:
            self.play_sound()

            if option == "Insertion Sort":
                spec = importlib.util.spec_from_file_location("insertion_sort_module", os.path.join("sorting", "insertion_sort.py"))
                insertion_sort_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(insertion_sort_module)
                self.canvas.destroy()
                insertion_sort_module.InsertionSortGame(self.master, go_back_callback=self.go_back_callback)

            elif option == "Merge Sort":
                spec = importlib.util.spec_from_file_location("merge_sort_module", os.path.join("sorting", "merge_sort.py"))
                merge_sort_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(merge_sort_module)
                self.canvas.destroy()
                merge_sort_module.MergeSortGame(self.master, go_back_callback=self.go_back_callback)

            elif option == "Hybrid Sort":
                spec = importlib.util.spec_from_file_location("hybrid_sort_module", os.path.join("sorting", "hybrid_sort.py"))
                hybrid_sort_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(hybrid_sort_module)
                self.canvas.destroy()
                hybrid_sort_module.HybridSortGame(self.master, go_back_callback=self.go_back_callback)

            elif option == "Binary Search":
                module_path = os.path.join("searching", "binary_search.py")
                print(f"[DEBUG] Loading from: {module_path}")
                print(f"[DEBUG] Absolute path: {os.path.abspath(module_path)}")
                print(f"[DEBUG] File exists: {os.path.exists(module_path)}")
                
                spec = importlib.util.spec_from_file_location("binary_search_module", module_path)
                if spec is None:
                    messagebox.showerror("Error", f"Could not find module at: {module_path}")
                    return
                    
                binary_search_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(binary_search_module)
                self.canvas.destroy()
                binary_search_module.BinarySearchGame(self.master, go_back_callback=self.go_back_callback)

        except Exception as e:
            error_msg = f"Error loading {option}:\\n{str(e)}\\n\\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)

    def go_to_mainMenu(self):
        self.play_sound()
        self.canvas.destroy()
        self.go_back_callback(self.master, self.__init__)

