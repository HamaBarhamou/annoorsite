# sitecontent/forms.py
from django import forms
from django.core.mail import EmailMessage
import csv, io

BASE_INPUT_CLASS = (
    "w-full rounded-lg border-slate-300 focus:border-orange-500 focus:ring-orange-500"
)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={"class": BASE_INPUT_CLASS, "placeholder": "Votre nom"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": BASE_INPUT_CLASS, "placeholder": "vous@exemple.com"}
        )
    )
    phone = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={"class": BASE_INPUT_CLASS, "placeholder": "+227 …"}
        ),
    )
    subject = forms.CharField(
        max_length=160,
        widget=forms.TextInput(
            attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Demande de devis / Assistance / Autre",
            }
        ),
    )
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "class": BASE_INPUT_CLASS + " min-h-36",
                "rows": "6",
                "placeholder": "Décrivez brièvement votre besoin, le contexte et les délais.",
            }
        ),
    )
    hp = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot

    def clean_hp(self):
        if self.cleaned_data.get("hp"):
            raise forms.ValidationError("Bot detected.")
        return ""

    def send_email(self):
        body = (
            f"From: {self.cleaned_data['name']} <{self.cleaned_data['email']}>\n"
            f"Phone: {self.cleaned_data.get('phone','')}\n\n"
            f"{self.cleaned_data['message']}"
        )
        EmailMessage(
            subject=self.cleaned_data["subject"],
            body=body,
            to=["contact@annoor.example"],
        ).send(fail_silently=True)

    def to_csv_bytes(self):
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["name", "email", "phone", "subject", "message"])
        cd = self.cleaned_data
        writer.writerow(
            [cd["name"], cd["email"], cd.get("phone", ""), cd["subject"], cd["message"]]
        )
        return buf.getvalue().encode()
