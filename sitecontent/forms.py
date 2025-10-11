from django import forms
from django.core.mail import EmailMessage
import csv, io


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=40, required=False)
    subject = forms.CharField(max_length=160)
    message = forms.CharField(widget=forms.Textarea)

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
