
maxsize=200

class Uri:
    def __init__(self, uri):
        self.uri = uri
    def __str__(self):
        return "<" + self.uri + ">"

class String:
    def __init__(self, value):
        self.value = value
    def __str__(self):

        val = self.value
        val = val.strip()
        val = val.replace("\t", " ")
        val = val.replace("  ", " ")

        # truncate
        val = val[:maxsize]

        return '"' + val + '"'

