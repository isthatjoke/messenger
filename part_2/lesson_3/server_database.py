from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapper, sessionmaker


class ServerDB:
    class AllUsers:

        def __init__(self, username):
            self.username = username
            self.id = None
            self.last_login = datetime.now()

    class ActiveUsers:

        def __init__(self, user_id, ip, port, login_time):
            self.user = user_id
            self.ip = ip
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:

        def __init__(self, user_id, ip, port, date):
            self.user = user_id
            self.login_time = date
            self.ip = ip
            self.port = port
            self.id = None

    class Messages:

        def __init__(self, user_id, to_user, text, date):
            self.user = user_id
            self.to_user = to_user
            self.text = text
            self.date = date
            self.id = None

    def __init__(self):
        self.engine = create_engine('sqlite:///server.database.db3', echo=False, pool_recycle=7200)
        self.metadata = MetaData()
        all_users_table = Table('all_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('username', String, unique=True),
                                Column('last_login', DateTime))

        active_users_table = Table('active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('all_users.id'), unique=True),
                                   Column('ip', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime))

        login_history_table = Table('login_history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('all_users.id')),
                                    Column('ip', String),
                                    Column('port', Integer),
                                    Column('login_time', DateTime))

        messages_table = Table('messages', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('user', ForeignKey('all_users.id')),
                               Column('to_user', String),
                               Column('text', Text),
                               Column('date', DateTime))

        self.metadata.create_all(self.engine)
        mapper(self.AllUsers, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)
        mapper(self.Messages, messages_table)

        make_session = sessionmaker(bind=self.engine)
        self.session = make_session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port):
        check_in_db = self.session.query(self.AllUsers).filter_by(username=username)

        if check_in_db.count():
            user = check_in_db.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip, port, datetime.now())
        self.session.add(new_active_user)

        new_history = self.LoginHistory(user.id, ip, port, datetime.now())
        self.session.add(new_history)

        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def get_message(self, username, to_user, text):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        new_message = self.Messages(user.id, to_user, text, datetime.now())
        self.session.add(new_message)
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
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
        query = self.session.query(
            self.AllUsers.username,
            self.Messages.to_user,
            self.Messages.text,
            self.Messages.date
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)

        return query.all()


if __name__ == '__main__':
    db = ServerDB()
    db.user_login('test_1', '1.1.1.1', 0000)
    db.user_login('test_2', '2.2.2.2', 0000)

    print(db.users_list())
    print(db.active_users_list())

    db.user_logout('test_1')

    print(db.active_users_list())

    print(db.login_history('test_1'))
    print(db.users_list())
    db.get_message('test_1', 'test_2', 'hi,man!')
    print(db.messages_list())
