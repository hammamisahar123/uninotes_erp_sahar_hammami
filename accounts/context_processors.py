from datetime import date


def annee_courante():
    today = date.today()
    if today.month >= 9:
        return f"{today.year}/{today.year + 1}"
    return f"{today.year - 1}/{today.year}"


def academic_year(request):
    return {'ANNEE_ACADEMIQUE': annee_courante()}
