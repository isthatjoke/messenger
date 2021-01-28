import configparser
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapper, sessionmaker


class ClientDB:
    class Users:
        def __init__(self, username):
            self.username = username
            self.id = None

    class History:
        def __init__(self, from_user, to_user, text):
            self.from_user = from_user
            self.to_user = to_user
            self.text = text
            self.date = datetime.now()
            self.id = None

    class Contacts:
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
                              Column('from_user', String),
                              Column('to_user', String),
                              Column('text', Text),
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
        if not self.session.query(self.Contacts).filter_by(username=contact).first():
            new_contact = self.Contacts(contact)
            self.session.add(new_contact)
        else:
            old_contact = self.session.query(self.Contacts).filter_by(username=contact).first()
            old_contact.date_remove = None
            old_contact.is_active = True
        self.session.commit()

    def del_contact(self, contact):
        old_contact = self.session.query(self.Contacts).filter_by(username=contact).first()
        old_contact.date_remove = datetime.now()
        old_contact.is_active = False
        self.session.commit()

    def check_user(self, contact):
        if self.session.query(self.Users).filter_by(username=contact).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        if self.session.query(self.Contacts).filter_by(username=contact).count():
            return True
        else:
            return False

    def add_users(self, users):
        self.session.query(self.Users).delete()
        for user in users:
            user = self.Users(user)
            self.session.add(user)
        self.session.commit()

    def save_new_message(self, from_user, to_user, message):
        new_message = self.History(from_user, to_user, message)
        self.session.add(new_message)
        self.session.commit()

    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.Contacts.username).
                filter(self.Contacts.is_active == True)]

    def get_users(self):
        return [user[0] for user in self.session.query(self.Users.username).all()]

    def get_history(self, from_=None, to_=None):
        query = self.session.query(self.History)
        if from_:
            query = query.filter_by(from_user=from_)
        if to_:
            query = query.filter_by(to_user=to_)
        return [(row.from_user, row.to_user, row.text, row.date) for row in query.all()]


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


