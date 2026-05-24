import json
from notes.models import Note
from catalogue.models import CategorieEvaluation
from inscription.models import ModuleChoisi


class NoteService:
    """Service métier pour la saisie et le calcul des notes."""

    def __init__(self, module_choisi):
        self.module_choisi = module_choisi
        self.categories = CategorieEvaluation.objects.filter(module=module_choisi.module_catalogue)

    def notes_existantes(self):
        return Note.objects.filter(module_choisi=self.module_choisi).en_dict_par_categorie()

    def est_complet(self):
        nb_notes = Note.objects.filter(module_choisi=self.module_choisi).count()
        return nb_notes == len(self.categories) and len(self.categories) > 0

    def moyenne_module(self):
        if not self.est_complet():
            return None
        total = Note.objects.filter(module_choisi=self.module_choisi).total_pondere()
        return total / 100.0

    def est_modification(self):
        return Note.objects.filter(module_choisi=self.module_choisi).exists()

    def sauvegarder_notes(self, post_data):
        messages_notes = []
        notes_actuelles = {
            n.categorie_evaluation_id: float(n.valeur) if n.valeur is not None else None
            for n in Note.objects.filter(module_choisi=self.module_choisi)
        }
        for cat in self.categories:
            key = f"note_{cat.id}"
            if key in post_data and post_data[key].strip() != '':
                valeur = float(post_data[key])
                if valeur < 0 or valeur > 20:
                    messages_notes.append(("error", "La note saisie doit être comprise entre 0 et 20."))
                    continue
                if cat.id in notes_actuelles:
                    if notes_actuelles[cat.id] == valeur:
                        messages_notes.append((
                            "error",
                            f"Une note a déjà été saisie pour la catégorie {cat.nom} "
                            f"du module {self.module_choisi.module_catalogue.intitule}."
                        ))
                        continue
                    Note.objects.update_or_create(
                        module_choisi=self.module_choisi, categorie_evaluation=cat,
                        defaults={'valeur': valeur}
                    )
                    messages_notes.append(("success", f"Note modifiée pour {cat.nom}."))
                else:
                    Note.objects.create(
                        module_choisi=self.module_choisi, categorie_evaluation=cat,
                        valeur=valeur
                    )
                    messages_notes.append(("success", f"Note enregistrée pour {cat.nom}."))
        return messages_notes


class CourbeService:
    """Service métier pour la courbe d'évolution."""

    def __init__(self, etudiant):
        self.etudiant = etudiant

    def get_all_notes(self):
        return Note.objects.filter(
            module_choisi__inscription__etudiant=self.etudiant
        ).order_by('date_saisie')

    def get_data(self):
        notes = self.get_all_notes()
        if not notes.exists():
            return {'etudiant': self.etudiant, 'dates': '[]', 'valeurs': '[]'}

        dates, valeurs = [], []
        for i in range(len(notes)):
            subset_ids = [n.id for n in notes[:i + 1]]
            moyenne = ModuleChoisi.objects.filter(
                inscription__etudiant=self.etudiant
            ).moyenne_ponderee_a_la_date(subset_ids)
            dates.append(notes[i].date_saisie.strftime('%d/%m %H:%M'))
            valeurs.append(round(moyenne, 2))

        return {
            'etudiant': self.etudiant,
            'dates': json.dumps(dates),
            'valeurs': json.dumps(valeurs),
        }
