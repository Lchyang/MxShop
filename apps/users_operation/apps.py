from django.apps import AppConfig


class UsersOperationConfig(AppConfig):
    name = 'users_operation'
    verbose_name = '用户操作'

    # 信号量处理时要在APP里面注册
    def ready(self):
        import users_operation.signals