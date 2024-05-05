import os
import shutil
import json
import subprocess

import pytest

from facefusion.typing import JobStep
from facefusion.job_manager import init_jobs, create_job, add_step, remove_step, set_step_status, set_step_action, move_job_file
from facefusion.job_runner import run_step, run_job
from facefusion.download import conditional_download


@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
	jobs_path = './.jobs'
	if os.path.exists(jobs_path):
		shutil.rmtree(jobs_path)
	init_jobs(jobs_path)

	conditional_download('.assets/examples',
		[
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.jpg',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-240p.mp4'
	])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vframes', '1', '.assets/examples/target-240p.jpg' ])


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

	remove_step('test_create_job_with_two_step', 1)
	with open('./.jobs/test_create_job_with_two_step.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert len(job_actual.get('steps')) == 1
	assert not remove_step('test_create_job_with_two_step', 12345)


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


def test_run_step() -> None:
	step : JobStep = {
		'action': 'process',
		'args': [ 'run.py', '--frame-processors', 'face_swapper', '-s', '.assets/examples/source.jpg', '-t', '.assets/examples/target-240p.jpg', '-o', '.assets/examples/test_swap_face_to_image.jpg', '--headless' ],
		'status': 'queued'
	}
	assert run_step(step)


def test_move_job_file() -> None:
	create_job('test_create_and_move_job_file_to_queued')
	assert move_job_file('test_create_and_move_job_file_to_queued', 'queued')
	create_job('test_create_and_move_job_file_to_failed')
	assert move_job_file('test_create_and_move_job_file_to_failed', 'failed')
	create_job('test_create_and_move_job_file_to_completed')
	assert move_job_file('test_create_and_move_job_file_to_completed', 'completed')


def test_create_job_with_one_completing_step_and_check_status() -> None:
	create_job('test_create_job_with_one_completing_step_and_check_status')
	step = [ 'run.py', '--frame-processors', 'face_swapper', '-s', '.assets/examples/source.jpg', '-t', '.assets/examples/target-240p.jpg', '-o', '.assets/examples/test_swap_face_to_image.jpg', '--headless' ]
	add_step('test_create_job_with_one_completing_step_and_check_status', step)

	assert run_job('test_create_job_with_one_completing_step_and_check_status')
	assert os.path.exists('./.jobs/completed/test_create_job_with_one_completing_step_and_check_status.json')
	with open('./.jobs/completed/test_create_job_with_one_completing_step_and_check_status.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual['steps'][0]['status'] == 'completed'


def test_create_job_with_one_failing_step_and_check_status() -> None:
	create_job('test_create_job_with_one_failing_step_and_check_status')
	step = [ 'error step' ]
	add_step('test_create_job_with_one_failing_step_and_check_status', step)

	assert run_job('test_create_job_with_one_failing_step_and_check_status')
	assert os.path.exists('./.jobs/failed/test_create_job_with_one_failing_step_and_check_status.json')
	with open('./.jobs/failed/test_create_job_with_one_failing_step_and_check_status.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual['steps'][0]['status'] == 'failed'
