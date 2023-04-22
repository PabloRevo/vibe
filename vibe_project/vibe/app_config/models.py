from django.db import models


class Variables(models.Model):
    variable = models.CharField(max_length=50, verbose_name='Переменная')
    value = models.IntegerField(default=0, verbose_name='Значение')

    def __str__(self):
        return self.variable

    class Meta:
        verbose_name = 'Переменная'
        verbose_name_plural = 'Переменные'
        db_table = 'variables'


class Refills(models.Model):
    crystal = models.IntegerField(default=0, verbose_name='Кристалы')
    price = models.IntegerField(default=0, verbose_name='Стоимость')
    percent = models.IntegerField(default=0, verbose_name='Процент')

    def __str__(self):
        return f"{self.crystal} за {self.price}руб."

    class Meta:
        verbose_name = 'Пополнение'
        verbose_name_plural = 'Пополнения'
        db_table = 'refills'


class Cities(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название города')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        db_table = 'cities'


class Schools(models.Model):
    city = models.ForeignKey(Cities, related_name='schools', on_delete=models.CASCADE, verbose_name='Город')
    title = models.CharField(max_length=100, verbose_name='Название школы')

    def __str__(self):
        return f"{self.city} - {self.title}"

    class Meta:
        verbose_name = 'Школа'
        verbose_name_plural = 'Школы'
        db_table = 'schools'


class Questions(models.Model):
    question = models.TextField(verbose_name='Вопрос')
    image = models.ImageField(upload_to='questions/', verbose_name='Изображение')

    def __str__(self):
        return f"{self.question}"

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        db_table = 'questions'


class DeleteMessage(models.Model):
    chat_id = models.BigIntegerField(verbose_name='Чат ID')
    message_id = models.CharField(max_length=200, verbose_name='Сообщение ID')

    def __str__(self):
        return f"{self.chat_id}"

    class Meta:
        verbose_name = 'Удаление сообщения'
        verbose_name_plural = 'Удаление сообщений'
        db_table = 'delete_message'


class Administrators(models.Model):
    user_id = models.BigIntegerField(verbose_name='Телеграм ID')

    def __str__(self):
        return f"{self.user_id}"

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'
        db_table = 'administrators'


class SignUp(models.Model):
    user_id = models.BigIntegerField(verbose_name='Телеграм ID')
    change_at = models.DateTimeField(verbose_name='Дата')
    is_city = models.BooleanField(default=False, verbose_name='Город')
    is_school = models.BooleanField(default=False, verbose_name='Школа')
    is_class = models.BooleanField(default=False, verbose_name='Класс')
    is_gender = models.BooleanField(default=False, verbose_name='Пол')
    is_name = models.BooleanField(default=False, verbose_name='Имя')

    def __str__(self):
        return f"{self.user_id}"

    class Meta:
        verbose_name = 'Не прошел регистрацию'
        verbose_name_plural = 'Не прошли регистрацию'
        db_table = 'sign_up'


class Statistics(models.Model):
    created_at = models.DateField(verbose_name='Дата создания')
    new_user = models.BigIntegerField(default=0, verbose_name='Новых регистраций')
    moscow = models.BigIntegerField(default=0, verbose_name='Регистраций в Москве')
    spb = models.BigIntegerField(default=0, verbose_name='Регистраций в Санкт-Петербурге')
    sochi = models.BigIntegerField(default=0, verbose_name='Регистраций в Сочи')
    ekb = models.BigIntegerField(default=0, verbose_name='Регистраций в Екатеринбурге')
    nsb = models.BigIntegerField(default=0, verbose_name='Регистраций в Новосибирске')
    is_city = models.BigIntegerField(default=0, verbose_name='Город')
    is_school = models.BigIntegerField(default=0, verbose_name='Школа')
    is_class = models.BigIntegerField(default=0, verbose_name='Класс')
    is_gender = models.BigIntegerField(default=0, verbose_name='Пол')
    is_name = models.BigIntegerField(default=0, verbose_name='Имя')
    answers = models.BigIntegerField(default=0, verbose_name='Ответы в квизах')
    timeouts = models.BigIntegerField(default=0, verbose_name='Таймауты')
    send_requests = models.BigIntegerField(default=0, verbose_name='Отправлено запросов')
    confirm_requests = models.BigIntegerField(default=0, verbose_name='Подтверждено запросов')
    signup_invite = models.BigIntegerField(default=0, verbose_name='Регистраций по инвайт')
    buy = models.BigIntegerField(default=0, verbose_name='Совершено покупок')

    def __str__(self):
        return f"{self.created_at}"

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'
        db_table = 'statistics'


class SchoolClass(models.Model):
    created_at = models.DateField(verbose_name='Дата создания')
    city = models.ForeignKey(Cities, related_name='school_class_city', on_delete=models.CASCADE, verbose_name='Город')
    school = models.ForeignKey(Schools, related_name='school_class', on_delete=models.CASCADE, verbose_name='Школа')
    class11 = models.BigIntegerField(default=0, verbose_name='11 класс')
    class10 = models.BigIntegerField(default=0, verbose_name='10 класс')
    class9 = models.BigIntegerField(default=0, verbose_name='9 класс')
    class8 = models.BigIntegerField(default=0, verbose_name='8 класс')
    class7 = models.BigIntegerField(default=0, verbose_name='7 класс')
    class6 = models.BigIntegerField(default=0, verbose_name='6 класс')
    class5 = models.BigIntegerField(default=0, verbose_name='5 класс')

    def __str__(self):
        return f"{self.created_at}"

    class Meta:
        verbose_name = 'Статистика по школам'
        verbose_name_plural = 'Статистика по школам'
        db_table = 'school_class'
