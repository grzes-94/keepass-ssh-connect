import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import argparse

from keepass_ssh.cli import KeePassSSHCLI, main
from keepass_ssh.server import ServerEntry

class TestMainModule:
    @pytest.fixture
    def cli_instance(self):
        """
        Fixture to create a KeePassSSHCLI instance for testing.
        """
        return KeePassSSHCLI()

    @pytest.fixture
    def no_discovery_patch(self):
        """
        Fixture to prevent file auto-discovery in tests.
        """
        with patch('keepass_ssh.cli.KeePassSSHCLI.find_keepass_files', return_value=(None, None)):
            yield

    @pytest.fixture
    def clear_env(self):
        """
        Fixture to clear environment variables.
        """
        with patch.dict(os.environ, clear=True):
            yield

    def test_parse_arguments_default(self, cli_instance, no_discovery_patch, clear_env):
        """
        Test parsing of default arguments.
        """
        with patch('sys.argv', ['keepass-ssh-connect']):
            args = cli_instance.parse_arguments()
            assert args.database is None
            assert args.key_file is None
            assert args.group == 'root'
            assert args.server is None
            assert not args.list
            assert not args.verbose

    def test_parse_arguments_env_vars(self, cli_instance, no_discovery_patch):
        """
        Test argument parsing with environment variables.
        """
        env_vars = {
            'KEEPASS_DB_PATH': 'Passwords.kdbx',
            'KEEPASS_KEY_PATH': '/env/keyfile.key',
            'KEEPASS_GROUP_PATH': '/Servers/Staging'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('sys.argv', ['keepass-ssh-connect']):
                with patch('os.path.exists', return_value=True):
                    args = cli_instance.parse_arguments()
                    assert args.database == 'Passwords.kdbx'
                    assert args.key_file == '/env/keyfile.key'
                    assert args.group == '/Servers/Staging'

    def test_parse_arguments_env_group(self, cli_instance, no_discovery_patch):
        """
        Test that environment variable for group path is respected.
        """
        with patch.dict(os.environ, {'KEEPASS_GROUP_PATH': 'Custom/Group'}):
            with patch('sys.argv', ['keepass-ssh-connect']):
                args = cli_instance.parse_arguments()
                assert args.group == 'Custom/Group'

    @patch('keepass_ssh.cli.KeePassDatabase')
    def test_main_interactive_selection(self, mock_db, cli_instance, no_discovery_patch):
        """
        Test the main function's interactive server selection workflow.
        """
        mock_servers = [
            ServerEntry(title='Server1', username='user1', password='pass1', url='host1', hostname='host1', port=22, description='notes1'),
            ServerEntry(title='Server2', username='user2', password='pass2', url='host2', hostname='host2', port=22, description='notes2')
        ]
        mock_db.return_value.get_entries.return_value = [
            MagicMock(title='Server1'), 
            MagicMock(title='Server2')
        ]

        with patch.dict(os.environ, clear=True):
            with patch('sys.argv', ['keepass-ssh-connect']):
                with patch('builtins.input', return_value='1'), \
                     patch('keepass_ssh.cli.ServerManager.from_keepass_entry', side_effect=lambda x: mock_servers[mock_db.return_value.get_entries.return_value.index(x)]), \
                     patch('keepass_ssh.cli.SSHConnector.connect') as mock_connect:
                    main()

                # Verify SSHConnector.connect was called with the first server
                mock_connect.assert_called_once_with(mock_servers[0])

    @patch('keepass_ssh.cli.KeePassDatabase')
    def test_main_with_server_arg(self, mock_db, cli_instance, no_discovery_patch):
        """
        Test main function when a specific server is provided.
        """
        mock_servers = [
            ServerEntry(title='production-server', username='user', password='pass', url='host', hostname='host', port=22, description='notes')
        ]
        mock_db.return_value.get_entries.return_value = [MagicMock(title='production-server')]

        with patch.object(sys, 'argv', ['keepass-ssh-connect', '-s', 'production-server']):
            with patch('keepass_ssh.cli.ServerManager.from_keepass_entry', return_value=mock_servers[0]), \
                 patch('keepass_ssh.cli.SSHConnector.connect') as mock_connect:
                main()

            # Verify SSHConnector.connect was called with the first server
            mock_connect.assert_called_once_with(mock_servers[0])

    @patch('keepass_ssh.cli.KeePassDatabase')
    def test_main_multiple_server_matches(self, mock_db, cli_instance, no_discovery_patch):
        """
        Test behavior when multiple servers match the filter.
        """
        mock_servers = [
            ServerEntry(title='server1-partial-match', username='user1', password='pass1', url='host1', hostname='host1', port=22, description='notes1'),
            ServerEntry(title='server2-partial-match', username='user2', password='pass2', url='host2', hostname='host2', port=22, description='notes2')
        ]
        mock_db.return_value.get_entries.return_value = [
            MagicMock(title='server1-partial-match'), 
            MagicMock(title='server2-partial-match')
        ]

        with patch.object(sys, 'argv', ['keepass-ssh-connect', '-s', 'partial-match']):
            with patch('builtins.input', return_value='1'), \
                 patch('keepass_ssh.cli.ServerManager.from_keepass_entry', side_effect=lambda x: mock_servers[mock_db.return_value.get_entries.return_value.index(x)]), \
                 patch('keepass_ssh.cli.SSHConnector.connect') as mock_connect:
                main()

            # Verify SSHConnector.connect was called with the first server
            mock_connect.assert_called_once_with(mock_servers[0])

    @patch('keepass_ssh.cli.KeePassDatabase')
    def test_main_list_servers(self, mock_db, cli_instance, no_discovery_patch):
        """
        Test main function when list flag is used.
        """
        mock_servers = [
            ServerEntry(title='Server1', username='user1', password='pass1', url='host1', hostname='host1', port=22, description='notes1'),
            ServerEntry(title='Server2', username='user2', password='pass2', url='host2', hostname='host2', port=22, description='notes2')
        ]
        mock_db.return_value.get_entries.return_value = [
            MagicMock(title='Server1'), 
            MagicMock(title='Server2')
        ]

        with patch.object(sys, 'argv', ['keepass-ssh-connect', '-l']):
            with patch('keepass_ssh.cli.ServerManager.from_keepass_entry', side_effect=lambda x: mock_servers[mock_db.return_value.get_entries.return_value.index(x)]), \
                 patch('keepass_ssh.cli.ServerManager.list_servers') as mock_list_servers, \
                 patch('sys.exit') as mock_exit, \
                 patch('builtins.input', side_effect=ValueError), \
                 patch('keepass_ssh.cli.SSHConnector.connect'):
                main()

        # Check that list_servers was called with the expected servers
        # Allow multiple calls, but ensure at least one call matches
        assert any(
            call.args[0] == mock_servers
            for call in mock_list_servers.call_args_list
        ), "list_servers was not called with the expected servers"
        
        # Check that sys.exit(0) was called at least once
        assert any(
            call.args[0] == 0
            for call in mock_exit.call_args_list
        ), "sys.exit(0) was not called"

    @patch('keepass_ssh.cli.KeePassDatabase')
    def test_main_no_servers_found(self, mock_db, cli_instance, no_discovery_patch):
        """
        Test behavior when no servers are found.
        """
        mock_db.return_value.get_entries.return_value = []

        with patch.object(sys, 'argv', ['keepass-ssh-connect']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            
            assert excinfo.value.code == 1

    @patch('keepass_ssh.cli.KeePassDatabase')
    def test_main_invalid_selection(self, mock_db, cli_instance, no_discovery_patch):
        """
        Test the main function's behavior with an invalid server selection.
        """
        mock_servers = [
            ServerEntry(title='Server1', username='user1', password='pass1', url='host1', hostname='host1', port=22, description='notes1'),
            ServerEntry(title='Server2', username='user2', password='pass2', url='host2', hostname='host2', port=22, description='notes2')
        ]
        mock_db.return_value.get_entries.return_value = [
            MagicMock(title='Server1'), 
            MagicMock(title='Server2')
        ]

        with patch.object(sys, 'argv', ['keepass-ssh-connect']):
            with patch('builtins.input', side_effect=ValueError):
                with pytest.raises(SystemExit) as excinfo:
                    main()
                
                # Verify the exit code is 1 for invalid selection
                assert excinfo.value.code == 1

    def test_parse_arguments_case_sensitivity(self, cli_instance, no_discovery_patch):
        """
        Test argument parsing is case-sensitive.
        """
        test_args = [
            'keepass-ssh-connect',
            '-D', '/path/to/database.kdbx',  # Uppercase D
            '-K', '/path/to/keyfile.key',    # Uppercase K
        ]
        
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit):
                cli_instance.parse_arguments()

    @patch('keepass_ssh.cli.KeePassSSHCLI.find_keepass_files', return_value=('/path/to/test.kdbx', '/path/to/test.keyx'))
    @patch('os.path.exists', return_value=True)
    @patch.dict('os.environ', clear=True)
    def test_parse_arguments_auto_discovery(self, mock_exists, mock_find, cli_instance, no_discovery_patch):
        """
        Test auto-discovery of KeePass files when no arguments or env vars are set.
        """
        with patch('sys.argv', ['keepass-ssh-connect']):
            args = cli_instance.parse_arguments()
            assert args.database == '/path/to/test.kdbx'
            assert args.key_file == '/path/to/test.keyx'
            assert args.group == 'root'

    @patch('keepass_ssh.cli.KeePassSSHCLI.find_keepass_files', return_value=('/path/to/test.kdbx', '/path/to/test.keyx'))
    @patch('os.path.exists', return_value=True)
    @patch.dict('os.environ', {'KEEPASS_DB_PATH': '/custom/db.kdbx'}, clear=True)
    def test_parse_arguments_no_auto_discovery_with_env_vars(self, mock_exists, mock_find, cli_instance, no_discovery_patch):
        """
        Test that auto-discovery does not occur when environment variables are set.
        """
        with patch('sys.argv', ['keepass-ssh-connect']):
            args = cli_instance.parse_arguments()
            assert args.database == '/custom/db.kdbx'
            assert args.key_file is None

    def test_parse_arguments_no_auto_discovery_with_server_arg(self, cli_instance, monkeypatch, tmp_path):
        """
        Test that auto-discovery occurs even when a server is specified.
        """
        # Create a test database file
        test_db_path = tmp_path / 'test.kdbx'
        test_db_path.touch()
        
        # Mock find_keepass_files to return the test database
        def mock_find_keepass_files():
            return str(test_db_path), None
        
        # Set up command-line arguments for server selection
        sys.argv = ['keepass-ssh-connect', '-s', 'mikr.us']
        
        # Create CLI instance and mock find_keepass_files
        cli_instance.find_keepass_files = mock_find_keepass_files
        
        # Parse arguments
        args = cli_instance.parse_arguments()
        
        # Assert that database is auto-discovered even when server is specified
        assert args.database == str(test_db_path)
        assert args.server == 'mikr.us'

    @patch.dict('os.environ', clear=True)
    def test_parse_arguments_default_group(self, cli_instance, no_discovery_patch):
        """
        Test that 'root' is used as the default group when no group is specified.
        """
        with patch('sys.argv', ['keepass-ssh-connect']):
            args = cli_instance.parse_arguments()
            assert args.group == 'root'
    
    @patch.dict('os.environ', {'KEEPASS_GROUP_PATH': 'Custom/Group'}, clear=True)
    def test_parse_arguments_env_group(self, cli_instance, no_discovery_patch):
        """
        Test that environment variable for group path is respected.
        """
        with patch('sys.argv', ['keepass-ssh-connect']):
            args = cli_instance.parse_arguments()
            assert args.group == 'Custom/Group'
