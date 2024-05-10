import sys
import subprocess
from facefusion.job_manager import read_job_file, set_step_status, move_job_file, get_all_job_ids, get_job_ids, resolve_job_path
from facefusion.typing import JobStep


def run_jobs() -> None:
	# TODO
	job_ids = get_all_job_ids()
	for job_id in job_ids:
		if job_id not in get_job_ids('failed') and job_id not in get_job_ids('completed'):
			if job_id in get_job_ids('unassigned'):
				move_job_file(job_id, 'queued')
			run_job(job_id)
			job = read_job_file(job_id)
			steps = job.get('steps')
			completed_steps = 0
			for step in steps:
				if step['status'] == 'completed':
					completed_steps += 1
			print(f'{completed_steps} / {len(steps)} steps completed: {resolve_job_path(job_id)}')


def run_job(job_id : str) -> bool:
	job = read_job_file(job_id)
	steps = job.get('steps')
	if run_steps(job_id, steps):
		return move_job_file(job_id, 'completed')
	return move_job_file(job_id, 'failed')


def run_step(step : JobStep) -> bool:
	commands = [sys.executable, *step['args']]
	run = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return run.returncode == 0 and 'image succeed' in run.stdout.decode() or 'video succeed' in run.stdout.decode()


def run_steps(job_id : str, steps : list[JobStep]) -> bool:
	for step_index, step in enumerate(steps):
		if run_step(step):
			set_step_status(job_id, step_index, 'completed')
		else:
			set_step_status(job_id, step_index, 'failed')
			return False
	return True
