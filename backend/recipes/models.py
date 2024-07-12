from django.db import models
from django.core.exceptions import ValidationError

from foodgram_backend import constants
from users.models import User


def validate_cooking_time(value):
    if value < constants.MIN_VALUE_COOCKING_TIME \
            or value > constants.MAX_VALUE_COOCKING_TIME:
        raise ValidationError(
            f'Допустимое количество времени от '
            f'{constants.MIN_VALUE_COOCKING_TIME} '
            f'до {constants.MAX_VALUE_COOCKING_TIME} минут'
        )


def validate_amount(value):
    if value < constants.MIN_VALUE_AMOUNT \
            or value > constants.MAX_VALUE_AMOUNT:
        raise ValidationError(
            f'Допустимое количество ингредиентов от '
            f'{constants.MIN_VALUE_AMOUNT} '
            f'до {constants.MAX_VALUE_AMOUNT}'
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=constants.MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        max_length=constants.MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=constants.MAX_LENGTH)
    measurement_unit = models.CharField(max_length=constants.MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=constants.MAX_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=True,
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.IntegerField(
        validators=[validate_cooking_time, ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RicipeUserModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='%(class)ss',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='%(class)ss',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_together_recipe_user'
            )
        ]
        ordering = ['-id']


class Favorite(RicipeUserModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} в избраннном у {self.user.username}'


class ShoppingCart(RicipeUserModel):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.recipe.name} в списке покупок у '
                f'{self.user.username}')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        'Количество',
        validators=[validate_amount, ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
