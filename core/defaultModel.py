import random

class applicant:
    # curEmploy: Boolean. If the person is currently employeed, True
    # curIncMo: int or float. if currently employeed, the monthly salary 
    # bankBal: int or float: money in the bank account
    # reminTerm: int: if there person is contracted, how many months remaining for the contract
    # avgInc: int or float: the income from the most recent job
    def __init__(self,curEmploy,curIncMo,bankBal,remainTerm,avgInc):
        self.curIncMo= curIncMo
        self.curEmploy = curEmploy
        self.bankBal = bankBal
        self.remainTerm = remainTerm
        self.curIncMo = curIncMo
        if not curEmploy:
            self.curIncMo = avgInc
        self.avgInc = avgInc
    

def getDeepCopy(app):
    return applicant(app.curEmploy,app.curIncMo,app.bankBal,
                       app.remainTerm,app.avgInc)
    

# Param:
    # applicant: the applicant created in the applicant class
    # rent: int, the rent for the new apartment
    # employment: probability to get a job within a month. By default, 
    # it is 0.7 unless user change it
    
# Output:
    # a list. item 0-11 are the default rate for a given month. e.g. the third 
    # one (index 2) is the default rate for the applicant at month 3
    #
    # list[12] is the average amount of money the applicant would have in the bank account
    # list[11] is the probabilty the applicant has a bank account balance below 0. 
    # i.e. real default. This is same as the default rate at the end of month 12
    
# Assumptions: The rent is 30% of the applicant's income and other expenses  
# have the same amount as rent in total. i.e. the applicant will speed 60% of income per month
# By default, the employment rate is 0.7 i.e. the probability for the applicant 
# to get a job with in a month is 0.7
    
# Methodology: Use simulations with randomization to simulate real life possiblities.
# When the applicant ends the contract, the model uses bernoulli trial with 
# p = employment. If the outcome is 1, the applicant gets a new job and to simulate 
# the real lifethe length/contract for the new job is either 1 or 2 or 3 or 4 
# months with the equal probability 

def individualDefaultRatio(applicant,rent,rentTerm,employment=.7):
    result = [0]*(rentTerm+1)
    for j in range(10000):
        app = getDeepCopy(applicant)
        for i in range(rentTerm):
            fixedExp = rent*2
            if app.remainTerm ==0:
                newJob = 1 if random.uniform(0,1)<employment else 0
                # applicant get the new job, the job is 
                if newJob==1:
                    app.remainTerm = random.randint(0,3)
                    app.bankBal = app.bankBal + app.curIncMo - fixedExp
                # the case that applicant doesn't get the new job
                else:
                    app.bankBal = app.bankBal - fixedExp
            else:
                app.bankBal = app.bankBal + app.curIncMo - fixedExp
                app.remainTerm  = app.remainTerm - 1
            if app.bankBal < 0:
                result[i] = result[i]+1
        result[rentTerm] = app.bankBal+result[rentTerm]
    result =  [i/10000 for i in result]
    
    #cast everything as float to avoid problems later on
    for i in range(len(result)):
        result[i] = float(result[i])
    return result

# ########### example call. DO NOT INCLUDE IN THE CODE ###########
# individualDefaultRatio(applicant(True,1000,200,2,900),300,6)
# ########### END OF EXAMPLE CALL ########################

# # For landlord, the only last result[11] is needed for landlord

# # For refugees and guaranteurs, they have the access for all information

# deplist = [x*20 for x in range(0, 31)]
# defaultProbList = [0]*len(deplist)
# index = 0
# for i in deplist:
#     a1 = applicant(True,1000,i,1,900)
#     defaultProbList[index] = individualDefaultRatio(a1,300)[11]
#     index = index+1
    
# diffList = []
# for i in range(len(defaultProbList)-1):
#     diffList.append(defaultProbList[i]-defaultProbList[i+1])
# diffList.index(max(diffList))