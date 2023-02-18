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


class HomeView(restroMixin, TemplateView):
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

class AllFoodView(restroMixin, TemplateView):
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

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class AboutView(restroMixin, TemplateView):
    template_name = "about.html"


class ContactView(restroMixin, TemplateView):
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



# admin pages


# class AdminLoginView(FormView):
#     template_name = "adminpages/adminlogin.html"
#     form_class = CustomerLoginForm
#     success_url = reverse_lazy("restroapp:adminhome")

#     def form_valid(self, form):
#         uname = form.cleaned_data.get("username")
#         pword = form.cleaned_data["password"]
#         usr = authenticate(username=uname, password=pword)
#         if usr is not None and Admin.objects.filter(user=usr).exists():
#             login(self.request, usr)
#         else:
#             return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
#         return super().form_valid(form)


# class AdminRequiredMixin(object):
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
#             pass
#         else:
#             return redirect("/admin-login/")
#         return super().dispatch(request, *args, **kwargs)


# class AdminHomeView(AdminRequiredMixin, TemplateView):
#     template_name = "adminpages/adminhome.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["pendingorders"] = Order.objects.filter(
#             order_status="Order Received").order_by("-id")
#         return context


# class AdminOrderDetailView(AdminRequiredMixin, DetailView):
#     template_name = "adminpages/adminorderdetail.html"
#     model = Order
#     context_object_name = "ord_obj"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["allstatus"] = ORDER_STATUS
#         return context


# class AdminOrderListView(AdminRequiredMixin, ListView):
#     template_name = "adminpages/adminorderlist.html"
#     queryset = Order.objects.all().order_by("-id")
#     context_object_name = "allorders"


# class AdminOrderStatuChangeView(AdminRequiredMixin, View):
#     def post(self, request, *args, **kwargs):
#         order_id = self.kwargs["pk"]
#         order_obj = Order.objects.get(id=order_id)
#         new_status = request.POST.get("status")
#         order_obj.order_status = new_status
#         order_obj.save()
#         return redirect(reverse_lazy("restroapp:adminorderdetail", kwargs={"pk": order_id}))


# class AdminProductListView(AdminRequiredMixin, ListView):
#     template_name = "adminpages/adminproductlist.html"
#     queryset = Food.objects.all().order_by("-id")
#     context_object_name = "allproducts"


# class AdminProductCreateView(AdminRequiredMixin, CreateView):
#     template_name = "adminpages/adminproductcreate.html"
#     form_class = FoodForm
#     success_url = reverse_lazy("restroapp:adminproductlist")

#     def form_valid(self, form):
#         p = form.save()
#         images = self.request.FILES.getlist("more_images")
#         for i in images:
#             FoodImage.objects.create(product=p, image=i)
#         return super().form_valid(form)
