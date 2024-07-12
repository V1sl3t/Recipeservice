from django.core.exceptions import ValidationError

from foodgram_backend import constants


def validate_cooking_time(value):
    if (value < constants.MIN_VALUE_COOCKING_TIME
            or value > constants.MAX_VALUE_COOCKING_TIME):
        raise ValidationError(
            f'Допустимое количество времени от '
            f'{constants.MIN_VALUE_COOCKING_TIME} '
            f'до {constants.MAX_VALUE_COOCKING_TIME} минут'
        )


def validate_amount(value):
    if (value < constants.MIN_VALUE_AMOUNT
            or value > constants.MAX_VALUE_AMOUNT):
        raise ValidationError(
            f'Допустимое количество ингредиентов от '
            f'{constants.MIN_VALUE_AMOUNT} '
            f'до {constants.MAX_VALUE_AMOUNT}'
        )
