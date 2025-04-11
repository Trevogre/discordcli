import unittest
import os
import json
import sqlite3
from unittest.mock import patch, MagicMock, call
import tempfile
import shutil

class TestDiscordCLI(unittest.TestCase):
    def setUp(self):
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # Create test environment
        patcher = patch.dict('os.environ', {
            'DISSCLI_CONFIG_PATH': os.path.join(self.test_dir, 'test_config.json'),
            'DISSCLI_DB_PATH': os.path.join(self.test_dir, 'test_db.sqlite')
        })
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_hook_management(self):
        """Test the complete lifecycle of hook management"""
        # Import after environment is set up
        from disscli.main import (
            init_db,
            add_hook,
            get_default_hook,
            get_hook_url,
            set_default_hook,
            delete_hook,
            get_db_connection
        )
        
        # Initialize database
        init_db()
        
        # Clear any existing data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM hooks")
        
        # When adding the first hook
        with patch('builtins.print') as mock_print:
            add_hook("test_hook", "http://test.webhook.url")
            mock_print.assert_has_calls([
                call("Hook 'test_hook' added successfully."),
                call("Hook 'test_hook' set as default since it's the only hook.")
            ])
        
        # It should automatically be the default
        self.assertEqual(get_default_hook(), "test_hook")
        self.assertEqual(get_hook_url("test_hook"), "http://test.webhook.url")
        
        # When adding a second hook
        add_hook("test_hook2", "http://test2.webhook.url")
        
        # The first hook should still be default
        self.assertEqual(get_default_hook(), "test_hook")
        
        # We should be able to change the default
        set_default_hook("test_hook2")
        self.assertEqual(get_default_hook(), "test_hook2")
        
        # We should not be able to add duplicate hooks
        with patch('builtins.print') as mock_print:
            add_hook("test_hook", "http://another.url")
            mock_print.assert_called_with("Error: A hook with the name 'test_hook' already exists.")
        
        # We should be able to delete hooks
        delete_hook("test_hook")
        self.assertIsNone(get_hook_url("test_hook"))
        
        # After deleting the non-default hook, test_hook2 should still be default
        self.assertEqual(get_default_hook(), "test_hook2")

    def test_message_management(self):
        """Test message operations"""
        # Import after environment is set up
        from disscli.main import (
            init_db,
            save_message,
            list_messages,
            delete_logs,
            get_db_connection
        )
        
        # Initialize database
        init_db()
        
        # Clear any existing data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM hooks")
        
        # Should be able to save messages without mentions
        save_message("Test message", [])
        
        # Should be able to save messages with mentions
        save_message("Hello @user1 and @user2", ["@user1", "@user2"])
        
        # Should be able to list all messages
        messages = list_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0][0], "Test message")
        self.assertEqual(messages[1][0], "Hello @user1 and @user2")
        
        # Should be able to delete all messages
        delete_logs()
        self.assertEqual(len(list_messages()), 0)

    def test_message_sending(self):
        """Test the message sending functionality"""
        # Import after environment is set up
        from disscli.main import (
            init_db,
            add_hook,
            set_default_hook,
            send_message,
            list_messages,
            get_db_connection
        )
        
        # Initialize database
        init_db()
        
        # Clear any existing data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM hooks")
        
        # Set up a test hook
        add_hook("test_hook", "http://test.webhook.url")
        set_default_hook("test_hook")
        
        # Mock the HTTP request
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 204
            
            # Send a test message
            send_message("http://test.webhook.url", "test_user", None, "Test message")
            
            # Verify the HTTP request
            mock_post.assert_called_with(
                "http://test.webhook.url",
                json={
                    "content": "Test message",
                    "username": "test_user",
                    "avatar_url": None,
                }
            )
        
        # Verify the message was saved
        messages = list_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], "Test message")

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Import after environment is set up
        from disscli.main import (
            init_db,
            delete_hook,
            set_default_hook,
            get_db_connection
        )
        
        # Initialize database
        init_db()
        
        # Clear any existing data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM hooks")
        
        # Test deleting non-existent hook
        with patch('builtins.print') as mock_print:
            delete_hook("non_existent_hook")
            mock_print.assert_called_with("Error: No hook found with the name 'non_existent_hook'.")
        
        # Test setting non-existent hook as default
        with patch('builtins.print') as mock_print:
            set_default_hook("non_existent_hook")
            mock_print.assert_called_with("Error: No hook found with the name 'non_existent_hook'.")

if __name__ == '__main__':
    unittest.main() 