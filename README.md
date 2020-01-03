# The Feud
Art by Brian Yeung\
Programming by Adam Wiley

## Operating Guide
### Using the Editor

The editor program is a single window for creating new surveys or modifying existing ones.
To create a new survey, give the survey a (preferably short) filename, a question, and at least one valid
response then click
the "Save" button.
If a response is blank or has a higher count than a response with a higher rank then it is considered invalid.
To modify a survey, enter the filename for that survey the click the "Load" button then edit the survey
as if creating a new survey. Saving this but leaving the same filename will overwrite the previous survey data.
At any point you can clear the entire editor by clicking the "Clear" button.

### Running a Game
This guide assumes you already know the rules of the game show.

To transfer surveys from the editor to the game, copy the .survey files from the editor surveys folder to the game
survey folder (example.survey should be present in both locations already).

When the game launches, two windows will appear. One will be the small control window for the operator and the other
will be the display window for everyone to see. The display window will always appear on your computer's primary
display screen.

The control window will begin in the preparing state. In this mode, the operator can select preparing for either the
main game or fast money. \
To prepare for the main game, simply select a survey from the list to preview it then click the "Set As Current"
button. After that you can go to any of the main game modes by clicking the mode's corresponding button
on the top of the window. \
To prepare for fast money, five surveys must be selected similarly to main game preparing. You can also set how
long each player will have to answer the fast money questions. After doing this, you can go to the Fast Money mode.

The main game has several associated different modes - the names should clearly correspond to the game mode you want
to use. \
The round selection controls the points multiplier for that round. \
The active team should be selected after face-off and before attempting to give any points - only the active team
may receive points. Manual editing of points is allowed by the operator. \
Strikes only accumulate in certain modes and the number can be edited at any time manually to be 1, 2, or 3. This
number corresponds to the number of strikes that will appear the next time the button is pressed.\
Some modes will remove the strike counter (but not the button), revealing mode will disable giving points, and
tiebreaker will disable round selection (since there is always a 3x multiplier for tiebreaker).
The tiebreaker mode will make sure there is only one survey response so use the mode for the
entire tiebreaker round. \
To reveal a response, press the corresponding show button.

You can start the timer by using the timer box to set either the first or second player's time then 
pressing "Start". \
To set a player's response phrase for fast money, simply type it into the corresponding text field. \
To set a count for a phrase, select that specific response using the corresponding "Select" button then link
to one of the survey responses by clicking the "Link" button next to the corresponding survey response. \
To reveal the response and count, press the reveal button after entering the phrase and linking the count. \
You can hide the screen by using the visibility box to cover the fast money screen with the logo. \
The try again sound button is used when the second player says a response that is too similar to the first 
player's response for the same question.

## Building

This program was built and tested with Python 3.7.2

The required packages can be found in requirements.txt (install with pip using `pip install -r requirements.txt`)

Using venv is recommended

Create either the editor or game executable by running `pyinstaller <spec file>` in the root directory
where the spec file is either the editor or game one (if pyinstaller multipackage support was currently working
then only one spec file would be necessary)
