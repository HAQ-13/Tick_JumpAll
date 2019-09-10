import pandas as pd

# /DataLibrary/futures/ticks/201809/DCE/20180906/p1901_20180906.csv
file = 'data/ticks/201809/DCE/20180903/y1901_20180903.csv'
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

result = pd.DataFrame(columns=['TradeDay', '0_jump', '1_jump', '-1_jump', '2_jump', '-2_jump', 'others', 'sum'])
result.loc[0, 'TradeDay'] = df.loc[0, 'TradingDay']
result.loc[0, '0_jump'] = _df.loc[0, 'varPrice']
result.loc[0, '1_jump'] = _df.loc[2, 'varPrice']
result.loc[0, '-1_jump'] = _df.loc[-2, 'varPrice']
result.loc[0, '2_jump'] = _df.loc[4, 'varPrice']
result.loc[0, '-2_jump'] = _df.loc[-4, 'varPrice']
result.loc[0, 'others'] = _sum - _df.loc[0, 'varPrice'] - _df.loc[2, 'varPrice'] - _df.loc[-2, 'varPrice'] - _df.loc[
    4, 'varPrice'] - _df.loc[-4, 'varPrice']
result.loc[0, 'sum'] = _sum

out_file = 'output/result_for_one.csv'
result.to_csv(out_file, index=False)
