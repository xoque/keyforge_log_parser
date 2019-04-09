import re
import sys
from prettytable import PrettyTable

###############################################################################
"""
# Keyforge Log Parser for Crucible Online Logs
# By XoquE
# Revision 1

# Changelog
 Revision 0.6 - 20190408 - First release, functionality to parse txt logs
 copied from Crucible Online games.
 - Parsing for Userids, Archons, First Player, Number of Turns, Winner
 - Parsing for Shuffles, Forges, Checks, Reaps, Steals, Amount Stolen,
 - Captures, Amount Captured, Aember Gained, and Aember Lost

# Limitations
 Due to the logging that is done on the Crucible Online, there are some
 limitations to what is possible with parsing.
 - I am unable to determine which house is selected because no text contains
   the house.
 - Logging for certain cards is lacking.  For example, Pandemonium captures
   1 aember for each undamaged creature, but there is no detail for how many
   captures occurred (except for after-turn aember count)
 - Similarly, when creatures are killed, there is no indication that they
   had captured aember
 - I don't have logs for each card, so I am sure that some cards do not
   parse correctly
 - Sometimes, the start character of a log gives the parser a UTF-8 error.
   If this happens, delete the first character of the first line of the log,
   add a blank line as the first line, and then add the first character back
   into the second line.

# TODO
 - Add Card Draw counts
 - Add "Not Listed" to Winner if log does not have a winner (for example when
   player leaves before conceding)
 - Add logging of Bonus Aember gained
 - Add logging of aember gained through card effects
 - Add more identified limitations

"""
###############################################################################


# Use the argument when this script is run to determine log to parse
filepath = sys.argv[1]
# Add error handling here for if no arguement is passed

# Debug mode - prints the data it is collecting each line
# - it is the second parameter.  1 is on, 0 is off
#debug_mode = int(sys.argv[2])
debug_mode = 0

rx_dict = {
    'shuffles': re.compile(r'(?P<shuffles_group>.*) is shuffling their deck'),
    'archons': re.compile(r'(?P<archons_group>.*) is playing as the Archon: (?P<archons_name_group>.*)'),
    'forges': re.compile(r'(?P<forges_group>.*) forges a key, paying (?P<forges_amt_group>\d+)'),
    'checks': re.compile(r' (?P<checks_group>.*) declares Check!'),
    'reaps': re.compile(r'(?P<reaps_group>.*) to reap with'),
    'steals': re.compile(r'(?P<steals_group>.*) to steal (?P<steals_number_group>\d*)'),
    'captures': re.compile(r'(?P<captures_group>.*) to capture (?P<captures_number_group>\d*)'),
    'firstplayer': re.compile(r'Key phase - (?P<firstplayer_group>.*)'),
    'turns': re.compile(r'Turn (?P<turns_group>\d+)'),
    'winner': re.compile(r' (?P<winner_group>.*) has won the game'),
    'aembergains': re.compile(r'(?P<ag_p1>.*): (?P<aembergains_group_1>\d+)  (?P<ag_p2>.*): (?P<aembergains_group_2>\d+)'),
    'losses': re.compile(r'(?P<losses_group>.*) lose (?P<losses_amt_group>.+)'),
}


def _parse_line(line):
    """
    Do a regex search against all defined regexes and
    return the key and match result of the first matching regex

    """

    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            return key, match
    # if there are no matches
    return None, None

