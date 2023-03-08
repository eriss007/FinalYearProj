from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
import requests
from django.http import HttpResponseRedirect
from .models import *
from .forms import *
# from django.utils.translation import ugettextlazy as


class restroMixin(object):
    #assigning a customer to a cart obj
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = ShoppingCart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(restroMixin, TemplateView):
    template_name = "home.html"

    #returning context (sending data from backend to frontend) displaying food cards
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_foods = Food.objects.all().order_by("-id")
        paginator = Paginator(all_foods, 8)
        page_number = self.request.GET.get('page')
        food_list = paginator.get_page(page_number)
        context['food_list'] = food_list
        return context

class AllFoodView(restroMixin, TemplateView):
    template_name = "allfood.html"

    #returning context (sending data from backend to frontend) displaying food cards
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_foods = Food.objects.all().order_by("-id")
        paginator = Paginator(all_foods, 12)
        page_number = self.request.GET.get('page')
        food_list = paginator.get_page(page_number)
        context['food_list'] = food_list
        return context


class CategoriesView(restroMixin, TemplateView):
    template_name = "categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context


class FoodDetailView(restroMixin, TemplateView):
    template_name = "fooddetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Food.objects.get(slug=url_slug)
        # product.view_count += 1
        product.save()
        context['food'] = product
        return context


class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("restroapp:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("restroapp:home")


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("restroapp:home")

    # form_valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    #
    def get_success_url(self):
        #if the next url specified is found user will be redirected there
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        #eelse they will be redirected to success url defined above
        else:
            return self.success_url


class AboutView(restroMixin, TemplateView):
    template_name = "about.html"


class ContactView(restroMixin,TemplateView):
    template_name = "contactus.html"


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"
    #customer must be logged in to check this
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Food.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw) | Q(return_policy__icontains=kw) | Q(category__title__icontains=kw))
        context["results"] = results
        return context


class AddToCartView(restroMixin, TemplateView):
    template_name = "cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #getting id of the requested food url
        food_id = self.kwargs['food_id']
        #getting the food item
        food_obj = Food.objects.get(id=food_id)
        #cart exists or not
        cart_id= self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = ShoppingCart.objects.get(id=cart_id)
            this_item = cart_obj.cartproduct_set.filter(food=food_obj)
            #this works when the items already exist in cart
            if this_item.exists():
                cartproduct = this_item.first()
                cartproduct.quantity += 1
                cartproduct.subtotal += food_obj.selling_price
                cartproduct.save()
                cart_obj.total += food_obj.selling_price
                cart_obj.save()
            #this works when th item does not exist in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, food=food_obj, rate=food_obj.selling_price, quantity=1, subtotal=food_obj.selling_price )
                cart_obj.total += food_obj.selling_price
                cart_obj.save()
        #creates new cart
        else:
            cart_obj = ShoppingCart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, food=food_obj, rate=food_obj.selling_price, quantity=1, subtotal=food_obj.selling_price )
            cart_obj.total += food_obj.selling_price
            cart_obj.save()

        # return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        return context

    
class MyCartView(restroMixin, TemplateView):
        template_name="usercart.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            #checking if we already have card in current session/using cart id as session key/dictionary
            cart_id = self.request.session.get("cart_id", None)
            #condition for if it exists
            if cart_id:
                cart = ShoppingCart.objects.get(id=cart_id)
            else:
                cart = None
            context['cart'] = cart
            return context

class ManageCartView(restroMixin, View):
    def get(self, request, *args, **kwargs):
        #self.kwargs is used to use dynamic id
        cp_id = self.kwargs["cp_id"]
        #action is the button parameters achieved through get methods
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id = cp_id)
        cart_obj = cp_obj.cart

        #adding new item and its details to cart
        if action == "add":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        #subtracting existing item and its details to cart
        elif action == "sub":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        #deleting existting item and its details to cart
        elif action == "del":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("restroapp:usercart")

class EmptyCartView(restroMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = ShoppingCart.objects.get(id=cart_id)
            #This accesses all cart products from cart models
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("restroapp:usercart")

class CheckoutView(restroMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("restroapp:home")

    def dispatch(self, request, *args, **kwargs):
        #fetching currently logged in user
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    #to send cart info to checkout page to display items
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = ShoppingCart.objects.get(id=cart_id)
        else: 
            cart_obj = None
        context['cart'] = cart_obj
        return context
    #

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = ShoppingCart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
        else:
            return redirect("restroapp:home")
        return super().form_valid(form)

class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_obj_name = "ord_obj"

    #customer must be logged in to check this
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class AdminLoginView(FormView):
    template_name = "admin/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("restroapp:adminhome")