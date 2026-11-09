import re
from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("shipping_name", "shipping_address", "shipping_city", "shipping_pincode", "shipping_phone", "payment_method")
        widgets = {
            "shipping_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "shipping_address": forms.TextInput(attrs={"autocomplete": "street-address"}),
            "shipping_city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "shipping_pincode": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "postal-code"}),
            "shipping_phone": forms.TelInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
        }

    def clean_shipping_pincode(self):
        value = self.cleaned_data["shipping_pincode"].strip()
        if not re.fullmatch(r"[0-9]{4,10}", value):
            raise forms.ValidationError("Enter a valid postal code (4–10 digits).")
        return value

    def clean_shipping_phone(self):
        value = self.cleaned_data["shipping_phone"].strip()
        if not re.fullmatch(r"\+?[0-9 ()-]{7,20}", value):
            raise forms.ValidationError("Enter a valid phone number.")
        return value
