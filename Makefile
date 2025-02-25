# Makefile for packaging a Kivy app using PyInstaller

.PHONY: all windows mac linux clean

# Use the appropriate path separator for additional data.
ifeq ($(OS),Windows_NT)
    ADD_DATA = main.kv;.
else
    ADD_DATA = main.kv:.
endif

# Default target (build for the host OS)
all: linux

# Build for Windows (must be run on Windows or a Windows cross-compiler environment)
windows:
	pyinstaller --onefile --windowed --add-data "$(ADD_DATA)" main.py

# Build for macOS (run on macOS)
mac:
	pyinstaller --onefile --windowed --add-data "$(ADD_DATA)" main.py

# Build for Linux
linux:
	pyinstaller --onefile --add-data "$(ADD_DATA)" main.py

# Clean up build artifacts
clean:
	rm -rf build dist *.spec
