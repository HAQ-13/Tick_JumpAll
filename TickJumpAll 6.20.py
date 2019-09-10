import pandas as pd

fn_all_file = 'data/files.csv'
df_all_file = pd.read_csv(fn_all_file)

# 为读取多份文件作预处理
df_all_file['TradeMonth'] = df_all_file['TradeDay'].astype(str).str.slice(stop=6)
df_all_file['filename'] = df_all_file['InstrumentID'].str.cat(df_all_file['TradeDay'].astype(str), sep='_')

rst = []
for idx, row in df_all_file.iterrows():
    _trademonth = row['TradeMonth']
    _tradeday = row['TradeDay']
    fn = 'data/ticks/{0}/DCE/{1}/{2}_{3}.csv'.format(_trademonth, _tradeday, row['InstrumentID'], _tradeday)
    df = pd.read_csv(fn, encoding='gbk')
    df['varVol'] = df['Volume'] - df['Volume'].shift(1)
    _df = df[df['varVol'] != 0]
    _df['varPrice'] = df['LastPrice'] - df['LastPrice'].shift(1)
    _df = pd.DataFrame(_df['varPrice'].value_counts())
    _df['jumps'] = _df.index / 2
    _sum = _df['varPrice'].sum()
    _df['pct'] = _df['varPrice'] / _sum
    _df.sort_values('jumps', inplace=True)

    rst.append({"TradeDay": _tradeday, "Jumps_0": _df.loc[0, 'varPrice'], "Jumps_1": _df.loc[2, 'varPrice']})

df = pd.DataFrame(rst)
df.to_csv('output/result.csv', index=False)
