# Game of riddles
A bare bones high difficulty logic/math riddle game.

# Project setup
Users (info + progress) and riddles are saved in dynamodb (AWS). 
Player needs to login with a username (no password required).
Player is presented with one riddle at a time and has a set number of attempts to solve it, if limit is reached a 12 hour time out starts counting down.
Eternal glory awaits the player finishing the riddles.