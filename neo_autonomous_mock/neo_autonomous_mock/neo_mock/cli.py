import os, sys, subprocess, webbrowser, time
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, os.pardir))
    server = os.path.join(project_root, "server_mock.py")
    ui_index = os.path.join(project_root, "ui", "index.html")
    if not os.path.exists(server):
        print("Hittar inte server_mock.py. Kör från projektroten.")
        sys.exit(1)
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "server_mock:app", "--port", "8123"], cwd=project_root)
    time.sleep(1.5)
    if os.path.exists(ui_index):
        webbrowser.open_new_tab("file://" + ui_index.replace("\\","/"))
    print("Neo Autonomous Mock kör. Avsluta med Ctrl+C.")
    proc.wait()