def parse_file(filepath):
    """
    Parse text at given filepath

    Parameters
    ----------
    filepath : str
        Filepath for file_object to be parsed

    """

    dataheaders = ['Name', 'Shuffles', 'Forges', 'Checks', 'Reaps', 'Steals', '# Stolen', 'Caps', '# Capd', 'Aember Gained', 'Lost']
    player1 = ['',0,0,0,0,0,0,0,0,0,0]
    player2 = ['',0,0,0,0,0,0,0,0,0,0]
    archon1 = ''
    archon2 = ''
    firstplayer = ''
    turns = 0
    winner = ''
    old_aembergains1 = 0
    old_aembergains2 = 0
    new_aembergains1 = 0
    new_aembergains2 = 0
    forges_amt1 = 0
    forges_amt2 = 0
    steals_amt1 = 0
    steals_amt2 = 0
    captures_amt1 = 0
    captures_amt2 = 0
    losses_amt1 = 0
    losses_amt2 = 0

    # open the file and read through it line by line
    with open(filepath, 'r') as file_object:
        line = file_object.readline()
        while line:
            # at each line check for a match with a regex
            key, match = _parse_line(line)

            # extract shuffler name
            if key == 'shuffles':
                shuffles = match.group('shuffles_group')
                if player1[0] == '':
                    player1[0] = shuffles
                    player1[1]+=1
                    if debug_mode:
                      print("Player 1 - Created with name ", shuffles)
                      print("Player 1 - Shuffles + 1 and total is now ", str(player1[1]))
                elif player1[0] == shuffles:
                    player1[1]+=1
                    if debug_mode:
                      print("Player 1 - Shuffles + 1 and total is now ", str(player1[1]))
                elif player2[0] == '':
                    player2[0] = shuffles
                    player2[1]+=1
                    if debug_mode:
                      print("Player 2 - Created with name ", shuffles)
                      print("Player 2 - Shuffles + 1 and total is now ", str(player1[1]))
                elif player2[0] == shuffles:
                    player2[1]+=1
                    if debug_mode:
                      print("Player 2 - Shuffles + 1 and total is now ", str(player1[1]))
                else:
                    print("Error.  Shuffles did not match = ", shuffles)

            # extract archon names
            if key == 'archons':
                archon = match.group('archons_name_group')
                if archon1 == '':
                    archon1 = archon
                    if debug_mode:
                      print("Player 1 - Using Archon ", archon1)
                elif archon2 == '':
                    archon2 = archon
                    if debug_mode:
                      print("Player 2 - Using Archon ", archon1)
                else:
                    print("Error.  Archons did not match = ", archon)


            # extract forger name
            if key == 'forges':
                forges = match.group('forges_group')
                if player1[0] == forges:
                    player1[2]+=1
                    forges_amt1 = int(match.group('forges_amt_group'))
                    if debug_mode:
                      print("Player 1 - Forges + 1 for ", str(forges_amt1), " aember and total forges is now ", str(player1[2]))
                elif player2[0] == forges:
                    player2[2]+=1
                    forges_amt2 = int(match.group('forges_amt_group'))
                    if debug_mode:
                      print("Player 2 - Forges + 1 for ", str(forges_amt2), " aember and total forges is now ", str(player2[2]))
                else:
                    print("Error.  Forges did not match = ", forges)

            # extract checker name
            if key == 'checks':
                checks = match.group('checks_group')
                if player1[0] == checks:
                    player1[3]+=1
                    if debug_mode:
                      print("Player 1 - Checks + 1 and total is now ", str(player1[3]))
                elif player2[0] == checks:
                    player2[3]+=1
                    if debug_mode:
                      print("Player 2 - Checks + 1 and total is now ", str(player2[3]))
                else:
                    print("Error.  Checks did not match = ", checks)

            # extract reaper name
            if key == 'reaps':
                reaps = match.group('reaps_group')
                if player1[0] in reaps:
                    player1[4]+=1
                    if debug_mode:
                      print("Player 1 - Reaps + 1 and total is now ", str(player1[4]))
                elif player2[0] in reaps:
                    player2[4]+=1
                    if debug_mode:
                      print("Player 2 - Reaps + 1 and total is now ", str(player2[4]))
                else:
                    print("Error.  Reaps did not match = ", reaps)

            # extract stealer name
            if key == 'steals':
                steals = match.group('steals_group')
                steals_number = match.group('steals_number_group')
                if steals_number == '':
                    steals_number = 1
                if player1[0] in steals:
                    if int(steals_number) > (old_aembergains2 - captures_amt1 - losses_amt2):
                      steals_number = old_aembergains2 - captures_amt1 - losses_amt2
                    if int(steals_number) != 0:
                      player1[5]+=1
                    player1[6]+=int(steals_number)
                    steals_amt1+=int(steals_number)
                    if debug_mode:
                      print("Player 1 - Steals + 1 and total is now ", str(player1[5]))
                      print("Player 1 - Steal amount + ", str(steals_number), " and total is now ", str(player1[6]))
                elif player2[0] in steals:
                    if int(steals_number) > (old_aembergains1 - captures_amt2 - losses_amt1):
                      steals_number = old_aembergains1 - captures_amt2 - losses_amt1
                    if int(steals_number) != 0:
                      player2[5]+=1
                    player2[6]+=int(steals_number)
                    steals_amt2+=int(steals_number)
                    if debug_mode:
                      print("Player 2 - Steals + 1 and total is now ", str(player2[5]))
                      print("Player 2 - Steal amount + ", str(steals_number), " and total is now ", str(player2[6]))
                else:
                    print("Error.  Steals did not match = ", steals)

            # extract capturer name
            if key == 'captures':
                captures = match.group('captures_group')
                captures_number = match.group('captures_number_group')
                if captures_number == '':
                    captures_number = 0
                if player1[0] in captures:
                    if int(captures_number) > (old_aembergains2 - steals_amt1 - losses_amt2):
                      captures_number = old_aembergains2 - steals_amt1 - losses_amt2
                    if int(captures_number) != 0:
                      player1[7]+=1
                    player1[8]+=int(captures_number)
                    captures_amt1 += int(captures_number)
                    if debug_mode:
                      print("Player 1 - Captures + 1 and total is now ", str(player1[7]))
                      print("Player 1 - Capture amount + ", str(captures_number), " and total is now ", str(player1[8]))
                elif player2[0] in captures:
                    if int(captures_number) > (old_aembergains1 - steals_amt2 - losses_amt1):
                      captures_number = old_aembergains1 - steals_amt2 - losses_amt1
                    if int(captures_number) != 0:
                      player2[7]+=1
                    player2[8]+=int(captures_number)
                    captures_amt2 += int(captures_number)
                    if debug_mode:
                      print("Player 2 - Captures + 1 and total is now ", str(player2[7]))
                      print("Player 2 - Capture amount + ", str(captures_number), " and total is now ", str(player2[8]))
                else:
                    print("Error.  Captures did not match = ", captures)

            # extract first player name
            if key == 'firstplayer':
                if firstplayer == '':
                    firstplayer = match.group('firstplayer_group')
                    if debug_mode:
                      print("First Player identified as ", str(firstplayer))

            # extract number of turns
            if key == 'turns':
                turns = match.group('turns_group')
                if debug_mode:
                    print("Turn identified as turn ", str(turns))

            # extract the winner
            if key == 'winner':
                winner = match.group('winner_group')
                if debug_mode:
                    print("Winner identified as ", str(winner))

            # extract the aember gains
            if key == 'aembergains':
                new_aembergains1 = match.group('aembergains_group_1')
                new_aembergains2 = match.group('aembergains_group_2')
                # Need to account for aember lost, aember captured, aember stolen
                if debug_mode:
                    print("*********************** - AEMBER GAINS")
                    print("Player 1 - new_aembergains1 is ", str(new_aembergains1), " and old_aembergains1 is ", str(old_aembergains1))
                    print("Player 1 - aember value before is ", str(player1[9]))
                    print("Player 2 - new_aembergains2 is ", str(new_aembergains2), " and old_aembergains2 is ", str(old_aembergains2))
                    print("Player 2 - aember value before is ", str(player2[9]))
                player1[9] += int(new_aembergains1) - int(old_aembergains1) + int(forges_amt1) + steals_amt2 + captures_amt2 + losses_amt1
                player2[9] += int(new_aembergains2) - int(old_aembergains2) + int(forges_amt2) + steals_amt1 + captures_amt1 + losses_amt2
                if debug_mode:
                    print("Player 1 - aember value after is ", str(player1[9]))
                    print("Player 2 - aember value after is ", str(player2[9]))
                old_aembergains1 = int(new_aembergains1)
                old_aembergains2 = int(new_aembergains2)
                forges_amt1 = 0
                forges_amt2 = 0
                steals_amt1 = 0
                steals_amt2 = 0
                captures_amt1 = 0
                captures_amt2 = 0
                losses_amt1 = 0
                losses_amt2 = 0

            # extract the losses - first get the losses that have a number.  if a loss of half is found, use last known aember to calculate
            if key == 'losses':
                losses = match.group('losses_group')
                losses_amt = match.group('losses_amt_group')
                if 'players' in losses:
                    losses_amt1 += (int(old_aembergains1) - forges_amt1) // 2
                    player1[10] += (int(old_aembergains1) - forges_amt1) // 2
                    losses_amt2 += (int(old_aembergains2) - forges_amt2) // 2
                    player2[10] += (int(old_aembergains2) - forges_amt2) // 2
                    if debug_mode:
                      print("############# players check - effevescent principle")
                      print("old_aembergains1 is ", old_aembergains1, " and what should have been added is ", str(losses_amt1))
                      print("old_aembergains2 is ", old_aembergains2, " and what should have been added is ", str(losses_amt2))
                elif player1[0] in losses:
                    losses_amt1 += int(losses_amt)
                    if losses_amt1 > (old_aembergains2 - captures_amt1 - steals_amt1):
                      losses_amt1 = old_aembergains2 - captures_amt1 - steals_amt1
                    player1[10] += int(losses_amt)
                    if debug_mode:
                      print("Player 1 - Losses amount + ", str(losses_amt), " and total is now ", str(player1[10]))
                elif player2[0] in losses:
                    losses_amt2 += int(losses_amt)
                    if losses_amt2 > (old_aembergains1 - captures_amt2 - steals_amt2):
                      losses_amt2 = old_aembergains1 - captures_amt2 - steals_amt2
                    player2[10] += int(losses_amt)
                    if debug_mode:
                      print("Player 2 - Losses amount + ", str(losses_amt), " and total is now ", str(player2[10]))
                else:
                    print("Error.  Losses did not match = ", losses)


            line = file_object.readline()

        # create a pandas DataFrame from the list of dicts
        print('Parsing for', filepath)

        # First table with match information
        headdata = []
        headdata = PrettyTable(["Player #", "Userid", "Archon", "     ", "First Player", "Number of Turns", "Winner"])
        headdata.add_row(["Player 1", player1[0], archon1, "     ", firstplayer,turns,winner])
        headdata.add_row(["Player 2", player2[0], archon2, "     ", "","",""])
        headdata.title = "Keyforge Crucible Log Parser"
        print(headdata)

        # Second table with player information
        t = PrettyTable(dataheaders)
        t.add_row(player1)
        t.add_row(player2)
        print(t)
    return

########################################################################

if __name__ == '__main__':
    parse_file(str(filepath))

