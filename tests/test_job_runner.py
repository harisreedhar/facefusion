import subprocess
import shutil
import pytest

from facefusion.download import conditional_download
from facefusion.job_manager import init_jobs, clear_jobs, create_step, get_job_status
from facefusion.job_runner import run_step, run_job


@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
	jobs_path = './.jobs'
	clear_jobs(jobs_path)
	init_jobs(jobs_path)
	conditional_download('.assets/examples',
	[
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.jpg',
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-240p.mp4'
	])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vframes', '1', '.assets/examples/target-240p.jpg' ])


def copy_json(source_path : str, destination_path : str) -> None:
	shutil.copyfile(source_path, destination_path)


def test_run_step() -> None:
	args = [ '--frame-processors', 'face_swapper', '-s', '.assets/examples/source.jpg', '-t', '.assets/examples/target-240p.jpg', '-o', '.assets/examples/test_swap_face_to_image.jpg' ]
	step = create_step(args)
	assert run_step(step)

	args = [ 'invalid' ]
	step = create_step(args)
	assert run_step(step) == False


def test_run_job() -> None:
	copy_json('tests/providers/test_run_job_completing.json', './.jobs/queued/test_run_job_completing.json')
	assert run_job('test_run_job_completing')
	assert get_job_status('test_run_job_completing') == 'completed'

	copy_json('tests/providers/test_run_job_failing.json', './.jobs/queued/test_run_job_failing.json')
	assert run_job('test_run_job_failing')
	assert get_job_status('test_run_job_failing') == 'failed'
