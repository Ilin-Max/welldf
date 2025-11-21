import lasio
import pandas
import numpy as np
import matplotlib.pyplot as plt


def read_well(filepath: str, **kwargs) -> WellFrame:
    """
    Чтение скважинных данных из различных форматов
    """
    import lasio
    
    if filepath.endswith('.las'):
        return _read_las(filepath, **kwargs)
    elif filepath.endswith('.csv'):
        return _read_csv(filepath, **kwargs)
    else:
        raise ValueError(f"Формат файла {filepath} не поддерживается")

def _read_las(las_path: str, **kwargs) -> WellFrame:
    """Чтение LAS файлов"""
    import lasio
    
    las = lasio.read(las_path)
    df = las.df()
    
    # Создаем WellFrame
    well_data = WellFrame(df, well_name=las.well['WELL'].value, **kwargs)
    
    # Сохраняем метаданные LAS
    well_data.metadata.update({
        'las_header': {
            'well': {item.mnemonic: item.value for item in las.well},
            'curves': {item.mnemonic: item.descr for item in las.curves},
            'parameters': {item.mnemonic: item.value for item in las.parameters}
        }
    })
    
    return well_data

def _read_csv(csv_path: str, depth_col: str = 'DEPT', **kwargs) -> WellFrame:
    """Чтение CSV файлов"""
    df = pandas.read_csv(csv_path, **kwargs)
    
    if depth_col not in df.columns:
        raise ValueError(f"Столбец глубины {depth_col} не найден")
    
    # Устанавливаем глубину как индекс
    df = df.set_index(depth_col)
    df.index.name = 'DEPTH'
    
    return WellFrame(df, **kwargs)


class WellSeries(pandas.Series):
    @property
    def _constructor(self):
        return WellSeries
    
    @property 
    def _constructor_expanddim(self):
        return WellFrame
    
    def plot(self, **kwargs):
        """Специальный plot для каротажных кривых"""
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (8, 10)))
        
        ax.plot(self.values, self.index, **kwargs)
        ax.set_ylabel('Depth (m)')
        ax.set_xlabel(self.name)
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()  # Глубина сверху вниз
        
        return fig, ax

class WellFrame(pandas.DataFrame):
    @property
    def _constructor(self):
        return WellFrame
    
    @property
    def _constructor_sliced(self):
        return WellSeries
    
    def __init__(self, *args, **kwargs):
        super.__init__()

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(result, pandas.Series):
            return WellSeries(result, name=key)
        return result
        
    