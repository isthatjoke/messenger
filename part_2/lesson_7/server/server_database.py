import configparser
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import default_comparator


class ServerDB:
    """
    Main class for server database for SQLAlchemy
    """
    class AllUsers:
        """
        all users class
        """
        def __init__(self, username, pwd_hash):
            self.username = username
            self.id = None
            self.last_login = datetime.now()
            self.pwd_hash = pwd_hash

    class ActiveUsers:
        """
        active users class
        """
        def __init__(self, user_id, ip, port, login_time, keys):
            self.user = user_id
            self.ip = ip
            self.port = port
            self.login_time = login_time
            self.id = None
            self.keys = keys

    class LoginHistory:
        """
        login history class
        """
        def __init__(self, user_id, ip, port, date):
            self.user = user_id
            self.login_time = date
            self.ip = ip
            self.port = port
            self.id = None

    class Messages:
        """
        messages history class
        """
        def __init__(self, user_id, to_user, text, date):
            self.user = user_id
            self.to_user = to_user
            self.text = text
            self.date = date
            self.id = None

    class Contacts:
        """
        contacts relations class
        """
        def __init__(self, user_id, friend_id, date_add, date_remove=None, is_active=True):
            self.user = user_id
            self.friend = friend_id
            self.date_add = date_add
            self.date_remove = date_remove
            self.is_active = is_active
            self.id = None

    class MessagesCount:
        """
        messages count class
        """
        def __init__(self, user_id, updated=None):
            self.user = user_id
            self.sent = 0
            self.received = 0
            self.updated = updated

    def __init__(self, path):
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()
        all_users_table = Table('all_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('username', String, unique=True),
                                Column('last_login', DateTime),
                                Column('pwd_hash', String))

        active_users_table = Table('active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('all_users.id'), unique=True),
                                   Column('ip', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime),
                                   Column('keys', Text))

        login_history_table = Table('login_history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('all_users.id')),
                                    Column('ip', String),
                                    Column('port', Integer),
                                    Column('login_time', DateTime))

        messages_table = Table('messages', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('user', ForeignKey('all_users.id')),
                               Column('to_user', ForeignKey('all_users.id')),
                               Column('text', Text),
                               Column('date', DateTime))

        contacts_table = Table('contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('user', ForeignKey('all_users.id')),
                               Column('friend', ForeignKey('all_users.id')),
                               Column('date_add', DateTime),
                               Column('date_remove', DateTime, nullable=True, default=None),
                               Column('is_active', String, default=True))

        messages_count_table = Table('messages_count', self.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('user', ForeignKey('all_users.id')),
                                     Column('sent', Integer, default=0),
                                     Column('received', Integer, default=0),
                                     Column('updated', DateTime, nullable=True))

        self.metadata.create_all(self.engine)
        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)
        mapper(self.Messages, messages_table)
        mapper(self.Contacts, contacts_table)
        mapper(self.MessagesCount, messages_count_table)

        make_session = sessionmaker(bind=self.engine)
        self.session = make_session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port, pwd_hash, keys):
        """
        user login func
        :param username: username
        :param ip: ip address
        :param port: ip port
        :param pwd_hash: user password hash
        :param keys: user public key
        :return:
        """
        check_in_db = self.session.query(self.AllUsers).filter_by(username=username)

        if check_in_db.count():
            user = check_in_db.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username, pwd_hash)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip, port, datetime.now(), keys)
        self.session.add(new_active_user)

        new_history = self.LoginHistory(user.id, ip, port, datetime.now())
        self.session.add(new_history)

        if not self.session.query(self.MessagesCount).filter_by(user=user.id).count():
            new_messages_count = self.MessagesCount(user.id)
            self.session.add(new_messages_count)

        self.session.commit()

    def user_logout(self, username):
        """
        user logout func
        :param username: username
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def get_message(self, username, to_user, text):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        other_user = self.session.query(self.AllUsers).filter_by(username=to_user).first()
        new_message = self.Messages(user.id, other_user.id, text, datetime.now())
        self.session.add(new_message)
        self.session.commit()

    def users_list(self):
        """
        list of all users
        :return: users queryset
        """
        query = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        """
        list of active users
        :return: active users queryset
        """
        query = self.session.query(
            self.AllUsers.username,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        """
        login user history
        :param username: username
        :return: login history queryset
        """
        query = self.session.query(
            self.AllUsers.username,
            self.LoginHistory.ip,
            self.LoginHistory.port,
            self.LoginHistory.login_time
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)

        return query.all()

    def messages_list(self, username=None):
        """
        get user message history
        :param username: username
        :return: messages history queryset
        """
        query = self.session.query(
            self.AllUsers.username,
            self.Messages.to_user,
            self.Messages.text,
            self.Messages.date
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)

        return query.all()

    def add_contact(self, user, friend):
        """
        func to add new contact and ave in database
        :param user: username
        :param friend: contact name
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(username=user).first()
        friend = self.session.query(self.AllUsers).filter_by(username=friend).first()

        if not friend or self.session.query(self.Contacts).filter_by(
                user=user.id, friend=friend.id, is_active=True).count():
            return
        elif self.session.query(self.Contacts).filter_by(user=user.id, friend=friend.id, is_active=False).count():
            contact = self.session.query(self.Contacts).filter_by(
                user=user.id, friend=friend.id, is_active=False).first()
            contact.is_active = True
        else:
            contact = self.Contacts(user.id, friend.id, datetime.now())
        self.session.add(contact)
        self.session.commit()

    def delete_contact(self, user, friend):
        """
        func to deactivate (delete) contact
        :param user: username
        :param friend: contact name
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(username=user).first()
        friend = self.session.query(self.AllUsers).filter_by(username=friend).first()

        if not friend or not self.session.query(self.Contacts).filter_by(user=user.id, friend=friend.id).count():
            return

        ex_friend = self.session.query(self.Contacts).filter_by(user=user.id, friend=friend.id).first()
        ex_friend.is_active = False
        ex_friend.date_remove = datetime.now()
        self.session.commit()

    def get_contact(self, username):
        """
        func returns users contacts list
        :param username: username
        :return: contacts lsit
        """
        user = self.session.query(self.AllUsers).filter_by(username=username).one()

        query = self.session.query(self.Contacts, self.AllUsers.username).filter_by(user=user.id). \
            join(self.AllUsers, self.Contacts.friend == self.AllUsers.id)

        query = query.filter(self.Contacts.is_active == True)

        return [contact[1] for contact in query.all()]

    def messages_count(self, sender, receiver):
        """
        func counts messages for each user
        :param sender: username
        :param receiver: username
        :return:
        """
        sender = self.session.query(self.AllUsers).filter_by(username=sender).first().id
        receiver = self.session.query(self.AllUsers).filter_by(username=receiver).first().id

        sender_id = self.session.query(self.MessagesCount).filter_by(user=sender).first()
        sender_id.sent += 1
        sender_id.updated = datetime.now()

        receiver_id = self.session.query(self.MessagesCount).filter_by(user=receiver).first()
        receiver_id.received += 1
        receiver_id.updated = datetime.now()

        self.session.commit()

    def get_messages_count(self, username=None):
        """
        returns count of messages
        :param username: username
        :return: queryset
        """
        query = self.session.query(
            self.AllUsers.username,
            self.MessagesCount.sent,
            self.MessagesCount.received).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)

        return query.all()

    def message_history(self):
        """
        returns messages for user
        :return: messages history queryset
        """
        query = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login,
            self.MessagesCount.sent,
            self.MessagesCount.received
        ).join(self.AllUsers)

        return query.all()

    def check_user(self, user):
        """
        func user existing
        :param user: username
        :return: bool
        """
        if self.session.query(self.AllUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_pwd(self, user):
        """
        returns password hash for user
        :param user: username
        :return: password hash, str
        """
        query = self.session.query(
            self.AllUsers.pwd_hash
        ).filter_by(username=user).first()
        return query

    def get_keys(self, name):
        """
        returns public key of user
        :param name:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(username=name).one()
        user = self.session.query(self.ActiveUsers).filter_by(user=user.id).first()
        return user.keys


if __name__ == '__main__':
    server_config = configparser.ConfigParser()
    server_config.read('server_.ini')
    db = ServerDB(server_config['SETTINGS']['db_file_name'])
    db.user_login('test_1', '1.1.1.1', 0000, 1234, 123)
    db.user_login('gumdrop', '2.2.2.2', 0000, 1234, 123)
    # db.user_login('test_3', '2.2.2.2', 0000)

    # print(db.users_list())
    print(db.active_users_list())

    db.user_logout('test_1')

    print(db.active_users_list())
    # print(db.check_pwd('test_1')[0])
    print(db.get_keys('gumdrop'))
    # print(db.login_history('test_1'))
    # print(db.users_list())
    # # db.get_message('test_1', 'test_2', 'hi,man!')
    # # print(db.messages_list())
    # db.add_contact('test_1', 'test_2')
    # db.add_contact('test_1', 'test_3')
    # # db.delete_contact('test_1', 'test_2')
    # print(db.get_contact('test_1'))
    # db.messages_count('test_1', 'test_2')
    # db.messages_count('test_2', 'test_1')
    # print(db.get_messages_count())
