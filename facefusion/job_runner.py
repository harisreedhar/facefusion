import sys
import subprocess
from facefusion import logger, wording
from facefusion.job_manager import read_job_file, set_step_status, move_job_file, get_job_ids, get_total_steps, get_step_status
from facefusion.typing import JobStep


def run_jobs() -> None:
	job_queued_ids = get_job_ids('queued')

	for job_id in job_queued_ids:
		run_job(job_id)
		total_steps = get_total_steps(job_id)
		completed_steps = 0

		for step_index in range(total_steps):
			if get_step_status(job_id, step_index) == 'completed':
				completed_steps += 1
		logger.info(wording.get('job_processed').format(completed_steps = completed_steps, total_steps = total_steps, job_id = job_id), __name__.upper())


def run_job(job_id : str) -> bool:
	job = read_job_file(job_id)
	steps = job.get('steps')

	if run_steps(job_id, steps):
		return move_job_file(job_id, 'completed')
	return move_job_file(job_id, 'failed')


def run_steps(job_id : str, steps : list[JobStep]) -> bool:
	for step_index, step in enumerate(steps):
		args_length = len(step.get('args'))
		if args_length > 0 and run_step(step):
			set_step_status(job_id, step_index, 'completed')
		else:
			set_step_status(job_id, step_index, 'failed')
			return False
	return True


def run_step(step : JobStep) -> bool:
	commands = [ sys.executable, 'run.py', '--headless', *step.get('args') ]
	run = subprocess.run(commands, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	return run.returncode == 0 and 'image succeed' in run.stdout.decode() or 'video succeed' in run.stdout.decode() #todo: has to be changed to returncode == 0 only
