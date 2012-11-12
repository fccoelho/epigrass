#coding:utf-8
"""
Library of discrete time population models

copyright 2012 Flávio Codeco Coelho
License: GPL-v3
"""

__author__ = 'fccoelho'

class Epimodel(object):
    """
    Defines a library of discrete time population models
    """
    def __init__(self,modtype='',v=[],bi=None,bp=None):
        """
        defines which models a given site will use
        and set variable names accordingly.
        """
        values = v
        bi = bi # dictionary of inits
        bp = bp # dictionary of parms
#        parentSite.vnames = ('E','I','S')
        self.step = selectModel(modtype)

    def __call__(self, *args, **kwargs):
        return self.step(**kwargs)

def selectModel(Type):
    """
    Sets the model engine
    """

    if Type=='SIR':
        return stepSIR
    elif Type == 'SIR_s':
        return stepSIR_s
    elif Type == 'SIS':
        return stepSIS
    elif Type == 'SIS_s':
        return stepSIS_s
    elif Type == 'SEIS':
        return stepSEIS
    elif Type == 'SEIS_s':
        return stepSEIS_s
    elif Type=='SEIR':
        return stepSEIR
    elif Type == 'SEIR_s':
        return stepSEIR_s
    elif Type == 'SIpRpS':
        return stepSIpRpS
    elif Type == 'SIpRpS_s':
        return stepSIpRpS_s
    elif Type == 'SEIpRpS':
        return stepSEIpRpS
    elif Type == 'SEIpRpS_s':
        return stepSEIpRpS_s
    elif Type == 'SIpR':
        parentSite.incidence2 = []
        return stepSIpR
    elif Type == 'SIpR_s':
        parentSite.incidence2 = []
        return stepSIpR_s
    elif Type == 'SEIpR':
        parentSite.incidence2 = []
        return stepSEIpR
    elif Type == 'SEIpR_s':
        parentSite.incidence2 = []
        return stepSEIpR_s
    elif Type == 'SIRS':
        return stepSIRS
    elif Type == 'SIRS_s':
        return stepSIRS_s
    elif Type == 'Influenza':
        return stepFlu
    elif Type == 'Custom':
        #adds the user model as a method of instance self
        try:
            #TODO: move this import to the graph level
            import CustomModel
            return CustomModel.Model
        except ImportError:
            print "You have to Create a CustomModel.py file before you can select\nthe Custom model type"
    else:
        sys.exit('Model type specified in .epg file is invalid')



def stepFlu(inits, simstep, totpop, theta=0,npass=0):
    """
    Flu model with classes S,E,I subclinical, I mild, I medium, I serious, deaths
    """
    tinicial = time.time()
    #Variable long names to be used in the database output.
    parentSite.vnames = ('Susc_age1','Incub_age1','Subc_age1','Sympt_age1','Comp_age1',
                              'Susc_age2','Incub_age2','Subc_age2','Sympt_age2','Comp_age2',
                              'Susc_age3','Incub_age3','Subc_age3','Sympt_age3','Comp_age3',
                              'Susc_age4','Incub_age4','Subc_age4','Sympt_age4','Comp_age4',)
    if simstep == 1: #get initial values
        S1,E1,Is1,Ic1,Ig1 = (bi['s1'],bi['e1'],bi['is1'],bi['ic1'],bi['ig1'])
        S2,E2,Is2,Ic2,Ig2 = (bi['s2'],bi['e2'],bi['is2'],bi['ic2'],bi['ig2'])
        S3,E3,Is3,Ic3,Ig3 = (bi['s3'],bi['e3'],bi['is3'],bi['ic3'],bi['ig3'])
        S4,E4,Is4,Ic4,Ig4 = (bi['s4'],bi['e4'],bi['is4'],bi['ic4'],bi['ig4'])
    else: #get values from last time step
        S1,E1,Is1,Ic1,Ig1,S2,E2,Is2,Ic2,Ig2,S3,E3,Is3,Ic3,Ig3,S4,E4,Is4,Ic4,Ig4 = inits
    N = totpop

    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameters: alpha,beta,r,e,c,g,d,pc1,pc2,pc3,pc4,pp1,pp2,pp3,pp4,b

    #Vacination event
    if parentSite.vaccineNow:
        S1 -= parentSite.vaccov*S1
        S2 -= parentSite.vaccov*S2
        S3 -= parentSite.vaccov*S3
        S4 -= parentSite.vaccov*S4

    #New cases by age class
    #beta=eval(values[2])

    Infectantes = Ig1+Ig2+Ig3+Ig4+Ic1+Ic2+Ic3+Ic4+0.5*(Is1+Is2+Is3+Is4)+theta
    L1pos = float(beta)*S1*(Infectantes/(N+npass))**alpha
    L2pos = float(beta)*S2*(Infectantes/(N+npass))**alpha
    L3pos = float(beta)*S3*(Infectantes/(N+npass))**alpha
    L4pos = float(beta)*S4*(Infectantes/(N+npass))**alpha

    ######################
    Lpos = L1pos+L2pos+L3pos+L4pos
    # Model
    # 0-2 anos
    E1pos = L1pos + (1-e)*E1
    Is1pos = (1-(pc1*c+(1-pc1)*r))*Is1 + e*E1
    Ic1pos = (1-(pp1*g+(1-pp1)*r))*Ic1 + pc1*c*Is1
    Ig1pos = (1-d)*Ig1 + pp1*g*Ic1
    S1pos = b+S1 - L1pos
    # 3-14 anos
    E2pos = L2pos + (1-e)*E2
    Is2pos = (1-(pc2*c+(1-pc2)*r))*Is2 + e*E2
    Ic2pos = (1-(pp2*g+(1-pp2)*r))*Ic2 + pc2*c*Is2
    Ig2pos = (1-d)*Ig2 + pp2*g*Ic2
    S2pos = b+S2 - L2pos
    # 15-59 anos
    E3pos = L3pos + (1-e)*E3
    Is3pos = (1-(pc3*c+(1-pc3)*r))*Is3 + e*E3
    Ic3pos = (1-(pp3*g+(1-pp3)*r))*Ic3 + pc3*c*Is3
    Ig3pos = (1-d)*Ig3 + pp3*g*Ic3
    S3pos = b+S3 - L3pos
    # >60 anos
    E4pos = L4pos + (1-e)*E4
    Is4pos = (1-(pc4*c+(1-pc4)*r))*Is4 + e*E4
    Ic4pos = (1-(pp4*g+(1-pp4)*r))*Ic4 + pc4*c*Is4
    Ig4pos = (1-d)*Ig4 + pp4*g*Ic4
    S4pos = b+S4 - L4pos

    #Migrating infecctious
    migInf = (Ig1pos+Ig2pos+Ig3pos+Ig4pos+Ic1pos+Ic2pos+Ic3pos+Ic4pos+0.5*(Is1pos+Is2pos+Is3pos+Is4pos))
    # Return variable values
    print "------> exiting in %s seconds"%(time.time()-tinicial)
    return [S1pos,E1pos,Is1pos,Ic1pos,Ig1pos,S2pos,E2pos,Is2pos,
            Ic2pos,Ig2pos,S3pos,E3pos,Is3pos,Ic3pos,Ig3pos,S4pos,
            E4pos,Is4pos,Ic4pos,Ig4pos], Lpos, migInf


