from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

INPUT_CLASSES = (
    'w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl text-sm '
    'focus:ring-2 focus:ring-purple-500/30 focus:border-purple-500 '
    'outline-none transition-all placeholder:text-slate-400'
)


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Nom d'utilisateur ou mot de passe incorrect. "
            "Vérifiez votre saisie (respect de la casse)."
        ),
        'inactive': "Ce compte est désactivé.",
    }

    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Votre nom d\'utilisateur',
            'required': True,
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Votre mot de passe',
            'required': True,
        })
    )


class SignupForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Rôle",
        widget=forms.Select(attrs={
            'class': 'w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-purple-500/30 focus:border-purple-500 outline-none transition-all bg-white appearance-none',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['username'].help_text = "150 caractères maximum. Lettres, chiffres et @/. /+/-/_ uniquement."
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': "Choisissez un nom d'utilisateur",
        })

        self.fields['password1'].label = "Mot de passe"
        self.fields['password1'].help_text = (
            "Minimum 8 caractères. Ne peut pas être un mot de passe "
            "courant ou entièrement numérique."
        )
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Créez un mot de passe',
        })

        self.fields['password2'].label = "Confirmation du mot de passe"
        self.fields['password2'].help_text = "Saisissez le même mot de passe pour vérification."
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Confirmez le mot de passe',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        if commit:
            user.save()
            Profile.objects.filter(user=user).update(role=role)
        return user
