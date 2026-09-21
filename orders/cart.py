"""Session-based shopping cart."""

from decimal import Decimal

from products.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    """Small wrapper around the session dict {product_id: {"quantity": n}}."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    # -- mutations --------------------------------------------------------
    def add(self, product, quantity=1, override=False):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {"quantity": 0}
        if override:
            self.cart[pid]["quantity"] = quantity
        else:
            self.cart[pid]["quantity"] += quantity
        if self.cart[pid]["quantity"] < 1:
            self.remove(product)
        self.save()

    def remove(self, product):
        self.cart.pop(str(product.id), None)
        self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    # -- reading ----------------------------------------------------------
    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        for product in products:
            quantity = self.cart[str(product.id)]["quantity"]
            yield {
                "product": product,
                "quantity": quantity,
                "price": product.final_price,
                "subtotal": product.final_price * quantity,
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def total(self):
        return sum(
            (item["subtotal"] for item in self), Decimal("0.00")
        )

    @property
    def is_empty(self):
        return len(self) == 0
