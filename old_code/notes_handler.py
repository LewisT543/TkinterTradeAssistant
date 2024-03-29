import csv

class Note:
    def __init__(self, title, contents):
        self.title = title
        self.contents = contents

class NotesHandler:
    def __init__(self):
        self.notes_file = 'notes.csv'
        self.notes = []
        self.fieldnames = ['title', 'note']
        self.get_notes_from_csv()
    
    def create_csv(self):
        with open(self.notes_file, 'w') as note_file:
            header_writer = csv.writer(note_file)
            header_writer.writerow(self.fieldnames)

    def get_notes_from_csv(self):
        try:
            with open(self.notes_file, 'r+', newline='') as note_file:
                note_reader = csv.DictReader(note_file, fieldnames=self.fieldnames)
                for line in note_reader:
                    note = Note(line['title'], line['note'])
                    if self.validate_note_text(note):
                        self.notes.append(note)
                    else:
                        print('Error getting notes, a field isnt valid in the csv file')
                        return
        except FileNotFoundError:
            print('Could not find csv file.')
            self.create_csv()

    def get_notes_from_csv2(self):
        try:
            with open(self.notes_file, 'r+', newline='') as note_file:
                reader = csv.reader(note_file)
                for line in reader:
                    note = Note(line[0], line[1])
                    if self.validate_note_text(note):
                        self.notes.append(note)
                    else:
                        print('Error getting notes, a field isnt valid in the csv file')
                        return
        except FileNotFoundError:
            print('Could not find csv file.')
            self.create_csv()

    def add_notes_to_csv(self):
        with open(self.notes_file, 'a+', newline='') as note_file:
            note_appender = csv.writer(note_file, fieldnames=self.fieldnames)
            for note in self.notes:
                if self.validate_note_text(note):
                    note_appender.writerow()
                else:
                    print('Error saving all notes, a field isnt valid')
            
    @staticmethod
    def validate_note_text(note):
        print('title', note.title.isalnum(), 'content', note.contents.isalnum(), 'title', note.title, 'content', note.contents)
        if note.title.isalnum() and note.contents.isalnum():
            return True
        else:
            return False
        
my_notes = NotesHandler()
my_notes.get_notes_from_csv2()
print(my_notes.notes)
for note in my_notes.notes:
    print(note.title, note.contents)
