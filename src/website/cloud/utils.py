def choose_root(image_id):
    if image_id == 'ami-0c93065e42589c42b':
        return 'alpine'
    elif image_id == 'ami-0ea939ebce565da44':
        return 'ubuntu'
    else:
        return ''

def get_game_server_details(game):
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