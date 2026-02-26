from django.urls import path
from .views import initiate_checkout, verify_payment


urlpatterns = [
    path("checkout/pay/", initiate_checkout, name="initiate_checkout"),
    path("payment/verify/<str:ref>/", verify_payment, name="verify_payment"),
]
