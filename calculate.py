from dailyscrape import *
import sqlite3

conn = sqlite3.Connection("n.db")
conn.execute("DROP TABLE IF EXISTS daily_players;")
conn.execute("CREATE TABLE daily_players(name, proj_score, price);")
for p in player_list:
    conn.execute("INSERT INTO daily_players VALUES (?, ?, ?)", (p.get_name(), p.get_proj_score(), p.get_price()))

def find_best_value():
    """
    Finds the best projected score per price players
    :return: A list of 40 tuples, with each tuple consisting of player name and 1000 * proj_score/price
    """
    print(conn.execute("SELECT name, 1000 * proj_score/price FROM daily_players ORDER BY -proj_score/price LIMIT 40;").fetchall())

def optimal_lineup(remaining_players, lineup):
    """
    Tree recursive method to find the optimal lineup given a player budget of $50000
    :param remaining_players: players that can still be added to the lineup
    :param lineup: players that are already added to the lineup
    :return: list of players in the order [PG, SG, SF, PF, C, G, F, UTIL]
    """
    total_salary = 0
    for spot in lineup:
        if spot is not None:
            if isinstance(spot, str):
                for player in player_list:
                    if player.get_name() == spot:
                        total_salary += player.get_price()
            else:
                total_salary += spot.get_price()
    if total_salary > 50000:
        return 0
    if None not in lineup:
        return lineup
    if remaining_players == []:
        return 0
    else:
        player = remaining_players[0]
        string_position = player.get_positions()
        positions = position_converter(string_position)
        slots = slot_converter(positions)
        available_slots = []
        for slot in slots:
            if lineup[slot] is None:
                available_slots.append(slot)
        possible_lineups=[lineup]
        for i in available_slots:
            possible_lineups.append(insertion(lineup, i, player))
        return max([optimal_lineup(remaining_players[1:], a) for a in possible_lineups], key=lambda x: lineup_score(x))

def position_converter(string_position):
    """
    Converts a string representing DraftKings position eligibility into a Python list
    :param string_position: DraftKings position eligibility (ex. 'PG/SG')
    :return: list consisting of eligible positions (ex. ['PG', 'SG'])
    """
    positions = []
    while string_position != '':
        if string_position[0] == "/":
            string_position = string_position[1:]
        current_position = string_position[0]
        string_position = string_position[1:]
        if string_position == '':
            positions.append(current_position)
        elif string_position[0] == "/":
            positions.append(current_position)
            string_position = string_position[1:]
        else:
            current_position = current_position + string_position[0]
            positions.append(current_position)
            string_position = string_position[1:]
    return positions

def slot_converter(positions):
    """
    Returns the lineup slot numbers that a player with given position eligibility can be inserted into
    :param positions: Python list of positions represented by strings
    :return: list of corresponding slot numbers
    """
    slots = []
    if 'P' in positions:
        if 0 not in slots:
            slots.append(0)
        if 1 not in slots:
            slots.append(1)
            
    if 'C' in positions:
        if 2 not in slots:
            slots.append(2)
        
    if '1B' in positions:
        if 3 not in slots:
            slots.append(3)
        
    if '2B' in positions:
        if 4 not in slots:
            slots.append(4)
        
    if '3B' in positions:
        if 5 not in slots:
            slots.append(5)
            
    if 'SS' in positions:
        if 6 not in slots:
            slots.append(6)
       
    if 'OF' in positions:
        if 7 not in slots:
            slots.append(7)
        if 8 not in slots:
            slots.append(8)
        if 9 not in slots:
            slots.append(9)
        
    return slots

def insertion(lineup, slot, player):
    """
    Inserts a player into a slot in a lineup
    :param lineup: DraftKings lineup
    :param slot: slot number for player to be entered into
    :param player: Player object to be entered into lineup
    :return: the new lineup with the Player object entered
    """
    new_lineup = lineup[:]
    new_lineup[slot]=player
    return new_lineup

def lineup_score(players_chosen):
    """
    Sums the projected scores of the players in a lineup
    :param players_chosen: either 0 or a list representing a DraftKings lineup
    :return: Projected score of the lineup
    """
    if players_chosen == 0:
        return 0
    else:
        proj_score = 0
        for p in players_chosen:
            if p is not None:
                if isinstance(p, str):
                    for player in new_player_list:
                        if p == player.get_name():
                            proj_score += player.get_proj_score()
                else:
                    proj_score += p.get_proj_score()
        return proj_score
new_player_list = []
for p in player_list:
    if p.get_proj_score()/p.get_price() > 0.005 and p.get_name() not in \
            ["John Lester","Mitch Garver","Joey Votto","Kris Bryant","Mike Trout","Nick Senzel"]:
        new_player_list.append(p)

best = optimal_lineup(new_player_list, 
                      ["John Lester", None,"Mitch Garver","Joey Votto",None,"Kris Bryant",None,
                       "Mike Trout","Nick Senzel",None])
for p in best:
    if isinstance(p, str):
        print(p)
    else:
        print(p.get_name())

