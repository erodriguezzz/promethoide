import unittest
from unittest.mock import patch, MagicMock
from pycron.scheduler import Scheduler
import threading

class TestScheduler(unittest.TestCase):

    @patch('pycron.scheduler.Task')
    def test_load_config(self, MockTask):
        mock_task_instance_1 = MagicMock()
        mock_task_instance_2 = MagicMock()
        MockTask.side_effect = [mock_task_instance_1, mock_task_instance_2]
        
        scheduler = Scheduler('tests/test_config.yaml')
        
        self.assertEqual(len(scheduler.tasks), 2)
        self.assertEqual(scheduler.tasks[0], mock_task_instance_1)
        self.assertEqual(scheduler.tasks[1], mock_task_instance_2)

    @patch('pycron.scheduler.Task')
    def test_run_task(self, MockTask):
        mock_task = MockTask.return_value
        mock_task.command = "echo 'Task 1'"
        mock_task.interval = 1
        scheduler = Scheduler('tests/test_config.yaml')
        scheduler.tasks = [mock_task]
        
        stop_event = threading.Event()
        
        with patch('time.time', side_effect=[1, 2, 3, 4, 5, 6, 7, 8]):
            with patch('time.sleep', return_value=None):
                thread = threading.Thread(target=scheduler.run_task, args=(mock_task,))
                thread.start()
                scheduler.stop_event.set()
                thread.join()
                self.assertTrue(mock_task.run.called)

    def test_signal_handler(self):
        scheduler = Scheduler('tests/test_config.yaml')
        with patch.object(scheduler.stop_event, 'set') as mock_set:
            with patch('threading.enumerate', return_value=[threading.main_thread()]):
                with patch('threading.Thread.join', return_value=None):
                    with self.assertRaises(SystemExit):
                        scheduler.signal_handler(None, None)
                        mock_set.assert_called_once()

if __name__ == '__main__':
    unittest.main()
