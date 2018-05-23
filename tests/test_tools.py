# -*- coding: utf-8 -*-
"""
Tests for tasking tools
"""
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from datetime import time

from model_mommy import mommy

from tasking.tools import (MAX_OCCURRENCES, generate_task_occurrences,
                           get_allowed_contenttypes)


class TestTools(TestCase):
    """
    Test class for tasking tools
    """

    def test_get_allowed_contenttypes(self):
        """
        Test get_allowed_contenttypes
        """
        input_expected = [
            {'app_label': 'tasking', 'model': 'task'},
            {'app_label': 'tasking', 'model': 'segmentrule'}]

        task_type = ContentType.objects.get(app_label='tasking', model='task')
        rule_type = ContentType.objects.get(app_label='tasking',
                                            model='segmentrule')

        allowed = get_allowed_contenttypes(
            allowed_content_types=input_expected)

        self.assertEqual(2, allowed.count())
        self.assertIn(task_type, allowed)
        self.assertIn(rule_type, allowed)

    def test_generate_task_occurrences(self):
        """
        Test generate_task_occurrences works correctly
        """
        task1 = mommy.make(
            'tasking.Task',
            timing_rule='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5'
        )
        task2 = mommy.make(
            'tasking.Task',
            timing_rule='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5000'
        )

        # we should get 5 occurrences
        occurrences1 = generate_task_occurrences(task1)
        self.assertEqual(5, occurrences1.count())

        # we should get {MAX_OCCURRENCES} occurrences
        occurrences2 = generate_task_occurrences(task2)
        self.assertEqual(MAX_OCCURRENCES, occurrences2.count())

        # the start times should all be from the timing_rule, whic in this
        # case is the time the task was created
        # the end_times should all be 23:59:59
        for item in occurrences1:
            self.assertEqual(
                item.start_time.hour,
                task1.start.astimezone(
                    timezone.get_current_timezone()).time().hour)
            self.assertEqual(
                item.start_time.minute,
                task1.start.astimezone(
                    timezone.get_current_timezone()).time().minute)
            self.assertEqual(
                item.start_time.second,
                task1.start.astimezone(
                    timezone.get_current_timezone()).time().second)
            self.assertEqual(item.end_time, time(23, 59, 59, 999999))

        # pylint: disable=line-too-long
        rule1 = 'DTSTART:20180501T070000Z RRULE:FREQ=YEARLY;BYDAY=SU;BYSETPOS=1;BYMONTH=1;UNTIL=20480521T210000Z'  # noqa
        task3 = mommy.make('tasking.Task', timing_rule=rule1)
        occurrences3 = generate_task_occurrences(task3)

        # we should have 30 occurrences
        self.assertEqual(30, occurrences3.count())

        # the start times should all be from the timing_rule, whicih in this
        # case 7am
        # the end_times should all be 23:59:59 apart from the last one which
        # should be from the timing rule, which in this case is 9pm
        for item in occurrences3:
            self.assertEqual(item.start_time, time(7, 0, 0, 0))
            if item == occurrences3.last():
                self.assertEqual(item.end_time, time(21, 0, 0, 0))
            else:
                self.assertEqual(item.end_time, time(23, 59, 59, 999999))

    def test_no_same_start_and_end(self):
        """
        Test that no occurrences are created when start and end times are
        the same (because it does not make sense)
        """

        # pylint: disable=line-too-long
        rule1 = 'DTSTART:20180501T210000Z RRULE:FREQ=YEARLY;BYDAY=SU;BYSETPOS=1;BYMONTH=1;UNTIL=20280521T210000Z'  # noqa
        task = mommy.make('tasking.Task', timing_rule=rule1)

        # we should have 9 instead of 10 occurrences because the very last
        # one would start at 9pm and end at 9pm
        self.assertEqual(9, generate_task_occurrences(task).count())

    # pylint: disable=invalid-name
    @override_settings(TASKING_BULK_CREATE_OCCURRENCES=False)
    def test_not_bulk_generate_task_occurrences(self):
        """
        Test generate_task_occurrences works correctly when not bulk
        """
        task1 = mommy.make(
            'tasking.Task',
            timing_rule='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5'
        )
        task2 = mommy.make(
            'tasking.Task',
            timing_rule='RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5000'
        )

        # we should get 5 occurrences
        occurrences1 = generate_task_occurrences(task1)
        self.assertEqual(5, occurrences1.count())

        # we should get {MAX_OCCURRENCES} occurrences
        occurrences2 = generate_task_occurrences(task2)
        self.assertEqual(MAX_OCCURRENCES, occurrences2.count())

        # the start times should all be from the timing_rule, whic in this
        # case is the time the task was created
        # the end_times should all be 23:59:59
        for item in occurrences1:
            self.assertEqual(
                item.start_time.hour,
                task1.start.astimezone(
                    timezone.get_current_timezone()).time().hour)
            self.assertEqual(
                item.start_time.minute,
                task1.start.astimezone(
                    timezone.get_current_timezone()).time().minute)
            self.assertEqual(
                item.start_time.second,
                task1.start.astimezone(
                    timezone.get_current_timezone()).time().second)
            self.assertEqual(item.end_time, time(23, 59, 59, 999999))

        # pylint: disable=line-too-long
        rule1 = 'DTSTART:20180501T070000Z RRULE:FREQ=YEARLY;BYDAY=SU;BYSETPOS=1;BYMONTH=1;UNTIL=20480521T210000Z'  # noqa
        task3 = mommy.make('tasking.Task', timing_rule=rule1)
        occurrences3 = generate_task_occurrences(task3)

        # we should have 30 occurrences
        self.assertEqual(30, occurrences3.count())

        # the start times should all be from the timing_rule, whicih in this
        # case 7am
        # the end_times should all be 23:59:59 apart from the last one which
        # should be from the timing rule, which in this case is 9pm
        for item in occurrences3:
            self.assertEqual(item.start_time, time(7, 0, 0, 0))
            if item == occurrences3.last():
                self.assertEqual(item.end_time, time(21, 0, 0, 0))
            else:
                self.assertEqual(item.end_time, time(23, 59, 59, 999999))
