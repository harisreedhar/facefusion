import os
import shutil
import json

import pytest

from facefusion.job_manager import init_jobs, create_job, add_step, delete_step, set_step_status, set_step_action, move_job_file, delete_job_file


@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
	jobs_path = './.jobs'
	if os.path.exists(jobs_path):
		shutil.rmtree(jobs_path)
	init_jobs(jobs_path)


def test_job_create() -> None:
	create_job('test_create_job')

	with open('./.jobs/test_create_job.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	with open('tests/providers/test_create_job.json', 'r') as file_expect:
		job_expect = json.load(file_expect)

	assert job_actual.get('version') == job_expect.get('version')
	assert job_actual.get('date_created')
	assert job_actual.get('date_updated') is None
	assert job_actual.get('steps') == job_expect.get('steps')
	assert len(job_actual.get('steps')) == 0


def test_job_create_and_delete() -> None:
	create_job('test_job_create_and_delete')
	assert os.path.exists('./.jobs/test_job_create_and_delete.json')

	delete_job_file('test_job_create_and_delete')
	assert not os.path.exists('./.jobs/test_job_create_and_delete.json')


def test_create_job_with_one_step() -> None:
	create_job('test_create_job_with_one_step')
	add_step('test_create_job_with_one_step', [])

	with open('./.jobs/test_create_job_with_one_step.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	with open('tests/providers/test_create_job_with_one_step.json', 'r') as file_expect:
		job_expect = json.load(file_expect)

	assert job_actual.get('steps') == job_expect.get('steps')
	assert len(job_actual.get('steps')) == 1


def test_create_job_add_two_steps_and_remove_one_step() -> None:
	create_job('test_create_job_with_two_step')
	add_step('test_create_job_with_two_step', [])
	add_step('test_create_job_with_two_step', [])

	with open('./.jobs/test_create_job_with_two_step.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	with open('tests/providers/test_create_job_with_two_step.json', 'r') as file_expect:
		job_expect = json.load(file_expect)

	assert job_actual.get('steps') == job_expect.get('steps')
	assert len(job_actual.get('steps')) == 2

	delete_step('test_create_job_with_two_step', 1)
	with open('./.jobs/test_create_job_with_two_step.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert len(job_actual.get('steps')) == 1
	assert not delete_step('test_create_job_with_two_step', 12345)


def test_create_job_with_one_step_and_set_status() -> None:
	create_job('test_create_job_with_one_step_and_set_status')
	add_step('test_create_job_with_one_step_and_set_status', [])

	with open('./.jobs/test_create_job_with_one_step_and_set_status.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	with open('tests/providers/test_create_job_with_one_step_and_set_status.json', 'r') as file_expect:
		job_expect = json.load(file_expect)

	assert job_actual.get('steps') == job_expect.get('steps')
	assert len(job_actual.get('steps')) == 1

	step_index = 0
	set_step_status('test_create_job_with_one_step_and_set_status', step_index, 'completed')
	with open('./.jobs/test_create_job_with_one_step_and_set_status.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual.get('steps')[step_index]['status'] == 'completed'
	assert not set_step_status('test_create_job_with_one_step_and_set_status', 12345, 'completed')


def test_create_job_with_one_step_and_set_action() -> None:
	create_job('test_create_job_with_one_step_and_set_action')
	add_step('test_create_job_with_one_step_and_set_action', [])

	with open('./.jobs/test_create_job_with_one_step_and_set_action.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	with open('tests/providers/test_create_job_with_one_step_and_set_action.json', 'r') as file_expect:
		job_expect = json.load(file_expect)

	assert job_actual.get('steps') == job_expect.get('steps')
	assert len(job_actual.get('steps')) == 1

	step_index = 0
	set_step_action('test_create_job_with_one_step_and_set_action', step_index, 'mix')
	with open('./.jobs/test_create_job_with_one_step_and_set_action.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual.get('steps')[step_index]['action'] == 'mix'
	assert not set_step_action('test_create_job_with_one_step_and_set_action', 12345, 'mix')


def test_move_job_file() -> None:
	create_job('test_create_and_move_job_file_to_queued')
	assert move_job_file('test_create_and_move_job_file_to_queued', 'queued')
	assert os.path.exists('./.jobs/queued/test_create_and_move_job_file_to_queued.json')

	create_job('test_create_and_move_job_file_to_failed')
	assert move_job_file('test_create_and_move_job_file_to_failed', 'failed')
	assert os.path.exists('./.jobs/failed/test_create_and_move_job_file_to_failed.json')

	create_job('test_create_and_move_job_file_to_completed')
	assert move_job_file('test_create_and_move_job_file_to_completed', 'completed')
	assert os.path.exists('./.jobs/completed/test_create_and_move_job_file_to_completed.json')


def test_add_remove_after_move_job_file() -> None:
	create_job('test_add_remove_after_move_job_file_to_queued')
	assert move_job_file('test_add_remove_after_move_job_file_to_queued', 'queued')
	assert os.path.exists('./.jobs/queued/test_add_remove_after_move_job_file_to_queued.json')
	assert add_step('test_add_remove_after_move_job_file_to_queued', [])
	assert delete_step('test_add_remove_after_move_job_file_to_queued', 0)

	create_job('test_add_remove_after_move_job_file_to_failed')
	assert move_job_file('test_add_remove_after_move_job_file_to_failed', 'failed')
	assert os.path.exists('./.jobs/failed/test_add_remove_after_move_job_file_to_failed.json')
	assert add_step('test_add_remove_after_move_job_file_to_failed', [])
	assert delete_step('test_add_remove_after_move_job_file_to_failed', 0)

	create_job('test_add_remove_after_move_job_file_to_completed')
	assert move_job_file('test_add_remove_after_move_job_file_to_completed', 'completed')
	assert os.path.exists('./.jobs/completed/test_add_remove_after_move_job_file_to_completed.json')
	assert add_step('test_add_remove_after_move_job_file_to_completed', [])
	assert delete_step('test_add_remove_after_move_job_file_to_completed', 0)
