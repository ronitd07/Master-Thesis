import random

secret = random.randint(1,10)

while True:
    guess = int(input('Enter your guess:'))
    if guess == secret:
        print('Correct')
        break
    else:
        print('Try again')




