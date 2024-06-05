import unittest
from unittest.mock import patch
from pycron.task import Task

class TestTask(unittest.TestCase):

    @patch('pycron.task.os.system')
    def test_run(self, mock_system):
        task = Task('echo "Hello, World!"', '1s')
        task.run()
        mock_system.assert_called_once_with('echo "Hello, World!"')

    def test_parse_interval(self):
        task = Task('echo "Hello, World!"', '1s')
        self.assertEqual(task.interval, 1)
        task = Task('echo "Hello, World!"', '2m')
        self.assertEqual(task.interval, 120)
        task = Task('echo "Hello, World!"', '1h')
        self.assertEqual(task.interval, 3600)

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            Task('echo "Hello, World!"', '1d')

if __name__ == '__main__':
    unittest.main()
