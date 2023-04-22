from database.models import *


def save_skip_answers() -> None:
    users = Users.select()
    if len(users) > 0:
        for user in users:
            answers = Answers.select().where(Answers.answering == user.id, Answers.status != 'Пропустил').count()
            skip = Answers.select().where(Answers.answering == user.id, Answers.status == 'Пропустил').count()
            user.answer_count = answers
            user.skip_count = skip
            user.save()
        print('Успешно')


save_skip_answers()
