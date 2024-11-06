
class CommentsParser:
    """Inherit from this class in order to provide additional parsing of
       comment strings before inserting into the HTML document."""
    def __init__(self):
        pass

    def ParseAll(self, comment):
        return comment

    def ParsePackage(self, comment):
        return self.ParseAll(comment)

    def ParseMessage(self, comment):
        return self.ParseAll(comment)

    def ParseField(self, comment):
        return self.ParseAll(comment)

    def ParseEnum(self, comment):
        return self.ParseAll(comment)

    def ParseEnumValue(self, comment):
        return self.ParseAll(comment)

    def ParseService(self, comment):
        return self.ParseAll(comment)

    def ParseServiceMethod(self, comment):
        return self.ParseAll(comment)
