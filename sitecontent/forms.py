# sitecontent/forms.py
from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
import csv, io
import logging

logger = logging.getLogger(__name__)
# 👇 Ajout des classes manquantes pour bordures visibles + confort + focus net
BASE_INPUT_CLASS = (
    "w-full border border-slate-300 rounded-lg px-3 py-2 text-[15px] "
    "placeholder-slate-400 focus:outline-none focus:border-orange-500 "
    "focus:ring-2 focus:ring-orange-500/40"
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

    # Anti-bot
    hp = forms.CharField(required=False, widget=forms.HiddenInput)

    # Option : recevoir une copie par email (avec CSV en PJ)
    # 👇 On garde la logique, on ajoute juste une classe visuelle
    send_copy_csv = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={"class": "h-4 w-4 accent-orange-600 align-middle"}
        ),
    )

    def clean_hp(self):
        if self.cleaned_data.get("hp"):
            raise forms.ValidationError("Bot detected.")
        return ""

    # --- Utilitaires ---

    def _csv_bytes(self) -> bytes:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["name", "email", "phone", "subject", "message"])
        cd = self.cleaned_data
        w.writerow(
            [cd["name"], cd["email"], cd.get("phone", ""), cd["subject"], cd["message"]]
        )
        return buf.getvalue().encode("utf-8")

    def _compose_internal_body(
        self, requester_ip: str = "", user_agent: str = ""
    ) -> str:
        cd = self.cleaned_data
        lines = [
            f"From: {cd['name']} <{cd['email']}>",
            f"Phone: {cd.get('phone','')}".rstrip(),
        ]
        if requester_ip:
            lines.append(f"IP: {requester_ip}")
        if user_agent:
            lines.append(f"UA: {user_agent}")
        lines.append("")  # blank
        lines.append(cd["message"])
        return "\n".join(lines)

    # --- Envoi principal + (option) copie à l’expéditeur ---

    def send_email(self, *, requester_ip: str = "", user_agent: str = "") -> bool:
        """
        Envoie 1) un mail interne à contact@annoor.tech
               2) si send_copy_csv=True : une copie à l’expéditeur, CSV en pièce jointe
        Retourne True si l’envoi interne a été tenté (pas forcément délivré).
        """
        cd = self.cleaned_data
        subject = cd["subject"].strip() or "Contact site"

        # 1) Interne -> boîte ANNOOR
        body_internal = self._compose_internal_body(
            requester_ip=requester_ip, user_agent=user_agent
        )
        from_email = settings.EMAIL_HOST_USER
        to_list = [getattr(settings, "CONTACT_INBOX", settings.EMAIL_HOST_USER)]

        msg_internal = EmailMessage(
            subject=subject,
            body=body_internal,
            from_email=from_email,
            to=to_list,
            reply_to=[f"{cd['name']} <{cd['email']}>"],
        )

        try:
            msg_internal.send(fail_silently=False)
        except Exception as e:
            # On laisse la vue gérer l’erreur via messages.error
            logger.exception("SMTP internal send failed: %s", getattr(e, "args", e))
            return False

        # 2) Copie à l’expéditeur (optionnelle)
        if cd.get("send_copy_csv"):
            body_copy = (
                "Bonjour,\n\n"
                "Voici une copie du message que vous avez envoyé via notre formulaire de contact.\n\n"
                f"Objet : {subject}\n"
                f"Nom : {cd['name']}\n"
                f"Email : {cd['email']}\n"
                f"Téléphone : {cd.get('phone','')}\n\n"
                "Message :\n"
                f"{cd['message']}\n\n"
                "— ANNOOR"
            )
            msg_copy = EmailMessage(
                subject=f"[Copie] {subject}",
                body=body_copy,
                from_email=from_email,
                to=[cd["email"]],
            )
            # joindre le CSV
            msg_copy.attach(
                filename="contact.csv",
                content=self._csv_bytes(),
                mimetype="text/csv",
            )
            try:
                msg_copy.send(fail_silently=True)
            except Exception:
                pass

        return True
