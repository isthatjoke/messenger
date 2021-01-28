from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import default_comparator


class ClientDB:
    """
    Main class for client_ database for SQLAlchemy
    """
    class Users:
        """
        all users class
        """
        def __init__(self, username):
            self.username = username
            self.id = None

    class History:
        """
        messages history class
        """
        def __init__(self, contact, direction, message):
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.now()
            self.id = None

    class Contacts:
        """
        contacts class
        """
        def __init__(self, username, date_remove=None, is_active=True):
            self.username = username
            self.date_add = datetime.now()
            self.date_remove = date_remove
            self.is_active = is_active
            self.id = None

    def __init__(self, client):
        self.engine = create_engine(f'sqlite:///clientDB.{client}.db3', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        users_table = Table('users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String, unique=True))

        history_table = Table('history', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('contact', String),
                              Column('direction', String),
                              Column('message', Text),
                              Column('date', DateTime))

        contacts_table = Table('contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('username', String, unique=True),
                               Column('date_add', DateTime),
                               Column('date_remove', DateTime, default=None, nullable=True),
                               Column('is_active', String, default=True))

        self.metadata.create_all(self.engine)
        mapper(self.Users, users_table)
        mapper(self.History, history_table)
        mapper(self.Contacts, contacts_table)
        make_session = sessionmaker(bind=self.engine)
        self.session = make_session()

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """
        managing contact relations adding func
        :param contact: str name of contact
        :return:
        """
        if not self.session.query(self.Contacts).filter_by(username=contact).first():
            new_contact = self.Contacts(contact)
            self.session.add(new_contact)
        else:
            old_contact = self.session.query(self.Contacts).filter_by(username=contact).first()
            old_contact.date_remove = None
            old_contact.is_active = True
        self.session.commit()

    def del_contact(self, contact):
        """
        managing contact relations deleting func
        :param contact: str name of contact
        :return:
        """
        old_contact = self.session.query(self.Contacts).filter_by(username=contact).first()
        old_contact.date_remove = datetime.now()
        old_contact.is_active = False
        self.session.commit()

    def check_user(self, contact):
        """
        check user exists
        :param contact: str
        :return: bool
        """
        if self.session.query(self.Users).filter_by(username=contact).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """
        check contact exists
        :param contact: str
        :return: bool
        """
        if self.session.query(self.Contacts).filter_by(username=contact).count():
            return True
        else:
            return False

    def add_users(self, users):
        """
        add user to database
        :param users: list of users
        :return:
        """
        self.session.query(self.Users).delete()
        for user in users:
            user = self.Users(user)
            self.session.add(user)
        self.session.commit()

    def save_new_message(self, contact, direction, message):
        """
        save new message to message history table
        :param contact: name
        :param direction: incoming or outgoing message
        :param message: dict
        :return:
        """
        new_message = self.History(contact, direction, message)
        self.session.add(new_message)
        self.session.commit()

    def get_contacts(self):
        """
        contacts in relation request
        :return: list
        """
        return [contact[0] for contact in self.session.query(self.Contacts.username).
                filter(self.Contacts.is_active == True)]

    def get_users(self):
        """
        all user request
        :return: list
        """
        return [user[0] for user in self.session.query(self.Users.username).all()]

    def get_history(self, contact):
        """
        message history request for user
        :param contact: name of contact
        :return: list
        """
        query = self.session.query(self.History).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    db = ClientDB('test')
    # db.add_contact('test_1')
    # db.add_contact('test_2')
    # print(db.get_contacts())
    # db.add_contact('test_1')
    # print(db.get_contacts())
    # db.del_contact('test_1')
    # print(db.get_contacts())
    # db.add_contact('test_1')
    # print(db.get_contacts())
    db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    print(db.get_users())
    # db.save_new_message('test_1', 'test_2', 'hi man!')
    # print(db.get_history('test_1'))
    # print(db.get_history(to_='test_2'))