def stepSIS(inits,simstep, totpop,theta=0, npass=0):
    """
    calculates the model SIS, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos + r*I

    #Migrating infecctious
    migInf = (Ipos)
    return [0,Ipos,Spos],Lpos,migInf

def stepSIS_s(inits, simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SIS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos + r*I

    #Migrating infecctious
    migInf = (Ipos)

    return [0,Ipos,Spos], Lpos, migInf

def stepSIR(inits,simstep, totpop,theta=0, npass=0):
    """
    calculates the model SIR, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    print inits
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameters: b ,r
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos
    Rpos = N-(Spos+Ipos)

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos],Lpos,migInf

def stepSIR_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SIR:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos
    Rpos = N-(Spos+Ipos)

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos, migInf

def stepSEIS(inits,simstep, totpop,theta=0, npass=0):
    """
    Defines the model SEIS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameters: b,e,r
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    #Model
    Epos = (1-e)*E + Lpos
    Ipos = e*E + (1-r)*I
    Spos = S + b - Lpos + r*I

    #Migrating infecctious
    migInf = Ipos

    return [Epos,Ipos,Spos], Lpos, migInf

def stepSEIS_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SEIS:
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,b,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #converting between parameterizations
        Lpos = negative_binomial(I,prob)

    Epos = (1-e)*E + Lpos
    Ipos = e*E + (1-r)*I
    Spos = S + b - Lpos + r*I

    #Migrating infecctious
    migInf = Ipos

    return [Epos,Ipos,Spos], Lpos,migInf

def stepSEIR(inits,simstep, totpop,theta=0, npass=0):
    """
    Defines the model SEIR:
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,B,w,p
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    #Model
    Epos = (1-e)*E + Lpos
    Ipos = e*E + (1-r)*I
    Spos = S + b - Lpos
    Rpos = N-(Spos+Epos+Ipos)
    #parentSite.totpop = Spos+Epos+Ipos+Rpos

    #Migrating infecctious
    migInf = Ipos

    return [Epos,Ipos,Spos], Lpos, migInf

def stepSEIR_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SEIR:
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = parentSite.totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,B,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp) #poisson(Lpos_esp)
    ##            if theta == 0 and Lpos_esp == 0 and Lpos > 0:
    ##                print Lpos,Lpos_esp,S,I,theta,N,parentSite.sitename
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)

    Epos = (1-e)*E + Lpos
    Ipos = e*E + (1-r)*I
    Spos = S + b - Lpos
    Rpos = N-(Spos+Epos+Ipos)

    #Migrating infecctious
    migInf = Ipos

    return [Epos,Ipos,Spos],Lpos, migInf

