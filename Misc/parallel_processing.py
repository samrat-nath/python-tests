"""
Testing Pandas Parallel Processing
"""
# import os
import numpy as np
import pandas as pd
import time
# import multiprocessing as mp
import swifter

# num_cores = os.cpu_count()

# def parallelize_dataframe(df, func, n_cores = 2):
#     df_split = np.array_split(df, n_cores)
#     pool = Pool(n_cores)
#     df = pd.concat(pool.map(func, df_split))
#     pool.close()
#     pool.join()
#     return df

def my_func(df):
    return df['A'] + df['B']

# if __name__ == '__main__':
n_rows = 1e6
df = pd.DataFrame(
    data={'A':np.arange(n_rows),
          'B':np.arange(n_rows,0,-1)}
    )

tic = time.time()
df['C'] = df.apply(my_func, axis=1)
toc = time.time()
print('Time taken without Multi-processing: {}s.'.format(round(toc-tic,2)))

# p = mp.Pool(mp.cpu_count()) # Data parallelism Object
tic = time.time()
# df_out2 = parallelize_dataframe(df_in, my_func)
# df_out2 = p.map(my_func, df_in)
df['C'] = df.swifter.apply(my_func, axis=1)
toc = time.time()
print('Time taken with Multi-processing: {}s.'.format(round(toc-tic,2)))
print(df.head())

tic = time.time()
df['C'] = my_func(df)
toc = time.time()
print('Time taken with Vectorization: {}s.'.format(round(toc-tic,2)))
