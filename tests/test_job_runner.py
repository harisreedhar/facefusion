import os
import shutil
import json
import subprocess

import pytest

from facefusion.typing import JobStep
from facefusion.job_manager import init_jobs, create_job, add_step, update_step
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


def test_run_step() -> None:
	step : JobStep = {
		'action': 'process',
		'args': [ '--frame-processors', 'face_swapper', '-s', '.assets/examples/source.jpg', '-t', '.assets/examples/target-240p.jpg', '-o', '.assets/examples/test_swap_face_to_image.jpg' ],
		'status': 'queued'
	}
	assert run_step(step)


def test_run_job_with_one_completing_step() -> None:
	create_job('test_create_job_with_one_completing_step_and_check_status')
	step = [ '--frame-processors', 'face_swapper', '-s', '.assets/examples/source.jpg', '-t', '.assets/examples/target-240p.jpg', '-o', '.assets/examples/test_swap_face_to_image.jpg' ]
	add_step('test_create_job_with_one_completing_step_and_check_status', step)

	assert run_job('test_create_job_with_one_completing_step_and_check_status')
	assert os.path.exists('.jobs/completed/test_create_job_with_one_completing_step_and_check_status.json')
	with open('.jobs/completed/test_create_job_with_one_completing_step_and_check_status.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual['steps'][0]['status'] == 'completed'


def test_run_job_with_one_failing_step() -> None:
	create_job('test_create_job_with_one_failing_step_and_check_status')
	step = [ 'invalid' ]
	add_step('test_create_job_with_one_failing_step_and_check_status', step)

	assert run_job('test_create_job_with_one_failing_step_and_check_status')
	assert os.path.exists('.jobs/failed/test_create_job_with_one_failing_step_and_check_status.json')
	with open('.jobs/failed/test_create_job_with_one_failing_step_and_check_status.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual['steps'][0]['status'] == 'failed'


def test_run_job_with_one_failing_step_and_update_with_completing_step() -> None:
	create_job('test_run_job_with_one_failing_step_update_with_completing_step')
	step = [ 'invalid' ]
	add_step('test_run_job_with_one_failing_step_update_with_completing_step', step)

	assert run_job('test_run_job_with_one_failing_step_update_with_completing_step')
	assert os.path.exists('.jobs/failed/test_run_job_with_one_failing_step_update_with_completing_step.json')
	with open('.jobs/failed/test_run_job_with_one_failing_step_update_with_completing_step.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual['steps'][0]['status'] == 'failed'

	step = [ '--frame-processors', 'face_swapper', '-s', '.assets/examples/source.jpg', '-t', '.assets/examples/target-240p.jpg', '-o', '.assets/examples/test_swap_face_to_image.jpg' ]
	update_step('test_run_job_with_one_failing_step_update_with_completing_step', 0, step)
	assert run_job('test_run_job_with_one_failing_step_update_with_completing_step')
	assert os.path.exists('.jobs/completed/test_run_job_with_one_failing_step_update_with_completing_step.json')
	with open('.jobs/completed/test_run_job_with_one_failing_step_update_with_completing_step.json', 'r') as file_actual:
		job_actual = json.load(file_actual)
	assert job_actual['steps'][0]['status'] == 'completed'
