from django.db import models
from app_config.models import Questions, Cities, Schools


class Users(models.Model):
    GENDER = [
        ('Парень', 'Парень'),
        ('Девушка', 'Девушка'),
    ]
    user_id = models.BigIntegerField(verbose_name='Телеграм ID')
    username = models.CharField(max_length=200, blank=True, null=True, verbose_name='Имя пользователя')
    city = models.ForeignKey(Cities, related_name='users', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Город')
    choice_city = models.CharField(max_length=50, blank=True, null=True, verbose_name='Выбор города')
    school = models.ForeignKey(Schools, related_name='users', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Школа')
    choice_school = models.CharField(max_length=50, blank=True, null=True, verbose_name='Выбор школы')
    school_class = models.IntegerField(blank=True, null=True, verbose_name='Класс')
    gender = models.CharField(max_length=50, choices=GENDER, blank=True, null=True, verbose_name='Пол')
    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Имя Фамилия')
    status_city = models.BooleanField(default=False, verbose_name='Статус города')
    status_school = models.BooleanField(default=False, verbose_name='Статус школы')
    balance = models.IntegerField(default=0, verbose_name='Баланс')
    count = models.IntegerField(default=0, verbose_name='Счётчик вопросов')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время последнего ответа')
    signup_at = models.DateField(blank=True, null=True, verbose_name='Дата регистрации')
    active_at = models.DateTimeField(blank=True, null=True, verbose_name='Активная команда')
    question_id = models.IntegerField(blank=True, null=True, verbose_name='Вопрос ID')
    classmate = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Одноклассник')
    friend = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Друзья')
    another = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Другие')
    current_key = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Текущая клавиатура')
    answer_count = models.IntegerField(default=0, verbose_name='Ответы')
    skip_count = models.IntegerField(default=0, verbose_name='Пропуски')

    def __str__(self):
        return f"{self.user_id} - {self.full_name}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'


class Friends(models.Model):
    user = models.ForeignKey(Users, related_name='users_user', on_delete=models.CASCADE, verbose_name='Пользователь')
    referral = models.ForeignKey(Users, related_name='users_referral', on_delete=models.CASCADE, verbose_name='Реферал')

    def __str__(self):
        return f"{self.user} | {self.referral}"

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        db_table = 'friends'


class Answers(models.Model):
    HIDDEN = (
        ('Скрытый', 'Скрытый'),
        ('Раскрытый', 'Раскрытый'),
        ('Запрос', 'Запрос'),
    )
    STATUS = [
        ('Новое', 'Новое'),
        ('Пропустил', 'Пропустил'),
        ('Просмотрен', 'Просмотрен')
    ]
    created_at = models.DateTimeField(null=True, verbose_name='Дата создания')
    question = models.ForeignKey(Questions, related_name='answers', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Вопрос')
    asking = models.ForeignKey(Users, related_name='answers_asking', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Спрашивающий')
    hidden_asking = models.CharField(max_length=50, choices=HIDDEN, blank=True, null=True, verbose_name='Скрытость спрашивающего')
    answering = models.ForeignKey(Users, related_name='answers_answering', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Отвечающий')
    hidden_answering = models.CharField(max_length=50, choices=HIDDEN, blank=True, null=True, verbose_name='Скрытость отвечающего')
    status = models.CharField(max_length=50, choices=STATUS, blank=True, null=True, verbose_name='Статус ответа')

    def __str__(self):
        return f"{self.question} | {self.answering}"

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        db_table = 'answers'
