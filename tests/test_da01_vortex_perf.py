import toolkit.data_analysis as da
import toolkit.util.os_utils as osu

import pytest
import os
import pandas as pd


class TestClass_VortexExtraction():
    test_path = './tmp/'
    input_archive = './tests/inputs/vortex-perf-extraction-class-test-input'
    test_path_dir = test_path + 'scripts/outputs/IISWC-COMP-vecadd/'
    df_golden = test_path_dir + 'dataframe-golden.feather'

    @pytest.mark.run('first')
    def test_vortex_perf_extraction(self):
        osu.mkdir(self.test_path)
        osu.cmd('tar -xzf {} -C {}'.format(self.input_archive, self.test_path))
        os.rename(self.test_path_dir + 'dataframe.feather', self.df_golden)
        df_golden = pd.read_feather(self.df_golden)
        test_extraction_obj = da.VortexPerfExtractionClass(path=self.test_path_dir,app='test')
        test_extraction_obj.extract()
        assert pd.read_feather(self.test_path_dir + 'dataframe.feather').equals(df_golden)

    @pytest.mark.run('last')
    def test_cleanup(self):
        osu.cmd('rm -rf {}'.format(self.test_path))