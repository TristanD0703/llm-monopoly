
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
import dotenv

def main():
    dotenv.load_dotenv()
    parser = argparse.ArgumentParser(prog="Agentic Monopoly", description="Allows humans and/or LLMs to play against each other in a game of Monopoly!")
    parser.add_argument('config_path')
    args = vars(parser.parse_args())
    filename = args['config_path']
    data = {}

    with open(filename, 'rb') as f:
        data = load(f)

    property_groups: dict[str, list[int]] = {}

    
    io = AgentIO.local_model_ollama('qwen3-coder:30b') 
    state = BoardState(property_groups)

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


    state.add_player(Player('AI Player 1', io))
    state.add_player(Player('AI Player 2', io))
    state.next_turn()

if __name__ == "__main__":
    main()
