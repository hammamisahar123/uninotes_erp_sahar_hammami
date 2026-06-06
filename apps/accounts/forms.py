from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

# Classes Tailwind centralisées pour éviter la répétition dans chaque widget
INPUT_CLASSES = (
    'w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl text-sm '
    'focus:ring-2 focus:ring-purple-500/30 focus:border-purple-500 '
    'outline-none transition-all placeholder:text-slate-400'
)


class LoginForm(AuthenticationForm):
    """
    Formulaire de connexion basé sur AuthenticationForm de Django.
    Personnalise les messages d'erreur en français et le style des champs.
    """

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
            'placeholder': "Votre nom d'utilisateur",
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
    """
    Formulaire d'inscription étendu depuis UserCreationForm.
    Ajoute un champ 'role' qui appartient au modèle Profile (et non User).
    Le rôle est sauvegardé manuellement dans save().
    """

    # Champ extra : n'appartient pas au modèle User mais à Profile
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Rôle",
        widget=forms.Select(attrs={
            'class': (
                'w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-xl '
                'text-sm focus:ring-2 focus:ring-purple-500/30 focus:border-purple-500 '
                'outline-none transition-all bg-white appearance-none'
            ),
        })
    )

    class Meta:
        model = User
        # 'role' est déclaré explicitement sur le formulaire (champ extra),
        # pas sur le modèle User — Django l'accepte dans ce cas.
        fields = ('username', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personnalisation du champ username
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['username'].help_text = (
            "150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement."
        )
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': "Choisissez un nom d'utilisateur",
        })

        # Personnalisation du champ password1
        self.fields['password1'].label = "Mot de passe"
        self.fields['password1'].help_text = (
            "Minimum 8 caractères. Ne peut pas être un mot de passe "
            "courant ou entièrement numérique."
        )
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Créez un mot de passe',
        })

        # Personnalisation du champ password2
        self.fields['password2'].label = "Confirmation du mot de passe"
        self.fields['password2'].help_text = (
            "Saisissez le même mot de passe pour vérification."
        )
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Confirmez le mot de passe',
        })

    def save(self, commit=True):
        # On crée l'objet User sans le sauvegarder en base pour l'instant
        user = super().save(commit=False)
        role = self.cleaned_data['role']

        if commit:
            # user.save() déclenche le signal post_save → Profile créé automatiquement
            user.save()

            # get_or_create garantit qu'on récupère ou crée le profil
            # même si le signal post_save était absent ou désactivé.
            # Évite le bug silencieux de filter().update() qui ne lève
            # aucune erreur si le profil n'existe pas.
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

        return user