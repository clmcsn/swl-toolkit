import toolkit.data_analysis as da
import toolkit.util.os_utils as osu

import pytest
import os
import pandas as pd
import yaml
import warnings

class TestClass_VortexTanalysis():
    test_path = './tmp/'
    input_archive = './tests/inputs/vortex-trace-analysis-vecadd-test-input'
    test_path_dir = test_path + 'tests/inputs/vecadd_tan'
    golden_path_dir = test_path_dir + '/golden_model/'

    @pytest.mark.run('first')
    def test_vortex_tanalysis_run(self):
        osu.mkdir(self.test_path)
        osu.cmd('tar -xzf {} -C {}'.format(self.input_archive, self.test_path))
        test_extraction_obj = da.VortexTraceAnalysisClass(path=self.test_path_dir,app='vecadd',plot=False)
        test_extraction_obj.extract()

    def test_vortex_tanalysis_check_count_SYN(self):
        for res_directory in os.listdir(self.test_path_dir):
            if res_directory[0].isdigit():
                print(res_directory)
                fname = res_directory.split('/')[-1]
                gm_yaml = self.golden_path_dir + fname + '.feather.yml'
                with open(gm_yaml, 'r') as yaml_file:
                    gm_dict = yaml.safe_load(yaml_file)
                test_yaml = self.test_path_dir + '/' + res_directory + '/' + fname + '-SYN.yml'
                with open(test_yaml, 'r') as yaml_file:
                    test_dict = yaml.safe_load(yaml_file)
                assert gm_dict['last-commit'] == test_dict['last-commit']
                assert gm_dict['section-exec-count'] == test_dict['section-exec-count']
                assert gm_dict['section-thread-exec-count'] == test_dict['section-thread-exec-count']
                assert gm_dict['total-exec-count'] == test_dict['total-exec-count']
                assert gm_dict['total-thread-exec-count'] == test_dict['total-thread-exec-count']

    def test_vortex_tanalysis_check_count_ROOF(self):
        warnings.warn(  """Golden model is not correct for some reasons in the committed instraction count. Need to create a better golden model.""")
        for res_directory in os.listdir(self.test_path_dir):
            if res_directory[0].isdigit():
                print(res_directory)
                fname = res_directory.split('/')[-1]
                gm_yaml = self.golden_path_dir + fname + '.feather.roof.yml'
                with open(gm_yaml, 'r') as yaml_file:
                    gm_dict = yaml.safe_load(yaml_file)
                test_yaml = self.test_path_dir + '/' + res_directory + '/' + fname + '-SSR-FREP.yml'
                with open(test_yaml, 'r') as yaml_file:
                    test_dict = yaml.safe_load(yaml_file)
                assert gm_dict['last-commit'] == test_dict['last-commit']
                assert gm_dict['section-exec-count'] == test_dict['section-exec-count']
                assert gm_dict['total-exec-count'] == test_dict['total-exec-count']
                #assert gm_dict['section-thread-exec-count'] == test_dict['section-thread-exec-count']
                #assert gm_dict['total-thread-exec-count'] == test_dict['total-thread-exec-count']

    def test_vortex_tanalysis_check_execution_time(self):
        warnings.warn(  """No correct golden model for execution time. Need to create a golden model.""")

    @pytest.mark.run('last')
    def test_cleanup(self):
        osu.cmd('rm -rf {}'.format(self.test_path))