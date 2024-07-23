import tkinter as tk
import base64
import subprocess
import os
import re
import json
import sv_ttk
from tkinter import ttk
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image, ImageTk

def password(pwd):
	pwdEncrypt = pwd.encode()
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt="B&x3P4EC2&UD5Wlb".encode(),
		iterations=1024,
		backend=default_backend()
	)
	key = base64.urlsafe_b64encode(kdf.derive(pwdEncrypt))
	return key


profilesPath = os.path.expandvars("%APPDATA%\\Opera Software\\Opera GX Stable\\_side_profiles")
profilesJSON = []

def detectProfilesJSON():
		for uuid in os.listdir(profilesPath):
				profileDir = f"{profilesPath}\\{uuid}"
				if os.path.isdir(profileDir):
						# Change into profile directory only if it exists
						os.chdir(profileDir)
				else:
						print(f"Directory does not exist: {profileDir}")
						
				# Check if "Opera On The Side.ico" exists in the directory
				iconfile = "Opera On The Side.ico" if "Opera On The Side.ico" in os.listdir(".") else ""

				for jsonFile in os.listdir("."):
						# Search for JSON files using RegEx
						jsonfile = re.findall(".*_sideprofile.json", jsonFile)
						result = jsonfile[0] if len(jsonfile) > 0 else ""

						# If JSON is found, append its contents to profilesJSON
						if bool(result):
								with open(result) as f:
										jsonFormatted = json.loads(f.read())

										profilesJSON.append({
												"uuid": uuid,
												"profileName": jsonFormatted["name"],
												"profileColor": jsonFormatted["color"],
												"icon": f"{profilesPath}\\{uuid}\\{iconfile}"
										})

								break

from PIL import Image, ImageTk

def generate_buttons(root, strings, image_paths, uuids):
    # Path to the application
    app = os.environ.get("LOCALAPPDATA") + "\\Programs\\Opera GX\\launcher.exe"

    # Common arguments
    common_arg = ['--with-feature:side-profiles --no-default-browser-check --disable-usage-statistics-question']
    
    for string, image_path, uuid in zip(strings, image_paths, uuids):
        if os.path.exists(image_path):
            # Load the image
            image = Image.open(image_path)

            # Resize the image using Image.Resampling.LANCZOS
            image = image.resize((128, 128), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)

            # Add spaces to the beginning of the text
            padded_string = '   ' + string

            # Create the button with the configured style
            button = ttk.Button(root, text=padded_string, image=photo, compound='left', style='TButton')

            # Set the command to launch the application with the common arguments and the profile UUID
            button.config(command=lambda uuid=uuid: subprocess.run([app] + [f'--side-profile-name={uuid}'] + common_arg))

            button.image = photo  # Keep a reference to the image
            button.pack(pady=5)  # Add vertical padding
        else:
            print(f"Image file does not exist: {image_path}")

# Function to create a new screen
def create_new_screen(size=None):
		# Destroy the current window
		root.destroy()

		# Create a new window
		new_root = tk.Tk()
		new_root.title("Opera Launcher")

		if size == "fullscreen":
				new_root.state("zoomed")

		detectProfilesJSON()

		# List of strings
		strings = [profile['profileName'] for profile in profilesJSON]

		# List of image paths
		image_paths = [profile['icon'] for profile in profilesJSON]

		# List of profile UUIDs
		uuids = [profile['uuid'] for profile in profilesJSON]

		sv_ttk.set_theme("dark")
		# Create a style
		style = ttk.Style()

		# Configure the style
		style.configure('TButton', font=("Helvetica", 20))

		generate_buttons(new_root, strings, image_paths, uuids)

		new_root.mainloop()

# Function to compare entered password to stored password
def compare_password(event=None):  # removed the event parameter
		entered_password = password(password_input.get())
		with open(f"{pathToKey}\\key.ole", "rb") as file:
			stored_password = file.read()
		if entered_password == stored_password:
				result_text.set("Password is correct")
				create_new_screen("fullscreen")
		else:
				result_text.set("Password is incorrect")


# Stored password
pathToKey = os.path.expandvars("%APPDATA%\\Opera Software\\OLE")


# Create the root window
root = tk.Tk()
root.title("Password Check")
root.configure(bg="#1c1c1c")

# Create a frame to hold the password input field and check button
input_frame = tk.Frame(root)
input_frame.pack(side="top", pady=(20, 10))

def create_password_file():
		new_window = tk.Toplevel(root, bg="#1c1c1c")
		new_window.title("Create Password File")
		new_window_frame = tk.Frame(new_window)
		new_window_frame.pack(side="top")
		

		instruction_label = tk.Label(new_window, text="Password file not found. Please enter a new password:", bg="#1c1c1c", fg="#fafafa")
		instruction_label.pack(side='top')

		new_password_input = ttk.Entry(new_window, show="*", foreground="#fafafa")
		new_password_input.pack(side='left')

		def save_new_password(event=None):
				with open(f"{pathToKey}\\key.ole", "wb") as file:
						file.write(password(new_password_input.get()))
				print('Password file created')
				new_window.destroy()

		save_button = ttk.Button(new_window, text="Save Password", command=save_new_password)
		save_button.pack(side='left')

		# Bind the Enter key to the save_new_password function
		new_window.bind('<Return>', save_new_password)

		sv_ttk.set_theme("dark")

		root.wait_window(new_window)

# Hide the main window
root.withdraw()

if not os.path.exists(pathToKey):
		os.mkdir(pathToKey)
if not os.path.isfile(f"{pathToKey}\\key.ole"):
		create_password_file()
else:
		print('Password file already exists')

# Show the main window
root.deiconify()

# Create a new password input field
password_input = ttk.Entry(input_frame, show="*")
password_input.pack(side='left')

# Button to check the password
check_button = ttk.Button(input_frame, text="Check Password", command=compare_password)
check_button.pack(side='left')

# Bind the Enter key to the compare_password function
root.bind('<Return>', compare_password)

# Create a StringVar to hold the result text
result_text = tk.StringVar()

# Create a label to display the result text
result_label = tk.Label(root, textvariable=result_text)
result_label.pack(side='top')

# Set focus to the password input field
password_input.focus_set()

sv_ttk.set_theme("dark")

root.mainloop()