#!/usr/bin/env python3
"""
KMZ Processor GUI - Complete Drone Mission Workflow Interface
User-friendly interface for processing KMZ files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import re
from pathlib import Path
from kmz_processor import KMZProcessor

class KMZProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone KMZ Processor - Complete Workflow")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_filename = tk.StringVar(value="5336EE45-2941-4996-B7F1-22BAA25F2639.kmz")
        self.enable_hover = tk.BooleanVar(value=True)
        self.hover_time = tk.StringVar(value="2")
        self.processing = False
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚁 Drone KMZ Processor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input KMZ File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_dir).grid(row=2, column=2, pady=5)
        
        # Output filename selection
        ttk.Label(main_frame, text="Output Filename:").grid(row=3, column=0, sticky=tk.W, pady=5)
        filename_frame = ttk.Frame(main_frame)
        filename_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        filename_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(filename_frame, textvariable=self.output_filename, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Label(filename_frame, text="(Customize for different DJI RC units)", 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=0, sticky=tk.W)
        
        ttk.Button(main_frame, text="Reset", command=self.reset_filename).grid(row=3, column=2, pady=5)
        
        # Hover options
        hover_frame = ttk.LabelFrame(main_frame, text="Hover Options", padding="15")
        hover_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        hover_frame.columnconfigure(1, weight=1)
        
        # Enable hover checkbox
        self.hover_checkbox = ttk.Checkbutton(hover_frame, text="Enable hover before photo", 
                                            variable=self.enable_hover, command=self.toggle_hover_options)
        self.hover_checkbox.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # Hover time selection
        ttk.Label(hover_frame, text="Hover time (seconds):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        
        time_frame = ttk.Frame(hover_frame)
        time_frame.grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        self.hover_time_entry = ttk.Entry(time_frame, textvariable=self.hover_time, width=8, font=("Arial", 9))
        self.hover_time_entry.grid(row=0, column=0, padx=(0, 10))
        
        # Quick time buttons
        ttk.Button(time_frame, text="1s", command=lambda: self.set_hover_time("1"), width=4).grid(row=0, column=1, padx=2)
        ttk.Button(time_frame, text="2s", command=lambda: self.set_hover_time("2"), width=4).grid(row=0, column=2, padx=2)
        ttk.Button(time_frame, text="3s", command=lambda: self.set_hover_time("3"), width=4).grid(row=0, column=3, padx=2)
        ttk.Button(time_frame, text="5s", command=lambda: self.set_hover_time("5"), width=4).grid(row=0, column=4, padx=2)
        
        # Info label
        ttk.Label(hover_frame, text="💡 Hover allows the drone to stabilize before taking photos", 
                 font=("Arial", 8), foreground="gray").grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="🚀 Process KMZ File", 
                                       command=self.process_kmz)
        self.process_button.grid(row=5, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))
        
        # Configure button style
        style = ttk.Style()
        style.configure("Process.TButton", font=("Arial", 12, "bold"), padding=(10, 5))
        self.process_button.configure(style="Process.TButton")
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log output
        ttk.Label(main_frame, text="Processing Log:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        
        # Text area for logs
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to process KMZ files")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Set default output directory
        self.output_dir.set(os.getcwd())
        
    def browse_input_file(self):
        """Browse for input KMZ file"""
        filename = filedialog.askopenfilename(
            title="Select KMZ File",
            filetypes=[("KMZ files", "*.kmz"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Set output directory to same as input file
            self.output_dir.set(os.path.dirname(filename))
            
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
            
    def reset_filename(self):
        """Reset filename to default"""
        self.output_filename.set("5336EE45-2941-4996-B7F1-22BAA25F2639.kmz")
        
    def set_hover_time(self, time):
        """Set hover time from quick buttons"""
        self.hover_time.set(time)
        
    def toggle_hover_options(self):
        """Enable/disable hover time controls based on checkbox"""
        state = "normal" if self.enable_hover.get() else "disabled"
        self.hover_time_entry.config(state=state)
            
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def process_kmz(self):
        """Process the KMZ file"""
        if self.processing:
            return
            
        # Validate inputs
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input KMZ file")
            return
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
            
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        if not os.path.exists(self.output_dir.get()):
            messagebox.showerror("Error", "Output directory does not exist")
            return
            
        # Validate filename
        filename = self.output_filename.get().strip()
        if not filename:
            messagebox.showerror("Error", "Output filename cannot be empty")
            return
            
        if not filename.lower().endswith('.kmz'):
            messagebox.showerror("Error", "Output filename must end with .kmz")
            return
        
        # Validate hover time if hover is enabled
        if self.enable_hover.get():
            try:
                hover_time = float(self.hover_time.get())
                if hover_time <= 0 or hover_time > 60:
                    messagebox.showerror("Error", "Hover time must be between 0.1 and 60 seconds")
                    return
            except ValueError:
                messagebox.showerror("Error", "Hover time must be a valid number")
                return
        
        # Check if output file already exists
        output_path = os.path.join(self.output_dir.get(), filename)
        if os.path.exists(output_path):
            response = messagebox.askyesno(
                "File Exists", 
                f"The file '{filename}' already exists in the output directory.\n\n"
                f"Do you want to overwrite it?\n\n"
                f"⚠️  WARNING: This will permanently delete the existing file!"
            )
            if not response:
                return
        
        # Start processing in separate thread
        self.processing = True
        self.process_button.config(state="disabled")
        self.progress.start()
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        thread = threading.Thread(target=self._process_kmz_thread)
        thread.daemon = True
        thread.start()
        
    def _process_kmz_thread(self):
        """Process KMZ in separate thread"""
        try:
            self.log_message("🚁 Starting KMZ Processing Workflow")
            self.log_message("=" * 50)
            
            # Create processor
            processor = KMZProcessor()
            
            # Process the file with custom filename and hover options
            hover_enabled = self.enable_hover.get()
            hover_time = float(self.hover_time.get()) if hover_enabled else 0
            
            # Override the print function to log to GUI
            import builtins
            original_print = builtins.print
            def gui_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                self.root.after(0, lambda: self.log_message(message))
            builtins.print = gui_print
            
            try:
                output_path = processor.process_kmz(self.input_file.get(), self.output_dir.get(), 
                                                  self.output_filename.get(), hover_enabled, hover_time)
            finally:
                # Restore original print function
                builtins.print = original_print
            
            if output_path:
                self.root.after(0, lambda: self._processing_complete(True, output_path))
            else:
                self.root.after(0, lambda: self._processing_complete(False, None))
                
        except Exception as e:
            self.root.after(0, lambda: self._processing_complete(False, str(e)))
            
    def _processing_complete(self, success, result):
        """Handle processing completion"""
        self.processing = False
        self.process_button.config(state="normal")
        self.progress.stop()
        
        if success:
            # Add important summary at the top
            self.log_message("\n" + "="*60)
            self.log_message("📊 MISSION SUMMARY")
            self.log_message("="*60)
            
            # Extract key info from the log (we'll need to parse it)
            self._add_mission_summary()
            
            self.log_message("\n🎉 SUCCESS!")
            self.log_message(f"📁 Input:  {self.input_file.get()}")
            self.log_message(f"📁 Output: {result}")
            self.log_message("🔗 All waypoints now have hover + photo actions!")
            
            self.status_var.set(f"Success! Output saved to: {os.path.basename(result)}")
            
            # Ask if user wants to open output directory
            if messagebox.askyesno("Success", 
                                 f"KMZ processed successfully!\n\nOutput: {os.path.basename(result)}\n\nOpen output directory?"):
                os.startfile(os.path.dirname(result))
        else:
            error_msg = str(result) if result else "Unknown error occurred"
            self.log_message(f"\n❌ FAILED: {error_msg}")
            self.status_var.set("Processing failed")
            messagebox.showerror("Error", f"Failed to process KMZ file:\n\n{error_msg}")
    
    def _add_mission_summary(self):
        """Add a summary of the most important mission information"""
        try:
            # Get the log content to extract key information
            log_content = self.log_text.get(1.0, tk.END)
            
            # Extract waypoint count
            waypoint_match = re.search(r'Found (\d+) waypoints', log_content)
            waypoint_count = waypoint_match.group(1) if waypoint_match else "Unknown"
            
            # Extract distance
            distance_match = re.search(r'Total distance: ([\d,]+\.?\d*) meters', log_content)
            distance = distance_match.group(1) if distance_match else "Unknown"
            
            # Extract total mission time
            time_match = re.search(r'Total mission time: (\d+m \d+s)', log_content)
            mission_time = time_match.group(1) if time_match else "Unknown"
            
            # Extract battery usage
            battery_match = re.search(r'Estimated battery usage: ~(\d+)%', log_content)
            battery_usage = battery_match.group(1) if battery_match else "Unknown"
            
            # Extract hover settings
            hover_enabled = self.enable_hover.get()
            hover_time = self.hover_time.get() if hover_enabled else "Disabled"
            
            # Add summary
            self.log_message(f"🎯 Waypoints: {waypoint_count}")
            self.log_message(f"📏 Distance: {distance} meters")
            self.log_message(f"⏱️  Mission Time: {mission_time}")
            self.log_message(f"🔋 Battery Usage: ~{battery_usage}%")
            self.log_message(f"🚁 Hover: {hover_time}s" if hover_enabled else "🚁 Hover: Disabled")
            self.log_message(f"📸 Actions: Photo capture at every waypoint")
            
        except Exception as e:
            self.log_message(f"⚠️  Could not generate summary: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run GUI
    app = KMZProcessorGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
