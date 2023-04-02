from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
import requests
from django.contrib import messages, auth
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
        context['reviews'] = ReviewRating.objects.all()
        return context

    def Review_rate(request):
        if request.method == "GET":
            food_id = request.GET.get('food_id')
            food = Food.objects.get(id=food_id)
            comment = request.GET.get('comment')
            rate = request.GET.get('rate')
            user = request.user
            Review(user=user, food=food, comment=comment, rate=rate).save()
            return redirect('food_detail', id=food_id)
    
    def post(self, request, slug):
        url = request.META.get('HTTP_REFERER')
        if request.method == "POST":
            try:
                food = Food.objects.get(slug=slug)
                # reviews = ReviewRating.objects.get(customer_id=request.user.customer.id, food__id=food.id)
                reviews = ReviewRating.objects.get(customer__id=request.user.customer.id, food__id=food.id)
                
                form = ReviewForm(request.POST, instance=reviews)
                form.save()
                messages.success(request, 'Your review has been updated.')

            except ReviewRating.DoesNotExist:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    data = ReviewRating()
                    data.subject = form.cleaned_data['subject']
                    data.rating = form.cleaned_data['rating']
                    data.review = form.cleaned_data['review']
                    food = Food.objects.get(slug=slug)
                    data.food_id = food.id
                    data.customer_id = request.user.customer.id
                    data.save()
                    messages.success(request, 'Your review has been submitted')
            return redirect(url)

# def submit_review(request, food_id):
#     url = request.META.get('HTTP_REFERER')
#     if request.method == 'POST':
#         try:
#             reviews = ReviewRating.objects.get(user__id=request.user.id, food__id=food_id)
#             # if instance is not passed new review will be created instead of update
#             form = ReviewForms(request.POST, instance=reviews)
#             form.save()
#             messages.success(request, 'Thank You! Your review has been updated.')
#             return redirect(url)
#         except ReviewRating.DoesNotExist:
#             form = ReviewForms(request.POST)
#             if form.is_valid():
#                 data = ReviewRating()
#                 data.subject = form.cleaned_data['subject']
#                 data.rating = form.cleaned_data['rating']
#                 data.review = form.cleaned_data['review']
#                 data.food_id = food_id
#                 data.user_id = request.user.id
#                 data.save()
#                 messages.success(request, 'Thank You! Your review has been submitted.')
#                 return redirect(url)


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

    # form_valid method is a type of post method + available in createview formview and updateview
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
        #since usr is not a variable you need to request it
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
            data = {"return_url": "http://127.0.0.1:8000/",
                "website_url": "https://example.com/",
                "amount": 1300,
                "purchase_order_id": "test12",
                "purchase_order_name": "test",
                }
            # replace the key with your live secret key
            headers = {"Authorization": "Key f2bbc1b8c9a34b2bad4ab22542723b25"

                    }
            response = requests.post("https://a.khalti.com/api/v2/epayment/initiate/", json=data, headers=headers)
            print(response, response.text)
            data = response.json()
            if response.status_code == 200:

                return HttpResponseRedirect(data.get("payment_url"))
            cart_obj = ShoppingCart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            print('Deleting cart ID from session2...')
            del self.request.session['cart_id']
            print('Deleting cart ID from session...')
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Khalti":
                # data = {"return_url": "http://127.0.0.1:8000/",
                #     "website_url": "https://example.com/",
                #     "amount": 1300,
                #     "purchase_order_id": "test12",
                #     "purchase_order_name": "test",
                #     }
                # # replace the key with your live secret key
                # headers = {"Authorization": "Key f2bbc1b8c9a34b2bad4ab22542723b25"

                #         }
                # response = requests.post("https://a.khalti.com/api/v2/epayment/initiate/", json=data, headers=headers)
                # print(response, response.text)
                # data = response.json()
                # if response.status_code == 200:
                pass
                #     return HttpResponseRedirect(data.get("payment_url"))
            elif pm == "Esewa":
                return redirect(reverse("restroapp:esewarequest") + "?o_id=" + str(order.id))

        else:
            return redirect("restroapp:home")
        return super().form_valid(form)

class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_obj_name = "ord_obj"

    #customer must be logged in to check this
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class AdminLoginView(FormView):
    template_name = "admin/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("restroapp:adminhome")

    def form_valid(self, form):
        #fetching uname and pwword of admin 
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

#making sure only admin can view the page
class AdminRequiredMixin(object):
    #restricting customers from viewing this page (or not logged in admins)
    #trying to access the admin page while logged in as a user will take them to admin login page
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)

class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "admin/adminhome.html"

    #sending data to html page
    def get_context_data(self, **kwargs):
        context = super().get_context_data(*kwargs)
        context["pendingorders"] = Order.objects.filter(order_status = "Order Received").order_by("-id")
        orders = Order.objects.all()
        customer = Customer.objects.all()
        total_customer = customer.count()
        total_order = orders.count()
        context["total_order"] = total_order
        delivered = orders.filter(order_status="Order Completed").count()
        pending = orders.filter(order_status="Order Received").count()
        context["delivered"] = delivered
        context["pending"] = pending
        return context

class AdminOrderdetailView(AdminRequiredMixin, DetailView):
    template_name = "admin/adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context

class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "admin/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"

class AdminStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        #getting new status data from fe to be
        new_status = request.POST.get("status")
        #changing value from old to new
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("restroapp:adminorderdetail", kwargs={"pk": order_id}))


      
      



                

 
        