from django import forms
from .models import Order, Customer, Food, ReviewRating, Ingredients
from django.contrib.auth.models import User

#creating orders obj to save it to db 
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address",
                  "mobile", "email", "payment_method"]
        widgets = {
            "ordered_by": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your Name...",
                "style": "width:400px; " ,
                "class": "form-control",
            }),
            "shipping_address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your Address...",
                "style": "width:400px",
                "class": "form-control",
            }),
            "mobile": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your Number...",
                "style": "width:400px",
                "class": "form-control",
            }),
            "email": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your Email...",
                "style": "width:400px",
                "class": "form-control",
            }),
            "payment_method": forms.Select(attrs={
                "class": "selectpicker form-control",
                "data-live-search": "true",
                "style": "width:400px",
                
            }),
        }


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Your Name', 'style': 'width:300px', 'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'style': 'width:300px', 'class':'form-control'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Enter Your Email', 'style': 'width:300px', 'class':'form-control'}))

    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]
        widgets = {
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your address here...",
                "style": "width:300px; " ,
                "class": "form-control",
            }),
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your full name...",
                "style": "width:300px",
                "class": "form-control",
            }),
        }

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError(
                "Customer with this username already exists.")

        return uname


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Your Name', 'style': 'width:300px', 'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'style': 'width:300px', 'class':'form-control'}))


class FoodForm(forms.ModelForm):
    more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={
        "class": "form-control",
        "multiple": True
    }))

    class Meta:
        model = Food
        fields = ["title", "slug", "category", "image",
                  "selling_price", "description", "return_policy"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the food title here..."
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the unique slug here..."
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling price of the food..."
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description of the food...",
                "rows": 5
            }),
            "return_policy": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the food return policy here..."
            }),

        }

class IngredientUpdateForm(forms.ModelForm):
    class Meta:
        model = Ingredients
        fields = ["title", "slug", 
                  "cost_price", "stock_level"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the food title here..."
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the unique slug here..."
            }),
            "cost_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling price of the food..."
            }),
            "stock_level": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling the amount..."
            }),
        }
        
class FoodUpdateForm(forms.ModelForm):

    class Meta:
        model = Food
        fields = ["title", "slug", "category", "image",
                  "selling_price", "description", "return_policy"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the food title here..."
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the unique slug here..."
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling price of the food..."
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description of the food...",
                "rows": 5
            }),
            "return_policy": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the food return policy here..."
            }),

        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']

