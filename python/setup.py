from setuptools import find_packages

from skbuild import setup

diva_source_dir = ".."
setup(name='diva-framework',
      version='0.0.1',
      packages=find_packages(),
      setup_requires=[
          'setuptools',
          'scikit-build'
      ],
      install_requires=[
          'kwiver',
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
          'kwiver.cpp_search_paths': [
              'diva_processes=diva.processes.register_cpp_processes:get_cpp_path']},
      scripts=[
          '{}/scripts/cli_helpers/cleanup_chunk.py'.format(diva_source_dir),
          '{}/scripts/cli_helpers/cleanup_experiment.py'.format(diva_source_dir),
          '{}/scripts/cli_helpers/generate_experiments.py'.format(diva_source_dir),
          '{}/scripts/cli_helpers/merge_videos.py'.format(diva_source_dir),
          '{}/scripts/eo_to_ir/eo_to_ir.py'.format(diva_source_dir)],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Topics :: Test',
      ])
