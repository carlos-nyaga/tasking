# -*- coding: utf-8 -*-
"""
Test for Task model
"""
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import six

from model_mommy import mommy


class TestTasks(TestCase):
    """
    Test class for task models
    """

    def test_task_model_str(self):
        """
        Test the str method on Task model
        """
        cow_price = mommy.make('tasking.Task', name="Cow prices")
        expected = 'Cow prices - {}'.format(cow_price.pk)
        self.assertEqual(expected, cow_price.__str__())

    def test_location_link(self):
        """
        Test the connection of Task and Location
        """
        nairobi = mommy.make('tasking.Location', name="Nairobi", country="KE")
        rice_harvest = mommy.make(
            'tasking.Task',
            name="Rice harvest",
            location=nairobi)
        self.assertEqual(
            nairobi.__str__(),
            rice_harvest.location.__str__())
