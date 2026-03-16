
import asyncio
import threading
from typing import Any
from .io.cli import CLI
from .move_broadcaster import MoveBroadcaster, Receiver
from .io.agent_io import AgentIO
from .board import BoardState
from json import load
import argparse
from .player import Player
from .spaces.card import Card
from .spaces.utilities import Utilities
from .spaces.jail import Jail
from .spaces.normal_property import NormalProperty
from .spaces.railroad import Railroad
from .spaces.space import Space
from .spaces.tax_space import TaxSpace
from .server import set_game_state_provider, socketio, spectator_count, start_socket
from flask_socketio import SocketIO
import dotenv

def config_argv():
    parser = argparse.ArgumentParser(prog="Agentic Monopoly", description="Allows humans and/or LLMs to play against each other in a game of Monopoly!")
    parser.add_argument('config_path')
    return vars(parser.parse_args())

def parse_spaces(state: BoardState, data: dict[str, Any]):
    for space in data['board']['spaces']:
        if space['type'] == 'space':
            state.add_space(Space(space['name']))
        elif space['type'] == 'property':
            state.add_space(NormalProperty(space['name'], space['price'], space['property_group'], space['mortgage_value'], space['house_cost'], space['rent_costs']))
        elif space['type'] == 'tax':
            state.add_space(TaxSpace(space['cost'], space['name']))
        elif space['type'] == 'railroad':
            state.add_space(Railroad(space['name'], space['price'], space['mortgage_value'], space['rent_costs']))
        elif space['type'] == 'jail':
            state.add_space(Jail('Jail'))
        elif space['type'] == 'utilities':
            state.add_space(Utilities(space['name'], space['price'], space['mortgage_value']))
        elif space['type'] == 'community_chest' or space['type'] == 'chance':
            state.add_space(Card(space['name'], state.random))

def parse_players(state: BoardState, data: dict[str, Any]):
    for player in data['players']:
            if player['type'] == 'local':
                io = AgentIO.local_model_ollama(player['model'])
            elif player['type'] == 'claude':
                io = AgentIO.claude_from_env(player['model'])
            elif player['type'] == 'gemini':
                io = AgentIO.gemini_from_env(player['model'])
            elif player['type'] == 'openai':
                io = AgentIO.openai_from_env(player['model'])
            elif player['type'] == 'openrouter':
                io = AgentIO.open_router_from_env(player['model'])
            elif player['type'] == 'cli':
                io = CLI()
            else:
                raise ValueError("Player type not supported.")
            curr_player = Player(player['name'], io)
            state.add_player(curr_player)

def load_config(args: dict[str, Any]):
    filename = args['config_path']
    with open(filename, 'rb') as f:
        data = load(f)
    return data

class SocketReceiver(Receiver):
    def __init__(self, socket: SocketIO):
        self.socket = socket

    def on_move(self, event: dict[str, Any]):
        self.socket.emit('move', event, namespace='/ws') # type: ignore

class PrintReceiver(Receiver):
    def on_move(self, event: dict[str, Any]):
        print(event)


async def main():
    dotenv.load_dotenv()
    args = config_argv()
    data = load_config(args)

    test = MoveBroadcaster([PrintReceiver(), SocketReceiver(socketio)]) 
    state = BoardState(
        broadcaster=test,
        force_trades_if_no_monopoly=(True, 100),
        viewer_count_provider=spectator_count,
    )

    parse_spaces(state, data) 
    parse_players(state, data) 
    set_game_state_provider(state.build_game_state)

    socket_thread = threading.Thread(target=lambda: start_socket(socketio), daemon=True)
    socket_thread.start()
    
    state.next_turn()

if __name__ == "__main__":
    asyncio.run(main())
