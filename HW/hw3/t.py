import random

random.seed(4)
for i in range(3):
    random.sample(range(1, 97), 4)

for i in range(100):
    print(random.randint(1, 20)-1, end = ' ')
