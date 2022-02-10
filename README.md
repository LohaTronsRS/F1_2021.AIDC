# F1 2021 AI Difficulty Tool
Basic console script for helping determine AI difficulty setting for the F1 2021 Game using UDP output

The tool will gather fastest AI and Player times of a OSQ Session, and generate a visual table of Players time difference to AI Times to help determine AI Difficulty for other gamemodes.

### Current comparsions include Players:
* SoB (Sum of Best valid sectors aka Theoretical session best)
* PB (Personal Best time)
* Average of Top 3 Players times 
* Average of Top 10 Players times
* Average of All Players times
These times will be compared against AI's top average finish for a specified difficulty

## Basic usage:
* Enable games UDP output in ingames telemetry settings (Script uses games default IP "127.0.0.1" and Port 20777, can edited if needed)
* Open the Tool
* Setup GP mode with few copies (~5) of same track for which you want to determine AI difficuly
* Use MyTeam car with Equal Car Performances turned on (Teammate doesn't really matter from personal expierence)
* For weekend settings enable One Shot Qualifying
* Set weather to Clear ( or any other setting thats not custom/random)
* Set AI Difficulty to basically anything (as you will be changing this later)
1. Jump in the weekend, load your setups
2. Do the OSQ, restart session and repeat 2 or 3 times
3. Advance to next Weekend by retiring from the race
4. Change the AI difficulty by 5 or 10 depending how 
* Repeat the 4 steps above few times until you are sick and tired of doing OSQ :)

I would recommend ATLEAST 5-10 laps total of OSQ ( 3-5 per difficuly step you drive against ), but after that its up to you how many laps you willing to put in. More laps per difficulty step does result in more accurate timings
Tool currently does not have any type of file handling, so make sure to note down final difficulty you wish to drive against.

##### UDP Packet format 2021, Version 1.15 (Didn't implement a version check but doubtful codies will update UDP output this far in the games cycle ...)

##### Written using Python 3.10

##### pls no bully the terrible code :)

##### Todo : Update this readme when im not falling asleep...
