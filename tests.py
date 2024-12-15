import unittest
from unittest.mock import MagicMock
from main import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Создание виртуального окружения для тестов."""
        self.emulator = ShellEmulator()

        # Создаем мок-объекты с реальными значениями
        root_folder = MagicMock()
        root_folder.name = "root_folder"
        root_folder.isdir.return_value = True
        root_folder.isfile.return_value = False
        root_folder.mode = 0o755

        another_folder = MagicMock()
        another_folder.name = "root_folder/another_folder"
        another_folder.isdir.return_value = True
        another_folder.isfile.return_value = False
        another_folder.mode = 0o755

        test_py = MagicMock()
        test_py.name = "root_folder/test.py"
        test_py.isdir.return_value = False
        test_py.isfile.return_value = True
        test_py.mode = 0o644

        example_txt = MagicMock()
        example_txt.name = "root_folder/example.txt"
        example_txt.isdir.return_value = False
        example_txt.isfile.return_value = True
        example_txt.mode = 0o644

        # Добавляем мок-объекты в VFS
        self.emulator.vfs = {
            "root_folder": root_folder,
            "root_folder/another_folder": another_folder,
            "root_folder/test.py": test_py,
            "root_folder/example.txt": example_txt,
        }
        self.emulator.current_path = "/"

    def test_resolve_path(self):
        """Тестирование преобразования путей."""
        self.assertEqual(self.emulator.resolve_path("root_folder"), "root_folder")
        self.assertEqual(self.emulator.resolve_path("/root_folder"), "root_folder")

    def test_change_directory(self):
        """Тестирование смены директорий."""
        self.assertEqual(self.emulator.change_directory("root_folder"), "Перешли в директорию root_folder")
        self.assertEqual(self.emulator.current_path, "root_folder")

        self.assertEqual(self.emulator.change_directory("another_folder"), "Перешли в директорию root_folder/another_folder")
        self.assertEqual(self.emulator.current_path, "root_folder/another_folder")

        self.assertEqual(self.emulator.change_directory("nonexistent"), "Нет такой директории: nonexistent")

    def test_list_directory(self):
        """Тестирование списка содержимого директории."""
        result = self.emulator.list_directory()
        self.assertIn("d root_folder (755)", result)

    def test_change_owner(self):
        """Тестирование смены владельца файла."""
        self.assertEqual(self.emulator.change_owner("root_folder/test.py", "user1"), "Changed owner of root_folder/test.py to user1")
        self.assertEqual(self.emulator.vfs["root_folder/test.py"].uname, "user1")

        self.assertEqual(self.emulator.change_owner("nonexistent_file", "user1"), "File not found or is not a file: nonexistent_file")

    def test_get_date(self):
        """Тестирование вывода текущей даты."""
        result = self.emulator.get_date()
        self.assertIn("Current date and time:", result)

    def test_echo(self):
        """Тестирование команды echo."""
        result = self.emulator.echo("Hello, World!")
        self.assertEqual(result, "Hello, World!")
    
    def test_exit(self):
        result = self.emulator.run_command("exit")
        self.assertEqual(result, "Выход из Shell Emulator")


if __name__ == "__main__":
    unittest.main()
