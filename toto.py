import copy


class Toto:
    def __init__(self):
        self.toto = [1, 2, 3]


toto = Toto()
titi = copy.copy(toto)

titi.toto[1] = 42

print(toto.toto)
print(titi.toto)
