import unittest
import os
import tempfile
import configparser
import zipfile
from unittest.mock import patch
from main import *

class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        self.temp_config = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.ini')
        self.temp_vfs = tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.zip')
        
        config_content = """
        [General]
        username = testuser
        log_file = log.txt
        vfs_path = {}
        start_script = start.sh
        """.format(self.temp_vfs.name)
        self.temp_config.write(config_content)
        self.temp_config.close()

        with zipfile.ZipFile(self.temp_vfs.name, 'w') as zipf:
            zipf.writestr('testfile.txt', 'Hello, World!')

        self.shell = ShellEmulator()
        self.shell.load_config(self.temp_config.name)

    def tearDown(self):
        os.unlink(self.temp_config.name)
        os.unlink(self.temp_vfs.name)
        os.rmdir(self.shell.temp_dir)

    def test_list_directory(self):
        output = self.shell.list_directory()
        self.assertIn('testfile.txt', output)
        self.shell.current_path = '/invalid_path'
        output = self.shell.list_directory()
        self.assertEqual(output, "Directory not found.")
        os.remove(os.path.join(self.shell.vfs_path, 'testfile.txt'))
        output = self.shell.list_directory()
        self.assertEqual(output, "")

    def test_change_directory(self):
        os.mkdir(os.path.join(self.shell.vfs_path, 'subdir'))
        output = self.shell.change_directory('subdir')
        self.assertIn('Changed directory to', output)
        output = self.shell.change_directory('invalid_dir')
        self.assertEqual(output, "No such file or directory.")
        output = self.shell.change_directory('..')
        self.assertIn('Changed directory to', output)

    def test_remove_directory(self):
        os.mkdir(os.path.join(self.shell.vfs_path, 'removable_dir'))
        output = self.shell.remove_directory('removable_dir')
        self.assertIn('Removed directory', output)
        os.mkdir(os.path.join(self.shell.vfs_path, 'non_empty_dir'))
        with open(os.path.join(self.shell.vfs_path, 'non_empty_dir', 'file.txt'), 'w') as f:
            f.write('content')
        output = self.shell.remove_directory('non_empty_dir')
        self.assertIn('Directory not empty', output)
        output = self.shell.remove_directory('missing_dir')
        self.assertIn('No such file or directory', output)

    def test_change_owner(self):
        pass

    def test_current_date(self):
        output = self.shell.current_date()
        self.assertRegex(output, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_echo(self):
        output = self.shell.echo("Hello, test!")
        self.assertEqual(output, "Hello, test!")
        output = self.shell.echo("")
        self.assertEqual(output, "")
        output = self.shell.echo("a" * 1000)
        self.assertEqual(output, "a" * 1000)

    def test_show_help(self):
        output = self.shell.show_help()
        self.assertIn("Available commands:", output)
        self.assertIn("ls", output)
        self.assertIn("exit", output)

    def test_run_command(self):
        output = self.shell.run_command("ls")
        self.assertIn("testfile.txt", output)
        output = self.shell.run_command("invalid_command")
        self.assertIn("command not found", output)
        output = self.shell.run_command("echo test")
        self.assertEqual(output, "test")

    def test_log_file(self):
        self.shell.clear_log_file()
        self.shell.write_to_the_log_file("Test log entry")
        with open(self.shell.log_file, 'r') as file:
            log_content = file.read()
        self.assertIn("Test log entry", log_content)
        self.shell.clear_log_file()
        with open(self.shell.log_file, 'r') as file:
            log_content = file.read()
        self.assertEqual(log_content, "")

if __name__ == '__main__':
    unittest.main()
