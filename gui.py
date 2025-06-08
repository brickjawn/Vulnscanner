import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import datetime

from scanner.portscan import scan_ports
from scanner.crawler import crawl_site
from scanner.xss import test_xss
from scanner.sqli import test_sqli
from scanner.parallel import parallel_scan
from scanner.report import generate_report

class VulnScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VulnScanner v2.0 - Advanced Penetration Testing Toolkit")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.setup_styles()
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # Variables
        self.url_var = tk.StringVar()
        self.threads_var = tk.StringVar(value="5")
        self.max_pages_var = tk.StringVar(value="10")
        self.timeout_var = tk.StringVar(value="5")
        self.portscan_var = tk.BooleanVar(value=True)
        self.output_format_var = tk.StringVar(value="cli")
        
        # Scan state
        self.scan_running = False
        self.scan_results = []
        
        self.create_widgets()
        self.check_queue()
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        
        # Configure custom colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='#e74c3c')
        style.configure('Warning.TLabel', font=('Arial', 10), foreground='#f39c12')
        
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="VulnScanner v2.0", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Scan Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Target URL
        ttk.Label(config_frame, text="Target URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        url_entry = ttk.Entry(config_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Advanced options frame
        advanced_frame = ttk.Frame(config_frame)
        advanced_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        advanced_frame.columnconfigure(1, weight=1)
        advanced_frame.columnconfigure(3, weight=1)
        
        # Threads
        ttk.Label(advanced_frame, text="Threads:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(advanced_frame, textvariable=self.threads_var, width=8).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        # Max pages
        ttk.Label(advanced_frame, text="Max Pages:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(advanced_frame, textvariable=self.max_pages_var, width=8).grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        # Timeout
        ttk.Label(advanced_frame, text="Timeout (s):").grid(row=0, column=4, sticky=tk.W)
        ttk.Entry(advanced_frame, textvariable=self.timeout_var, width=8).grid(row=0, column=5, sticky=tk.W, padx=(5, 0))
        
        # Options frame
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Port scan checkbox
        ttk.Checkbutton(options_frame, text="Enable Port Scanning", 
                       variable=self.portscan_var).grid(row=0, column=0, sticky=tk.W)
        
        # Output format
        ttk.Label(options_frame, text="Output Format:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        format_combo = ttk.Combobox(options_frame, textvariable=self.output_format_var, 
                                   values=["cli", "json", "csv"], width=10, state="readonly")
        format_combo.grid(row=0, column=2, sticky=tk.W)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Scan button
        self.scan_btn = ttk.Button(button_frame, text="🚀 Start Scan", command=self.start_scan)
        self.scan_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Output", command=self.clear_output)
        clear_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Save report button
        self.save_btn = ttk.Button(button_frame, text="💾 Save Report", command=self.save_report, state=tk.DISABLED)
        self.save_btn.grid(row=0, column=3)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Scan Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to scan", style='Header.TLabel')
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Statistics frame
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        stats_frame.columnconfigure(5, weight=1)
        
        # Statistics labels
        ttk.Label(stats_frame, text="Pages:").grid(row=0, column=0, sticky=tk.W)
        self.pages_label = ttk.Label(stats_frame, text="0")
        self.pages_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(stats_frame, text="Forms:").grid(row=0, column=2, sticky=tk.W)
        self.forms_label = ttk.Label(stats_frame, text="0")
        self.forms_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(stats_frame, text="Findings:").grid(row=0, column=4, sticky=tk.W)
        self.findings_label = ttk.Label(stats_frame, text="0", style='Success.TLabel')
        self.findings_label.grid(row=0, column=5, sticky=tk.W, padx=(5, 0))
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Scan Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Output text with custom styling
        self.output_box = scrolledtext.ScrolledText(
            output_frame, 
            width=100, 
            height=20, 
            state=tk.DISABLED, 
            font=('Consolas', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white'
        )
        self.output_box.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.output_box.tag_configure("info", foreground="#3498db")
        self.output_box.tag_configure("success", foreground="#27ae60")
        self.output_box.tag_configure("warning", foreground="#f39c12")
        self.output_box.tag_configure("error", foreground="#e74c3c")
        self.output_box.tag_configure("critical", foreground="#c0392b", font=('Consolas', 10, 'bold'))
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def validate_inputs(self):
        """Validate user inputs"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a target URL.")
            return False
        
        try:
            threads = int(self.threads_var.get())
            if threads < 1 or threads > 50:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Threads must be a number between 1 and 50.")
            return False
        
        try:
            max_pages = int(self.max_pages_var.get())
            if max_pages < 1 or max_pages > 100:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Max pages must be a number between 1 and 100.")
            return False
        
        try:
            timeout = int(self.timeout_var.get())
            if timeout < 1 or timeout > 60:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Timeout must be a number between 1 and 60 seconds.")
            return False
        
        return True
    
    def start_scan(self):
        """Start the vulnerability scan"""
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
        
        # Reset progress
        self.progress_var.set(0)
        self.status_label.config(text="Initializing scan...")
        self.pages_label.config(text="0")
        self.forms_label.config(text="0")
        self.findings_label.config(text="0")
        
        # Start scan in separate thread
        scan_thread = threading.Thread(target=self.run_scan_thread, daemon=True)
        scan_thread.start()
    
    def stop_scan(self):
        """Stop the current scan"""
        self.scan_running = False
        self.log_message("Scan stopped by user", "warning")
        self.scan_complete()
    
    def run_scan_thread(self):
        """Run the actual scan in a separate thread"""
        try:
            url = self.url_var.get().strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            threads = int(self.threads_var.get())
            max_pages = int(self.max_pages_var.get())
            timeout = int(self.timeout_var.get())
            enable_portscan = self.portscan_var.get()
            
            self.log_message(f"Starting scan of {url}", "info")
            self.log_message(f"Configuration: {threads} threads, {max_pages} max pages, {timeout}s timeout", "info")
            
            start_time = time.time()
            findings = []
            
            # Port scanning
            if enable_portscan and self.scan_running:
                host = url.split("//")[-1].split("/")[0]
                self.log_message(f"Starting port scan for: {host}", "info")
                self.status_label.config(text="Port scanning...")
                
                open_ports = scan_ports(host)
                
                if open_ports:
                    self.log_message(f"Found {len(open_ports)} open ports", "success")
                    for port_info in open_ports:
                        findings.append({
                            'type': 'Open Port',
                            'url': host,
                            'details': f"{port_info['port']}/{port_info['protocol']} {port_info['service']}",
                            'severity': 'info'
                        })
                else:
                    self.log_message("No open ports found", "info")
            
            # Web crawling
            if self.scan_running:
                self.log_message(f"Crawling {url} for forms and links...", "info")
                self.status_label.config(text="Crawling website...")
                
                pages_crawled = 0
                def crawl_progress(increment):
                    nonlocal pages_crawled
                    pages_crawled += increment
                    self.message_queue.put(('update_pages', pages_crawled))
                
                links, forms = crawl_site(url, max_pages=max_pages, timeout=timeout, 
                                        progress_callback=crawl_progress)
                
                self.message_queue.put(('update_forms', len(forms)))
                
                if not forms:
                    self.log_message("No forms found for vulnerability testing", "warning")
                else:
                    self.log_message(f"Found {len(forms)} forms for testing", "success")
                    
                    # XSS Testing
                    if self.scan_running:
                        self.log_message("Testing for XSS vulnerabilities...", "info")
                        self.status_label.config(text="Testing XSS vulnerabilities...")
                        
                        xss_tested = 0
                        def xss_progress(increment):
                            nonlocal xss_tested
                            xss_tested += increment
                            progress = (xss_tested / len(forms)) * 30  # 30% of total progress
                            self.message_queue.put(('update_progress', 30 + progress))
                        
                        xss_findings = parallel_scan(
                            lambda f: test_xss([f[0]], [f], progress_callback=xss_progress),
                            forms,
                            threads=threads
                        )
                        findings.extend(xss_findings)
                        
                        if xss_findings:
                            self.log_message(f"Found {len(xss_findings)} XSS vulnerabilities", "error")
                    
                    # SQLi Testing
                    if self.scan_running:
                        self.log_message("Testing for SQL Injection vulnerabilities...", "info")
                        self.status_label.config(text="Testing SQL injection...")
                        
                        sqli_tested = 0
                        def sqli_progress(increment):
                            nonlocal sqli_tested
                            sqli_tested += increment
                            progress = (sqli_tested / len(forms)) * 30  # 30% of total progress
                            self.message_queue.put(('update_progress', 60 + progress))
                        
                        sqli_findings = parallel_scan(
                            lambda f: test_sqli([f[0]], [f], progress_callback=sqli_progress),
                            forms,
                            threads=threads
                        )
                        findings.extend(sqli_findings)
                        
                        if sqli_findings:
                            self.log_message(f"Found {len(sqli_findings)} SQL injection vulnerabilities", "critical")
            
            # Complete scan
            if self.scan_running:
                scan_time = time.time() - start_time
                self.scan_results = findings
                
                self.message_queue.put(('scan_complete', {
                    'findings': len(findings),
                    'scan_time': scan_time,
                    'url': url
                }))
            
        except Exception as e:
            self.message_queue.put(('scan_error', str(e)))
    
    def scan_complete(self):
        """Handle scan completion"""
        self.scan_running = False
        self.scan_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.status_label.config(text="Scan completed")
    
    def log_message(self, message, level="info"):
        """Add a message to the output log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.message_queue.put(('log', formatted_message, level))
    
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
        """Check for messages from scan thread"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message[0] == 'log':
                    text, level = message[1], message[2]
                    self.output_box.config(state=tk.NORMAL)
                    self.output_box.insert(tk.END, text, level)
                    self.output_box.see(tk.END)
                    self.output_box.config(state=tk.DISABLED)
                    
                elif message[0] == 'update_progress':
                    self.progress_var.set(message[1])
                    
                elif message[0] == 'update_pages':
                    self.pages_label.config(text=str(message[1]))
                    
                elif message[0] == 'update_forms':
                    self.forms_label.config(text=str(message[1]))
                    
                elif message[0] == 'scan_complete':
                    data = message[1]
                    self.findings_label.config(text=str(data['findings']))
                    self.log_message(f"Scan completed in {data['scan_time']:.2f} seconds", "success")
                    self.log_message(f"Found {data['findings']} total findings", "success")
                    self.scan_complete()
                    
                elif message[0] == 'scan_error':
                    self.log_message(f"Scan error: {message[1]}", "error")
                    self.scan_complete()
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = VulnScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()