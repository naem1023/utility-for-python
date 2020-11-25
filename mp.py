import multiprocessing 
import parmap 
import numpy as np 

num_cores = multiprocessing.cpu_count() # 12 

def square(input_list): 
    print("input_list", input_list)
    return [x*x for x in input_list] 
    
data = list(range(1, 25)) 

splited_data = np.array_split(data, num_cores) 
splited_data = [x.tolist() for x in splited_data] 

result = parmap.map(square, splited_data, pm_pbar=True, pm_processes=num_cores)

print(result)
