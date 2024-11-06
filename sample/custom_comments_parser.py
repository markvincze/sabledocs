
import json
import re

class CustomCommentsParser(CommentsParser):
    def __init__(self):
        pass

    def ParseAll(self, comment):
        comment_simple = ' '.join(comment.split()) # remove all new lines and duplicate spaces before json parse
        try:
            comments_dict = json.loads(comment_simple)
        except json.decoder.JSONDecodeError:
            # could print an error here if comments_simple starts with '{' or something
            pass
        else:
            if "desc" in comments_dict:
                # wherever there was a "<p>" replace that with "\n\n" for (utimately) HTML formatting as a new paragraph
                comment = re.sub(r'<p>', r'\n\n', comments_dict["desc"])

        return comment
