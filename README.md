# Project-Cleanup
This script cleans up unused sprites and audio files from Fraytools projects. It takes all of these files and creates a new folder called "cleanup" where these unused files can then be reviewed prior to deletion.

# How to use
Simply select a Fraytools project folder that you wish to clean with the folder browse button! If the folder is deemed to be valid, then the program will parse through the files and remove anything that is not used by the character (aka bye bye Frankyie)
The program does take some time to execute especially for larger projects so please be patient.

# Options
This program does have a few options such as batch cleanup and advanced audio cleanup.

## Batch Cleanup
This allows you to clean mulitple projects all from one program run. Instead of selecting one project folder, select the folder that has multiple project folders inside of it.

## Advanced audio cleanup
This method attempts to clean unused audio files by looking at a users code along with CharacterStats.hx file to determine what audio is used in the proejct. Any unused audio will be removed.
Since this is attempting to parse code, there will be errors since there are a million ways to play audio in Fraytools, hence why this is listed as experimental and should be used at your own RISK!!
