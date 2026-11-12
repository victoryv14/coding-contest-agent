import os
import sys
import time
import threading
import webbrowser
import subprocess

def get_venv_python():
    """Finds the python executable inside .venv if it exists."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == "win32":
        venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(base_dir, ".venv", "bin", "python")
    
    if os.path.exists(venv_python):
        return venv_python
    return None

def open_browser(url, delay=1.5):
    """Opens browser after server has started."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass

def main():
    venv_python = get_venv_python()

    # If running with global python and dependencies aren't here, switch to .venv python
    try:
        import uvicorn
    except ImportError:
        if venv_python and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
            print(f"[*] Switching to virtual environment: {venv_python}")
            result = subprocess.run([venv_python, os.path.abspath(__file__)] + sys.argv[1:])
            sys.exit(result.returncode)
        else:
            print("[!] Error: Required dependencies not found.")
            print("[!] Run: pip install -r requirements.txt")
            sys.exit(1)

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("=" * 60)
    print("🚀  Starting ContestPulse...")
    print(f"🌐  Website URL: {url}")
    print("✨  Opening website in your browser...")
    print("🛑  Press Ctrl+C in this terminal to stop.")
    print("=" * 60)

    # Launch browser in a background thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
