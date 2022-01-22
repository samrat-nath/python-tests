"""
Testing genetic algorithm using pymoo package
@author: Samrat Nath

https://pymoo.org/customization/discrete.html
https://pymoo.org/problems/definition.html
https://pymoo.org/algorithms/soo/ga.html#nb-ga
"""

## Importing Libraries
import numpy as np
from pymoo.factory import get_algorithm, get_crossover, get_mutation, get_sampling
from pymoo.optimize import minimize
from pymoo.core.problem import Problem

## Global variables for a custom knapsack problem
v = np.array([4, 2, 1, 10, 2])  # values
w = np.array([12, 2, 1, 4, 1])     # weights
C = 15                               # weight capacity
# x = [0, 1, 1, 0, 1, 0]             # sample solution  

class MyProblem(Problem):
    # Definition of a custom Knapsack problem
    def __init__(self):
        super().__init__(n_var=5,
                         n_obj=1,
                         n_constr=1,
                         xl=0,
                         xu=1,
                         type_var=int
                         )

    def _evaluate(self, x, out, *args, **kwargs):
        # Objective and Constraint functions
        out["F"] = -np.sum(x*v, axis=1)      # Objetive Value
        out["G"] = np.sum(x*w, axis=1) - C   # Weight Constraint

method = get_algorithm("ga",
                       pop_size=20,
                       sampling=get_sampling("int_random"),
                       crossover=get_crossover("int_sbx", prob=1.0, eta=3.0),
                       mutation=get_mutation("int_pm", eta=3.0),
                       eliminate_duplicates=True,
                       )

res = minimize(MyProblem(),
               method,
               termination=('n_gen', 30),
               seed=1,
               save_history=True
               )

print("Best solution found: %s" % res.X)
print("Function value: %s" % res.F)
print("Constraint violation: %s" % res.CV)

#%% Visualization of Convergence 

import matplotlib.pyplot as plt
# number of evaluations in each generation
n_evals = np.array([e.evaluator.n_eval for e in res.history])  
# optimum value in each generation
opt = np.array([e.opt[0].F for e in res.history])

plt.title("Convergence")
plt.plot(n_evals, opt, "--")
plt.show()