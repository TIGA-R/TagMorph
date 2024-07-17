
from functools import partial
import pathlib
from parse.node_strategies import type_case_wrapper, type_prefix_removal
from parse.tag_process import TagProcessor

path = str(pathlib.Path(__file__).parent.resolve()) + '/tests/json/7-15-2024/'
single_site_file = 'simple single site tags.json'
original_single_site_file = 'single site tags.json'
single_well_file = 'single well tags.json'
south_site_file = 'south tags.json'
north_site_file = 'north tags.json'

type_case_correction = type_case_wrapper()
missing_udt_dict = {}
import time

start = time.time()

with TagProcessor(
    path+north_site_file,
    'North',
    atomic_process_steps = [
    ],
    udtInstance_process_steps = [
        type_prefix_removal,
        partial(type_case_correction, missing_udt_dict),
    ],
    udtType_process_steps = [
        type_prefix_removal,
        partial(type_case_correction, missing_udt_dict),
    ],
) as processor:
    processor.process()
    processor.to_file(path + 'north_scrub.json')

mid = time.time()

finish = time.time()
print(f"Time to process: {mid-start} s")
print(f"Time to map: {finish-mid} s")
