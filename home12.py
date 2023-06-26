import json
from datetime import date


class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass


class Name(Field):
    pass


class Phone(Field):
    def validate(self, value):
        if not value.isdigit():
            raise ValueError("Phone number should only contain digits.")


class Birthday(Field):
    def validate(self, value):
        try:
            day, month = map(int, value.split('.'))
            date(year=2000, month=month, day=day)
        except ValueError:
            raise ValueError("Invalid birthday format. Please use dd.mm format.")

        if month < 1 or month > 12:
            raise ValueError("Invalid month value.")
        if day < 1 or day > 31:
            raise ValueError("Invalid day value.")


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phone = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phone.append(Phone(phone))

    def remove_phone(self, phone):
        self.phone = [p for p in self.phone if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phone:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def days_to_birthday(self):
        if self.birthday:
            today = date.today()
            current_year_birthday = self.birthday.value.replace(year=today.year)
            if current_year_birthday < today:
                next_birthday = current_year_birthday.replace(year=today.year + 1)
            else:
                next_birthday = current_year_birthday
            days = (next_birthday - today).days
            return days


class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def __iter__(self):
        return iter(self.data.values())

    def save_address_book(self, filename):
        with open(filename, 'w') as file:
            data = {
                'contacts': [record.__dict__ for record in self.data.values()]
            }
            json.dump(data, file)

    def load_address_book(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            records = []
            for record_data in data['contacts']:
                record = Record(record_data['name'], record_data['birthday'])
                for phone in record_data['phone']:
                    record.add_phone(phone['value'])
                records.append(record)
            self.data = {record.name.value: record for record in records}

    def search_contacts(self, query):
        results = []
        for record in self.data.values():
            if (
                query in record.name.value.lower()
                or any(query in phone.value for phone in record.phone)
            ):
                results.append(record)
        return results


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid command."

    return wrapper


def handle_hello():
    return "How can I help you?"


@input_error
def handle_add(name, phone, address_book, birthday=None):
    if name in address_book.data:
        return "Contact added successfully."
    record = Record(name, birthday)
    record.add_phone(phone)
    address_book.add_record(record)
    return "Contact added"


@input_error
def handle_change(name, phone, address_book):
    if name not in address_book.data:
        return "Contact not found."
    record = address_book.data[name]
    record.add_phone(phone)
    return "Phone number changed successfully."


@input_error
def handle_phone(name, address_book):
    if name not in address_book.data:
        return "Contact not found."
    record = address_book.data[name]
    phones = [phone.value for phone in record.phone]
    return ", ".join(phones)


@input_error
def handle_days_to_birthday(name, address_book):
    if name not in address_book.data:
        return "Contact not found."
    record = address_book.data[name]
    days = record.days_to_birthday()
    if days is None:
        return "No birthday date provided."
    return f"Days until {name}'s birthday: {days}"


def handle_show_all(address_book, page=1, page_size=5):
    if not address_book.data:
        return "No contacts found."

    total_pages = (len(address_book.data) + page_size - 1) // page_size
    if page < 1 or page > total_pages:
        return "Invalid page number."

    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    output = ""
    contacts = list(address_book.data.values())[start_index:end_index]
    for record in contacts:
        phones = [phone.value for phone in record.phone]
        output += f"{record.name.value}: {', '.join(phones)}\n"

    output += f"Page {page}/{total_pages}"
    return output.strip()


def main():
    address_book = AddressBook()
    while True:
        command = input("Enter a command: ").lower()
        if command == "hello":
            response = handle_hello()
        elif command.startswith("add"):
            params = command.split()
            if len(params) == 3:
                _, name, phone = params
                response = handle_add(name, phone, address_book)
            elif len(params) == 4:
                _, name, phone, birthday = params
                response = handle_add(name, phone, address_book, birthday)
            else:
                response = "Invalid command."
        elif command.startswith("change"):
            _, name, phone = command.split()
            response = handle_change(name, phone, address_book)
        elif command.startswith("phone"):
            _, name = command.split()
            response = handle_phone(name, address_book)
        elif command.startswith("days to birthday"):
            _, name = command.split()
            response = handle_days_to_birthday(name, address_book)
        elif command.startswith("show all"):
            params = command.split()
            page = int(params[2]) if len(params) > 2 else 1
            response = handle_show_all(address_book, page)
        elif command.startswith("save"):
            _, filename = command.split()
            address_book.save_address_book(filename)
            response = "Address book saved."
        elif command.startswith("load"):
            _, filename = command.split()
            address_book.load_address_book(filename)
            response = "Address book loaded."
        elif command.startswith("search"):
            _, query = command.split()
            results = address_book.search_contacts(query.lower())
            if results:
                response = "Search results:\n"
                for result in results:
                    phones = [phone.value for phone in result.phone]
                    response += f"{result.name.value}: {', '.join(phones)}\n"
            else:
                response = "No contacts found for the search query."
        elif command in ["good bye", "close", "exit"]:
            response = "Good bye!"
            break
        else:
            response = "Invalid command."
        print(response)


if __name__ == "__main__":
    main()
