class HighScore:
    def __init__(self, table):
        self.hs_table = table

    def update(self, name, score):
        self.hs_table[name] = score