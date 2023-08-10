import toolkit.data_analysis as da
import seaborn as sns
import pandas as pd
import util.os_utils as osu
import pytest

test_path = './output/'
test_path_raw = test_path + 'raw/'

iris  = sns.load_dataset('iris')    
pengs = sns.load_dataset('penguins')
taxis = sns.load_dataset('taxis')

test_df = pd.DataFrame({})

class TestClass_DataExtraction_Reduction(da.DataExtractionClass):
    def __init__(self,path,app):
        super(TestClass_DataExtraction_Reduction, self).__init__(  path=path,
                                                            app=app)
        self.extracton_func = self.reduce_dataframes

    @staticmethod
    def reduce_dataframes(path):
        df = pd.read_feather(path)
        return df

@pytest.mark.dependency()
def test_MakeTest():
    osu.mkdir(test_path_raw)
    iris.to_feather(test_path_raw + 'iris.feather')
    pengs.to_feather(test_path_raw + 'pengs.feather')
    taxis.to_feather(test_path_raw + 'taxis.feather')
    try:
        test_reduction_obj = TestClass_DataExtraction_Reduction(path=test_path_raw,app='test')
        test_reduction_obj.extract()
        test_df = test_reduction_obj.df
    except Exception as e:
        print(e)
        assert False


@pytest.mark.dependency(depends=['test_MakeTest'])
def test_base_class_dataframe_lenght():
    assert len(test_df) == len(iris) + len(pengs) + len(taxis)

@pytest.mark.dependency(depends=['test_MakeTest'])
def test_base_class_dataframe_correctness():
    assert test_df.equals(iris.append(pengs).append(taxis))