# Se hacen test unitarios.

import os
import time
from datetime import datetime

import pandas as pd
import requests
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from glom import glom
from rest_framework import status
from termcolor import colored

from countries.models import Countries
from countries.views import encrypt

os.system('color')
timeout = 2
URL = "https://restcountries.com/v3.1/subregion/South%20America"

faker = Faker()
column_names_first_dataframe = ["name", "languages", "population"]
column_names_second_dataframe = ["name", "languages", "population", "SHA1"]


def isConnected(URL):
    now = datetime.now()
    op = requests.get(URL, timeout=timeout).status_code
    sleep_time = 0
    try:
        if op == 200:
            print(now, colored("Connected", "green"))
            sleep_time = 10
        else:
            print(now, colored("Status Code is not 200", "red"))
            print("status Code", op)
    except:
        print(now, colored("Not Connected", "red"))
        print("status Code", op)
        sleep_time = 5
    time.sleep(sleep_time)


class CountriesTest(TestCase):
    isConnected(URL)

    @classmethod
    def setUpTestData(cls):
        CountriesFactory().create_country()

    def test_population_is_a_number(self):
        country_population = Countries.objects.all().first()
        try:
            expected_number = int(country_population.population)
            print("Is a Number", expected_number)
        except ValueError:
            raise Exception("Is not a number")

    def test_api_response(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-countries')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_readUrl(self):
        try:
            info = pd.read_json(URL)
            return info
        except IOError as e:
            print(e)

    def test_setUpFirstDataFrame(self):
        try:
            info = self.test_readUrl()
            languages = []
            for lan in info['languages']:
                str1 = ", "
                languages.append(str1.join(list(lan.values())))
            fix_languages = {
                'languages': languages
            }

            name = pd.DataFrame(info['name'].apply(lambda row: glom(row, 'official')))
            languages = pd.DataFrame(fix_languages)
            population = pd.DataFrame(info['population'])
            data = pd.concat([name, languages, population], axis=1, join="inner")
            return data
        except IOError as e:
            print(e)

    def test_setUpSecondDataFrame(self):
        try:
            info = self.test_readUrl()
            languages = []
            for lan in info['languages']:
                str1 = ", "
                languages.append(str1.join(list(lan.values())))
            fix_languages = {
                'languages': languages
            }

            name_sha1 = []
            for name in info['name'].apply(lambda row: glom(row, 'official')):
                name_sha1.append(encrypt(name.encode('utf-8')))
            fix_sha1 = {
                'SHA1': name_sha1
            }

            name = pd.DataFrame(info['name'].apply(lambda row: glom(row, 'official')))
            languages = pd.DataFrame(fix_languages)
            population = pd.DataFrame(info['population'])
            sha1 = pd.DataFrame(fix_sha1)
            data = pd.concat([name, languages, population, sha1], axis=1, join="inner")
            return data
        except IOError as e:
            print(e)

    def test_ColumnNames(self):
        self.assertListEqual(list(self.test_setUpFirstDataFrame().columns), column_names_first_dataframe)
        self.assertListEqual(list(self.test_setUpSecondDataFrame().columns), column_names_second_dataframe)


class CountriesFactory:

    def build_country_JSON(self):
        return {
            'index': str(faker.random_number(digits=2)),
            'name': faker.country(),
            'languages': faker.texts(),
            'population': str(faker.random_number(digits=11)),
            'sha1': faker.sha1()
        }

    def create_country(self):
        return Countries.objects.create(**self.build_country_JSON())
