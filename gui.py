import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font
import threading
import queue
import time
import datetime
import subprocess
import json
import os

class VulnScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 VulnScanner v2.0 - Elite Penetration Testing Toolkit")
        
        # Get screen dimensions for responsive design
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window size based on screen size (80% of screen)
        window_width = min(1400, int(screen_width * 0.8))
        window_height = min(900, int(screen_height * 0.8))
        
        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # Configure professional theme
        self.setup_professional_theme()
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # Variables
        self.url_var = tk.StringVar()
        self.threads_var = tk.StringVar(value="5")
        self.max_pages_var = tk.StringVar(value="10")
        self.timeout_var = tk.StringVar(value="5")
        self.portscan_var = tk.BooleanVar(value=True)
        self.output_format_var = tk.StringVar(value="cli")
        self.progress_var = tk.DoubleVar()
        
        # Scan state
        self.scan_running = False
        self.scan_results = []
        
        self.create_widgets()
        self.check_queue()
        
    def setup_professional_theme(self):
        """Configure a professional light theme with high contrast for readability."""
        # Professional light color palette
        self.colors = {
            'bg_primary': '#f0f0f0',      # Main window background
            'bg_secondary': '#ffffff',    # Card/widget background
            'text_primary': '#212121',    # Primary text (near black)
            'text_secondary': '#5f5f5f',  # Secondary text (gray)
            'accent_primary': '#0078d4',  # Professional blue
            'accent_success': '#107c10',  # Dark green
            'accent_warning': '#f7a800',  # Amber
            'accent_error': '#d83b01',    # Dark orange/red
            'border': '#cccccc',          # Light gray border
            'hover': '#e1e1e1'            # Hover state for buttons
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        style = ttk.Style(self.root)
        
        # General widget styling
        style.configure('.',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))

        style.configure('Title.TLabel', 
                       font=('Segoe UI', 20, 'bold'), 
                       foreground=self.colors['text_primary'])
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'), 
                       foreground=self.colors['accent_primary'])

        style.configure('Success.TLabel', font=('Segoe UI', 10, 'bold'), foreground=self.colors['accent_success'])
        style.configure('Error.TLabel', font=('Segoe UI', 10, 'bold'), foreground=self.colors['accent_error'])
        style.configure('Warning.TLabel', font=('Segoe UI', 10, 'bold'), foreground=self.colors['accent_warning'])
        
        # Frame and LabelFrame (Card) styling
        style.configure('TFrame', background=self.colors['bg_primary'])
        style.configure('Card.TLabelframe', 
                       background=self.colors['bg_secondary'],
                       relief='solid',
                       borderwidth=1,
                       bordercolor=self.colors['border'])
        style.configure('Card.TLabelframe.Label', 
                       font=('Segoe UI', 11, 'bold'),
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'])
        
        # Entry widget styling
        style.configure('TEntry',
                       fieldbackground=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       insertcolor=self.colors['text_primary'],
                       bordercolor=self.colors['border'],
                       lightcolor=self.colors['border'],
                       darkcolor=self.colors['border'])
        
        # Button styling
        style.configure('TButton',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=self.colors['bg_secondary'],
                       background=self.colors['accent_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 5))
        style.map('TButton',
                 background=[('active', '#005a9e'), ('disabled', '#cccccc')])
        
        style.configure('Danger.TButton', background=self.colors['accent_error'])
        style.map('Danger.TButton', background=[('active', '#a22c00')])

        # Progressbar styling
        style.configure('Horizontal.TProgressbar',
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['border'],
                       thickness=8)

        # Checkbutton and Combobox
        style.configure('TCheckbutton', background=self.colors['bg_secondary'])
        style.configure('TCombobox',
                        fieldbackground=self.colors['bg_secondary'],
                        foreground=self.colors['text_primary'],
                        arrowcolor=self.colors['accent_primary'])

    def create_widgets(self):
        """Create and layout a structured and readable GUI."""
        # --- Main Container ---
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- PanedWindow for Resizable Sections ---
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # --- Top Pane (Controls) ---
        top_pane = ttk.Frame(paned_window, padding=(0, 0, 0, 10))
        paned_window.add(top_pane, weight=0)
        top_pane.columnconfigure(0, weight=1)

        # --- Bottom Pane (Output) ---
        output_container = ttk.Frame(paned_window, padding=(0, 10, 0, 0))
        paned_window.add(output_container, weight=1)
        output_container.columnconfigure(0, weight=1)
        output_container.rowconfigure(0, weight=1)

        # --- Configuration Section ---
        config_frame = ttk.LabelFrame(top_pane, text="Scan Configuration", style='Card.TLabelframe', padding=15)
        config_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="Target URL:").grid(row=0, column=0, sticky='w')
        url_entry = ttk.Entry(config_frame, textvariable=self.url_var, font=('Segoe UI', 10))
        url_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        
        # --- Advanced Options ---
        adv_frame = ttk.Frame(config_frame)
        adv_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        ttk.Label(adv_frame, text="Threads:").pack(side='left', pady=(0, 5))
        ttk.Entry(adv_frame, textvariable=self.threads_var, width=5).pack(side='left', padx=(5, 15), pady=(0, 5))
        
        ttk.Label(adv_frame, text="Max Pages:").pack(side='left', pady=(0, 5))
        ttk.Entry(adv_frame, textvariable=self.max_pages_var, width=5).pack(side='left', padx=(5, 15), pady=(0, 5))

        ttk.Label(adv_frame, text="Timeout (s):").pack(side='left', pady=(0, 5))
        ttk.Entry(adv_frame, textvariable=self.timeout_var, width=5).pack(side='left', padx=(5, 0), pady=(0, 5))

        ttk.Checkbutton(adv_frame, text="Enable Port Scan", variable=self.portscan_var).pack(side='left', padx=(20, 0), pady=(0, 5))

        # --- Control Buttons ---
        button_frame = ttk.Frame(top_pane)
        button_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        self.scan_btn = ttk.Button(button_frame, text="Start Scan", command=self.start_scan, style='TButton')
        self.scan_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))

        self.stop_btn = ttk.Button(button_frame, text="Stop Scan", command=self.stop_scan, style='Danger.TButton', state=tk.DISABLED)
        self.stop_btn.pack(side='left', expand=True, fill='x', padx=(5, 5))

        clear_btn = ttk.Button(button_frame, text="Clear Output", command=self.clear_output)
        clear_btn.pack(side='left', expand=True, fill='x', padx=(5, 5))
        
        self.save_btn = ttk.Button(button_frame, text="Save Report", command=self.save_report, state=tk.DISABLED)
        self.save_btn.pack(side='left', expand=True, fill='x', padx=(5, 0))

        # --- Progress Section ---
        progress_frame = ttk.LabelFrame(top_pane, text="Scan Progress", style='Card.TLabelframe', padding=15)
        progress_frame.grid(row=2, column=0, sticky='ew')
        progress_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(progress_frame, text="Ready to scan", style='Header.TLabel')
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, style='Horizontal.TProgressbar', maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky='ew')
        self.pages_label = ttk.Label(stats_frame, text="Pages: 0")
        self.pages_label.pack(side='left', expand=True, fill='x')
        self.forms_label = ttk.Label(stats_frame, text="Forms: 0")
        self.forms_label.pack(side='left', expand=True, fill='x')
        self.findings_label = ttk.Label(stats_frame, text="Findings: 0")
        self.findings_label.pack(side='left', expand=True, fill='x')

        # --- Output Window ---
        output_frame = ttk.LabelFrame(output_container, text="Live Scan Output", style='Card.TLabelframe', padding=10)
        output_frame.grid(row=0, column=0, sticky="nsew")
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        self.output_box = scrolledtext.ScrolledText(
            output_frame,
            state=tk.DISABLED,
            font=('Consolas', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0
        )
        self.output_box.grid(row=0, column=0, sticky="nsew")

        # Configure text tags for colored output
        self.output_box.tag_configure("info", foreground=self.colors['accent_primary'])
        self.output_box.tag_configure("success", foreground=self.colors['accent_success'])
        self.output_box.tag_configure("warning", foreground=self.colors['accent_warning'])
        self.output_box.tag_configure("error", foreground=self.colors['accent_error'])
        self.output_box.tag_configure("critical", foreground=self.colors['accent_error'], font=('Consolas', 10, 'bold'))
        self.output_box.tag_configure("header", foreground=self.colors['text_primary'], font=('Consolas', 11, 'bold'))
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_bar.grid(row=1, column=0, sticky="ew", pady=(10, 0))
    
    def validate_inputs(self):
        """Validate user inputs"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Configuration Error", "🎯 Please enter a target URL to begin the penetration test.")
            return False
        
        try:
            threads = int(self.threads_var.get())
            if threads < 1 or threads > 50:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Configuration Error", "⚙️ Threads must be a number between 1 and 50.")
            return False
        
        try:
            max_pages = int(self.max_pages_var.get())
            if max_pages < 1 or max_pages > 100:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Configuration Error", "📄 Max pages must be a number between 1 and 100.")
            return False
        
        try:
            timeout = int(self.timeout_var.get())
            if timeout < 1 or timeout > 60:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Configuration Error", "⏱️ Timeout must be a number between 1 and 60 seconds.")
            return False
        
        return True
    
    def start_scan(self):
        """Start the Docker scan"""
        if not self.validate_inputs():
            return
        
        self.scan_running = True
        self.scan_results = []
        
        # Update UI state
        self.scan_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        
        # Clear previous output
        self.clear_output()
        
        # Reset progress with modern styling
        self.progress_var.set(0)
        self.status_label.config(text="Initializing scan...")
        self.status_bar.config(text="Scan in progress...")
        self.pages_label.config(text="Pages: 0")
        self.forms_label.config(text="Forms: 0")
        self.findings_label.config(text="Findings: 0")
        
        # Start scan in separate thread
        self.scan_process = None
        scan_thread = threading.Thread(target=self.run_scan_thread, daemon=True)
        scan_thread.start()
    
    def stop_scan(self):
        """Stop the current Docker scan"""
        self.scan_running = False
        self.log_message("⏹️  Scan stopped by user.", "warning")
        self.status_label.config(text="⏹️ Scan Stopped", style='Warning.TLabel')
        self.status_bar.config(text="Scan stopped by user.")
        
        if self.scan_process:
            try:
                # Attempt to stop the Docker container gracefully first
                subprocess.run(["docker", "stop", "vulnscanner-gui-backend"], timeout=5, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.scan_process.terminate() # End the process if still running
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass # Ignore errors if docker isn't found or takes too long
            finally:
                self.scan_process = None
                self.scan_complete()
    
    def run_scan_thread(self):
        """Run the scan in a Docker container and stream results."""
        self.scan_running = True
        
        try:
            url = self.url_var.get().strip()
            threads = self.threads_var.get()
            max_pages = self.max_pages_var.get()
            timeout = self.timeout_var.get()
            
            # Build the Docker command
            docker_command = [
                "docker", "run", "--rm", "-i",
                "--name", "vulnscanner-gui-backend",
                "vulnscanner/vulnscanner:latest",
                "--url", url,
                "--threads", threads,
                "--max-pages", max_pages,
                "--timeout", timeout,
                "--gui-comms"
            ]
            
            if self.portscan_var.get():
                docker_command.append("--enable-portscan")

            self.log_message("🚀 Starting Dockerized scan...", "info")
            
            self.scan_process = subprocess.Popen(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1 # Line-buffered
            )

            # Process stderr in a separate thread to avoid blocking
            stderr_thread = threading.Thread(target=self.stream_stderr, args=(self.scan_process,), daemon=True)
            stderr_thread.start()

            # Process stdout line-by-line
            for line in self.scan_process.stdout:
                if not self.scan_running:
                    break
                try:
                    message = json.loads(line)
                    self.message_queue.put(message)
                except json.JSONDecodeError:
                    # Non-json output can be treated as a generic log
                    self.message_queue.put({'type': 'log', 'data': {'level': 'info', 'message': line.strip()}})

            self.scan_process.wait()

        except FileNotFoundError:
            self.message_queue.put({'type': 'scan_error', 'data': "Docker is not installed or not in the system's PATH."})
        except Exception as e:
            self.message_queue.put({'type': 'scan_error', 'data': f"An unexpected error occurred: {e}"})
        finally:
            if self.scan_running: # If the scan wasn't stopped manually
                self.message_queue.put({'type': 'scan_complete', 'data': {}}) # Signal completion
            self.scan_running = False

    def stream_stderr(self, process):
        """Reads stderr from the subprocess and logs it, checking for specific errors."""
        for line in process.stderr:
            if "permission denied" in line.lower() and "docker.sock" in line.lower():
                # This is a specific, common error that we can give a helpful message for.
                self.message_queue.put({'type': 'docker_permission_error'})
            else:
                self.message_queue.put({'type': 'log', 'data': {'level': 'error', 'message': f"DOCKER-ERROR: {line.strip()}"}})

    def scan_complete(self):
        """Handle scan completion"""
        self.scan_running = False
        self.scan_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.status_label.config(text="✅ Scan completed successfully!", style='Success.TLabel')
        self.status_bar.config(text="🟢 Scan completed - Ready for new scan")
    
    def log_message(self, message, level="info"):
        """Puts a log message onto the queue in the standard dict format."""
        self.message_queue.put({
            'type': 'log',
            'data': {
                'level': level,
                'message': message
            }
        })
    
    def clear_output(self):
        """Clear the output text box"""
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete(1.0, tk.END)
        self.output_box.config(state=tk.DISABLED)
    
    def save_report(self):
        """Save scan results to file"""
        if not self.scan_results:
            messagebox.showwarning("Warning", "No scan results to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    import json
                    with open(filename, 'w') as f:
                        json.dump(self.scan_results, f, indent=2)
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='') as f:
                        if self.scan_results:
                            writer = csv.DictWriter(f, fieldnames=self.scan_results[0].keys())
                            writer.writeheader()
                            writer.writerows(self.scan_results)
                else:
                    with open(filename, 'w') as f:
                        for finding in self.scan_results:
                            f.write(f"{finding}\n")
                
                messagebox.showinfo("Success", f"Report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")
    
    def check_queue(self):
        """Check for messages from the scan thread and update the GUI."""
        try:
            # Check if the GUI window still exists
            if not self.root.winfo_exists():
                return
                
            while True:
                message = self.message_queue.get_nowait()
                msg_type = message.get('type')
                msg_data = message.get('data', {})

                # Helper to consistently format and append text to the output box
                def append_log(text, level):
                    try:
                        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                        formatted_message = f"[{timestamp}] {text}\\n"
                        self.output_box.config(state=tk.NORMAL)
                        self.output_box.insert(tk.END, formatted_message, level)
                        self.output_box.see(tk.END)
                        self.output_box.config(state=tk.DISABLED)
                    except tk.TclError:
                        # GUI has been destroyed, stop processing
                        return

                if msg_type == 'log':
                    append_log(msg_data.get('message', ''), msg_data.get('level', 'info'))
                
                elif msg_type == 'progress':
                    # A simple increment provides visual feedback that the scan is active
                    try:
                        current_progress = self.progress_var.get()
                        if current_progress < 99: # Avoid hitting 100 prematurely
                            self.progress_var.set(current_progress + 0.5)
                    except tk.TclError:
                        return

                elif msg_type == 'update_pages':
                    try:
                        self.pages_label.config(text=f"Pages: {msg_data}")
                    except tk.TclError:
                        return
                    
                elif msg_type == 'update_forms':
                    try:
                        self.forms_label.config(text=f"Forms: {msg_data}")
                    except tk.TclError:
                        return

                elif msg_type == 'finding':
                    finding_text = f"VULNERABILITY: {msg_data.get('type')} in {msg_data.get('details')}"
                    append_log(finding_text, 'critical')
                    
                    # Safely increment the findings count
                    try:
                        current_findings = int(self.findings_label.cget("text").split(": ")[1])
                        self.findings_label.config(text=f"Findings: {current_findings + 1}")
                    except (IndexError, ValueError, tk.TclError):
                        try:
                            self.findings_label.config(text="Findings: 1") # Recover if parsing fails
                        except tk.TclError:
                            return
                    
                elif msg_type == 'scan_complete':
                    total_findings = 0
                    try:
                        total_findings = int(self.findings_label.cget("text").split(": ")[1])
                    except (IndexError, ValueError, tk.TclError):
                        pass # Use 0 if label can't be parsed
                        
                    scan_time = msg_data.get('scan_time', 0)
                    append_log(f"Scan completed in {scan_time:.2f} seconds.", "success")
                    append_log(f"Found {total_findings} total findings.", "success")
                    try:
                        self.scan_complete()
                    except tk.TclError:
                        return
                    
                elif msg_type == 'scan_error':
                    append_log(f"SCAN ERROR: {msg_data}", "error")
                    try:
                        self.scan_complete()
                    except tk.TclError:
                        return
                
                elif msg_type == 'docker_permission_error':
                    try:
                        self.scan_complete() # End the scan process visually
                        messagebox.showerror(
                            "Docker Permission Error",
                            "Could not connect to the Docker daemon.\n\n"
                            "This is a common permissions issue. To fix it, please run the following command in your terminal:\n\n"
                            "sudo usermod -aG docker ${USER}\n\n"
                            "IMPORTANT: You MUST log out and log back in for this change to take effect."
                        )
                    except tk.TclError:
                        return
                    
        except queue.Empty:
            pass
        except tk.TclError:
            # GUI has been destroyed, stop the queue checking
            return
        
        # Schedule the next check only if GUI still exists
        try:
            self.root.after(100, self.check_queue)
        except tk.TclError:
            pass

def main():
    root = tk.Tk()
    app = VulnScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()