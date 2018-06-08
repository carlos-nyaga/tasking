# -*- coding: utf-8 -*-
"""
Tasking Serializers
"""
from __future__ import unicode_literals

from dateutil.rrule import rrulestr
from rest_framework import serializers

from tasking.common_tags import (INVALID_END_DATE, INVALID_START_DATE,
                                 INVALID_TIMING_RULE)
from tasking.models import Task, TaskLocation
from tasking.serializers.base import GenericForeignKeySerializer
from tasking.utils import get_rrule_end, get_rrule_start
from tasking.validators import validate_rrule


def check_timing_rule(value):
    """
    Validate timing rule
    """
    if validate_rrule(value) is True:
        return value
    raise serializers.ValidationError(
        {'timing_rule': INVALID_TIMING_RULE}
    )


class TaskLocationSerializer(serializers.ModelSerializer):
    """
    TaskLocation serialzier class
    """

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """
        Meta options for TaskLocationSerializer
        """
        model = TaskLocation
        fields = [
            'task',
            'created',
            'modified',
            'location',
            'timing_rule',
            'start',
            'end'
        ]

    # pylint: disable=no-self-use
    def validate_timing_rule(self, value):
        """
        Validate timing rule
        """
        return check_timing_rule(value)


class TaskSerializer(GenericForeignKeySerializer):
    """
    Task serializer class
    """
    start = serializers.DateTimeField(required=False)
    submission_count = serializers.SerializerMethodField()

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """
        Meta options for TaskSerializer
        """
        fields = [
            'id',
            'created',
            'modified',
            'name',
            'parent',
            'estimated_time',
            'description',
            'start',
            'end',
            'timing_rule',
            'total_submission_target',
            'user_submission_target',
            'status',
            'submission_count',
            'target_content_type',
            'target_id',
            'segment_rules',
            'locations',
        ]

        model = Task

    # pylint: disable=no-self-use
    def validate_timing_rule(self, value):
        """
        Validate timing rule
        """
        return check_timing_rule(value)

    def validate(self, attrs):
        """
        Object level validation method for TaskSerializer
        """

        # if timing_rule is provided, we extract start and end from its value
        if self.instance is not None:
            # we are doing an update
            timing_rule = attrs.get('timing_rule', self.instance.timing_rule)
        else:
            # we are creating a new object
            timing_rule = attrs.get('timing_rule')

        if timing_rule is not None:
            # get start and end values from timing_rule
            attrs['start'] = get_rrule_start(rrulestr(timing_rule))
            attrs['end'] = get_rrule_end(rrulestr(timing_rule))

        end_date = attrs.get('end')
        start_date = attrs.get('start')

        # If end date is present we validate that it is greater than start_date
        if end_date is not None:
            # If end date is lesser than the start date raise an error
            if end_date < start_date:
                raise serializers.ValidationError(
                    {'end': INVALID_END_DATE, 'start': INVALID_START_DATE}
                )

        return super(TaskSerializer, self).validate(attrs)

    def get_submission_count(self, obj):
        """
        Add a custom method to get submission count
        """
        try:
            return obj.submission_count
        except AttributeError:
            return obj.submissions
