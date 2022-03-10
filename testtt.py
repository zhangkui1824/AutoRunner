import pandas as pd
if __name__ == '__main__':
    df = pd.read_excel('./stu.xlsx',)
    print(df)
    df=df.iloc[:,:]
    del (df.iloc['姓名'])
    print(df)
    df.to_excel('./3.xlsx')
    nrows = df.shape[0]
    ncols = df.columns.size
    print(df.columns)
    stuno_list = []

    for i in range(0, nrows):
        stuno_list.append(df.iloc[i,0])
    print(stuno_list)