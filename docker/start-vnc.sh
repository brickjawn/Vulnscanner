#!/bin/bash

# VNC startup script for VulnScanner GUI
set -e

echo "Starting VulnScanner GUI with VNC support..."

# Set default resolution if not provided
RESOLUTION=${RESOLUTION:-1024x768}

# Start Xvfb (Virtual display)
echo "Starting virtual display (Xvfb)..."
Xvfb :1 -screen 0 ${RESOLUTION}x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

# Wait for display to be ready
sleep 2

# Start window manager
echo "Starting window manager (Fluxbox)..."
DISPLAY=:1 fluxbox &
FLUXBOX_PID=$!

# Start VNC server
echo "Starting VNC server on port 5900..."
DISPLAY=:1 x11vnc -forever -usepw -create -shared -rfbport 5900 &
VNC_PID=$!

# Start noVNC web interface
echo "Starting noVNC web interface on port 6080..."
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &
NOVNC_PID=$!

# Wait for VNC to be ready
sleep 3

echo "VNC server is running!"
echo "Connect via:"
echo "  VNC Client: localhost:5900 (password: vulnscan123)"
echo "  Web Browser: http://localhost:6080/vnc.html"

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $NOVNC_PID $VNC_PID $FLUXBOX_PID $XVFB_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start the GUI application
echo "Starting VulnScanner GUI..."
DISPLAY=:1 python /app/gui.py &
GUI_PID=$!

# Keep the script running and monitor processes
while true; do
    # Check if any critical process died
    if ! kill -0 $XVFB_PID 2>/dev/null; then
        echo "Xvfb died, exiting..."
        cleanup
    fi
    
    if ! kill -0 $VNC_PID 2>/dev/null; then
        echo "VNC server died, exiting..."
        cleanup
    fi
    
    sleep 5
done 