# test_model_ptd
test_pulp_model

You can run model by simply running test.py file
It first read ip_data.csv file which as input grid data
It also need arguments for class TestModel for various constraints which can be added when class is called
This code will generate .lp file of model which is made using Pulp and will solve using pulp's default cbc solver
In the end it will save output solution_pulp_test_model.csv file which has PTD data of selected decision variables in final output 
Model
Variable needed 
Decision variables 
p_t_d_binary variable – if variable is selected (equal to 1) meaning for given row P and column T value D is selected and 0 refers to not selected
p_t_d_val variable – its value is that of value of D in selected binary variable p_t_d
p_d_row variable – its indicator of if for row P at any column T value D is selected or not, meaning for given row if any times value D is selected this variable will take value 1
t_d_column variable – its indicator of if for column T at any row P value D is selected or not, meaning for given column T if any times value D is selected this variable will take value 1
Objective function
Maximize 
Constraints        SUM(m_val_of_cell * p_t_d_bin_var )
Linking constraints
i)	Link between p_t_d_binary variable and p_t_d_val variable
For every cell value is of selected p_t_d_binary variable * D of that variable
SUM( D * p_d_t_bin_var) = p_t_d_val  
For all P and T..
ii)	Link between p_t_d_binary variable and p_d_row variable
Even if once p_t_d_bin var for all column T if D is selected then for that P row occurrence of D has happened
P_d_row_var <= SUM( p_d_t_bin_var) <= length(t) * p_d_row_var 
For all P 
iii)	Link between p_t_d_binary variable and t_d column variable
Even if once p_t_d_bin var for all row P if D is selected then for that T column occurrence of D has happened
t_d column_var <= SUM( p_d_t_bin_var) <= length(p) * t_d column_var 
For all P 
Constraints
Constraint 12
        Constraint that only one value of D for cell P - T is to be selected
        sum( p_t_d_bin_var) = 1 ....for given P and T cell

Constraint 9 
summation of u values across grid to be more than u_grid
        SUM(u_val_of_all_cell _ptd* p_t_d_bin_var) >= u_grid_threshold ...sum for given entire grid
        ie. for all p,t,d values
Constraint 7 
summation of u values across row i.e. for given P  to be less than u_max_row
 Assumption this is same as part 2 of constraint 9 If this assumption is wrong then have to add separately
        SUM(u_val_of_cell * p_t_d_bin_var ) <= u_max_row   ...sum for given row ie. for given P

Constraint 6 
 if there is min and max value of D for row P
d_min < = p_t_d_var_value <= d_max
Constraint 10 
 summation of u values across grid to be more than M_grid
        SUM(m_val_of_cell * p_t_d_bin_var )>= m_threshold
 Note this is basically objective function which we are maximizing, So ideally this is not to be added separately. If objective value of solution is greater than this given threshold value, then this constraint will become automatically valid

Constraint 11
If order for row of D is given ascending or descending, then adding constraint
        for ascending p_t1_d_var_value <= p_t2_d_var_value
        for descending p_t1_d_var_value >= p_t2_d_var_value
….for all row P

Constraint 5 
Difference between successive D in a row p
 x <= p_t2_d_var_value - p_t1_d_var_value <= y
 …for all row P and t2 and t1 are consecutive x,y are least and most difference

Constraint 3
 If times of minimum or maximum unique occurrence of D in a row P is given
           i<= sum(p_d_row_var) <= j   ... for every row of P
 p_d_row_var is 1 if even one p_t_d variable is selected then for given row P , D is occurred once

Constraint 1 ,2
Assumption that groups are along each column of T           
To divide column of T into N groups row wise ie. unique occurrence of assignment of D in column T is equal to number N
           Sum(t_d_column_var) == N   ... for every column of T
           p_t_column_var is 1 if even one p_t_d  variable is selected then for given column T ,   D is occurred once

Constraint 8 
 Difference between D values of N groups in a column T
        A<= D2 * t_d2_column_var - D1 * t_d1_column_var <= B .... for all column T
    A,B are least and most difference

Note : Following  Constraint no. 4 is not built as it will require little more time than I had
Duration of each level for a row is at least L and at most M, duration means successive cells having same value of decision variable  


