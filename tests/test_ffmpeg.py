import glob
import subprocess
import pytest

import facefusion.globals
from facefusion import process_manager
from facefusion.filesystem import get_temp_directory_path, create_temp, clear_temp, move_temps_to_temp
from facefusion.download import conditional_download
from facefusion.ffmpeg import extract_frames, read_audio_buffer


@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
	process_manager.start()
	conditional_download('.assets/examples',
	[
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.jpg',
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.mp3',
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-240p.mp4'
	])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/source.mp3', '.assets/examples/source.wav' ])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vf', 'fps=25', '.assets/examples/target-240p-25fps.mp4' ])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vf', 'fps=30', '.assets/examples/target-240p-30fps.mp4' ])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vf', 'fps=60', '.assets/examples/target-240p-60fps.mp4' ])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vf', 'fps=25', '.assets/examples/target-240p-25fps_0.mp4' ])
	subprocess.run([ 'ffmpeg', '-i', '.assets/examples/target-240p.mp4', '-vf', 'fps=25', '.assets/examples/target-240p-25fps_1.mp4' ])


@pytest.fixture(scope = 'function', autouse = True)
def before_each() -> None:
	facefusion.globals.trim_frame_start = None
	facefusion.globals.trim_frame_end = None
	facefusion.globals.temp_frame_format = 'jpg'


def test_extract_frames() -> None:
	target_paths =\
	[
		'.assets/examples/target-240p-25fps.mp4',
		'.assets/examples/target-240p-30fps.mp4',
		'.assets/examples/target-240p-60fps.mp4'
	]

	for target_path in target_paths:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '452x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == 324

		clear_temp(target_path)


def test_extract_frames_with_trim_start() -> None:
	facefusion.globals.trim_frame_start = 224
	data_provider =\
	[
		('.assets/examples/target-240p-25fps.mp4', 55),
		('.assets/examples/target-240p-30fps.mp4', 100),
		('.assets/examples/target-240p-60fps.mp4', 212)
	]

	for target_path, frame_total in data_provider:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '452x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == frame_total

		clear_temp(target_path)


def test_extract_frames_with_trim_start_and_trim_end() -> None:
	facefusion.globals.trim_frame_start = 124
	facefusion.globals.trim_frame_end = 224
	data_provider =\
	[
		('.assets/examples/target-240p-25fps.mp4', 120),
		('.assets/examples/target-240p-30fps.mp4', 100),
		('.assets/examples/target-240p-60fps.mp4', 50)
	]

	for target_path, frame_total in data_provider:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '452x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == frame_total

		clear_temp(target_path)


def test_extract_frames_with_trim_end() -> None:
	facefusion.globals.trim_frame_end = 100
	data_provider =\
	[
		('.assets/examples/target-240p-25fps.mp4', 120),
		('.assets/examples/target-240p-30fps.mp4', 100),
		('.assets/examples/target-240p-60fps.mp4', 50)
	]

	for target_path, frame_total in data_provider:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '426x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == frame_total

		clear_temp(target_path)


def test_read_audio_buffer() -> None:
	assert isinstance(read_audio_buffer('.assets/examples/source.mp3', 1, 1), bytes)
	assert isinstance(read_audio_buffer('.assets/examples/source.wav', 1, 1), bytes)
	assert read_audio_buffer('.assets/examples/invalid.mp3', 1, 1) is None


def test_extract_frames_with_trim_start_and_trim_end_2() -> None:
	facefusion.globals.trim_frame_start = 0
	facefusion.globals.trim_frame_end = 10

	target_path_0 = '.assets/examples/target-240p-25fps_0.mp4'
	target_path_1 = '.assets/examples/target-240p-25fps_1.mp4'
	frame_total = 10

	temp_directory_path_0 = get_temp_directory_path(target_path_0)
	create_temp(target_path_0)
	assert extract_frames(target_path_0, '452x240', 25.0) is True
	assert len(glob.glob1(temp_directory_path_0, '*.jpg')) == frame_total

	temp_directory_path_1 = get_temp_directory_path(target_path_1)
	create_temp(target_path_1)
	assert extract_frames(target_path_1, '452x240', 25.0) is True
	assert len(glob.glob1(temp_directory_path_1, '*.jpg')) == frame_total

	combined_temp_directory_path = get_temp_directory_path('combined_temp_directory')
	create_temp('combined_temp_directory')

	move_temps_to_temp([temp_directory_path_0, temp_directory_path_1], combined_temp_directory_path)
	assert len(glob.glob1(combined_temp_directory_path, '*.jpg')) == frame_total * 2

	clear_temp('combined_temp_directory')
