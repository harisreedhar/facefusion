import json
import os
from datetime import datetime
from typing import Optional

from facefusion.filesystem import is_file, is_directory
from facefusion.typing import JobStep, Job, JobArgs, JobStepStatus, JobStepAction

JOBS_PATH : Optional[str] = None


def get_current_datetime() -> str:
	date_time = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
	return date_time


def init_jobs(jobs_path : str) -> bool:
	global JOBS_PATH

	JOBS_PATH = jobs_path
	os.makedirs(JOBS_PATH, exist_ok = True)
	return is_directory(JOBS_PATH)


def resolve_job_path(job_id : str) -> str:
	job_file_name = job_id + '.json'
	job_path = os.path.join(JOBS_PATH, job_file_name)
	return job_path


def create_step(args : list[str]) -> JobStep:
	step : JobStep =\
	{
		'action': 'process',
		'args': args,
		'status': 'queued'
	}
	return step


def create_job(job_id : str) -> bool:
	job : Job =\
	{
		"version": "1",
		"date_created": get_current_datetime(),
		"date_updated": None,
		"steps": []
	}
	return write_job_file(job_id, job)


def add_step(job_id : str, args : JobArgs) -> bool:
	step = create_step(args)
	job = read_job_file(job_id)
	job['steps'].append(step)
	return update_job_file(job_id, job)


def remove_step(job_id : str, step_index : int) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']

	if step_index in range(len(steps)):
		job['steps'].pop(step_index)
		return update_job_file(job_id, job)
	return False


def set_step_status(job_id : str, step_index : int, status : JobStepStatus) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']

	if step_index in range(len(steps)):
		job['steps'][step_index]['status'] = status
		return update_job_file(job_id, job)
	return False


def set_step_action(job_id : str, step_index : int, action : JobStepAction) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']

	if step_index in range(len(steps)):
		job['steps'][step_index]['action'] = action
		return update_job_file(job_id, job)
	return False


def read_job_file(job_id : str) -> Optional[Job]:
	job_path = resolve_job_path(job_id)
	with open(job_path, 'r') as job_file:
		job = json.load(job_file)
	return job


def write_job_file(job_id : str, job : Job) -> bool:
	job_path = resolve_job_path(job_id)
	with open(job_path, 'w') as job_file:
		json.dump(job, job_file, indent = 4)
	return is_file(job_path)


def update_job_file(job_id : str, job : Job) -> bool:
	job['date_updated'] = get_current_datetime()
	return write_job_file(job_id, job)
