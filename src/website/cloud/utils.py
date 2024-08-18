class Utils:
    @staticmethod
    def choose_root(image_id):
        """
        Determines the root user based on the provided AMI ID.

        Parameters:
            image_id (str): The ID of the AMI.

        Returns:
            str: The root user for the specified AMI.
        """
        if image_id == 'ami-0a2202cf4c36161a1':
            return 'ec2-user'
        elif image_id == 'ami-0ea939ebce565da44':
            return 'ubuntu'
        else:
            return ''

    @staticmethod
    def get_game_server_details(game):
        """
        Retrieves the AMI ID and instance type for a specified game server.

        Parameters:
            game (str): The identifier for the game server.

        Returns:
            tuple: A tuple containing the AMI ID and instance type, or (None, None) if not found.
        """
        game_details = {
            'cs16': {'ami_id': 'ami-0ea939ebce565da44', 'instance_type': 't2.medium'}
        }

        if game in game_details:
            server_game_specs = game_details[game]
            ami_id = server_game_specs['ami_id']
            instance_type = server_game_specs['instance_type']
            return ami_id, instance_type
        else:
            print(f"Game {game} not found in game details.")
            return None, None