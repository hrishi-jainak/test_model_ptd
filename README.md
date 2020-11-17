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

Maximize SUM(m_val_of_cell * p_t_d_bin_var )

Constraints        

Linking constraints

i)	Link between p_t_d_binary variable and p_t_d_val variable

For every cell value is of selected p_t_d_binary variable * D of that variable

SUM( D * p_d_t_bin_var) = p_t_d_val  ...For all P and T..

ii)	Link between p_t_d_binary variable and p_d_row variable

Even if once p_t_d_bin var for all column T if D is selected then for that P row occurrence of D has happened

P_d_row_var <= SUM( p_d_t_bin_var) <= length(t) * p_d_row_var   ....For all P 

iii)	Link between p_t_d_binary variable and t_d column variable

Even if once p_t_d_bin var for all row P if D is selected then for that T column occurrence of D has happened

t_d column_var <= SUM( p_d_t_bin_var) <= length(p) * t_d column_var ...For all P 

Constraints

Constraint 12

Constraint that only one value of D for cell P - T is to be selected
        
sum( p_t_d_bin_var) = 1 ....for given P and T cell

Constraint 9 

summation of u values across grid to be more than u_grid

SUM(u_val_of_all_cell _ptd* p_t_d_bin_var) >= u_grid_threshold ...sum for given entire grid
        ie. for all p,t,d values
        
Constraint 7 

Summation of u values across row i.e. for given P  to be less than u_max_row

Assumption this is same as part 2 of constraint 9 If this assumption is wrong then have to add separately
 
SUM(u_val_of_cell * p_t_d_bin_var ) <= u_max_row   ...sum for given row ie. for given P

Constraint 6 

If there is min and max value of D for row P

d_min < = p_t_d_var_value <= d_max

Constraint 10

Smmation of u values across grid to be more than M_grid

SUM(m_val_of_cell * p_t_d_bin_var )>= m_threshold

Note this is basically objective function which we are maximizing, So ideally this is not to be added separately. If objective value of solution is greater than this given threshold value, then this constraint will become automatically valid

Constraint 11

If order for row of D is given ascending or descending, then adding constraint

for ascending p_t1_d_var_value <= p_t2_d_var_value

for descending p_t1_d_var_value >= p_t2_d_var_value ...for all row P

Constraint 5 

Difference between successive D in a row p

 x <= p_t2_d_var_value - p_t1_d_var_value <= y …for all row P and t2 and t1 are consecutive x,y are least and most difference

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

