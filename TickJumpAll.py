import pandas as pd
from arch import arch_model

# /DataLibrary/futures/ticks/201809/DCE/20180906/p1901_20180906.csv
# 读取包含所有文件信息的csv文件
all_file = 'data/files.csv'
all_file_df = pd.read_csv(all_file)

# 为读取多份文件作预处理
all_file_df['TradeMonth'] = all_file_df['TradeDay'].astype(str).str.slice(stop=6)
all_file_df['filename'] = all_file_df['InstrumentID'].str.cat(all_file_df['TradeDay'].astype(str), sep='_')

# 初始化result
result = pd.DataFrame(columns=['TradeDay', '0_jump', 'abs1_jump', 'abs2_jump', 'others', 'sum'])

for i in range(all_file_df.shape[0]):
    file = 'data/ticks/{0}/DCE/{1}/{2}.csv'.format(all_file_df.loc[i, 'TradeMonth'], all_file_df.loc[i, 'TradeDay'],
                                                   all_file_df.loc[i, 'filename'])
    df = pd.read_csv(file, encoding='gbk')

    df.sort_values(by=['TradingDay', 'UpdateTime', 'UpdateMillisec'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['varVol'] = df['Volume'] - df['Volume'].shift(1)

    _df = df[df['varVol'] != 0]
    _df['varPrice'] = df['LastPrice'] - df['LastPrice'].shift(1)
    _df = pd.DataFrame(_df['varPrice'].value_counts())
    _df['jumps'] = _df.index / 2
    _sum = _df['varPrice'].sum()
    _df['pct'] = _df['varPrice'] / _sum
    _df.sort_values('jumps', inplace=True)

    result.loc[i, 'TradeDay'] = df.loc[0, 'TradingDay']
    result.loc[i, '0_jump'] = _df.loc[0, 'varPrice']
    result.loc[i, 'abs1_jump'] = _df.loc[2, 'varPrice'] + _df.loc[-2, 'varPrice']
    result.loc[i, 'abs2_jump'] = _df.loc[4, 'varPrice'] + _df.loc[-4, 'varPrice']
    result.loc[i, 'others'] = _sum - _df.loc[0, 'varPrice'] - _df.loc[2, 'varPrice'] - _df.loc[-2, 'varPrice'] - \
                              _df.loc[4, 'varPrice'] - _df.loc[-4, 'varPrice']
    result.loc[i, 'sum'] = _sum

# EWMA
# 0jump的std最大，直接相减得出
result['ewma_1_jump'] = result['abs1_jump'].ewm(span=10, min_periods=10).mean()
result['ewma_2_jump'] = result['abs2_jump'].ewm(span=10, min_periods=10).mean()
result['ewma_0_jump'] = result['sum'] - result['ewma_1_jump'] - result['ewma_2_jump']

out1_file = 'output/result.csv'
result.to_csv(out1_file, encoding='gbk', index=False)

"""
# GARCH
out2_file = 'output/garch.csv'
garch1 = arch_model(result['0_jump'].astype('double'), p=1, q=1)
res1 = garch1.fit(update_freq=10)
print(res1.summary())
garch2 = arch_model(result['abs1_jump'].astype('double'), p=1, q=1)
res2 = garch2.fit(update_freq=10)
print(res2.summary())
garch3 = arch_model(result['abs2_jump'].astype('double'), p=1, q=1)
res3 = garch3.fit(update_freq=10)
print(res4.summary())

"""
