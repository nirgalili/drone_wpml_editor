#!/usr/bin/env python3
"""
Drone WPML Editor
A desktop application for editing WPML files from Dronelink for drone navigation and actions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import os


class DroneWPMLEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone WPML Editor")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Current file path
        self.current_file = None
        self.wpml_data = None
        
        # Create the main interface
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Menu bar
        self.create_menu_bar()
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Open WPML File", command=self.open_file).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="Save WPML File", command=self.save_file).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(file_frame, text="Save As...", command=self.save_as_file).grid(row=0, column=2, padx=(0, 5))
        
        # File info label
        self.file_info_label = ttk.Label(file_frame, text="No file loaded")
        self.file_info_label.grid(row=0, column=3, padx=(20, 0))
        
        # Mission details frame
        mission_frame = ttk.LabelFrame(main_frame, text="Mission Details", padding="5")
        mission_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        mission_frame.columnconfigure(1, weight=1)
        
        # Mission name
        ttk.Label(mission_frame, text="Mission Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.mission_name_var = tk.StringVar()
        ttk.Entry(mission_frame, textvariable=self.mission_name_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Mission description
        ttk.Label(mission_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.mission_desc_var = tk.StringVar()
        ttk.Entry(mission_frame, textvariable=self.mission_desc_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Main content area with notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Waypoints tab
        self.create_waypoints_tab()
        
        # Actions tab
        self.create_actions_tab()
        
        # Settings tab
        self.create_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open WPML...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Waypoint", command=self.add_waypoint)
        edit_menu.add_command(label="Add Action", command=self.add_action)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_waypoints_tab(self):
        """Create the waypoints editing tab"""
        waypoints_frame = ttk.Frame(self.notebook)
        self.notebook.add(waypoints_frame, text="Waypoints")
        
        # Waypoints list
        list_frame = ttk.Frame(waypoints_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for waypoints
        columns = ("#", "Latitude", "Longitude", "Altitude", "Speed", "Actions")
        self.waypoints_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.waypoints_tree.heading(col, text=col)
            self.waypoints_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.waypoints_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.waypoints_tree.xview)
        self.waypoints_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.waypoints_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Waypoint buttons
        button_frame = ttk.Frame(waypoints_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Waypoint", command=self.add_waypoint).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Edit Waypoint", command=self.edit_waypoint).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Waypoint", command=self.delete_waypoint).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Move Up", command=self.move_waypoint_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Move Down", command=self.move_waypoint_down).pack(side=tk.LEFT)
        
    def create_actions_tab(self):
        """Create the actions editing tab"""
        actions_frame = ttk.Frame(self.notebook)
        self.notebook.add(actions_frame, text="Actions")
        
        # Actions list
        list_frame = ttk.Frame(actions_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for actions
        columns = ("Waypoint", "Action Type", "Parameters", "Delay")
        self.actions_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.actions_tree.heading(col, text=col)
            self.actions_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.actions_tree.xview)
        self.actions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.actions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(actions_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Action", command=self.add_action).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Edit Action", command=self.edit_action).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Action", command=self.delete_action).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings content
        ttk.Label(settings_frame, text="Drone Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Default altitude
        alt_frame = ttk.Frame(settings_frame)
        alt_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(alt_frame, text="Default Altitude (m):").pack(side=tk.LEFT)
        self.default_altitude_var = tk.StringVar(value="50")
        ttk.Entry(alt_frame, textvariable=self.default_altitude_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # Default speed
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(speed_frame, text="Default Speed (m/s):").pack(side=tk.LEFT)
        self.default_speed_var = tk.StringVar(value="5")
        ttk.Entry(speed_frame, textvariable=self.default_speed_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # RTH settings
        rth_frame = ttk.Frame(settings_frame)
        rth_frame.pack(fill=tk.X, padx=20, pady=5)
        self.rth_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(rth_frame, text="Enable Return to Home", variable=self.rth_enabled_var).pack(side=tk.LEFT)
        
    def open_file(self):
        """Open a WPML file"""
        file_path = filedialog.askopenfilename(
            title="Open WPML File",
            filetypes=[("WPML files", "*.wpml"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.load_wpml_file(file_path)
                self.current_file = file_path
                self.file_info_label.config(text=f"Loaded: {Path(file_path).name}")
                self.status_var.set(f"Opened {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
                
    def load_wpml_file(self, file_path):
        """Load and parse WPML file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Store the parsed data
        self.wpml_data = root
        
        # Extract mission info
        mission_name = root.find(".//mission/name")
        if mission_name is not None:
            self.mission_name_var.set(mission_name.text or "")
            
        mission_desc = root.find(".//mission/description")
        if mission_desc is not None:
            self.mission_desc_var.set(mission_desc.text or "")
        
        # Load waypoints
        self.load_waypoints()
        
        # Load actions
        self.load_actions()
        
    def load_waypoints(self):
        """Load waypoints from WPML data"""
        # Clear existing waypoints
        for item in self.waypoints_tree.get_children():
            self.waypoints_tree.delete(item)
            
        # Find waypoints in WPML
        waypoints = self.wpml_data.findall(".//waypoint")
        
        for i, wp in enumerate(waypoints, 1):
            lat = wp.get("lat", "0")
            lon = wp.get("lon", "0")
            alt = wp.get("alt", "0")
            speed = wp.get("speed", "0")
            
            # Count actions for this waypoint
            actions_count = len(wp.findall(".//action"))
            
            self.waypoints_tree.insert("", "end", values=(
                str(i), lat, lon, alt, speed, str(actions_count)
            ))
            
    def load_actions(self):
        """Load actions from WPML data"""
        # Clear existing actions
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
            
        # Find actions in WPML
        waypoints = self.wpml_data.findall(".//waypoint")
        
        for wp_idx, wp in enumerate(waypoints, 1):
            actions = wp.findall(".//action")
            for action in actions:
                action_type = action.get("type", "Unknown")
                params = action.get("params", "")
                delay = action.get("delay", "0")
                
                self.actions_tree.insert("", "end", values=(
                    str(wp_idx), action_type, params, delay
                ))
                
    def save_file(self):
        """Save the current WPML file"""
        if self.current_file:
            self.save_wpml_file(self.current_file)
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save WPML file with new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save WPML File As",
            defaultextension=".wpml",
            filetypes=[("WPML files", "*.wpml"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            self.save_wpml_file(file_path)
            self.current_file = file_path
            self.file_info_label.config(text=f"Saved: {Path(file_path).name}")
            
    def save_wpml_file(self, file_path):
        """Save WPML data to file"""
        if self.wpml_data is None:
            messagebox.showwarning("Warning", "No data to save")
            return
            
        try:
            # Update mission info
            mission = self.wpml_data.find(".//mission")
            if mission is not None:
                name_elem = mission.find("name")
                if name_elem is not None:
                    name_elem.text = self.mission_name_var.get()
                else:
                    name_elem = ET.SubElement(mission, "name")
                    name_elem.text = self.mission_name_var.get()
                    
                desc_elem = mission.find("description")
                if desc_elem is not None:
                    desc_elem.text = self.mission_desc_var.get()
                else:
                    desc_elem = ET.SubElement(mission, "description")
                    desc_elem.text = self.mission_desc_var.get()
            
            # Write to file
            tree = ET.ElementTree(self.wpml_data)
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            self.status_var.set(f"Saved {Path(file_path).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            
    def add_waypoint(self):
        """Add a new waypoint"""
        # This would open a dialog to add waypoint details
        messagebox.showinfo("Add Waypoint", "Waypoint dialog would open here")
        
    def edit_waypoint(self):
        """Edit selected waypoint"""
        selection = self.waypoints_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a waypoint to edit")
            return
        messagebox.showinfo("Edit Waypoint", "Waypoint edit dialog would open here")
        
    def delete_waypoint(self):
        """Delete selected waypoint"""
        selection = self.waypoints_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a waypoint to delete")
            return
        messagebox.showinfo("Delete Waypoint", "Waypoint would be deleted")
        
    def move_waypoint_up(self):
        """Move selected waypoint up"""
        selection = self.waypoints_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a waypoint to move")
            return
        messagebox.showinfo("Move Up", "Waypoint would be moved up")
        
    def move_waypoint_down(self):
        """Move selected waypoint down"""
        selection = self.waypoints_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a waypoint to move")
            return
        messagebox.showinfo("Move Down", "Waypoint would be moved down")
        
    def add_action(self):
        """Add a new action"""
        messagebox.showinfo("Add Action", "Action dialog would open here")
        
    def edit_action(self):
        """Edit selected action"""
        selection = self.actions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an action to edit")
            return
        messagebox.showinfo("Edit Action", "Action edit dialog would open here")
        
    def delete_action(self):
        """Delete selected action"""
        selection = self.actions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an action to delete")
            return
        messagebox.showinfo("Delete Action", "Action would be deleted")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """Drone WPML Editor v1.0

A desktop application for editing WPML files from Dronelink
for drone navigation and action planning.

Features:
- Edit waypoints and flight paths
- Manage drone actions and commands
- Visual mission planning
- Export to WPML format

Created with Python and Tkinter"""
        
        messagebox.showinfo("About Drone WPML Editor", about_text)


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = DroneWPMLEditor(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
