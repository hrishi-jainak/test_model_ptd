
import pandas as pd
import pulp
import time
import os


class TestModel:

    def __init__(self,n=None,i=None,j=None,l=None,m=None,a=None,b=None,x=None,y=None,
                 umax_row=None,u_threshold=None,u_row_threshold=None,mthreshold=None,
                 p_d_value_dict=None,p_row_d_value_order = None):
        self.start_time = time.time()
        self.run_time = 1000
        # if you want to run for specific  solver time and get solution at that point
        # Read inputs and set class objects

        self.ip_df = pd.read_csv("ip_data.csv")

        # list of unique P,T,and D
        self.list_p = self.ip_df['P'].drop_duplicates().to_list()
        self.list_t = self.ip_df['T'].drop_duplicates().to_list()
        self.list_d = self.ip_df['D'].drop_duplicates().to_list()
        self.list_d.sort()

        self.n_groups = n
        self.i_least_d_values = i
        self.j_most_d_values = j
        self.l_least_successive_d = l
        self.m_most_successive_d = m
        self.a_least_column_val_diff = a
        self.b_most_column_val_diff = b
        self.x_least_successive_diff_in_row_d = x
        self.y_most_successive_diff_in_row_d = y
        self.u_max_row = umax_row
        self.u_row_threshold = u_row_threshold
        # TODO Assumption
        # Assumption u_max_row ---constraint 7  and   u_row_threshold ---part of constraint 9 are same

        self.u_grid_threshold = u_threshold
        self.m_threshold = mthreshold
        # Here p_d_value dictionary is in form of
        # {'P1':[10,40],'P2':[30,50]} ie. P dimension as key with Dmin and Dmax as its value
        self.p_d_value_dict = p_d_value_dict
        self.p_row_d_value_order = p_row_d_value_order


        # For variable creation
        self.ip_dict = self.ip_df.set_index(['P','T','D']).T.to_dict('list')


        # maximisation model
        self.model = pulp.LpProblem(name="test_model", sense=pulp.LpMaximize)

        # Objective function
        self.objective = pulp.LpConstraintVar(name='objective_function')
        self.model.setObjective(self.objective)

        self.ptd_bin_var_dict = {}
        self.pt_d_value_var_dict = {}
        self.pd_row_var_dict = {}
        self.td_column_var_dict = {}

        self.cons_pdt_bin_pdt_val_relation_dict = {}
        self.cons_pdt_bin_pd_row_relation_dict = {}
        self.cons_pdt_bin_td_column_relation_dict = {}

        self.cons_ptd_var_dict = {}
        self.cons_unique_pt_dict = {}
        self.cons_u_grid_threshold = {}
        self.cons_u_max_row = {}
        self.cons_p_d_value_range = {}
        self.cons_m_grid_threshold = {}
        self.cons_p_row_d_order_dict = {}
        self.cons_p_row_d_successive_diff_most_dict = {}
        self.cons_p_row_d_successive_diff_least_dict = {}
        self.cons_p_row_d_occurrence_least_dict = {}
        self.cons_p_row_d_occurrence_most_dict = {}
        self.cons_td_column_group_dict = {}
        self.cons_t_column_d_value_diff_least_dict = {}
        self.cons_t_column_d_value_diff_most_dict = {}
        print('hi')


    def add_unique_pt_con(self):
        '''
        Constraint 12
        Constraint that only one value of D for cell P - T is to be selected
        sum( p_t_d_bin_var) = 1 ....for given P and T cell

        '''
        for p in self.list_p:
            for t in self.list_t:
                constraint_name = 'con_unique_pt_p' + str(p) + '_t' + str(t)
                unique_pt_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintEQ,
                                                            rhs=1)

                self.model.addConstraint(unique_pt_constraint.constraint)

                self.cons_unique_pt_dict[p,t] = unique_pt_constraint


    def add_u_grid_threshold_con(self):
        '''
        # adding constraint 9 : of minimum summation of u values across grid to be more than u_grid
        SUM(u_val_of_cell * p_t_d_bin_var) <= u_grid_threshold ...sum for given entire grid
        ie. for all p,t,d values
        '''
        if self.u_grid_threshold:
            constraint_name = 'con_u_grid_threshold'
            u_grid_threshold_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                               sense=pulp.LpConstraintGE,
                                                               rhs=self.u_grid_threshold)

            self.model.addConstraint(u_grid_threshold_constraint.constraint)

            self.cons_u_grid_threshold['u_grid'] = u_grid_threshold_constraint


    def add_u_row_max_con(self):
        '''
        adding constraint 7 : of minimum summation of u values across row i.e. for given P
        to be less than u_max_row
        Assumption this is same as part 2 of constraint 9
        If this assumption is wrong then have to add separately
        SUM(u_val_of_cell * p_t_d_bin_var ) <= u_max_row   ...sum for given row ie. for given P
        '''

        if self.u_max_row:
            for p in self.list_p:
                constraint_name = 'con_u_max_row_p' + str(p)
                u_max_row_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintLE,
                                                            rhs=self.u_max_row)

                self.model.addConstraint(u_max_row_constraint.constraint)

                self.cons_u_max_row[p] = u_max_row_constraint


    def add_p_d_value_range_con(self):
        '''
        adding constraint 6 : if there is min and max value of D for row P
        d_min < = p_t_d_var_value <= d_max

        '''
        if self.p_d_value_dict:
            for p,d in self.p_d_value_dict.items():

                constraint_name = 'con_p_d_min_p' + str(p)
                p_d_min_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintGE,
                                                          rhs=d[0])

                self.model.addConstraint(p_d_min_constraint.constraint)

                self.cons_p_d_value_range[p,'min'] = p_d_min_constraint

                constraint_name = 'con_p_d_max_p' + str(p)
                p_d_max_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintLE,
                                                          rhs=d[1])

                self.model.addConstraint(p_d_max_constraint.constraint)

                self.cons_p_d_value_range[p, 'max'] = p_d_max_constraint


    def add_m_grid_threshold_con(self):
        '''
        adding constraint 10 : of minimum summation of u values across grid to be more than m_grid
        SUM(m_val_of_cell * p_t_d_bin_var )>= m_threshold
        Note this is basically objective function which we are maximising
        SO ideally this is not to be added separately
        If objective value of solution is greater than this given threshold value,then this constraint will
        become automatically valid
        '''
        if self.m_threshold:
            constraint_name = 'con_m_grid_threshold'
            m_grid_threshold_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintGE,
                                                               rhs=self.m_threshold)

            self.model.addConstraint(m_grid_threshold_constraint.constraint)

            self.cons_m_grid_threshold['m_grid'] = m_grid_threshold_constraint


    def add_p_row_d_value_order_con(self):
        '''
        Adding constraint 11
        If order for row of D is given ascending or descending then adding constraint
        for ascending  p_t1_d_var_value <= p_t2_d_var_value
        for descending  p_t1_d_var_value >= p_t2_d_var_value

        '''
        if self.p_row_d_value_order:
            for p in self.list_p:
                for t in range(len(self.list_t) - 1):
                    t1 = self.list_t[t]
                    t2 = self.list_t[t + 1]
                    constraint_name = 'con_p_row_d_order_p' + str(p) + '_t' + str(t1) + '_t' + str(t2)
                    if self.p_row_d_value_order =='ascending':
                        p_row_d_order_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintLE,
                                                                            rhs=0)

                    else:
                        p_row_d_order_constraint = pulp.LpConstraintVar(name=constraint_name, sense=pulp.LpConstraintGE,
                                                                        rhs=0)

                    self.model.addConstraint(p_row_d_order_constraint.constraint)

                    self.cons_p_row_d_order_dict[p, t1, t2] = p_row_d_order_constraint


    def add_pdt_bin_pdt_val_relation_con(self):
        '''
        Adding constraint to define relationship between
        pdt_bin_var - decision variable of all d value selected for P - T
        pdt_val_var - value of pdt_bin var selected
        SUM( d * pdt_bin_var) = pdt_val_var

        '''
        for p in self.list_p:
            for t in self.list_t:
                constraint_name = 'con_pdt_bin_pdt_val_relation_p' + str(p) + '_t' + str(t)

                pdt_bin_pdt_val_relation_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                           sense=pulp.LpConstraintEQ,
                                                                           rhs=0)

                self.model.addConstraint(pdt_bin_pdt_val_relation_constraint.constraint)

                self.cons_pdt_bin_pdt_val_relation_dict[p, t] = pdt_bin_pdt_val_relation_constraint


    def add_p_row_d_successive_diff_con(self):
        '''
        Adding Constraint 5 - Difference between successive D in a row p
        x <= p_t2_d_var_value - p_t1_d_var_value <= y
        x,y are least and most difference

        '''
        for p in self.list_p:
            for t in range(len(self.list_t) - 1):
                t1 = self.list_t[t]
                t2 = self.list_t[t + 1]

                if self.x_least_successive_diff_in_row_d:
                    constraint_name = 'con_p_row_d_successive_diff_least_p' + str(p) + '_t' + str(t1) + '_t' + str(t2)

                    p_row_d_successive_diff_least_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                                    sense=pulp.LpConstraintGE,
                                                                                    rhs=self.x_least_successive_diff_in_row_d)

                    self.model.addConstraint(p_row_d_successive_diff_least_constraint.constraint)

                    self.cons_p_row_d_successive_diff_least_dict[p, t1, t2] = p_row_d_successive_diff_least_constraint
                if self.y_most_successive_diff_in_row_d:
                    constraint_name = 'con_p_row_d_successive_diff_most_p' + str(p) + '_t' + str(t1) + '_t' + str(t2)

                    p_row_d_successive_diff_most_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                                   sense=pulp.LpConstraintLE,
                                                                                   rhs=self.y_most_successive_diff_in_row_d)

                    self.model.addConstraint(p_row_d_successive_diff_most_constraint.constraint)

                    self.cons_p_row_d_successive_diff_most_dict[p, t1, t2] = p_row_d_successive_diff_most_constraint


    def add_p_d_row_least_most_occurrence_con(self):

        '''
           Adding constraint 3
           If times of minimum or maximum unique occurrence of D in a row P is given
           i<= sum(p_d_row_var) <= j   ... for every row of P
           p_d_row_var is 1 if even one p_t_d variable is selected then for given row P ,
           D is occurred once

        '''
        for p in self.list_p:
            if self.i_least_d_values:
                constraint_name = 'con_p_row_d_occurrence_least_p' + str(p)

                p_row_d_occurrence_least_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                           sense=pulp.LpConstraintGE,
                                                                           rhs=self.i_least_d_values)

                self.model.addConstraint(p_row_d_occurrence_least_constraint.constraint)

                self.cons_p_row_d_occurrence_least_dict[p] = p_row_d_occurrence_least_constraint
            if self.j_most_d_values:
                constraint_name = 'con_p_row_d_occurrence_most_p' + str(p)

                p_row_d_occurrence_most_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                          sense=pulp.LpConstraintLE,
                                                                          rhs=self.j_most_d_values)

                self.model.addConstraint(p_row_d_occurrence_most_constraint.constraint)

                self.cons_p_row_d_occurrence_most_dict[p] = p_row_d_occurrence_most_constraint


    def add_pdt_bin_pd_row_relation_con(self):
        '''
        Adding constraint to define relationship between
        pdt_bin_var - decision variable of all d value selected for P - T
        pd_row_var - if at all value D is selected for row P
        pd_row_var <= SUM( pdt_bin_var) <= len(t) * pd_row_var

        '''
        for p in self.list_p:
            for d in self.list_d:
                constraint_name = 'con_pdt_bin_pd_row_relation_lh_p' + str(p) + '_d' + str(d)

                pdt_bin_pd_row_relation_lh_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                             sense=pulp.LpConstraintGE,
                                                                             rhs=0)

                self.model.addConstraint(pdt_bin_pd_row_relation_lh_constraint.constraint)

                self.cons_pdt_bin_pd_row_relation_dict[p, d,'lh'] = pdt_bin_pd_row_relation_lh_constraint


                constraint_name = 'con_pdt_bin_pd_row_relation_rh_p' + str(p) + '_d' + str(d)

                pdt_bin_pd_row_relation_rh_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                             sense=pulp.LpConstraintLE,
                                                                             rhs=0)

                self.model.addConstraint(pdt_bin_pd_row_relation_rh_constraint.constraint)

                self.cons_pdt_bin_pd_row_relation_dict[p, d,'rh'] = pdt_bin_pd_row_relation_rh_constraint


    def add_pdt_bin_td_column_relation_con(self):
        '''
        Adding constraint to define relationship between
        pdt_bin_var - decision variable of all d value selected for P - T
        td_column_var - if at all value D is selected for column T
        td_column_var <= SUM( pdt_bin_var) <= len(p) * pt_column_var

        '''
        for t in self.list_t:
            for d in self.list_d:
                constraint_name = 'con_pdt_bin_td_column_relation_lh_t' + str(t) + '_d' + str(d)

                pdt_bin_td_column_relation_lh_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                                sense=pulp.LpConstraintGE,
                                                                                rhs=0)

                self.model.addConstraint(pdt_bin_td_column_relation_lh_constraint.constraint)

                self.cons_pdt_bin_td_column_relation_dict[t, d, 'lh'] = pdt_bin_td_column_relation_lh_constraint

                constraint_name = 'con_pdt_bin_td_column_relation_rh_p' + str(t) + '_d' + str(d)

                pdt_bin_td_column_relation_rh_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                             sense=pulp.LpConstraintLE,
                                                                             rhs=0)

                self.model.addConstraint(pdt_bin_td_column_relation_rh_constraint.constraint)

                self.cons_pdt_bin_td_column_relation_dict[t, d, 'rh'] = pdt_bin_td_column_relation_rh_constraint


    def add_td_column_group_con(self):

        '''
           TODO This is Assumption that groups are along each column of T
           Adding constraint 1 ,2
           To divide column of T into N groups row wise
           ie. unique occurrence of assignment of D in column T is equal to number N
           Sum(t_d_column_var) == N   ... for every column of T
           p_t_column_var is 1 if even one p_t_d  variable is selected then for given column T ,
           D is occurred once

        '''
        for t in self.list_t:
            if self.n_groups:
                constraint_name = 'con_td_column_group_t' + str(t)

                td_column_group_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                  sense=pulp.LpConstraintEQ,
                                                                  rhs=self.n_groups)

                self.model.addConstraint(td_column_group_constraint.constraint)

                self.cons_td_column_group_dict[t] = td_column_group_constraint


    def add_t_column_d_value_diff_con(self):
        '''
        Adding Constraint 8 - Difference between D values of N groups in a column T
        A<= D2 * t_d2_column_var - D1 * t_d1_column_var <= B .... for all column T
        A,B are least and most difference

        '''

        for t in self.list_t:
            for d1_idx in range(len(self.list_d) - 1):
                for d2_idx in range(d1_idx+1,len(self.list_d)):
                    d1 = self.list_d[d1_idx]
                    d2 = self.list_t[d2_idx]

                    if self.a_least_column_val_diff:
                        constraint_name = 'con_t_column_d_value_diff_least_t' + str(t) + '_d' + str(d1) + '_d' + str(d2)

                        t_column_d_value_diff_least_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                                      sense=pulp.LpConstraintGE,
                                                                                      rhs=self.a_least_column_val_diff)

                        self.model.addConstraint(t_column_d_value_diff_least_constraint.constraint)

                        self.cons_t_column_d_value_diff_least_dict[t, d1, d2] = t_column_d_value_diff_least_constraint
                    if self.b_most_column_val_diff:
                        constraint_name = 'con_pt_column_d_value_diff_most_t' + str(t) + '_d' + str(d1) + '_d' + str(d2)

                        t_column_d_value_diff_most_constraint = pulp.LpConstraintVar(name=constraint_name,
                                                                                     sense=pulp.LpConstraintLE,
                                                                                     rhs=self.b_most_column_val_diff)

                        self.model.addConstraint(t_column_d_value_diff_most_constraint.constraint)

                        self.cons_t_column_d_value_diff_most_dict[t, d1, d2] = t_column_d_value_diff_most_constraint

    def generate_ptd_bin_var(self):
        # Adding P - T - D binary variable which determine amongst all which D value is selected
        for key,val in self.ip_dict.items():
            p = key[0]
            t = key[1]
            d = key[2]
            M = val[2]
            u = val[0]

            ptd_name = 'p' + str(p) + ';' + '_t' + str(t) + ';' + '_d' + str(d)
            ptd_bin_var = pulp.LpVariable(name=ptd_name, lowBound=0,
                                          upBound=1,cat=pulp.LpBinary)

            self.ptd_bin_var_dict[p, t, d] = ptd_bin_var

            # Add variable to objective function
            self.objective.addVariable(var=ptd_bin_var, coeff=M)

            # Add variable to constraint linking ptd binary var and its value in terms of selected D
            self.cons_pdt_bin_pdt_val_relation_dict[p, t].addVariable(var=ptd_bin_var, coeff=d)

            # Add variable to constraint linking ptd binary var occurrence of D in row P
            self.cons_pdt_bin_pd_row_relation_dict[p, d, 'lh'].addVariable(var=ptd_bin_var, coeff=1)
            self.cons_pdt_bin_pd_row_relation_dict[p, d, 'rh'].addVariable(var=ptd_bin_var, coeff=1)

            # Add variable to constraint linking ptd binary var occurrence of D in column T
            self.cons_pdt_bin_td_column_relation_dict[t, d, 'lh'].addVariable(var=ptd_bin_var, coeff=1)
            self.cons_pdt_bin_td_column_relation_dict[t, d, 'rh'].addVariable(var=ptd_bin_var, coeff=1)

            # Add var to constraint 12
            self.cons_unique_pt_dict[p, t].addVariable(var=ptd_bin_var, coeff=1)

            # Add var to constraint 9
            if self.u_grid_threshold:
                self.cons_u_grid_threshold['u_grid'].addVariable(var=ptd_bin_var, coeff=u)

            # Add var to constraint 7
            if self.u_max_row:
                self.cons_u_max_row[p].addVariable(var=ptd_bin_var, coeff=u)

            # Add var to constraint 10
            if self.m_threshold:
                self.cons_m_grid_threshold['m_grid'].addVariable(var=ptd_bin_var, coeff=M)

            # Add var to constraint 3
            if self.i_least_d_values:
                self.cons_p_row_d_occurrence_least_dict[p].addVariable(var=ptd_bin_var, coeff=1)
            if self.j_most_d_values:
                self.cons_p_row_d_occurrence_most_dict[p].addVariable(var=ptd_bin_var, coeff=1)


    def generate_ptd_val_var(self):
        # Adding variable of exact value of P - T cell value
        for p in self.list_p:
            for t in self.list_t:
                pt_name = 'p' + str(p) + ';' + '_t' + str(t)
                pt_d_val_var = pulp.LpVariable(name=pt_name, lowBound=0,
                                               upBound=1000, cat=pulp.LpInteger)
                self.pt_d_value_var_dict[p, t] = pt_d_val_var

                # Add variable to constraint linking ptd binary var and its value in terms of selected D
                self.cons_pdt_bin_pdt_val_relation_dict[p, t].addVariable(var=pt_d_val_var, coeff=-1)

                # Add variable to constraint 6
                if self.p_d_value_dict:
                    self.cons_p_d_value_range[p, 'min'].addVariable(var=pt_d_val_var, coeff=1)
                    self.cons_p_d_value_range[p, 'max'].addVariable(var=pt_d_val_var, coeff=1)

                # Add variable to constraint 11 and 5
                if self.list_t.index(t) == 0:
                    t1 = t
                    t2 = self.list_t[1]
                    if self.p_row_d_value_order:
                        self.cons_p_row_d_order_dict[p, t1, t2].addVariable(var=pt_d_val_var, coeff=1)
                    if self.x_least_successive_diff_in_row_d:
                        self.cons_p_row_d_successive_diff_least_dict[p, t1, t2].addVariable(var=pt_d_val_var, coeff=-1)
                    if self.y_most_successive_diff_in_row_d:
                        self.cons_p_row_d_successive_diff_most_dict[p, t1, t2].addVariable(var=pt_d_val_var, coeff=-1)

                elif self.list_t.index(t) == 0 and self.list_t.index(t) < len(self.list_t)-1:
                    t1 = t
                    t2 = self.list_t[self.list_t.index(t) + 1]
                    t3 = self.list_t[self.list_t.index(t) - 1]
                    if self.p_row_d_value_order:
                        self.cons_p_row_d_order_dict[p, t1, t2].addVariable(var=pt_d_val_var, coeff=1)
                        self.cons_p_row_d_order_dict[p, t3, t1].addVariable(var=pt_d_val_var, coeff=-1)
                    if self.x_least_successive_diff_in_row_d:
                        self.cons_p_row_d_successive_diff_least_dict[p, t1, t2].addVariable(var=pt_d_val_var, coeff=-1)
                        self.cons_p_row_d_successive_diff_least_dict[p, t3, t1].addVariable(var=pt_d_val_var, coeff=1)
                    if self.y_most_successive_diff_in_row_d:
                        self.cons_p_row_d_successive_diff_most_dict[p, t1, t2].addVariable(var=pt_d_val_var, coeff=-1)
                        self.cons_p_row_d_successive_diff_most_dict[p, t3, t1].addVariable(var=pt_d_val_var, coeff=1)

                elif self.list_t.index(t) == len(self.list_t)-1:
                    t1 = t
                    t3 = self.list_t[self.list_t.index(t) - 1]
                    if self.p_row_d_value_order:
                        self.cons_p_row_d_order_dict[p, t3, t1].addVariable(var=pt_d_val_var, coeff=-1)
                    if self.x_least_successive_diff_in_row_d:
                        self.cons_p_row_d_successive_diff_least_dict[p, t3, t1].addVariable(var=pt_d_val_var, coeff=1)
                    if self.y_most_successive_diff_in_row_d:
                        self.cons_p_row_d_successive_diff_most_dict[p, t3, t1].addVariable(var=pt_d_val_var, coeff=1)


    def generate_pd_row_var(self):
        # Adding variable to find for given row P if D value is assigned or not
        for p in self.list_p:
            for d in self.list_d:
                pd_name = 'p' + str(p) + ';' + '_d' + str(d)
                p_d_row_var = pulp.LpVariable(name=pd_name, lowBound=0,
                                              upBound=1, cat=pulp.LpBinary)
                self.pd_row_var_dict[p, d] = p_d_row_var

                # Add variable to constraint linking ptd binary var occurrence of D in row P
                self.cons_pdt_bin_pd_row_relation_dict[p, d, 'lh'].addVariable(var=p_d_row_var, coeff=-1)
                self.cons_pdt_bin_pd_row_relation_dict[p, d, 'rh'].addVariable(var=p_d_row_var, coeff=len(self.list_t))


    def generate_td_column_var(self):
        '''
        Adding variable to find for given T column if D value is assigned or not
        This is needed to identify number of groups in column
        '''
        for t in self.list_t:
            for d in self.list_d:
                td_name = 't' + str(t) + ';' + '_d' + str(d)
                t_d_column_var = pulp.LpVariable(name=td_name, lowBound=0,
                                              upBound=1, cat=pulp.LpBinary)
                self.td_column_var_dict[t, d] = t_d_column_var

                # Add variable to constraint linking ptd binary var occurrence of D in row P
                self.cons_pdt_bin_td_column_relation_dict[t, d, 'lh'].addVariable(var=t_d_column_var, coeff=-1)
                self.cons_pdt_bin_td_column_relation_dict[t, d, 'rh'].addVariable(var=t_d_column_var, coeff=len(self.list_t))

                # Add variable to constraint 1 and 2
                if self.n_groups:
                    self.cons_td_column_group_dict[t].addVariable(var=t_d_column_var, coeff=1)

                # Add variable to constraint 8
                if self.list_d.index(d) == 0:
                    d1 = d
                    d2 = self.list_d[1]
                    if self.a_least_column_val_diff:
                        self.cons_t_column_d_value_diff_least_dict[t, d1, d2].addVariable(var=t_d_column_var, coeff=-d)
                    if self.b_most_column_val_diff:
                        self.cons_t_column_d_value_diff_most_dict[t, d1, d2].addVariable(var=t_d_column_var, coeff=-d)

                elif self.list_d.index(d) == 0 and self.list_d.index(d) < len(self.list_d) - 1:
                    d1 = d
                    d2 = self.list_d[self.list_d.index(d) + 1]
                    d3 = self.list_d[self.list_d.index(d) - 1]
                    if self.a_least_column_val_diff:
                        self.cons_t_column_d_value_diff_least_dict[t, d1, d2].addVariable(var=t_d_column_var, coeff=-d)
                        self.cons_t_column_d_value_diff_least_dict[t, d3, d1].addVariable(var=t_d_column_var, coeff=d)
                    if self.b_most_column_val_diff:
                        self.cons_t_column_d_value_diff_most_dict[t, d1, d2].addVariable(var=t_d_column_var, coeff=-d)
                        self.cons_t_column_d_value_diff_most_dict[t, d3, d1].addVariable(var=t_d_column_var, coeff=d)

                elif self.list_d.index(d) == len(self.list_d) - 1:
                    d1 = d
                    d3 = self.list_d[self.list_d.index(d) - 1]
                    if self.a_least_column_val_diff:
                        self.cons_p_row_d_order_dict[t, d3, d1].addVariable(var=t_d_column_var, coeff=d)
                    if self.b_most_column_val_diff:
                        self.cons_p_row_d_order_dict[t, d3, d1].addVariable(var=t_d_column_var, coeff=d)


    def save_as_lp_pulp(cls, model, name, path='lp_models' ):
        """Saves the input model in the lp format in the input path"""
        full_path = path + "//" + name + ".lp"

        if not (os.path.isdir(path)):
            os.makedirs(path)
        model.writeLP(filename=full_path,max_length=150)

    def solve_model(self):

        print("\n--- TOTAL Model Build Time ---\n")
        print("--- %s seconds ---" % (time.time() - self.start_time))

        # Make Lp file to verify the model

        # self.model.writeLP(filename='C:\\Users\\hrishikesh.jainak\\Desktop\\acc_wh_idn.lp')

        self.save_as_lp_pulp(model=self.model, name=f'test')


        #self.result_status = self.model.solve(pulp.PULP_CBC_CMD(msg=1, maxSeconds=300))
        self.result_status = self.model.solve(pulp.PULP_CBC_CMD(fracGap=0.005, maxSeconds=self.run_time, msg=1))

        if self.result_status == pulp.LpStatusOptimal:
            print('Optimal solution found')
        elif self.result_status == pulp.LpSolutionInfeasible:
            print('solution is infeasible')
        elif self.result_status == pulp.LpSolutionUnbounded:
            print('solution in unbounded')
        else:
            print("solution is abnormal")

        print('objective value', pulp.value(self.model.objective))

        print('Number of variables =', self.model.numVariables())
        print('Number of constraints =', self.model.numConstraints())

    def get_solution(self):

        # assert self.solver.VerifySolution(1e-7, True)

        if self.result_status == pulp.LpStatusOptimal:

            solution_list = []
            for ptd_var in self.ptd_bin_var_dict.values():
                if ptd_var.varValue > 0.0001:
                    ptd_name = ptd_var.name

                    ptd_sol = ptd_name + ';' + str(ptd_var.varValue)
                    # print(xa_sol)
                    solution_list.append(ptd_sol.split(';'))

            self.sol_df = pd.DataFrame(solution_list)

            self.sol_df.columns = ['p', 't', 'd','var_value']
            self.sol_df.to_csv('solution_pulp_test_model.csv', encoding='utf-8', index=False)

    def run(self):
        print('hi')



# Running the model with input parameters and solving it
test_model = TestModel(n=None,i=None,j=None,l=None,m=None,a=None,b=None,x=None,y=None,
                 umax_row=None,u_threshold=None,u_row_threshold=None,mthreshold=None,
                 p_d_value_dict=None,p_row_d_value_order = None)
test_model.run()

