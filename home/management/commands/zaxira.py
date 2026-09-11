"""`python manage.py zaxira` — bazadan qo'lda zaxira nusxa oladi.

Misollar:
    python manage.py zaxira
    python manage.py zaxira --jild D:/zaxiralar
    python manage.py zaxira --royxat
"""

from django.core.management.base import BaseCommand, CommandError

from home import zaxira as zaxira_moduli


class Command(BaseCommand):
    help = "Ma'lumotlar bazasidan xavfsiz zaxira nusxa oladi (sayt ishlab turganda ham)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--jild', default=None,
            help="Nusxa saqlanadigan jild (standart: ma'lumot jildidagi zaxira/).",
        )
        parser.add_argument(
            '--royxat', action='store_true',
            help="Mavjud nusxalarni sanab chiqadi, yangisini olmaydi.",
        )

    def handle(self, *args, **sozlama):
        if sozlama['royxat']:
            jild = zaxira_moduli.ZAXIRA_JILDI
            nusxalar = sorted(jild.glob('db_*.sqlite3')) if jild.exists() else []
            if not nusxalar:
                self.stdout.write(self.style.WARNING('Hozircha zaxira nusxa yo\'q.'))
                return
            for n in nusxalar:
                self.stdout.write(f'  {n.name}   {n.stat().st_size / 1024:.0f} KB')
            self.stdout.write(self.style.SUCCESS(f'Jami {len(nusxalar)} ta nusxa: {jild}'))
            return

        try:
            nusxa = zaxira_moduli.zaxira_ol(jild=sozlama['jild'])
        except Exception as xato:
            raise CommandError(f'Zaxira olinmadi: {xato}')

        self.stdout.write(self.style.SUCCESS(
            f'Zaxira tayyor: {nusxa}  ({nusxa.stat().st_size / 1024:.0f} KB)'
        ))
