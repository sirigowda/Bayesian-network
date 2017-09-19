import copy
import itertools
import  properties

util = []
utilparent=[]
tofind = []
parentkeys = {}
knownvalues = {}
bayesntk = {}
allvars = []

def enum_ask_cond_woquery(observedvar):
    allvars.reverse()
    x = enum_all(allvars, observedvar)
    allvars.reverse()
    return x

def find_max_eu(queryvar,observedeu, f):

    eu_values={}
    if len(queryvar)==1:
        observedeu[queryvar[0]]='+'
        eu_values['+']=find_eu(observedeu, f)
        observedeu[queryvar[0]] = '-'
        eu_values['-'] = find_eu(observedeu, f)
        del observedeu[queryvar[0]]
        key=max(eu_values, key=eu_values.get)
        print >> f,key,eu_values[key]
        return eu_values[key]

    else:
        table=list(itertools.product(['+', '-'], repeat=len(queryvar)))
        for utilassign in table:
            newobs = copy.deepcopy(observedeu)
            # assign each combination to the unassigned parent
            for par in range(0, len(queryvar)):
                newobs[queryvar[par]] = utilassign[par]
            eu_values[utilassign]=find_eu(newobs, f)
        key = max(eu_values, key=eu_values.get)
        printkey=""
        for val in key:
            printkey+=" "+val
        print >> f, printkey[1:], eu_values[key]
        return eu_values[key]


def find_eu(observedvars, f):
    if (len(utilparent) == 1):
        evidence = copy.deepcopy(observedvars)

        # if single parent value is given
        if utilparent[0] in observedvars:
            boolpar = observedvars[utilparent[0]]
            for u in util:
                if boolpar in u:
                    utilv = u.split()[0]
            eu_res = findconditionalprob(observedvars, evidence) * int(utilv)
            return int(round(eu_res+0.1))

        # else when the value is unknown consider true and false
        for u in util:
            if '+' in u:
                utrue = u.split()[0]
            elif '-' in u:
                ufalse = u.split()[0]
        observedvars[utilparent[0]] = '+'
        eu_utilpar_true = findconditionalprob(observedvars, evidence) * int(utrue)
        observedvars[utilparent[0]] = '-'
        eu_utilpar_false = findconditionalprob(observedvars, evidence) * int(ufalse)
        del observedvars[utilparent[0]]
        eu_res = eu_utilpar_true + eu_utilpar_false
        return int(round(eu_res+0.1))

    # when util has more than one parent
    else:
        eudependents = copy.deepcopy(utilparent)
        e = copy.deepcopy(observedvars)
        # remove the parents that already have an assignment from list since we do not have to assign values to them
        for upar in eudependents:
            if upar in observedvars:
                eudependents.remove(upar)
        table = list(itertools.product(['+', '-'], repeat=len(eudependents)))
        eu_res = 0
        #print observedvars

        # iterate over the various combinations of values
        for utilassign in table:

            newobs = copy.deepcopy(observedvars)
            # assign each combination to the unassigned parent
            for par in range(0, len(eudependents)):
                newobs[eudependents[par]] = utilassign[par]
            # now all the parents have an assignment
            # find the utility value of the assignment from the util table
            val = ""
            for parvalue in utilparent:
                val += " " + newobs[parvalue]
            getutil = ""
            for uval in util:
                if val in uval:
                    getutil = uval.split()[0]
                    break
            # calculate the product of each combination and add to result
            eu_res += findconditionalprob(newobs, e) * int(getutil)
        return int(round(eu_res+0.1))


# find joint probability
def enum_all(variables, observed):

    vars = copy.deepcopy(variables)
    if len(vars) == 0:
        return 1
    y = vars.pop()
    if y in observed:
        res = condprob(y, observed[y], parentkeys[y], observed) * enum_all(vars, observed)
        vars.append(y)
        return res
    else:
        observed[y] = '+';
        resTrue = (condprob(y, '+', parentkeys[y], observed) * enum_all(vars, observed))
        observed[y] = '-'
        resFalse = (condprob(y, '-', parentkeys[y], observed) * enum_all(vars, observed))
        del observed[y]
        vars.append(y)
        return resTrue + resFalse

def condprob(var, val, parents, observedvar):
    if len(parents) == 0:
        if 'decision' in bayesntk[var]:
            trueval = 1
            return float(trueval)
        else:
            trueval = bayesntk[var]
    else:
        parentVals = ""
        for parent in parents:
            parentVals += " " + observedvar[parent]
        valtable = bayesntk[var]
        for vals in valtable:
            if parentVals in vals:
                trueval = vals.split()[0]
    if val == '+':
        return float(trueval)
    else:
        return 1.0 - float(trueval)

def enum_ask_util(observedvar):
    allvars.reverse()
    x = enum_all_util(allvars, observedvar)
    allvars.reverse()
    return x

# find joint probability
def enum_all_util(variables, observed):
    vars = copy.deepcopy(variables)
    if len(vars) == 0:
        return 1
    y = vars.pop()
    if y in observed:
        res = condprob(y, observed[y], parentkeys[y], observed) * enum_all(vars, observed)
        vars.append(y)
        return res
    else:
        observed[y] = '+';
        resTrue = (condprob(y, '+', parentkeys[y], observed) * enum_all(vars, observed))
        observed[y] = '-'
        resFalse = (condprob(y, '-', parentkeys[y], observed) * enum_all(vars, observed))
        del observed[y]
        vars.append(y)
        return resTrue + resFalse


def findconditionalprob(observed, evidence):
    num = enum_ask_cond_woquery(observed)
    den = enum_ask_cond_woquery(evidence)
    return num / den


