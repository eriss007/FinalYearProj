from django.urls import path
from .views import *


app_name = "restroapp"
urlpatterns = [

    # Client side pages
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("allfood/", AllFoodView.as_view(), name="allfood"),
    path("categories/", CategoriesView.as_view(), name="categories"),
    path("product/<slug:slug>/", FoodDetailView.as_view(), name="fooddetail"),

    path("add-to-cart-<int:food_id>/", AddToCartView.as_view(), name="addtocart"),

    path("register/",
         CustomerRegistrationView.as_view(), name="customerregistration"),

    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),

    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),

    path("search/", SearchView.as_view(), name="search"),

    path("my-cart/", MyCartView.as_view(), name="usercart"),
    path("manage-cart/<int:cp_id>", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),

    path("checkout/", CheckoutView.as_view(), name="checkout"),

    path("profile/order-<int:pk>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),

        path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),

]
