import sys
import subprocess
from facefusion.job_manager import read_job_file, set_step_status, move_job_file
from facefusion.typing import JobStep


def run_jobs() -> None:
	# TODO
	pass


def run_job(job_id : str) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']
	completed_steps = run_steps(job_id, steps)
	if completed_steps == len(steps):
		return move_job_file(job_id, 'completed')
	return move_job_file(job_id, 'failed')


def run_step(step : JobStep) -> bool:
	commands = [sys.executable, *step['args']]
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

