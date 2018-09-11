import math

#Param list:
#curIncMo: int or float: current monthly income if user input is hourly wage, 
#            curIncMo = 200*wage (consider working 200 hours per month)
#curHouseExp: int: current housing expense per month
#workExp: boolean. If user has work experience: True, else: False
#bankAcc: Boolean. If user has bank account: True, else: False
#bankBal: int or float: user's bank account balance
#cashBal: int or float: user's cash available for purchase
#arrLenMo: int: months that the user has been to Europe
#outDebt: Boolean: if the user has outstanding debt/loan from bank or NGO: True
#outDebtAmt: int or float: amount of the debt 
#outDebtTerm: int: number of months for the debt
#paidDebt: Boolean: if the user has been issued loan and the loan has been fully repaid
#misPay: Boolean: if the user has any missed payment in the past 2 years 
#misPayFreq: int: total frequencies the user missed a payment in the past 2 years 
 
def creditScore(curIncMo, curHouseExp,workExp, bankAcc, bankBal, cashBal,arrLenMo,outDebt, outDebtAmt, outDebtTerm, paidDebt, misPay, misPayFreq):
    arrLen = arrLenMo / float(12)

    #cast!!!!!!!!
    curIncMo = float(curIncMo)
    curHouseExp = float(curHouseExp)
    workExp = float(workExp)
    bankAcc = float(bankAcc)
    bankBal = float(bankBal)
    cashBal = float(cashBal)
    arrLenMo = float(arrLenMo)
    outDebt = float(outDebt)
    outDebtAmt = float(outDebtAmt)
    outDebtTerm = float(outDebtTerm)
    paidDebt = float(paidDebt)

    # Base case if the refugee just entered EU, no credit history and if the refugee 
    # never has a job, no credit history 
    if arrLen == 0:
        return 0

    if not workExp and curIncMo ==0:
        return 0
    
    moneyAvail = bankBal + cashBal
    
    if outDebt:
        moLIAB = outDebtAmt/outDebtTerm
    else: 
        moLIAB = 0
    pt = 0
    
    if (misPay) & (misPayFreq/arrLen >1): 
        pt = pt - math.log(misPayFreq/arrLen)*10
        if misPay/arrLen <4:
            pt = pt+ math.log(-misPayFreq/arrLen+5)*15
    elif arrLen > .5:
        pt = pt+10*math.log(arrLen+.5)+30
        
    # Assumption: the fixed expense shouldn't exceed 40% of income 
    if (curHouseExp+moLIAB)/curIncMo > .4:
        penalty =(((curHouseExp+moLIAB)/curIncMo)-.4) *100
        # maximum penalty
        if penalty > 30:
            penalty = 30
        pt = pt - penalty
    else:
        pt = pt+min(math.sqrt((.4-((float(curHouseExp)+moLIAB)/float(curIncMo))))*20,30)
        
    if arrLen > .5:
        pt = pt+math.log(arrLen+.5)*10
        
    if bankAcc:
        pt = pt+10
        
    if moneyAvail < curHouseExp*.5 and curHouseExp > 0:
        # max bounus here is 20 points 
        pt = pt + ((moneyAvail)/curHouseExp)/.025
    elif moneyAvail >= curHouseExp*.5 and curHouseExp > 0:
        pt = pt + min(math.log(moneyAvail/curHouseExp+1.5)*10 +13,30)
    if paidDebt:
        pt = pt +30
    
    return int(min(pt,100))