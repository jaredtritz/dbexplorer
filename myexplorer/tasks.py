from __future__ import absolute_import
from celery import shared_task
from celery.contrib import rdb
from myexplorer.models import Sample, Comparison

def mydebug(data):
    import os
    with open('/Users/jtritz/bitbucket/transfer/reboot_flag.txt', 'w') as f:
        read_data = f.write(data)

@shared_task
def add(x, y):
    import os
    with open('/Users/jtritz/bitbucket/transfer/reboot_flag.txt', 'w') as f:
        read_data = f.write('reboot')
    return x + y

@shared_task
def test(arg):
    mydebug(arg)
    return None

@shared_task
def sample_retriever(who, sample_id, link):
    Sample.retrieve(who, sample_id, link)
    return None

@shared_task
def property_calculator(sample_property_ids, who, email):
    Sample.calculate_properties(sample_property_ids, who, email)
    return None

@shared_task
def comparison_calculator(who, comparisons_ids):
    Comparison.calculate_comparisons(who, comparisons_ids)
    return None





