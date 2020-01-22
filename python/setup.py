from setuptools import find_packages

from skbuild import setup

with open('../README.rst') as f:
    long_description = f.read()

diva_source_dir = ".."
setup(name='diva-framework',
      version='0.0.6',
      author='Kitware, Inc.',
      author_email='diva-framework@kitware.com',
      url='https://github.com/Kitware/DIVA',
      license='BSD 3-Clause',
      description='The DIVA Framework is a software framework designed'
      'to provide an architecture and a set of software modules which'
      'will facilitate the development of DIVA analytics',
      long_description=long_description,
      packages=find_packages(),
      setup_requires=[
          'setuptools',
          'scikit-build'
      ],
      install_requires=[
          'kwiver==1.4.5',
          'opencv-python'
      ],
      cmake_args=[
          '-DCMAKE_BUILD_TYPE=Release',
          '-DKWIVER_PYTHON_MAJOR_VERSION=3',
          '-DDIVA_PYTHON_MAJOR_VERSION=3',
          '-DDIVA_SUPERBUILD=OFF',
          '-DDIVA_BUILD_SHARED=OFF',
          '-DDIVA_BUILD_WITH_CUDA=OFF',
          '-DDIVA_BUILD_WITH_CUDNN=OFF',
          '-DDIVA_ENABLE_PROCESS=ON',
      ],
      cmake_install_dir='diva',
      cmake_source_dir=diva_source_dir,
      entry_points={
          'kwiver.python_plugin_registration' : [
              'simple_draw_detected_object_set=diva.arrows.simple_draw_detected_object_set',
              'image_viewer_process=diva.processes.image_viewer_process',
              'simple_detector_process=diva.processes.simple_detector_process'],
          'kwiver.cpp_search_paths': [
              'diva_processes=diva.processes.register_cpp_processes:get_cpp_path']},
      scripts=[
          '{}/scripts/cli_helpers/cleanup_chunk.py'.format(diva_source_dir),
          '{}/scripts/cli_helpers/cleanup_experiment.py'.format(diva_source_dir),
          '{}/scripts/cli_helpers/generate_experiments.py'.format(diva_source_dir),
          '{}/scripts/cli_helpers/merge_videos.py'.format(diva_source_dir)],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Operating System :: Unix',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'],
      platforms=['linux', 'Unix'],
      python_requires='>=3.5')
