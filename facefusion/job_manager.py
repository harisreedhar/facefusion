import json
import os
import shutil
from datetime import datetime
from typing import Optional

from facefusion.filesystem import is_file, is_directory
from facefusion.typing import JobStep, Job, JobArgs, JobStepStatus, JobStepAction, JobStatus, Args

JOBS_PATH : Optional[str] = None
ARGS : Optional[Args] = None


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


def register_args(args : list[str], has_value : bool) -> None:
	global ARGS

	if ARGS is None:
		ARGS = {
			'valued_args' : [],
			'non_valued_args' : []
		}
	if has_value:
		ARGS['valued_args'].extend(args)
	else:
		ARGS['non_valued_args'].extend(args)


def resolve_job_path(job_id : str) -> str:
	job_file_name = job_id + '.json'
	job_file_path = os.path.join(JOBS_PATH, job_file_name)
	job_statuses = ['queued', 'failed', 'completed']
	for job_status in job_statuses:
		if job_file_name in os.listdir(os.path.join(JOBS_PATH, job_status)):
			job_file_path = os.path.join(JOBS_PATH, job_status, job_file_name)
	return job_file_path


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


def delete_step(job_id : str, step_index : int) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']

	if step_index in range(len(steps)):
		job['steps'].pop(step_index)
		return update_job_file(job_id, job)
	return False


def update_step(job_id : str, step_index : int, args : JobArgs) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']

	if step_index in range(len(steps)):
		job['steps'][step_index] = create_step(args)
		return update_job_file(job_id, job)
	return False


def set_step_status(job_id : str, step_index : int, step_status : JobStepStatus) -> bool:
	job = read_job_file(job_id)
	steps = job['steps']

	if step_index in range(len(steps)):
		job['steps'][step_index]['status'] = step_status
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


def move_job_file(job_id : str, job_status : JobStatus) -> bool:
	job_path = resolve_job_path(job_id)
	if job_status == 'unassigned':
		job_status_path = JOBS_PATH
	else:
		job_status_path = os.path.join(JOBS_PATH, job_status)
	job_file_path_moved = shutil.move(job_path, job_status_path)
	return is_file(job_file_path_moved)


def delete_job_file(job_id : str) -> bool:
	job_path = resolve_job_path(job_id)
	if is_file(job_path):
		os.remove(job_path)
		return True
	return False


def get_all_job_ids() -> list[Optional[str]]:
	job_ids = []
	job_ids.extend(get_job_ids('unassigned'))
	job_ids.extend(get_job_ids('queued'))
	job_ids.extend(get_job_ids('failed'))
	job_ids.extend(get_job_ids('completed'))
	return job_ids


def get_job_ids(job_status : JobStatus) -> list[Optional[str]]:
	job_ids = []
	job_sub_path = '' if job_status == 'unassigned' else job_status
	job_file_names = os.listdir(os.path.join(JOBS_PATH, job_sub_path))
	for job_file_name in job_file_names:
		if is_file(os.path.join(JOBS_PATH, job_sub_path, job_file_name)):
			job_ids.append(os.path.splitext(job_file_name)[0])
	return job_ids


def filter_args(args: list[str]) -> list[str]:
	valued_args = ARGS.get('valued_args')
	non_valued_args = ARGS.get('non_valued_args')
	filtered_args = []

	for index, arg in enumerate(args):
		if arg in valued_args:
			filtered_args.append(arg)
			for sub_index in range(index + 1, len(args)):
				if args[sub_index].startswith('--') or args[sub_index].startswith('-'):
					break
				else:
					filtered_args.append(args[sub_index])
		elif arg in non_valued_args:
			filtered_args.append(arg)
		else:
			continue
	return filtered_args
