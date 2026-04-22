#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import json
import os
import sys
from pathlib import Path
import webbrowser

class BlackIceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BlackIce Shellcode Loader Generator")
        self.root.geometry("1000x750")
        
        # Apply a dark theme
        self.root.tk_setPalette(background='#2b2b2b', foreground='#ffffff', 
                                activeBackground='#404040', activeForeground='#ffffff')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_main_tab()
        self.create_execution_tab()
        self.create_evasion_tab()
        self.create_encoding_tab()
        self.create_advanced_tab()
        self.create_output_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Process reference for stopping operations
        self.blackice_process = None
        self.blackice_thread = None
        
        # Find BlackIce binary
        self.find_blackice_binary()
    
    def find_blackice_binary(self):
        # Try to find the BlackIce binary in common locations
        possible_paths = [
            "./build/blackice_linux_amd64",
            "./blackice_linux_amd64",
            "/usr/local/bin/blackice",
            "/usr/bin/blackice"
        ]
        
        self.blackice_path = None
        for path in possible_paths:
            if os.path.exists(path):
                self.blackice_path = path
                self.status_var.set(f"Found BlackIce at {path}")
                return
        
        # If not found, ask user to locate it
        self.status_var.set("BlackIce binary not found. Please specify the path in the Advanced tab.")
    
    def create_main_tab(self):
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Main")
        
        # Required parameters section
        required_frame = ttk.LabelFrame(main_frame, text="Required Parameters")
        required_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(required_frame, text="Input:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(required_frame, textvariable=self.input_var, width=60)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.input_browse_button = ttk.Button(required_frame, text="Browse", command=self.browse_input)
        self.input_browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(required_frame, text="Output:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(required_frame, textvariable=self.output_var, width=60)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.output_browse_button = ttk.Button(required_frame, text="Browse", command=self.browse_output)
        self.output_browse_button.grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(required_frame, text="Format:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.format_var = tk.StringVar(value="exe")
        self.format_combo = ttk.Combobox(required_frame, textvariable=self.format_var, values=["exe", "dll"])
        self.format_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Architecture section
        arch_frame = ttk.LabelFrame(main_frame, text="Architecture")
        arch_frame.pack(fill="x", padx=10, pady=10)
        
        self.arch_var = tk.StringVar(value="amd64")
        ttk.Radiobutton(arch_frame, text="amd64", variable=self.arch_var, value="amd64").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(arch_frame, text="386", variable=self.arch_var, value="386").pack(side=tk.LEFT, padx=5)
        
        # Quick options section
        quick_frame = ttk.LabelFrame(main_frame, text="Quick Options")
        quick_frame.pack(fill="x", padx=10, pady=10)
        
        self.verbose_var = tk.BooleanVar()
        self.verbose_check = ttk.Checkbutton(quick_frame, text="Verbose", variable=self.verbose_var)
        self.verbose_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.compress_var = tk.BooleanVar()
        self.compress_check = ttk.Checkbutton(quick_frame, text="Compress", variable=self.compress_var)
        self.compress_check.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.calc_var = tk.BooleanVar()
        self.calc_check = ttk.Checkbutton(quick_frame, text="Use calc.exe shellcode (no input needed)", variable=self.calc_var)
        self.calc_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.rand_var = tk.BooleanVar()
        self.rand_check = ttk.Checkbutton(quick_frame, text="Random parameters (for testing)", variable=self.rand_var)
        self.rand_check.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Generate button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.generate_button = ttk.Button(button_frame, text="Generate Loader", command=self.generate_loader)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", state=tk.DISABLED, command=self.stop_generation)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_execution_tab(self):
        exec_frame = ttk.Frame(self.notebook)
        self.notebook.add(exec_frame, text="Execution")
        
        # Execution technique section
        technique_frame = ttk.LabelFrame(exec_frame, text="Execution Technique")
        technique_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(technique_frame, text="Technique:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.exec_var = tk.StringVar(value="SuspendedProcess")
        self.exec_combo = ttk.Combobox(technique_frame, textvariable=self.exec_var, 
                                      values=["SuspendedProcess", "ProcessHollowing", "NtCreateThreadEx", 
                                             "EtwpCreateEtwThread", "NtQueueApcThreadEx", "No-RWX"])
        self.exec_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(technique_frame, text="Process:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.proc_var = tk.StringVar(value="notepad.exe")
        self.proc_entry = ttk.Entry(technique_frame, textvariable=self.proc_var, width=30)
        self.proc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Sleep option
        sleep_frame = ttk.LabelFrame(exec_frame, text="Sleep")
        sleep_frame.pack(fill="x", padx=10, pady=10)
        
        self.sleep_var = tk.BooleanVar()
        self.sleep_check = ttk.Checkbutton(sleep_frame, text="Delay shellcode execution", variable=self.sleep_var)
        self.sleep_check.pack(anchor="w", padx=5, pady=5)
    
    def create_evasion_tab(self):
        evasion_frame = ttk.Frame(self.notebook)
        self.notebook.add(evasion_frame, text="Evasion")
        
        # Evasion options section
        evasion_options_frame = ttk.LabelFrame(evasion_frame, text="Evasion Options")
        evasion_options_frame.pack(fill="x", padx=10, pady=10)
        
        self.sandbox_var = tk.BooleanVar()
        self.sandbox_check = ttk.Checkbutton(evasion_options_frame, text="Enable sandbox evasion", variable=self.sandbox_var)
        self.sandbox_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.hashing_var = tk.BooleanVar()
        self.hashing_check = ttk.Checkbutton(evasion_options