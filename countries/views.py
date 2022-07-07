import hashlib
import time
from functools import wraps

import pandas as pd
from django.http import HttpResponse
from glom import glom
from rest_framework import generics
from sqlalchemy import create_engine

from .models import Countries
from .resources import CountriesResource
from .serializers import CountriesSerializer


def encrypt(string):
    return hashlib.sha1(string).hexdigest()


# Imprimir cuanto tiempo tardo el proceso.
def timer(func):
    """helper function to estimate view execution time"""

    @wraps(func)  # used for copying func metadata
    def wrapper(*args, **kwargs):
        # record start time
        start = time.time()

        # func execution
        result = func(*args, **kwargs)

        duration = (time.time() - start) * 1000
        # output execution time to console
        print('view {} takes {:.2f} ms'.format(
            func.__name__,
            duration
        ))
        return result

    return wrapper


@timer
def countries(request):
    # De https://restcountries.com/ obtén todos los países de América del Sur.
    url = 'https://restcountries.com/v3.1/subregion/South%20America'
    info = pd.read_json(url)

    # Se desglosa el lenguaje por comas y se convierte en un dict
    languages = []
    for lan in info['languages']:
        str1 = ", "
        languages.append(str1.join(list(lan.values())))
    fix_languages = {
        'languages': languages
    }

    # Se obtiene el nombre completo de cada pais para encriptarlo y guardarlo en un dict
    name_sha1 = []
    for name in info['name'].apply(lambda row: glom(row, 'official')):
        name_sha1.append(encrypt(name.encode('utf-8')))
    fix_sha1 = {
        'SHA1': name_sha1
    }

    # Usando pandas hacer una DataFrame con los datos: Nombre, lenguajes(separados por comas), y población.
    name = pd.DataFrame(info['name'].apply(lambda row: glom(row, 'official')))
    languages = pd.DataFrame(fix_languages)
    population = pd.DataFrame(info['population'])
    pd.concat([name, languages, population], axis=1, join="inner")

    # Agregar al DataFrame una columna adicional con el nombre del país encriptado con SHA1.
    sha1 = pd.DataFrame(fix_sha1)
    table_2 = pd.concat([name, languages, population, sha1], axis=1, join="inner")

    # Guardar la información en una BD SQLite.
    engine = create_engine('sqlite:///db.sqlite3')
    table_2.to_sql(name='countries', con=engine, if_exists='replace')

    # Obtener todos los datos de la BD y exportarlos a un archivo.json ordenados por población.
    # El modelo ordenado se obtiene de el archivo resources.py
    countries_resource = CountriesResource()
    dataset = countries_resource.export()
    response = HttpResponse(dataset.json, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="countries.json"'
    return response


# Api opcional para mandar en formato json los paises ordenados por poblacion
class CountriesView(generics.ListAPIView):
    queryset = Countries.objects.order_by('population')
    serializer_class = CountriesSerializer
