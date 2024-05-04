import sys
import subprocess
from facefusion.job_manager import read_job_file, set_step_status
from facefusion.typing import JobStep


def run_jobs() -> None:
	# TODO
	pass


def run_job(job_id : str) -> None:
	job = read_job_file(job_id)
	steps = job['steps']
	completed_steps = run_steps(job_id, steps)
	if completed_steps == len(steps):
		set_job_status(job_id, 'completed')
	else:
		set_job_status(job_id, 'failed')


def run_step(step : JobStep) -> bool:
	commands = [sys.executable, 'run.py', *step['args']]
	run = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return 'image succeed' in run.stdout.decode() or 'video succeed' in run.stdout.decode()


def run_steps(job_id : str, steps: list[JobStep]) -> int:
	completed_steps = 0
	for step_index, step in enumerate(steps):
		if run_step(step):
			set_step_status(job_id, step_index, 'completed')
			completed_steps += 1
		else:
			set_step_status(job_id, step_index, 'failed')
	return completed_steps


def set_job_status(job_id : str, status : str) -> None:
	# TODO
	pass