def findjointprob(observed):
    return enum_ask_cond_woquery(observed)


def enum_ask_cond_woquery_opt(vars,observedvar):
    x = enum_all(vars, observedvar)
    return x


def findresults(f):
    for ques in tofind:
        if "P" in ques:
            find_probability(ques, f)
        elif "MEU" in ques:
            find_meu(ques, f)
        elif "EU" in ques:
            find_expec_utility(ques)
        elif "******" in ques:
            continued = True
            break


def find_expec_utility(ques, f):
    ques = ques.strip(')').replace(ques[:3], '')
    if '|' in ques:
        observedeu = {}
        obvquer = ques.split('|')
        for obvar in obvquer[0].split(','):
            ob = obvar.split('=')
            observedeu[ob[0].strip()] = ob[1].strip()
        for obvar in obvquer[1].split(','):
            ob = obvar.split('=')
            observedeu[ob[0].strip()] = ob[1].strip()
    else:
        observedeu = {}
        for obvar in ques.split(','):
            ob = obvar.split('=')
            observedeu[ob[0].strip()] = ob[1].strip()
    print >> f, find_eu(observedeu, f)


def find_meu(ques, f):
    ques = ques.strip(')').replace(ques[:4], '')
    queryvar = []
    if '|' in ques:
        observedeu = {}
        obvquer = ques.split('|')
        for obvar in obvquer[0].split(','):
            queryvar.append(obvar.strip())
        for obvar in obvquer[1].split(','):
            ob = obvar.split('=')
            observedeu[ob[0].strip()] = ob[1].strip()
    else:
        observedeu = {}
        for obvar in ques.split(','):
            queryvar.append(obvar.strip())
    find_max_eu(queryvar, observedeu, f)

def find_more_probs(arr1, continued, i, inputlength, lines):
    if continued:
        continued = False
        while i < inputlength:
            if "***" not in lines[i]:
                # variable with no parents
                if lines[i].isalpha():
                    allvars.append(lines[i])
                    bayesntk[lines[i]] = lines[i + 1]
                    arr1.append([lines[i]])
                    i = i + 1
                    arr1.append([lines[i]])

                # variables with parents
                elif "|" in lines[i]:
                    vars = []
                    tablelabel = lines[i].split()
                    bayestable = []
                    pars = []
                    allvars.append(tablelabel[0])

                    # parentkeys are maintained here
                    for par in range(1, len(tablelabel)):
                        if "|" not in tablelabel[par]:
                            pars.append(tablelabel[par])
                    parentkeys[tablelabel[0]] = pars
                    bayestable.append(pars)

                    # bayesnetwork is created here
                    for row in range(1, (2 ** (len(pars))) + 1):
                        bayestable.append(lines[row + i])
                    bayesntk[lines[i].split()[0]] = bayestable
                    for var in tablelabel:
                        if var.isalpha():
                            vars.append(var)
                    arr1.append(vars)

                # values in tables
                elif "+" or "-" in lines[i]:
                    probs = []
                    for var in lines[i].split():
                        probs.append(var)
                    arr1.append(probs)
            else:
                if "******" in lines[i]:
                    continued = True
                    break
            i += 1
    return continued, i


def probs_to_find(continued, i, lines, tofind):
    for i in range(0, len(lines)):
        if "******" in lines[i]:
            continued = True
            break
        else:
            tofind.append(lines[i])
            i += 1
    return continued, i


def find_probability(ques, f):
    ques = ques.strip(')').replace(ques[:2], '')
    # find marginal probability
    if ("|" not in ques) and ("," not in ques):
        observed = {}
        ob = ques.split('=')
        observed[ob[0].strip()] = ob[1].strip()
        print >> f, "%.2f" % float(int(findjointprob(observed) * 1000 + 1) / 1000.0)

    # find joint probability
    elif "|" not in ques:
        observed = {}
        for obvar in ques.split(','):
            ob = obvar.split('=')
            observed[ob[0].strip()] = ob[1].strip()
        print >> f, "%.2f" % float(int(findjointprob(observed) * 1000 + 1) / 1000.0)

    # find conditional probability
    else:
        observed = {}
        evidence = {}
        obvquer = ques.split('|')
        for obvar in obvquer[0].split(','):
            ob = obvar.split('=')
            observed[ob[0].strip()] = ob[1].strip()
        for obvar in obvquer[1].split(','):
            ob = obvar.split('=')
            observed[ob[0].strip()] = ob[1].strip()
            evidence[ob[0].strip()] = ob[1].strip()
        print >> f, "%.2f" % float(int(findconditionalprob(observed, evidence) * 1000 + 1) / 1000.0)


def main():
    rawinput = open(properties.INPUT_FILE_PATH, 'r')
    lines = rawinput.read().splitlines()
    i = 0
    inputlength = len(lines)
    continued = False

    continued, i = probs_to_find(continued, i, lines, tofind)
    i = i + 1

    arr1 = []
    k = 0
    continued, i = find_more_probs(arr1, continued, i, inputlength, lines)
    i += 1

    f = open(properties.OUTPUT_FILE_PATH, 'w')
    print >> f, "test"

    # to add nodes with no parents to parentkeys
    for v in allvars:
        if v not in parentkeys:
            parentkeys[v] = []

    # utility node stored in util array
    if continued:
        while i < inputlength:
            util.append(lines[i])
            if "|" in lines[i]:
                vars = []
                utilparent = lines[i].split('|')[1].strip().split()
                for var in lines[i].split():
                    if var.isalpha():
                        vars.append(var)
            elif "+" or "-" in lines[i]:
                probs = []
                for var in lines[i].split():
                    probs.append(var)
            i += 1

if __name__ == "__main__":
    main()