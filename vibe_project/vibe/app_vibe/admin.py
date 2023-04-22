from django.contrib import admin
from . models import Users, Friends, Answers


class UsersAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'signup_at', 'user_id', 'username', 'city', 'choice_city', 'school', 'choice_school', 'school_class', 'gender',
        'full_name', 'status_city', 'status_school', 'balance', 'count', 'created_at', 'active_at', 'answer_count', 'skip_count'
    ]
    list_display_links = [
        'id', 'signup_at', 'user_id', 'username', 'city', 'choice_city', 'school', 'choice_school', 'school_class', 'gender',
        'full_name', 'status_city', 'status_school', 'balance', 'count', 'created_at', 'active_at', 'answer_count', 'skip_count'
    ]


class FriendsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'referral']
    list_display_links = ['id', 'user', 'referral']


class AnswersAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'question', 'asking', 'hidden_asking', 'answering', 'hidden_answering', 'status']
    list_display_links = ['created_at', 'question', 'asking', 'hidden_asking', 'answering', 'hidden_answering', 'status']


admin.site.register(Users, UsersAdmin)
admin.site.register(Friends, FriendsAdmin)
admin.site.register(Answers, AnswersAdmin)
