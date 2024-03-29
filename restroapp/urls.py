from django.urls import path
from .views import *
from django.conf.urls import include
from . import views


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

    path('update/<int:pk>/', FoodUpdateView.as_view(), name="update"),
    path('food-create/', FoodCreateView.as_view(), name="food-create"),
    path('food-delete/<int:pk>/', FoodDeleteView.as_view(), name="food-delete"),
    path('admin-foodlist/', FoodListView.as_view(), name="foodlist"),
    path('admin-ingredientlist/', IngredientListView.as_view(), name="ingredientlist"),
    path('ingredient-update/<int:pk>/', IngredientUpdateView.as_view(), name="ingredientupdate"),
    path('ingredient-create/', IngredientCreateView.as_view(), name="ingredient-create"),
    path('ingredient-delete/<int:pk>/', IngredientDeleteView.as_view(), name="ingredient-delete"),



    path("profile/order-<int:id>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),

    path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),
    # path("admin-add/", AdminAddView.as_view(), name="adminadd"),
    path("admin-home/", AdminHomeView.as_view(), name="adminhome"),
    path("admin-order/<int:pk>/", AdminOrderdetailView.as_view(), name="adminorderdetail"),
    path("admin-all-orders/", AdminOrderListView.as_view(), name="adminorderlist"),
    path("admin-order-<int:pk>-change/", AdminStatusChangeView.as_view(), name="adminorderstatuschange"),


]
