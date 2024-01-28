from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """
    Model representing customers in the system.

    Fields:
    - user: Foreign key to the User model, linking the customer to a Django user.
    - name: Customer's name.
    - email: Customer's email address.
    """
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model representing products in the system.

    Fields:
    - name: Product name.
    - price: Product price.
    - digital: Boolean field indicating whether the product is digital.
    - image: Product image.
    """
    name = models.CharField(max_length=200)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        """
        Property that returns the URL of the product image.
        Used for displaying the image in templates.
        """
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    """
    Model representing orders in the system.

    Fields:
    - customer: Foreign key to the Customer model, indicating the customer who placed the order.
    - date_ordered: Date and time when the order was placed.
    - complete: Boolean field indicating whether the order is complete.
    - transaction_id: Unique transaction identifier.
    """
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        """
        Property indicating whether shipping is required for any non-digital products in the order.
        """
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        """
        Property that returns the total cost of items in the order.
        """
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        """
        Property that returns the total quantity of items in the order.
        """
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    """
    Model representing items within an order.

    Fields:
    - product: Foreign key to the Product model, indicating the product in the order.
    - order: Foreign key to the Order model, indicating the order to which the item belongs.
    - quantity: Quantity of the product in the order.
    - date_added: Date and time when the item was added to the order.
    """
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        """
        Property that returns the total cost of the item.
        """
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    """
    Model representing shipping addresses for orders.

    Fields:
    - customer: Foreign key to the Customer model, indicating the customer associated with the address.
    - order: Foreign key to the Order model, indicating the order to which the address belongs.
    - address: Street address for shipping.
    - city: City for shipping.
    - state: State for shipping.
    - zipcode: ZIP code for shipping.
    - date_added: Date and time when the address was added.
    """
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
