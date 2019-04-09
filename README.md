# keyforge_log_parser
Keyforge log parser for text logs from The Crucible Online

Usage: python keyforge_log_parser.py `<path to log file>`

User libraries: sys, re, PrettyTable


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
