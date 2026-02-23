from .board import BoardState
from json import load
import argparse

from .io.cli import CLI
from .player import Player
from .spaces.utilities import Utlities
from .spaces.jail import Jail
from .spaces.normal_property import NormalProperty
from .spaces.railroad import Railroad
from .spaces.space import Space
from .spaces.tax_space import TaxSpace

def main():
    parser = argparse.ArgumentParser(prog="Agentic Monopoly", description="Allows humans and/or LLMs to play against each other in a game of Monopoly!")
    parser.add_argument('config_path')
    args = vars(parser.parse_args())
    filename = args['config_path']
    data = {}

    with open(filename, 'rb') as f:
        data = load(f)

    property_groups: dict[str, list[int]] = {}
    io = CLI()
    state = BoardState(property_groups, io, None)

    for i, space in enumerate(data['board']['spaces']):
        if space['type'] == 'space':
            state.add_space(Space(space['name']))
        elif space['type'] == 'property':
            state.add_space(NormalProperty(space['name'], space['price'], space['property_group'], space['mortgage_value'], space['house_cost'], space['rent_costs']))
            if space['property_group'] not in property_groups:
                property_groups[space['property_group']] = []
            property_groups[space['property_group']].append(i)
        elif space['type'] == 'tax':
            state.add_space(TaxSpace(space['cost'], space['name']))
        elif space['type'] == 'railroad':
            state.add_space(Railroad(space['name'], space['price'], space['mortgage_value'], space['rent_costs']))
        elif space['type'] == 'jail':
            state.add_space(Jail('Jail'))
        elif space['type'] == 'utilities':
            state.add_space(Utlities(space['name'], space['price'], space['mortgage_value']))


    state.add_player(Player('tristan', 0))
    state.next_turn()

if __name__ == "__main__":
    main()
