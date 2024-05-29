import unittest
import asyncio
from unittest.mock import patch, MagicMock
import tkinter as tk
from gui import *

class TestGUI(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.games_listbox = tk.Listbox(self.root)
        self.game_entry = tk.Entry(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('gui.messagebox')
    def test_add_game(self, mock_messagebox):
        self.game_entry.insert(0, 'New Game')
        add_game()
        self.assertIn('New Game', self.games_listbox.get(0, tk.END))
        mock_messagebox.showwarning.assert_not_called()

    @patch('gui.messagebox')
    def test_add_duplicate_game(self, mock_messagebox):
        self.games_listbox.insert(tk.END, 'Existing Game')
        self.game_entry.insert(0, 'Existing Game')
        add_game()
        self.assertEqual(self.games_listbox.size(), 1)
        mock_messagebox.showerror.assert_called_once()

    @patch('gui.messagebox')
    def test_add_game_not_in_database(self, mock_messagebox):
        with patch('gui.find_process_name', return_value=False):
            self.game_entry.insert(0, 'Unknown Game')
            add_game()
            mock_messagebox.showwarning.assert_called_once()

    def test_remove_game(self):
        self.games_listbox.insert(tk.END, 'Game 1')
        self.games_listbox.insert(tk.END, 'Game 2')
        self.games_listbox.selection_set(0)
        remove_game()
        self.assertEqual(self.games_listbox.size(), 1)
        self.assertEqual(self.games_listbox.get(0), 'Game 2')

    @patch('gui.messagebox')
    def test_remove_game_none_selected(self, mock_messagebox):
        remove_game()
        mock_messagebox.showwarning.assert_called_once()

    @patch('gui.messagebox')
    def test_start_button_click_no_games(self, mock_messagebox):
        start_button_click()
        mock_messagebox.showwarning.assert_called_once()

    @patch('gui.messagebox')
    @patch('gui.start_monitoring')
    def test_start_button_click_with_games(self, mock_start_monitoring, mock_messagebox):
        self.games_listbox.insert(tk.END, 'Game 1')
        self.root.iconify = MagicMock()
        mock_messagebox.showinfo = MagicMock()
        start_button_click()
        mock_start_monitoring.assert_called_once()
        self.root.iconify.assert_called_once()
        mock_messagebox.showinfo.assert_called_once()

    @patch('gui.messagebox')
    def test_start_button_click_long_bio(self, mock_messagebox):
        self.games_listbox.insert(tk.END, 'Game 1')
        default_bio_text = tk.Text(self.root)
        default_bio_text.insert(tk.END, 'A' * 71)
        start_button_click()
        mock_messagebox.showerror.assert_called_once()

    @patch('gui.is_game_running')
    @patch('gui.update_status')
    def test_main(self, mock_update_status, mock_is_game_running):
        mock_is_game_running.side_effect = [True, True, False, False]
        games = [('Game 1', 'process1')]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(main(games, self.root))
        loop.run_until_complete(asyncio.sleep(0.2))
        task.cancel()
        loop.run_until_complete(task)
        loop.close()
        self.assertEqual(mock_update_status.call_count, 4)

if __name__ == '__main__':
    unittest.main()
