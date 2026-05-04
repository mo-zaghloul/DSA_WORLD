import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame
import os
from sorting.timer import SortingTimer


class BinarySearchGame:
    def __init__(self, master, go_back_callback):
        self.master = master
        self.go_back_callback = go_back_callback

        # Initialize sound system
        pygame.mixer.init()
        self.button_sound = pygame.mixer.Sound(os.path.join("assets", "music", "push_button.mp3"))
        self.back_sound = pygame.mixer.Sound(os.path.join("assets", "music", "menu_button.mp3"))

        # Destroy previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.title("DSA World - Binary Search")
        self.master.geometry("800x950")
        self.master.resizable(False, False)

        # Color palette
        self.COLORS = {
            "black": "#0D0D0D",
            "dark_blue": "#131B23",
            "blue": "#00498F",
            "light_blue": "#00A1DE",
            "cyan": "#00F0FF",
            "green": "#00FF9D",
            "yellow": "#FFCF00",
            "orange": "#FF8B00",
            "red": "#E72000",
            "purple": "#A91ED8",
            "white": "#FFFFFF"
        }

        # Sorting state
        self.array = []
        self.array_colors = []
        self.sorting = False
        self.sorted_indices = set()

        # ── Single timer for BOTH sort + search ─────────────────
        self.timer = SortingTimer()
        self.total_elapsed = 0.0  # accumulated time across sort and search
        self.is_sorter = False    # track if array has been sorted
        # ────────────────────────────────────────────────────────

        # ── Binary Search state ──────────────────────────────
        self.searching = False
        self.search_target = None
        self.search_result_index = None
        self.bs_left = None
        self.bs_right = None
        self.bs_mid = None
        # ────────────────────────────────────────────────────

        self.create_ui()
        self.generate_random_array()

    def play_button_sound(self):
        """Play the regular button click sound"""
        self.button_sound.play()

    def play_back_sound(self):
        """Play the special back button sound"""
        self.back_sound.play()

    def create_ui(self):
        """Create the user interface"""
        self.main_frame = tk.Frame(self.master, bg=self.COLORS["black"])
        self.main_frame.pack(fill="both", expand=True)

        # Title
        title_label = tk.Label(
            self.main_frame,
            text="BINARY SEARCH VISUALIZER",
            font=("Courier", 24, "bold"),
            bg=self.COLORS["black"],
            fg=self.COLORS["cyan"],
            pady=15
        )
        title_label.pack()

        # Canvas for visualization
        self.canvas_frame = tk.Frame(
            self.main_frame,
            bg=self.COLORS["black"],
            bd=2,
            relief=tk.RIDGE
        )
        self.canvas_frame.pack(padx=20, pady=10)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=700,
            height=300,
            bg=self.COLORS["black"],
            bd=0,
            highlightthickness=2,
            highlightbackground=self.COLORS["cyan"]
        )
        self.canvas.pack(padx=10, pady=10)

        # Timer display (shows total time: sort + search)
        self.timer_label = tk.Label(
            self.main_frame,
            text="Time: 00:00.00",
            font=("Courier", 16, "bold"),
            bg=self.COLORS["black"],
            fg=self.COLORS["yellow"],
            pady=5
        )
        self.timer_label.pack()

        # ── Custom input frame ───────────────────────────────
        input_frame = tk.Frame(self.main_frame, bg=self.COLORS["black"], pady=5)
        input_frame.pack()

        input_label = tk.Label(
            input_frame,
            text="Enter array (comma-separated):",
            font=("Courier", 10),
            bg=self.COLORS["black"],
            fg=self.COLORS["white"]
        )
        input_label.grid(row=0, column=0, padx=10)

        self.array_input = tk.Entry(
            input_frame,
            font=("Courier", 10),
            width=30,
            bg=self.COLORS["dark_blue"],
            fg=self.COLORS["white"],
            insertbackground=self.COLORS["cyan"]
        )
        self.array_input.grid(row=0, column=1, padx=10)
        self.array_input.insert(0, "50, 30, 70, 20, 80")

        self.load_array_button = tk.Button(
            input_frame,
            text="LOAD",
            font=("Courier", 10, "bold"),
            bg=self.COLORS["blue"],
            fg=self.COLORS["white"],
            padx=10,
            pady=3,
            command=lambda: [self.play_button_sound(), self.load_custom_array()]
        )
        self.load_array_button.grid(row=0, column=2, padx=10)

        # ── Step 1: Sort controls ──────────────────────────
        sort_label = tk.Label(
            self.main_frame,
            text="── STEP 1: SORT THE ARRAY ──",
            font=("Courier", 11, "bold"),
            bg=self.COLORS["black"],
            fg=self.COLORS["light_blue"],
            pady=5
        )
        sort_label.pack()

        button_frame = tk.Frame(self.main_frame, bg=self.COLORS["black"], pady=5)
        button_frame.pack()

        self.generate_button = tk.Button(
            button_frame,
            text="GENERATE",
            font=("Courier", 12, "bold"),
            bg=self.COLORS["blue"],
            fg=self.COLORS["white"],
            padx=15,
            pady=5,
            command=lambda: [self.play_button_sound(), self.generate_random_array()]
        )
        self.generate_button.grid(row=0, column=0, padx=8)

        self.sort_button = tk.Button(
            button_frame,
            text="SORT",
            font=("Courier", 12, "bold"),
            bg=self.COLORS["green"],
            fg=self.COLORS["black"],
            padx=15,
            pady=5,
            command=lambda: [self.play_button_sound(), self.start_sort()]
        )
        self.sort_button.grid(row=0, column=1, padx=8)

        self.reset_button = tk.Button(
            button_frame,
            text="RESET",
            font=("Courier", 12, "bold"),
            bg=self.COLORS["purple"],
            fg=self.COLORS["white"],
            padx=15,
            pady=5,
            command=lambda: [self.play_button_sound(), self.reset()]
        )
        self.reset_button.grid(row=0, column=2, padx=8)

        # ── Step 2: Binary Search controls ───────────────────
        search_label = tk.Label(
            self.main_frame,
            text="── STEP 2: BINARY SEARCH ──",
            font=("Courier", 11, "bold"),
            bg=self.COLORS["black"],
            fg=self.COLORS["orange"],
            pady=5
        )
        search_label.pack()

        search_frame = tk.Frame(self.main_frame, bg=self.COLORS["black"], pady=5)
        search_frame.pack()

        search_input_label = tk.Label(
            search_frame,
            text="Search target:",
            font=("Courier", 10),
            bg=self.COLORS["black"],
            fg=self.COLORS["white"]
        )
        search_input_label.grid(row=0, column=0, padx=10)

        self.search_input = tk.Entry(
            search_frame,
            font=("Courier", 10),
            width=10,
            bg=self.COLORS["dark_blue"],
            fg=self.COLORS["white"],
            insertbackground=self.COLORS["orange"]
        )
        self.search_input.grid(row=0, column=1, padx=10)

        self.search_button = tk.Button(
            search_frame,
            text="SEARCH",
            font=("Courier", 12, "bold"),
            bg=self.COLORS["orange"],
            fg=self.COLORS["black"],
            padx=15,
            pady=5,
            command=lambda: [self.play_button_sound(), self.start_binary_search()]
        )
        self.search_button.grid(row=0, column=2, padx=8)

        self.random_target_button = tk.Button(
            search_frame,
            text="RANDOM TARGET",
            font=("Courier", 10, "bold"),
            bg=self.COLORS["dark_blue"],
            fg=self.COLORS["cyan"],
            padx=10,
            pady=5,
            command=lambda: [self.play_button_sound(), self.pick_random_target()]
        )
        self.random_target_button.grid(row=0, column=3, padx=8)

        # ── Legend ───────────────────────────────────────────
        legend_frame = tk.Frame(self.main_frame, bg=self.COLORS["black"], pady=3)
        legend_frame.pack()

        legends = [
            ("■ Search Range", self.COLORS["light_blue"]),
            ("■ Left / Right", self.COLORS["purple"]),
            ("■ Mid (Checking)", self.COLORS["yellow"]),
            ("■ Found!", self.COLORS["green"]),
            ("■ Not in Range", self.COLORS["red"]),
        ]
        for i, (text, color) in enumerate(legends):
            tk.Label(
                legend_frame,
                text=text,
                font=("Courier", 9),
                bg=self.COLORS["black"],
                fg=color
            ).grid(row=0, column=i, padx=6)

        # ── Status label ─────────────────────────────────────
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready",
            font=("Courier", 12),
            bg=self.COLORS["black"],
            fg=self.COLORS["green"],
            pady=5
        )
        self.status_label.pack()

        # ── Instructions ───────────────────────────────────
        instruction_text = (
            "INSTRUCTIONS:\n"
            "1. Click GENERATE to create a random array\n"
            "2. Click SORT to sort the array (required for binary search)\n"
            "3. Enter a number and click SEARCH — watch Binary Search in action!\n"
            "   Yellow = mid element | Green = found | Red = eliminated"
        )

        instructions_label = tk.Label(
            self.main_frame,
            text=instruction_text,
            font=("Courier", 10),
            bg=self.COLORS["black"],
            fg=self.COLORS["yellow"],
            justify="left",
            pady=5
        )
        instructions_label.pack()

        # ── Back button ──────────────────────────────────────
        self.back_button = tk.Button(
            self.main_frame,
            text="Back to Menu",
            font=("Courier", 12, "bold"),
            bg=self.COLORS["dark_blue"],
            fg=self.COLORS["white"],
            padx=20,
            pady=5,
            command=lambda: [self.play_back_sound(), self.go_back()]
        )
        self.back_button.pack(pady=10)

    def update_timer_display(self):
        """Update the timer display — shows total accumulated time"""
        if self.timer.is_running:
            current_session = self.timer.get_elapsed()
            total = self.total_elapsed + current_session
            formatted_time = self.timer.format_time(total)
            self.timer_label.config(text=f"Time: {formatted_time}")
            self.master.update()

    def _update_final_timer(self):
        """Stop timer and add current session to total"""
        if self.timer.is_running:
            self.timer.stop()
            self.total_elapsed += self.timer.get_total_time()
        formatted = self.timer.format_time(self.total_elapsed)
        self.timer_label.config(text=f"Time: {formatted}")

    def generate_random_array(self):
        """Generate a random array"""
        if self.sorting or self.searching:
            messagebox.showwarning("Busy", "Wait for the current operation to finish!")
            return

        self.array = [random.randint(10, 100) for _ in range(20)]
        self.array_colors = [self.COLORS["light_blue"] for _ in self.array]
        self.sorted_indices = set()
        self._reset_search_state()

        # Reset total time when generating new array
        self.total_elapsed = 0.0
        self.is_sorted = False
        self.timer.reset()
        self.timer_label.config(text="Time: 00:00.00")

        self.status_label.config(text="Array generated! Click SORT before searching.", fg=self.COLORS["green"])
        self.draw_array()

    def load_custom_array(self):
        """Load a custom array from user input"""
        if self.sorting or self.searching:
            messagebox.showwarning("Busy", "Wait for the current operation to finish!")
            return

        input_text = self.array_input.get().strip()
        if not input_text:
            messagebox.showwarning("Input Error", "Please enter array values!")
            return

        try:
            self.array = [int(x.strip()) for x in input_text.split(",")]
            if len(self.array) == 0:
                messagebox.showwarning("Input Error", "Please enter at least one value!")
                return
            if any(x < 0 for x in self.array):
                messagebox.showwarning("Input Error", "Please use positive numbers only!")
                return

            self.array_colors = [self.COLORS["light_blue"] for _ in self.array]
            self.sorted_indices = set()
            self._reset_search_state()

            # Reset total time when loading new array
            self.total_elapsed = 0.0
            self.is_sorted = False
            self.timer.reset()
            self.timer_label.config(text="Time: 00:00.00")

            self.status_label.config(
                text=f"Custom array loaded! {len(self.array)} elements. Click SORT before searching.",
                fg=self.COLORS["green"]
            )
            self.draw_array()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers separated by commas!\nExample: 50, 30, 70, 20, 80")

    def draw_array(self):
        """Draw the current state of the array with binary search pointers"""
        self.canvas.delete("all")

        if not self.array:
            return

        canvas_width = 700
        canvas_height = 300
        bar_width = canvas_width / len(self.array)
        max_value = max(self.array) if self.array else 1

        for i, value in enumerate(self.array):
            x1 = i * bar_width
            x2 = (i + 1) * bar_width
            bar_height = (value / max_value) * (canvas_height - 40)
            y1 = canvas_height - bar_height
            y2 = canvas_height

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=self.array_colors[i],
                outline=self.COLORS["white"],
                width=1
            )

            if len(self.array) <= 20:
                self.canvas.create_text(
                    (x1 + x2) / 2,
                    y2 + 15,
                    text=str(value),
                    fill=self.COLORS["white"],
                    font=("Courier", 8)
                )

            if self.searching or self.search_result_index is not None:
                labels = []
                if i == self.bs_left:
                    labels.append("L")
                if i == self.bs_right:
                    labels.append("R")
                if i == self.bs_mid:
                    labels.append("M")
                if labels:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        y1 - 10,
                        text="/".join(labels),
                        fill=self.COLORS["yellow"],
                        font=("Courier", 8, "bold")
                    )

        self.master.update()

    # ═══════════════════════════════════════════════════════
    #  SORT METHODS (Merge Sort)
    # ═══════════════════════════════════════════════════════

    def start_sort(self):
        """Start the merge sort animation"""
        if not self.array:
            messagebox.showwarning("Empty Array", "Please generate an array first!")
            return
        if self.sorting:
            messagebox.showwarning("Busy", "Sort is already in progress!")
            return
        if self.searching:
            messagebox.showwarning("Busy", "Wait for search to finish!")
            return

        self.sorting = True
        self._set_buttons_state("disabled")
        self._reset_search_state()

        self.status_label.config(text="Sorting in progress...", fg=self.COLORS["yellow"])

        # Start timer (continues from any previous accumulated time)
        self.timer.reset()
        self.timer.start()

        self.array_copy = self.array.copy()
        self.merge_sort_animate(0, len(self.array_copy) - 1, "Dividing...")

        # Stop timer and add to total
        self._update_final_timer()

        self.array_colors = [self.COLORS["green"] for _ in self.array_colors]
        self.draw_array()

        formatted = self.timer.format_time(self.total_elapsed)
        self.status_label.config(
            text=f"Sorted! ✓  Now enter a target and click SEARCH.  [{formatted}]",
            fg=self.COLORS["green"]
        )
        self.is_sorted = True
        self.sorting = False
        self._set_buttons_state("normal")

    def merge_sort_animate(self, left, right, phase):
        """Recursive merge sort with animation"""
        if left < right:
            mid = (left + right) // 2

            self.highlight_range(left, right, self.COLORS["orange"])
            self.status_label.config(text=f"Dividing: [{left}, {right}]", fg=self.COLORS["orange"])
            self.update_timer_display()
            time.sleep(0.2)

            self.merge_sort_animate(left, mid, "Left")
            self.merge_sort_animate(mid + 1, right, "Right")
            self.merge_animate(left, mid, right)

    def merge_animate(self, left, mid, right):
        """Merge two sorted subarrays with animation"""
        left_arr = self.array_copy[left:mid+1]
        right_arr = self.array_copy[mid+1:right+1]

        i = j = 0
        k = left

        self.highlight_range(left, right, self.COLORS["purple"])
        self.status_label.config(text=f"Merging: [{left}, {mid}] + [{mid+1}, {right}]", fg=self.COLORS["purple"])
        self.update_timer_display()
        time.sleep(0.1)

        while i < len(left_arr) and j < len(right_arr):
            if left_arr[i] <= right_arr[j]:
                self.array_copy[k] = left_arr[i]
                i += 1
            else:
                self.array_copy[k] = right_arr[j]
                j += 1
            k += 1

            self.array = self.array_copy.copy()
            self.highlight_range(left, right, self.COLORS["cyan"])
            self.draw_array()
            self.update_timer_display()
            time.sleep(0.05)

        while i < len(left_arr):
            self.array_copy[k] = left_arr[i]
            self.array = self.array_copy.copy()
            self.highlight_range(left, right, self.COLORS["cyan"])
            self.draw_array()
            self.update_timer_display()
            i += 1
            k += 1
            time.sleep(0.05)

        while j < len(right_arr):
            self.array_copy[k] = right_arr[j]
            self.array = self.array_copy.copy()
            self.highlight_range(left, right, self.COLORS["cyan"])
            self.draw_array()
            self.update_timer_display()
            j += 1
            k += 1
            time.sleep(0.05)

    def highlight_range(self, left, right, color):
        """Highlight a range of array elements"""
        for i in range(len(self.array_colors)):
            if left <= i <= right:
                self.array_colors[i] = color
            elif i not in self.sorted_indices:
                self.array_colors[i] = self.COLORS["light_blue"]

    # ═══════════════════════════════════════════════════════
    #  BINARY SEARCH METHODS
    # ═══════════════════════════════════════════════════════

    def pick_random_target(self):
        """Fill the search box with a random element from the array (50/50: exists or not)"""
        if not self.array:
            messagebox.showwarning("No Array", "Generate an array first!")
            return
        if random.random() < 0.5:
            val = random.choice(self.array)
        else:
            val = random.randint(min(self.array), max(self.array))
        self.search_input.delete(0, tk.END)
        self.search_input.insert(0, str(val))

    def start_binary_search(self):
        """Validate inputs, check array is sorted, then run animated binary search"""
        if not self.array:
            messagebox.showwarning("No Array", "Please generate and sort an array first!")
            return
        if self.sorting or self.searching:
            messagebox.showwarning("Busy", "Wait for the current operation to finish!")
            return

        # Check if sorted
        if self.array != sorted(self.array):
            messagebox.showwarning(
                "Not Sorted",
                "Binary Search requires a sorted array!\nPlease click SORT first."
            )
            return

        # Parse target
        target_text = self.search_input.get().strip()
        if not target_text:
            messagebox.showwarning("No Target", "Please enter a number to search for!")
            return
        try:
            target = int(target_text)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer!")
            return

        self.search_target = target
        self._reset_search_state()
        self.searching = True
        self._set_buttons_state("disabled")

        # Continue timer from where sort left off (don't reset!)
        self.timer.reset()
        self.timer.start()

        result = self._binary_search_animate(target)

        # Stop and add search time to total
        self._update_final_timer()

        self.searching = False
        self.search_result_index = result
        self._set_buttons_state("normal")

        formatted = self.timer.format_time(self.total_elapsed)

        if result >= 0:
            self.array_colors = [self.COLORS["dark_blue"] for _ in self.array]
            self.array_colors[result] = self.COLORS["green"]
            self.draw_array()
            self.status_label.config(
                text=f"✓ Found {target} at index {result}!  [Total: {formatted}]",
                fg=self.COLORS["green"]
            )
            try:
                win_sound = pygame.mixer.Sound(os.path.join("assets", "music", "win.mp3"))
                win_sound.play()
            except Exception:
                pass
        else:
            self.array_colors = [self.COLORS["red"] for _ in self.array]
            self.draw_array()
            time.sleep(0.4)
            self.array_colors = [self.COLORS["light_blue"] for _ in self.array]
            self.draw_array()
            self.status_label.config(
                text=f"✗ {target} not found in the array.  [Total: {formatted}]",
                fg=self.COLORS["red"]
            )
            try:
                err_sound = pygame.mixer.Sound(os.path.join("assets", "music", "Error.mp3"))
                err_sound.play()
            except Exception:
                pass

    def _binary_search_animate(self, target):
        """Animated binary search. Returns index if found, -1 otherwise."""
        left = 0
        right = len(self.array) - 1
        step = 0

        while left <= right:
            step += 1
            mid = (left + right) // 2

            self.bs_left = left
            self.bs_right = right
            self.bs_mid = mid

            for i in range(len(self.array)):
                if i < left or i > right:
                    self.array_colors[i] = self.COLORS["dark_blue"]
                elif i == mid:
                    self.array_colors[i] = self.COLORS["yellow"]
                elif i == left or i == right:
                    self.array_colors[i] = self.COLORS["purple"]
                else:
                    self.array_colors[i] = self.COLORS["light_blue"]

            self.draw_array()
            self.status_label.config(
                text=f"Step {step}: L={left}  M={mid}  R={right}  |  arr[{mid}]={self.array[mid]}  vs  target={target}",
                fg=self.COLORS["yellow"]
            )
            self.update_timer_display()
            time.sleep(0.6)

            if self.array[mid] == target:
                self.array_colors[mid] = self.COLORS["green"]
                self.bs_mid = mid
                self.draw_array()
                return mid
            elif self.array[mid] < target:
                for i in range(left, mid + 1):
                    self.array_colors[i] = self.COLORS["red"]
                self.draw_array()
                self.status_label.config(
                    text=f"Step {step}: arr[{mid}]={self.array[mid]} < {target}  →  search RIGHT half",
                    fg=self.COLORS["orange"]
                )
                time.sleep(0.4)
                left = mid + 1
            else:
                for i in range(mid, right + 1):
                    self.array_colors[i] = self.COLORS["red"]
                self.draw_array()
                self.status_label.config(
                    text=f"Step {step}: arr[{mid}]={self.array[mid]} > {target}  →  search LEFT half",
                    fg=self.COLORS["orange"]
                )
                time.sleep(0.4)
                right = mid - 1

        return -1

    # ═══════════════════════════════════════════════════════
    #  HELPERS
    # ═══════════════════════════════════════════════════════

    def _reset_search_state(self):
        """Reset binary search state variables"""
        self.searching = False
        self.search_result_index = None
        self.bs_left = None
        self.bs_right = None
        self.bs_mid = None

    def _set_buttons_state(self, state):
        """Enable or disable all control buttons"""
        for btn in (
            self.generate_button,
            self.sort_button,
            self.reset_button,
            self.search_button,
            self.random_target_button,
            self.load_array_button,
            self.back_button,
        ):
            btn.config(state=state)

    def reset(self):
        """Reset the visualizer"""
        if self.sorting or self.searching:
            messagebox.showwarning("Busy", "Wait for the current operation to finish!")
            return

        self.array = []
        self.array_colors = []
        self.sorted_indices = set()
        self._reset_search_state()

        # Reset everything including total time
        self.total_elapsed = 0.0
        self.is_sorted = False
        self.timer.reset()
        self.timer_label.config(text="Time: 00:00.00")

        self.status_label.config(text="Reset complete. Generate a new array.", fg=self.COLORS["cyan"])
        self.draw_array()

    def go_back(self):
        """Go back to the previous menu"""
        for widget in self.master.winfo_children():
            widget.destroy()

        if self.go_back_callback:
            from screens.SortingMenu import SortingMenuScreen
            SortingMenuScreen(self.master, self.go_back_callback)