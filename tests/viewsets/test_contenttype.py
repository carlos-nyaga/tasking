# -*- coding: utf-8 -*-
"""
Tests ContentType viewsets.
"""
from __future__ import unicode_literals

from collections import OrderedDict
from model_mommy import mommy
from rest_framework.test import APIRequestFactory, force_authenticate
from tests.base import TestBase

from tasking.viewsets import ContentTypeViewSet


class TestContentTypeViewSet(TestBase):
    """
    Test LocationViewSet class.
    """

    def setUp(self):
        super(TestContentTypeViewSet, self).setUp()
        self.factory = APIRequestFactory()

    def test_list_contenttype(self):
        """
        Test that we can get the list of allowed content types
        """
        user = mommy.make('auth.User')
        view = ContentTypeViewSet.as_view({'get': 'list'})

        expected_data = [
            OrderedDict([('name', 'group')]),
            OrderedDict([('name', 'location')]),
            OrderedDict([('name', 'project')]),
            OrderedDict([('name', 'segment rule')]),
            OrderedDict([('name', 'submission')]),
            OrderedDict([('name', 'task')]),
            OrderedDict([('name', 'user')])
        ]

        request = self.factory.get('/contenttypes')
        force_authenticate(request, user=user)
        response = view(request=request)

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            expected_data, response.data)
