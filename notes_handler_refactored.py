

class NoteHandler:
    def __init__(self):
        self.notes_file = 'notes.txt'
        self.get_text_from_file()

    def get_text_from_file(self):
        try:
            with open(self.notes_file, 'r') as reader:
                all_lines = reader.read()
                if self.validate_text(all_lines):
                    return all_lines
        except FileNotFoundError:
            print('File not found, creating new one')
            self.create_text_file(self.notes_file)

    def save_text(self, text):
        with open(self.notes_file, 'w+') as writer:
            if self.validate_text(text):
                writer.write(text)

    @staticmethod
    def create_text_file(file):
        with open(file, 'w+'):
            pass

    @staticmethod    
    def validate_text(string):
        if isinstance(string, str):
            if len(string) < 10_000:
                return True
            else:
                False


