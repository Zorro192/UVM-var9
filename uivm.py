
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, tempfile, os

ROOT = tk.Tk()
ROOT.title("UVM Variant 9 - Simple GUI")
text = tk.Text(ROOT, width=100, height=30)
text.pack()

def open_file():
    p = filedialog.askopenfilename(filetypes=(("YAML files","*.yml *.yaml"),("All","*.*")))
    if p:
        with open(p,'r',encoding='utf-8') as f:
            text.delete('1.0',tk.END)
            text.insert('1.0', f.read())

def save_file():
    p = filedialog.asksaveasfilename(defaultextension=".yml")
    if p:
        with open(p,'w',encoding='utf-8') as f:
            f.write(text.get('1.0',tk.END))
        messagebox.showinfo("Saved","Saved to "+p)

def assemble_and_run():
    yml = text.get('1.0',tk.END)
    tmpy = tempfile.NamedTemporaryFile(delete=False, suffix='.yml')
    tmpy.write(yml.encode('utf-8'))
    tmpy.close()
    binp = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
    binp.close()
    # call assembler
    try:
        subprocess.check_call(['python','assembler.py', tmpy.name, binp.name])
        # run interpreter and create dump
        dump = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        dump.close()
        subprocess.check_call(['python','interpreter.py', binp.name, dump.name])
        with open(dump.name,'r',encoding='utf-8') as f:
            out = f.read()
        messagebox.showinfo("Memory dump (XML)", out[:10000])
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", str(e))
    finally:
        pass

frm = tk.Frame(ROOT)
frm.pack()
tk.Button(frm, text="Open", command=open_file).pack(side='left')
tk.Button(frm, text="Save", command=save_file).pack(side='left')
tk.Button(frm, text="Assemble & Run", command=assemble_and_run).pack(side='left')

ROOT.mainloop()
