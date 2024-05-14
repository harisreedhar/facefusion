import sys
import subprocess
from facefusion import logger
from facefusion.job_manager import read_job_file, set_step_status, move_job_file, get_job_ids, resolve_job_path
from facefusion.typing import JobStep


def run_jobs() -> None:
	job_ids = get_job_ids('unassigned')
	for job_id in job_ids:
		move_job_file(job_id, 'queued')
	job_ids = get_job_ids('queued')
	for job_id in job_ids:
		run_job(job_id)
		job = read_job_file(job_id)
		steps = job.get('steps')
		completed_steps = 0
		for step in steps:
			if step['status'] == 'completed':
				completed_steps += 1
		logger.info(f'{completed_steps} of {len(steps)} step completed, {resolve_job_path(job_id)}', __name__.upper())


def run_job(job_id : str) -> bool:
	job = read_job_file(job_id)
	steps = job.get('steps')
	if run_steps(job_id, steps):
		return move_job_file(job_id, 'completed')
	return move_job_file(job_id, 'failed')


def run_step(step : JobStep) -> bool:
	if len(step.get('args')) == 0:
		return False
	commands = [sys.executable, 'run.py', '--headless', *step.get('args')]
	run = subprocess.run(commands, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	return run.returncode == 0 and 'image succeed' in run.stdout.decode() or 'video succeed' in run.stdout.decode()


def run_steps(job_id : str, steps : list[JobStep]) -> bool:
	for step_index, step in enumerate(steps):
		if run_step(step):
			set_step_status(job_id, step_index, 'completed')
		else:
			set_step_status(job_id, step_index, 'failed')
			return False
	return True
