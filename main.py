import os
import tarfile
import tempfile
from datetime import datetime
import configparser
import logging
import atexit


class ShellEmulator:
    def __init__(self):
        self.config_path = "config.ini"
        self.load_config()
        self.temp_dir = tempfile.mkdtemp()
        self.vfs = {}
        self.current_path = "/"
        self.init_logging()
        self.load_tar_file()
        atexit.register(self.cleanup)
    
    def cleanup(self):
        if hasattr(self, 'tar_file') and self.tar_file:
            self.tar_file.close()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        self.username = config["General"]["username"]
        self.log_file = config["General"]["log_file"]
        self.vfs_tar_path = config["General"]["vfs_path"]
        self.start_script = config["General"]["start_script"]

    def init_logging(self):
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format="%(message)s")
        self.clear_log_file()

    def clear_log_file(self):
        open(self.log_file, "w").close()

    def log(self, message):
        logging.info(message)

    def load_tar_file(self):
        try:
            self.tar_file = tarfile.open(self.vfs_tar_path, "r:")
            self.build_vfs()
        except Exception as e:
            print(f"Ошибка открытия tar-архива: {e}")
            exit(1)

    def build_vfs(self):
        for member in self.tar_file.getmembers():
            self.vfs[member.name] = member
        

    def resolve_path(self, path):
        """Приводит путь к абсолютному и согласованному с VFS формату."""
        if path.startswith("/"):
            abs_path = os.path.normpath(path)
        else:
            abs_path = os.path.normpath(os.path.join(self.current_path, path))
        
        abs_path = abs_path.replace("\\", "/").lstrip("/")
        return abs_path

    def prompt(self):
        return f"{self.username}:{self.current_path}$ "

    def list_directory(self):
        current_dir = self.current_path.strip("/")
        results = []

        for path in self.vfs:
            if path.startswith(current_dir) and path != current_dir:
                sub_path = path[len(current_dir):].strip("/")
                if "/" not in sub_path:  
                    item = self.vfs[path]
                    item_type = "d" if item.isdir() else "-"
                    results.append(f"{item_type} {item.name.split("/")[-1]} ({oct(item.mode)[-3:]})")
        
        return "\n".join(results) if results else "Пусто."

    def change_directory(self, path):
        """Изменяет текущую директорию, если путь существует в VFS."""
        new_path = self.resolve_path(path)
        if new_path in self.vfs and self.vfs[new_path].isdir():
            self.current_path = new_path
            return f"Перешли в директорию {self.current_path}"
        else:
            return f"Нет такой директории: {path}"

    def show_help(self):
        help_text = (
            "Available commands:\n"
            "  ls              - List directory contents\n"
            "  cd <directory>  - Change directory\n"
            "  date            - Show current date and time\n"
            "  echo <text>     - Print text\n"
            "  chown <file> <new_owner> - Change owner of file\n"
            "  help            - Show this help message\n"
            "  exit            - Exit the shell emulator\n")
        return help_text

    def get_date(self):
        """Возвращает текущую дату и время."""
        return f"Current date and time: {self.current_date()}"

    def echo(self, text):
        """Возвращает переданный текст."""
        return text

    def change_owner(self, filename, new_owner):
        """Эмулирует изменение владельца файла."""
        full_path = self.resolve_path(filename)
        if full_path in self.vfs and self.vfs[full_path].isfile():
            self.vfs[full_path].uname = new_owner
            return f"Changed owner of {filename} to {new_owner}"
        else:
            return f"File not found or is not a file: {filename}"

    def run_command(self, cmd):
        parts = cmd.strip().split()
        if not parts:
            return "Команда не указана."
        

        command = parts[0]
        args = parts[1:]

        if command == "cd":
            if len(args) != 1:
                return "cd: неверное количество аргументов"
            return self.change_directory(args[0])
        elif command == "ls":
            return self.list_directory()
        elif command == "date":
            return self.get_date()
        elif command == "echo":
            return self.echo(" ".join(args))
        elif command == "chown":
            if len(args) != 2:
                return "chown: неверное количество аргументов"
            return self.change_owner(args[0], args[1])
        elif command == "help":
            return self.show_help()
        elif command == "exit":
            return "Выход из Shell Emulator"
        else:
            return f"Неизвестная команда: {command}"


    def start(self):
        print("Добро пожаловать в Shell Emulator!")
        while True:
            try:
                command = input(self.prompt())
                self.log(f"{self.username}, {self.current_date()}, {command}")
                output = self.run_command(command)
                print(output)
                if command.strip() == "exit":
                    break
            except Exception as e:
                print(f"Ошибка: {e}")

    def current_date(self):
        return datetime.now().strftime("%Y-%m-%d, %H:%M:%S")


if __name__ == "__main__":
    emulator = ShellEmulator()
    emulator.start()
