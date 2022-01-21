from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import random

# read in list of possible wordle answers
answers = []
f = open("wordle-answers-alphabetical.txt", "r")
for word in f.readlines():
    answers.append(word.strip())


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.powerlanguage.co.uk/wordle/")

Elem = driver.find_element_by_tag_name('html')

Elem.click()

time.sleep(2)

Elem.send_keys(['r','o','a','t','e'])
Elem.send_keys(Keys.ENTER)
time.sleep(2)


host = driver.find_element_by_tag_name("game-app")
game = driver.execute_script("return arguments[0].shadowRoot.getElementById('game')", host)

boardcontainer = game.find_element_by_id("board-container")
board = boardcontainer.find_element_by_id("board")

rows = board.find_elements_by_tag_name("game-row")

# from website HTML gets the attributes of each row of guesses 
# returns array with correct letters and placement, and two strings for present and absent letters
def getfeedback(rows):
    correct, present, absent = [], [], ""
    for row in rows:
        tiles = driver.execute_script("return arguments[0].shadowRoot.querySelectorAll('.row')", row)
        for tile in tiles:
            gametile = tile.find_elements_by_tag_name("game-tile")
            count = 0
            for t in gametile:
                letter = driver.execute_script("return arguments[0].getAttribute('letter');",t)
                if letter != None:
                    evaluation = driver.execute_script("return arguments[0].getAttribute('evaluation');",t)

                    if evaluation == "correct" and (letter, count) not in correct:
                        correct.append((letter, count))
                    elif evaluation == "present" and letter not in present:
                        present.append((letter, count))
                    elif evaluation == "absent" and letter not in absent:
                        absent += letter

                count += 1
    return (correct, present, absent)

# returns array containing all words that align with the known information
def possibleguesses(answers, correct, present, absent):
    possible = []
    # loop through each word and stores words that meet conditions
    for word in answers:
        match = True
        for letter, placement in correct:
            if word[placement] != letter: match = False
        for letter, placement in present:
            if letter not in word or word[placement] == letter: match = False
        for letter in absent:
            if letter in word and letter not in present and letter not in correct: match = False
        
        if match:
            possible.append(word)

    return possible

def findbestguess(answers, correct, present, absent):
        guesslist = possibleguesses(answers, correct, present, absent)
        freqdict = {}
        listlength= len(guesslist)
        for letter in "qwertyuiopasdfghjklzxcvbnm":
            letteroccurance = sum(s.count(letter) for s in guesslist)
            if letteroccurance>listlength: letteroccurance = 0
            elif letteroccurance>listlength/2: letteroccurance = listlength-letteroccurance
            print("letter {0} occurance:{1}".format(letter, letteroccurance))
            freqdict[letter] = letteroccurance
        print(freqdict)

        maxpoints = -1
        bestword = ""
        for word in guesslist:
            points  = 0
            for letter in word:
                points += freqdict[letter]
            print("word:{0}, points:{1}".format(word, points))

            if points > maxpoints: 
                maxpoints = points
                bestword = word
        print(bestword)
        return bestword

correct, present, absent = getfeedback(rows)

while len(correct) != 5: 
    print("correct: {0}, present: {1}, absent: {2}".format(correct, present, absent))
    #guesslist = possibleguesses(answers, correct, present, absent)
    #print(guesslist)
    #choice = random.choice(guesslist)

    choice = findbestguess(answers, correct, present, absent)

    guess = [letter for letter in choice]

    time.sleep(2)
    Elem.send_keys(guess)
    Elem.send_keys(Keys.ENTER)

    correct, present, absent = getfeedback(rows)
