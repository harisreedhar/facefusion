import json
import os
import shutil
from datetime import datetime
from typing import Optional

from facefusion.filesystem import is_file, is_directory
from facefusion.typing import JobStep, Job, JobArgs, JobStepStatus, JobStepAction, JobStatus, Args

JOBS_PATH : Optional[str] = None
ARGS_REGISTRY : Optional[Args] = None


def get_current_datetime() -> str:
	date_time = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
	return date_time


def init_jobs(jobs_path : str) -> bool:
	global JOBS_PATH

	JOBS_PATH = jobs_path
	os.makedirs(JOBS_PATH, exist_ok = True)
	queued_path = os.path.join(JOBS_PATH, 'queued')
	os.makedirs(queued_path, exist_ok=True)
	completed_path = os.path.join(JOBS_PATH, 'completed')
	os.makedirs(completed_path, exist_ok=True)
	failed_path = os.path.join(JOBS_PATH, 'failed')
	os.makedirs(failed_path, exist_ok=True)
	return is_directory(JOBS_PATH) and is_directory(queued_path) and is_directory(completed_path) and is_directory(failed_path)


def clear_jobs(jobs_path : str) -> None:
	if os.path.exists(jobs_path):
		shutil.rmtree(jobs_path)


def register_args(args : list[str], has_value : bool) -> None:
	global ARGS_REGISTRY

	if ARGS_REGISTRY is None:
		ARGS_REGISTRY =\
		{
			'valued_args' : [],
			'non_valued_args' : []
		}
	if has_value:
		ARGS_REGISTRY.get('valued_args').extend(args)
	else:
		ARGS_REGISTRY.get('non_valued_args').extend(args)


def resolve_job_path(job_id : str) -> str:
	job_file_name = job_id + '.json'
	job_statuses = [ 'queued', 'failed', 'completed' ]

	for job_status in job_statuses:
		if job_file_name in os.listdir(os.path.join(JOBS_PATH, job_status)):
			return os.path.join(JOBS_PATH, job_status, job_file_name)
	return os.path.join(JOBS_PATH, 'queued', job_file_name)


def create_step(args : list[str]) -> JobStep:
	step : JobStep =\
	{
		'action' : 'process',
		'args' : args,
		'status': 'queued'
	}
	return step


def create_job(job_id : str) -> bool:
	job : Job =\
	{
		'version' : '1',
		'date_created' : get_current_datetime(),
		'date_updated' : None,
		'steps' : []
	}
	return write_job_file(job_id, job)


def add_step(job_id : str, args : JobArgs) -> bool:
	step = create_step(args)
	job = read_job_file(job_id)
	job.get('steps').append(step)
	return update_job_file(job_id, job)


def insert_step(job_id : str, step_index : int, args : JobArgs) -> bool:
	step = create_step(args)
	job = read_job_file(job_id)

	if step_index < 0:
		step_index = len(job.get('steps')) + step_index + 1
	job.get('steps').insert(step_index, step)
	return update_job_file(job_id, job)


def remove_step(job_id : str, step_index : int) -> bool:
	job = read_job_file(job_id)
	steps = job.get('steps')
	step_length = len(steps)

	if step_index in range(-step_length, step_length):
		job.get('steps').pop(step_index)
		return update_job_file(job_id, job)
	return False


def set_step_status(job_id : str, step_index : int, step_status : JobStepStatus) -> bool:
	job = read_job_file(job_id)
	steps = job.get('steps')

	if step_index in range(len(steps)):
		job.get('steps')[step_index]['status'] = step_status
		return update_job_file(job_id, job)
	return False


def get_step_status(job_id : str, step_index : int) -> Optional[JobStepStatus]:
	job = read_job_file(job_id)
	steps : list[JobStep] = job.get('steps')

	if step_index in range(len(steps)):
		return steps[step_index].get('status')
	return None


def set_step_action(job_id : str, step_index : int, action : JobStepAction) -> bool:
	job = read_job_file(job_id)
	steps = job.get('steps')

	if step_index in range(len(steps)):
		job.get('steps')[step_index]['action'] = action
		return update_job_file(job_id, job)
	return False


def read_job_file(job_id : str) -> Optional[Job]:
	job_path = resolve_job_path(job_id)

	if is_file(job_path):
		with open(job_path, 'r') as job_file:
			return json.load(job_file)
	return None


def write_job_file(job_id : str, job : Job) -> bool:
	job_path = resolve_job_path(job_id)
	with open(job_path, 'w') as job_file:
		json.dump(job, job_file, indent = 4)
	return is_file(job_path)


def update_job_file(job_id : str, job : Job) -> bool:
	job['date_updated'] = get_current_datetime()
	return write_job_file(job_id, job)


def move_job_file(job_id : str, job_status : JobStatus) -> bool:
	job_path = resolve_job_path(job_id)
	job_file_path_moved = shutil.move(job_path, os.path.join(JOBS_PATH, job_status))
	return is_file(job_file_path_moved)


def delete_job_file(job_id : str) -> bool:
	job_path = resolve_job_path(job_id)
	if is_file(job_path):
		os.remove(job_path)
		return True
	return False


def get_all_job_ids() -> list[Optional[str]]:
	job_ids = []
	job_ids.extend(get_job_ids('queued'))
	job_ids.extend(get_job_ids('failed'))
	job_ids.extend(get_job_ids('completed'))
	return job_ids


def get_job_ids(job_status : JobStatus) -> list[Optional[str]]:
	job_ids = []
	job_file_names = os.listdir(os.path.join(JOBS_PATH, job_status))

	for job_file_name in job_file_names:
		if is_file(os.path.join(JOBS_PATH, job_status, job_file_name)):
			job_ids.append(os.path.splitext(job_file_name)[0])
	return job_ids


def get_job_status(job_id : str) -> Optional[JobStatus]:
	job_statuses : list[JobStatus] = [ 'queued', 'failed', 'completed' ]
	for job_status in job_statuses:
		if job_id in get_job_ids(job_status):
			return job_status
	return None


def get_total_steps(job_id : str) -> int:
	job = read_job_file(job_id)
	steps = job.get('steps')
	return len(steps)


def filter_args(args: list[str]) -> list[str]:
	valued_args = ARGS_REGISTRY.get('valued_args')
	non_valued_args = ARGS_REGISTRY.get('non_valued_args')
	filtered_args = []

	for index, arg in enumerate(args):
		if arg in non_valued_args:
			filtered_args.append(arg)
		elif arg in valued_args:
			filtered_args.append(arg)
			next_index = index + 1
			while next_index < len(args) and not args[next_index].startswith('--') and not args[next_index].startswith('-'):
				filtered_args.append(args[next_index])
				next_index += 1
	return filtered_args
