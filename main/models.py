from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Product(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    short_description = models.TextField(blank=True, verbose_name="Короткое описание")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение")
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, verbose_name="Размер")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_hot_sales = models.BooleanField(default=False, verbose_name="Горячая продажа")
    is_bestseller = models.BooleanField(default=False, verbose_name="Бестселлер")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f'{self.category} | {self.name} | {self.price} | {self.created_at}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('packing', 'Упаковка'),
        ('shipped', 'В пути'),
        ('delivered', 'Доставлен'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные при выдаче'),
        ('card', 'Банковская карта'),
        ('sbp', 'СБП'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Почта")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оформления")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, default='cash', verbose_name="Способ оплаты")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='packing', verbose_name="Статус")

    class Meta:
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f"Заказ №{self.id} от {self.first_name} {self.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"Сообщение от {self.name} ({self.email})"