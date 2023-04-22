"""
Файл - взаимодействует с базой данных
"""

from peewee import *
from settings.settings import DATABASE, USER, PASSWORD, HOST, PORT


db = PostgresqlDatabase(
    database=DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    autorollback=True,
)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class BotMessages(BaseModel):
    variable = CharField(max_length=50)
    message = TextField()
    image = CharField(max_length=100, null=True)

    class Meta:
        db_table = 'bot_message'


class Variables(BaseModel):
    variable = CharField(max_length=50)
    value = IntegerField(default=0)

    class Meta:
        db_table = 'variables'


class Refills(BaseModel):
    crystal = IntegerField(default=0)
    price = IntegerField(default=0)
    percent = IntegerField(default=0)

    class Meta:
        db_table = 'refills'


class Cities(BaseModel):
    title = CharField(max_length=100)

    class Meta:
        db_table = 'cities'


class Schools(BaseModel):
    city = ForeignKeyField(Cities, related_name='schools', on_delete='CASCADE')
    title = CharField(max_length=100)

    class Meta:
        db_table = 'schools'


class Questions(BaseModel):
    question = TextField()
    image = CharField(max_length=100, null=True)

    class Meta:
        db_table = 'questions'


class Users(BaseModel):
    user_id = BigIntegerField()
    username = CharField(max_length=200, null=True)
    city = ForeignKeyField(Cities, related_name='users', null=True, on_delete='CASCADE')
    choice_city = CharField(max_length=50, null=True)
    school = ForeignKeyField(Schools, related_name='users', null=True, on_delete='CASCADE')
    choice_school = CharField(max_length=50, null=True)
    school_class = IntegerField(null=True)
    gender = CharField(max_length=50, null=True)
    full_name = CharField(max_length=100, null=True)
    status_city = BooleanField(default=False)
    status_school = BooleanField(default=False)
    balance = IntegerField(default=0)
    count = IntegerField(default=0)
    created_at = DateTimeField(null=True)
    signup_at = DateField(null=True)
    active_at = DateTimeField(null=True)
    question_id = IntegerField(null=True)
    classmate = CharField(max_length=200, null=True)
    friend = CharField(max_length=200, null=True)
    another = CharField(max_length=200, null=True)
    current_key = CharField(max_length=200, null=True)
    answer_count = IntegerField(default=0)
    skip_count = IntegerField(default=0)

    class Meta:
        db_table = 'users'


class Friends(BaseModel):
    user = ForeignKeyField(Users, related_name='users_user', on_delete='CASCADE')
    referral = ForeignKeyField(Users, related_name='users_referral', on_delete='CASCADE')

    class Meta:
        db_table = 'friends'


class Answers(BaseModel):
    created_at = DateTimeField(null=True)
    question = ForeignKeyField(Questions, related_name='answers', null=True, on_delete='CASCADE')
    asking = ForeignKeyField(Users, related_name='answers_asking', null=True, on_delete='CASCADE')
    hidden_asking = CharField(max_length=50, null=True)
    answering = ForeignKeyField(Users, related_name='answers_answering', null=True, on_delete='CASCADE')
    hidden_answering = CharField(max_length=50, null=True)
    status = CharField(max_length=50, null=True)

    class Meta:
        db_table = 'answers'


class DeleteMessage(BaseModel):
    chat_id = BigIntegerField()
    message_id = CharField(max_length=200)

    class Meta:
        db_table = 'delete_message'


class Administrators(BaseModel):
    user_id = BigIntegerField(verbose_name='Телеграм ID')

    class Meta:
        db_table = 'administrators'


class SignUp(BaseModel):
    user_id = BigIntegerField()
    change_at = DateTimeField()
    is_city = BooleanField(default=False)
    is_school = BooleanField(default=False)
    is_class = BooleanField(default=False)
    is_gender = BooleanField(default=False)
    is_name = BooleanField(default=False)

    class Meta:
        db_table = 'sign_up'


class Statistics(BaseModel):
    created_at = DateField()
    new_user = BigIntegerField(default=0)
    moscow = BigIntegerField(default=0)
    spb = BigIntegerField(default=0)
    sochi = BigIntegerField(default=0)
    ekb = BigIntegerField(default=0)
    nsb = BigIntegerField(default=0)
    is_city = BigIntegerField(default=0)
    is_school = BigIntegerField(default=0)
    is_class = BigIntegerField(default=0)
    is_gender = BigIntegerField(default=0)
    is_name = BigIntegerField(default=0)
    answers = BigIntegerField(default=0)
    timeouts = BigIntegerField(default=0)
    send_requests = BigIntegerField(default=0)
    confirm_requests = BigIntegerField(default=0)
    signup_invite = BigIntegerField(default=0)
    buy = BigIntegerField(default=0)

    class Meta:
        db_table = 'statistics'


class SchoolClass(BaseModel):
    created_at = DateField()
    city = ForeignKeyField(Cities, related_name='school_class_city', on_delete='CASCADE')
    school = ForeignKeyField(Schools, related_name='school_class_school', on_delete='CASCADE')
    class11 = BigIntegerField(default=0)
    class10 = BigIntegerField(default=0)
    class9 = BigIntegerField(default=0)
    class8 = BigIntegerField(default=0)
    class7 = BigIntegerField(default=0)
    class6 = BigIntegerField(default=0)
    class5 = BigIntegerField(default=0)

    class Meta:
        db_table = 'school_class'

