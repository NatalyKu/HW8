from collections import UserDict

from datetime import datetime, date, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value: str):
        if len(value) == 10 and value.isdigit():
            super().__init__(value) 
        else:
            raise ValueError  

class Birthday(Field):
    def __init__(self, value):
        try:
            if isinstance(value, str):                          
                datetime.strptime(value, "%d.%m.%Y")
                super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.birthday = None
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None             
    
    def remove_phone(self, phone):
        if self.find_phone(phone):
            self.phones = [p for p in self.phones if p.value != phone]
        else:
            raise ValueError

    def edit_phone(self, phone, new_phone):
        if self.find_phone(phone):
            self.add_phone(new_phone)
            self.remove_phone(phone)
        else:
            raise ValueError

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
            
    def show_birthday(self):
        return self.birthday
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        return self.data   

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if self.find(name):
            self.data.pop(name) 
            return "Record deleted"
        else:
            raise ValueError
    
    def date_to_string(self, date):
        return date.strftime("%d.%m.%Y")
    
    def string_to_date(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y").date()

    def find_next_weekday(self, date):
        days_ahead = 7 - date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, date):
        if date.weekday() >= 5:
            return self.find_next_weekday(date)
        return date

    def get_birthdays(self):
        days = 7
        upcoming_birthdays = []
        today = date.today()
        next_year = today.year + 1

        for record in self.data.values():
            if record.birthday is not None:
                birthday_date = self.string_to_date(record.birthday.value)
                birthday_this_year = birthday_date.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=next_year)
                
                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date = self.adjust_for_weekend(birthday_this_year)
                    congratulation_date_str = self.date_to_string(congratulation_date)
                    upcoming_birthdays.append({"name": record.name.value, "birthday": congratulation_date_str})
                
        return upcoming_birthdays

    def __str__(self):
        records = '\n'.join(str(record) for record in self.data.values())
        return f"AddressBook:\n{records}"
    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Check your contact is right"
        except KeyError:
            return "Check if the name you wrote is correct."
    return inner   

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phone numbers: {', '.join(phone.value for phone in record.phones)}"
    else:
        return "Contact not found."
    
@input_error
def change_contact(args, contacts):
    name, phone = args
    if name in contacts:
        contacts[name] = phone
        return "Contact updated."
    else:
        return "Are you sure that name is not wrong"

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "Are you sure that name is not wrong"
    
@input_error   
def show_all(book):
    return str(book)

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday is not None: 
            return f"Contact name: {record.name.value}, birthday: {record.birthday.value}"
        else:
            return "No birthday set"
    else:
        return "Contact not found."

@input_error
def birthdays(book):
    return book.get_birthdays()

def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook() 
           
filename = "addressbook.pkl"
def save_data(book, filename):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def main():
    book = load_data(filename) 
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            save_data(book, filename)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(load_data(filename),show_all(book))
        elif command == "add_birthday": 
            print(add_birthday(args, book))
        elif command == "show_birthday": 
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
