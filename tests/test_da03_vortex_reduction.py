import toolkit.data_analysis as da
import toolkit.util.os_utils as osu

import pytest
import os
import pandas as pd
import yaml
import warnings

class TestClass_VortexExpReduction():
    test_path = './tmp/'
    input_archive = './tests/inputs/vortex-post-processing-class-test-input'
    yml_file = './tests/inputs/REDU-gcn.yml'
    test_path_dir = test_path + 'outputs/'
    df_path_dir = test_path_dir + 'IISWC-COMP-gcn/dataframe.feather'
    merge_on = ["clusters", 
                "cores",
                "warps",
                "threads",
                "local_worksize"]

    @pytest.mark.run('first')
    def test_vortex_exp_red_run(self):
        osu.mkdir(self.test_path)
        osu.cmd('tar -xzf {} -C {}'.format(self.input_archive, self.test_path))
        os.rename(self.test_path_dir + 'IISWC-COMP-gcn/dataframe.feather', self.test_path_dir + 'IISWC-COMP-gcn/dataframe.feather.golden')
        test_extraction_obj = da.VortexExperimentReductionClass(path=self.test_path_dir,app='test', yml_file=self.yml_file)
        test_extraction_obj.extract()

    def test_vortex_cycle_reduction(self):
        df      = pd.read_feather(self.df_path_dir)
        dfgm    = pd.read_feather(self.df_path_dir + '.golden')
        merged  = pd.merge(df, dfgm, on=self.merge_on, suffixes=('_t', '_gm'))
        assert    merged['cycles_t'].equals(merged['cycles_gm'])

    @pytest.mark.run('last')
    def test_cleanup(self):
        osu.cmd('rm -rf {}'.format(self.test_path))