def stepSIpRpS(inits,simstep, totpop,theta=0, npass=0):
    """
    calculates the model SIpRpS, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos + (1-delta)*r*I
    Rpos = N-(Spos+Ipos) + delta*r*I

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos, migInf

def stepSIpRpS_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SIpRpS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,B,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos + (1-delta)*r*I
    Rpos = N-(Spos+Ipos) + delta*r*I

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos, migInf

def stepSEIpRpS(inits,simstep, totpop,theta=0, npass=0):
    """
    Defines the model SEIpRpS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = parentSite.totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p

    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    Epos = (1-e)*E + Lpos
    Ipos = e*E + (1-r)*I
    Spos = S + b - Lpos + (1-delta)*r*I
    Rpos = N-(Spos+Epos+Ipos) + delta*r*I

    #Migrating infecctious
    migInf = Ipos

    return [Epos,Ipos,Spos], Lpos, migInf

def stepSEIpRpS_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SEIpRpS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = parentSite.totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)

    Epos = (1-e)*E + Lpos
    Ipos = e*E + (1-r)*I
    Spos = S + b - Lpos + (1-delta)*r*I
    Rpos = N-(Spos+Epos+Ipos) + delta*r*I

    #Migrating infecctious
    migInf = Ipos

    return [Epos,Ipos,Spos], Lpos, migInf

def stepSIpR(inits,simstep, totpop,theta=0, npass=0):
    """
    calculates the model SIpR, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    R = N-E-I-S
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
    Lpos2 = p*float(beta)*R*((I+theta)/(N+npass))**alpha #number of secondary Infections

    # Model
    Ipos = (1-r)*I + Lpos + Lpos2
    Spos = S + b - Lpos
    Rpos = N-(Spos+Ipos) - Lpos2

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos+Lpos2, migInf

def stepSIpR_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SIpRs:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
    R = N-E-I-S

    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
    Lpos2_esp = p*float(beta)*R*((I+theta)/(N+npass))**alpha #number of secondary Infections

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
        Lpos2 = poisson(Lpos2_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)
        prob = I/(I+Lpos2_esp) #convertin between parameterizations
        Lpos2 = negative_binomial(I,prob)

    # Model
    Ipos = (1-r)*I + Lpos + Lpos2
    Spos = S + b - Lpos
    Rpos = N-(Spos+Ipos) - Lpos2

    #Migrating infecctious
    migInf = Ipos
    return [0,Ipos,Spos], Lpos+Lpos2, migInf

def stepSEIpR(inits,simstep, totpop,theta=0, npass=0):
    """
    calculates the model SEIpR, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    R = N-E-I-S
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameters: beta,alpha,e,r,delta,b,w,p

    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
    Lpos2 = p*float(beta)*R*((I+theta)/(N+npass))**alpha # secondary infections

    # Model
    Epos = (1-e)*E + Lpos + Lpos2
    Ipos = e*E+ (1-r)*I
    Spos = S + b - Lpos
    Rpos = N-(Spos+Ipos) - Lpos2

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos+Lpos2, migInf

def stepSEIpR_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SEIpRs:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,B,w,p
    R = N-E-I-S

    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
    Lpos2_esp = p*float(beta)*R*((I+theta)/(N+npass))**alpha # secondary infections

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
        Lpos2 = poisson(Lpos2_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #converting between parameterizations
        Lpos = negative_binomial(I,prob)
        prob = I/(I+Lpos2_esp) #converting between parameterizations
        Lpos2 = negative_binomial(I,prob)

    # Model
    Epos = (1-e)*E + Lpos + Lpos2
    Ipos = e*E+ (1-r)*I
    Spos = S + b - Lpos
    Rpos = N-(Spos+Ipos) - Lpos2

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos+Lpos2, migInf

def stepSIRS(inits,simstep, totpop,theta=0, npass=0):
    """
    calculates the model SIRS, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    R = N - E + I + S
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
    Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos + w*R
    Rpos = N-(Spos+Ipos) - w*R

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos, migInf

def stepSIRS_s(inits,simstep, totpop,theta=0, npass=0,dist='poisson'):
    """
    Defines an stochastic model SIR:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1: #get initial values
        E,I,S = (bi['e'],bi['i'],bi['s'])
    else:
        E,I,S = inits
    N = totpop
    R = N - E + I + S
    for k, v in bp.items():
        exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
    Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I/(I+Lpos_esp) #convertin between parameterizations
        Lpos = negative_binomial(I,prob)

    # Model
    Ipos = (1-r)*I + Lpos
    Spos = S + b - Lpos + w*R
    Rpos = N-(Spos+Ipos) - w*R

    #Migrating infecctious
    migInf = Ipos

    return [0,Ipos,Spos], Lpos, migInf

