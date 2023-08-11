import toolkit.data_analysis as da
import seaborn as sns
import pandas as pd
import toolkit.util.os_utils as osu
import pytest

test_path = './tmp/'
test_path_raw = test_path + 'raw/'

iris  = sns.load_dataset('iris')
iris["ID"] = [i for i in range(len(iris))]
pengs = sns.load_dataset('penguins')
pengs["ID"] = [i for i in range(len(iris), len(iris) + len(pengs))]
taxis = sns.load_dataset('taxis')
taxis["ID"] = [i for i in range(len(iris) + len(pengs), len(taxis) + len(iris) + len(pengs))]

checkpoint_df = pd.DataFrame({'ID':[i for i in range(len(iris) + len(pengs) + len(taxis))]})

test_df = pd.DataFrame({})

class TClass_DataExtraction_Reduction(da.DataExtractionClass):
    def __init__(self,path,app):
        super(TClass_DataExtraction_Reduction, self).__init__(  path=path,
                                                            app=app)
        self.extracton_func = self.reduce_dataframes

    @staticmethod
    def reduce_dataframes(path):
        df = pd.read_feather(path)
        return df

@pytest.mark.run('first')
def test_MakeTest():
    osu.mkdir(test_path_raw)
    iris.to_feather(test_path_raw + 'iris.feather')
    pengs.to_feather(test_path_raw + 'pengs.feather')
    taxis.to_feather(test_path_raw + 'taxis.feather')
    checkpoint_df.to_feather(test_path + 'checkpoint.feather')
    try:
        test_reduction_obj = TClass_DataExtraction_Reduction(path=test_path,app='test')
        test_reduction_obj.extract()
    except Exception as e:
        print(e)
        assert False

def test_import_dataframe():
        _ = pd.read_feather(test_path + 'dataframe.feather')

def test_base_class_dataframe_lenght():
    test_df = pd.read_feather(test_path + 'dataframe.feather')
    assert len(test_df) == len(iris) + len(pengs) + len(taxis)

def test_rerun():
    test_MakeTest()

def test_cleanup():
    osu.cmd('rm -rf {}'.format(test_path))