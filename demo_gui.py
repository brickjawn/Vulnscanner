#!/usr/bin/env python3
"""
VulnScanner GUI Demo Script
Demonstrates the modern, cutting-edge GUI interface

Usage:
    python3 demo_gui.py
"""

import tkinter as tk
from gui import VulnScannerGUI

def main():
    """Launch the VulnScanner GUI with demo configuration"""
    print("🔒 VulnScanner v2.0 - Elite Penetration Testing Toolkit")
    print("=" * 55)
    print("🚀 Launching modern GUI interface...")
    print("🎯 Features:")
    print("   • Dark theme with cutting-edge design")
    print("   • Responsive layout that adapts to screen size")
    print("   • Real-time progress monitoring")
    print("   • Professional status updates with emojis")
    print("   • Modern stat cards for metrics")
    print("   • Terminal-style output with syntax highlighting")
    print("=" * 55)
    
    # Create and configure the main window
    root = tk.Tk()
    
    # Initialize the GUI application
    app = VulnScannerGUI(root)
    
    # Pre-populate with demo values for convenience
    app.url_var.set("http://testphp.vulnweb.com/")
    app.threads_var.set("5")
    app.max_pages_var.set("10")
    app.timeout_var.set("5")
    app.portscan_var.set(True)
    
    print("✅ GUI loaded successfully!")
    print("💡 Example target pre-loaded: http://testphp.vulnweb.com/")
    print("🔧 Ready to start penetration testing!")
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 