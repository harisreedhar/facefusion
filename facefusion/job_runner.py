import sys
import subprocess
from facefusion.job_manager import read_job_file, set_step_status, move_job_file
from facefusion.typing import JobStep, JobStepStatus


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


def run_step(step : JobStep) -> JobStepStatus:
	commands = [sys.executable, *step['args']]
	run = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if run.returncode == 0 and 'image succeed' in run.stdout.decode() or 'video succeed' in run.stdout.decode():
		return 'completed'
	return 'failed'


def run_steps(job_id : str, steps : list[JobStep]) -> int:
	completed_steps = 0
	for step_index, step in enumerate(steps):
		status = step.get('status')
		if status == 'queued' or status == 'failed':
			status = run_step(step)
			set_step_status(job_id, step_index, status)
		if status == 'completed':
			completed_steps += 1
		else:
			break
	return completed_steps