What is needed :
1.	Model for above written in python PuLP, if it is not possible for you to write the model, provide pseudocode / some sort of detail instructions from which it can be easily written
Almost most of model is written 
2.	Answer to following questions :
i.	Is there a different way of framing this problem which is better than the matrix view ? i.e. array of sets, set of sets or any other way? Why so?
I think this is best way to store data in db with P,T and D as primary keys and data is not hard to manipulate or loop to make other data structure
As of now I cant think of its drawbacks but might need more time if performance issue occur to build the model
ii.	What is the suggested choice of open source solver ?
I am aware of only few of open source solver in CBC (called using pulp),lp_solve,ampl ,glpk, But used only CBC till now. So I would suggest that, did not get chance to test and compare others
iii.	We also can access a Gurobi solver, in that case is it advisable to write it in any different way, i.e. not through PuLP ?
Yes it is advisable to write in Gurobi as there are hundreds of parameters you can use to test and change while solving the problem if you are using Gurobi solver. But strictly speaking writing can be done in pulp and that model can be solved using other solver through pulp but get limited options . As one case you cant feed the lp file generated using pulp to Cplex as those are not compatible but you can call cplex solver through pulp but its inconvinient
iv.	Is there any advantage in writing this in specific OR modeling language like minizinc?
I did not used minizinc till now as I used Gurobi,pulp or cplex library till now
v.	What can be done to optimize the model i.e. can anything specifically be done for symmetry breaking etc.?
I have to think (cant say within this limited time looking at problem) and look at the data to see about symmetry breaking or adding heuristics or extra constraints .
vi.	Is it better to create a custom algo to do this rather than using a solver ? how much better will be the performance? Note that we have not yet written this problem and do not know what will be the performance.
Its not easy to say right now as have to determine how and which metaheuristic algos can be used . Also it will depend on how easily feasible solution is gettable as there might be infeasibility as in current state some constraints seems contradictory
vii.	We believe this problem can be infeasible due to either constraint 7,9 or 10. Is there a way for the model to throw out which of these three constraints are failing? 
As I mentioned constraint 10 is basically your objective function and you are forcing it to be true which problem might not attend that value . I would suggest removing it.
As for 7 and 9 I need more understanding about model and actual business sense to see if these constraints are correct or not.

In your responses you may assume that we have solved similar, slightly less complicated problems using PuLP and open source solvers and gurobi solver. The team does not have extensive OR experience or formal training in OR but is conversant with Python coding and Machine Learning coding. It is best if you can provide us code but if not possible, kindly suggest what effort is most feasible for you.

What is needed :
1.  A MIP solution for the maximization problem.
Model built
2. We expect you to submit a working code in Python preferably using PuLP with a detailed document explaining the mathematical model constructed.
As for documentation I have written comments in code to which constraint and variables are added how. And this document have all model equations.
3. Submitting using Git with git history, well-documented code, readme will be a plus.
As code is readable and quite understandable if you have understanding of operations research. As for documentation I could not get more time to do it properly
Also I just have made Git account to submit this and will be uploading my other projects in short while
4. Please explain variables and constants used properly including temporary variables.
This doc contains these at the start
5. You are free to assume that all values will be less than 999999. 
6. Answer to following questions:
a. What are the complications you faced while developing the solution.
This problem has decent complexity as some constraints are hard to write and will need bit more time than 2 3 days to write model plus code. Also need to look at actual business sense as some constraints I feel might be contradictory
b. What are points of infeasibility and what is the approach you can take to prevent an infeasible solution.
As previously mentioned, constraint 10 and 9 might make it infeasible. Also minimum and maximum in row for D , order od increasing /decreasing D ,differences between successive D values these might contradict each other for certain values. 
To remove infeasibility, I need to look at input data and all possible input parameters and arrive some preprocessing to find inconsistencies in these parameters. At this point I can’t suggest anything for certain.
c. Is there any other approach you would like to take to solve this problem? 
One might try to find somehow feasible solution and try genetic algorithm or simulated annealing. But I have not seen such problem before to comment about how to get initial feasible solution

