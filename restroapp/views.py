from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *
import requests


class restroMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = ShoppingCart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "home.html"

    #returning context (sending data from backend to frontend) displaying food cards
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_foods = Food.objects.all().order_by("-id")
        paginator = Paginator(all_foods, 4)
        page_number = self.request.GET.get('page')
        print(page_number)
        food_list = paginator.get_page(page_number)
        context['food_list'] = food_list
        return context

class AllFoodView(TemplateView):
    template_name = "allfood.html"

        #returning context (sending data from backend to frontend) displaying food cards
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_foods = Food.objects.all().order_by("-id")
        paginator = Paginator(all_foods, 12)
        page_number = self.request.GET.get('page')
        print(page_number)
        food_list = paginator.get_page(page_number)
        context['food_list'] = food_list
        return context


class CategoriesView(TemplateView):
    template_name = "categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context


class FoodDetailView(TemplateView):
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

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class AboutView(TemplateView):
    template_name = "about.html"


class ContactView(TemplateView):
    template_name = "contactus.html"


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

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
        print(results)
        context["results"] = results
        return context


class AddToCartView(TemplateView):
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

        return context

    
class MyCartView(TemplateView):
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