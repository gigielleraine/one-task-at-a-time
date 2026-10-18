import os
import unittest
import database
from main import app, get_random_task

class TestTaskApp(unittest.TestCase):
    """Automated tests for our randomiser logic and database security."""

    def setUp(self):
        """Runs automatically BEFORE each test to create a fresh test database."""
        database.DATABASE_NAME = 'test_tasks.db'
        database.init_db()

    def tearDown(self):
        """Runs automatically AFTER each test to clean up the test database."""
        if os.path.exists('test_tasks.db'):
            os.remove('test_tasks.db')

    def test_empty_list_returns_none(self):
        """Ensure an empty task list safely returns None without crashing."""
        result = get_random_task([])
        self.assertIsNone(result)

    def test_switch_task_never_repeats(self):
        """Ensure switching tasks never picks the current task twice in a row."""
        sample_tasks = [
            {'id': 1, 'title': 'Task One'},
            {'id': 2, 'title': 'Task Two'}
        ]
        for _ in range(20):
            chosen = get_random_task(sample_tasks, current_id=1)
            self.assertEqual(chosen['id'], 2)

    def test_rejects_empty_or_oversized_tasks(self):
        """Ensure security filters block blank spaces and >200 character inputs."""
        initial_count = len(database.get_active_tasks())
        
        database.add_task('     ')
        database.add_task('A' * 205)
        
        final_count = len(database.get_active_tasks())
        self.assertEqual(initial_count, final_count)

    def test_complete_task_moves_to_completed_list(self):
        """Ensure completing a task removes it from active and adds it to completed."""
        active_before = database.get_active_tasks()
        target_id = active_before[0]['id']
        
        database.complete_task(target_id)
        
        active_ids = [t['id'] for t in database.get_active_tasks()]
        completed_ids = [t['id'] for t in database.get_completed_tasks()]
        
        self.assertNotIn(target_id, active_ids)
        self.assertIn(target_id, completed_ids)

    def test_theme_toggle_switches_modes(self):
        """Ensure the theme toggle route switches between light and dark mode."""
        client = app.test_client()
        
        # First click should switch from default 'light' to 'dark'
        response = client.post('/toggle-theme', follow_redirects=True)
        self.assertIn(b'<body class="dark-mode">', response.data)
        
        # Second click should switch back to 'light'
        response = client.post('/toggle-theme', follow_redirects=True)
        self.assertIn(b'<body class="">', response.data)

if __name__ == '__main__':
    unittest.main()
