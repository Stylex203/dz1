import os
import sys
import zipfile
import tempfile
from datetime import datetime
import win32security
import configparser

class ShellEmulator:
    def init(self):
        self.load_config("config.ini")
        self.current_path = self.vfs_path

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            config = configparser.ConfigParser()
            config.read_file(file)
            self.username = config['General']['username']
            self.log_file = config['General']['log_file']
            self.vfs_zip_path = config['General']['vfs_path']
            self.start_script=config['General']['start_script']

        self.temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(self.vfs_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        self.vfs_path = self.temp_dir

    def prompt(self):
        return f"{self.username}:{self.current_path}$ "

    def write_to_the_log_file(self, text):
        with open(self.log_file, mode='a') as file:
            try:
                file.write(text+"\n")
            except:
                pass

    def clear_log_file(self):
        with open(self.log_file, mode='w') as file:
            file.write('')

    def list_directory(self):
        try:
            items = os.listdir(self.current_path)
            result = []
            for item in items:
                item_path = os.path.join(self.current_path, item)
                owner_sid = win32security.GetFileSecurity(item_path, win32security.OWNER_SECURITY_INFORMATION)
                owner_sid_val = owner_sid.GetSecurityDescriptorOwner()
                owner_name, domain, _ = win32security.LookupAccountSid(None, owner_sid_val)
                result.append(f"{item} (owner: {owner_name})")
            return "\n".join(result)
        except FileNotFoundError:
            return "Directory not found."
        except Exception as e:
            return str(e)

    def change_directory(self, path):
        new_path = os.path.join(self.current_path, path)
        if os.path.isdir(new_path):
            self.current_path = new_path
            return f"Changed directory to {new_path}"
        else:
            pass

    def remove_directory(self, dirname):
        path_to_remove = os.path.join(self.current_path, dirname)
        try:
            os.rmdir(path_to_remove)
            return f"Removed directory {dirname}"
        except OSError as e:
            return str(e)

    def change_owner(self, filename, new_owner):
        try:
            path = os.path.join(self.current_path, filename)
            new_owner_sid = win32security.LookupAccountName(None, new_owner)[0]
            security_info = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
            security_info.SetSecurityDescriptorOwner(new_owner_sid, 0)
            win32security.SetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION, security_info)
            return f"Changed owner of {filename} to {new_owner}"
        except Exception as e:

            return str(e)

    def current_date(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def echo(self, text):
        self.text = text
        return text

    def show_help(self):
        help_text = (
            "Available commands:\n"
            "  ls              - List directory contents\n"
            "  cd <directory>  - Change directory\n"
            "  date            - Show current date and time\n"
            "  echo            - Print text\n"
            "  chown <file> <new_owner> - Change owner of file\n"
            "  help            - Show this help message\n"
            "  exit            - Exit the shell emulator\n")
        return help_text

    def run_command(self, command):
        full_text = command
        parts = command.strip().split()
        if not parts:
            return ""

        cmd = parts[0]
        if cmd == "ls":
            self.write_to_the_log_file(f"{self.current_date()} {self.list_directory()}")
            return self.list_directory()
        elif cmd == "cd":
            if len(parts) < 2:
                self.write_to_the_log_file(f"{self.current_date()} cd: missing argument")
                return "cd: missing argument"
            self.write_to_the_log_file(f"{self.current_date()} {self.change_directory(parts[1])}")
            return self.change_directory(parts[1])
        elif cmd == "date":
            self.write_to_the_log_file(f"{self.current_date()} {self.current_date()}")
            return self.current_date()
        elif cmd == "help":
            self.write_to_the_log_file(f"{self.current_date()} {self.show_help()}")
            return self.show_help()
        elif cmd == "echo":
            if len(parts) < 2:
                self.write_to_the_log_file(f"{self.current_date()} echo: missing text")
                return "echo: missing text"
            self.write_to_the_log_file(f"{self.current_date()} {self.echo(full_text[5:])}")
            return self.echo(full_text[5:])
        elif cmd == "chown":
            if len(parts) < 3:
                self.write_to_the_log_file(f"{self.current_date()} chown: missing arguments")
                return "chown: missing arguments"
            filename = parts[1]
            new_owner = parts[2]
            self.write_to_the_log_file(f"{self.current_date()} {self.change_owner(filename, new_owner)}")
            return self.change_owner(filename, new_owner)
        elif cmd == "exit":
            self.write_to_the_log_file(f"{self.current_date()} Exiting...")
            return "Exiting..."
        else:
            self.write_to_the_log_file(f"{self.current_date()} {cmd}: command not found")
            return f"{cmd}: command not found"

    def start(self):
        self.clear_log_file()
        self.write_to_the_log_file(f"{self.current_date()} Welcome to the Shell Emulator!")
        print("Welcome to the Shell Emulator!")
        while True:
            command = input(self.prompt())
            self.write_to_the_log_file(f"{self.username} {self.current_date()} {command}")
            output = self.run_command(command)
            print(output)
            if command.strip() == "exit":
                break

if __name__ == "__main__":
    emulator = ShellEmulator()
    emulator.init()
    emulator.start()