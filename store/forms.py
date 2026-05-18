from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Order, Product, Category

User = get_user_model()


# ====================== Auth Forms ======================
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500'
    }))
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500'
    }))

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500'
            })


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email or Username", widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500'
    }))


# ====================== Checkout Form ======================
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'country',
            'payment_method', 'notes'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'state': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'zip_code': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'}),
            'payment_method': forms.RadioSelect(attrs={'class': 'focus:ring-green-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget.attrs.update({
            'class': 'focus:ring-green-500'
        })


# ====================== Admin Forms (Optional) ======================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['created_at', 'updated_at']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']


# ====================== Utility Forms ======================
class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-16 text-center border border-gray-300 rounded-xl'
        })
    )
    