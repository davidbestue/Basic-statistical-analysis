
# coding: utf-8

# In[158]:


import easygui
from pandas import read_excel, DataFrame
from statsmodels.formula.api import ols
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

#Analyze data by group (three groups in the example)

#Read the file and decide the columnto analyze
#You will end up with a pandas dataframe with columns where the first is the group, and the 
#others are the column names
column = easygui.enterbox(msg='Enter the column to analyze', title='Column')
column=int(column)

df=read_excel('path/aaa.xlsx') #L data
group=['WT', 'HD', 'HD_T']
column_names=[ 'group', 'mit_axon', 'Relative_values', 'Am', 'Pm', 'Circ', 'AR', 'Am_Pm2',  'FF', 'FF_Relative_values', 'AR Relative_values', 'subj']
df.columns=column_names


#Get the matrix of the column to analyze
Matrix = DataFrame({"group":df['group'], column_names[column]: df[column_names[column]]})
print 'N =  ' +str(len(Matrix))
print '                           '
print '                           '


#take off outliers per group
def remove_outlier(df_in, col_name):
    q1 = df_in[col_name].quantile(0.25)
    q3 = df_in[col_name].quantile(0.75)
    iqr = q3-q1 #Interquartile range
    fence_low  = q1-1.5*iqr
    fence_high = q3+1.5*iqr
    df_out = df_in.loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
    return df_out


from pandas import concat
frames=[]
for group_label in ['WT', 'HD', 'HD_T']:
    sub_group=Matrix.groupby('group').get_group(group_label)
    #CI
    #interval = sub_group.quantile([0.05, 0.95]).unstack(level=1)
    #removed_out = sub_group.loc[(sub_group[column_names[column]]>interval[0]) & (sub_group[column_names[column]]<interval[1])] 
    #Quartiles
    removed_out = remove_outlier(sub_group, column_names[column] )
    frames.append(  removed_out   )
    
    #Print the result
    before_outliers=len(sub_group)
    after_outliers=len(removed_out)
    print 'Outliers in ' + group_label + ' = ' +str(before_outliers-after_outliers)
    


Matrix = concat(frames)
print '                           '
print '                           '
print 'N (without oultiers) =  ' +str(len(Matrix))
print '                           '
print '                           '



####### Describe the data by grouos
gruped=Matrix.groupby('group')

print '                                 Summary Table'
print '=============================================================================='
print gruped.describe()
print '=============================================================================='
print '                                 '

 
 

###### Anova model
mod = ols(formula=column_names[column] +' ~ group', data=Matrix).fit()
aov_table = sm.stats.anova_lm(mod, typ=2)
print '                                 '
print '                                 Anova Table'
print '=============================================================================='
print aov_table
print '=============================================================================='
print '                                 '

####### Multiple comparisons
tukey = pairwise_tukeyhsd(endog=Matrix[column_names[column]].values, groups=Matrix['group'].values,  alpha=0.05)
print tukey.summary()    

print '                                 '


print '                                 '
print '                                 '

###### Liniar models
#Put the WT in the intercept
Matrix['group'] = Matrix['group'].replace('WT', 'A_WT')
mod = ols(formula=column_names[column] +' ~ group', data=Matrix).fit()

print mod.summary()
Matrix['group'] = Matrix['group'].replace('A_WT', 'WT')



