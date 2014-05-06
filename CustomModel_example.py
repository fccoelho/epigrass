# This is a custom model to used in place of Epigrass' built-in models. Custom
# models must always be on a file named CustomModel.py and contain at least 
# a function named Model. Both the File name and the function Names are case-sensitive,
# so be careful. Please refer to the manual for intructions on how to write your 
# own custom models.

def Model(self, vars, par, theta=0, npass=0):
    """
    Calculates the model SIR, and return its values.
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B, w, p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    #Defining variable names
    self.parentSite.vnames = ('Exposed', 'Infeccious', 'Susceptible')
    #Initializing
    if self.parentSite.parentGraph.simstep == 1:  #get initial values
        E, I, S = (self.bi['e'], self.bi['i'], self.bi['s'])
    else:
        E, I, S = vars
    N = self.parentSite.totpop
    beta, alpha, e, r, delta, B, w, p = par
    #Vacination event (optional)
    if self.parentSite.vaccineNow:
        S -= self.parentSite.vaccov * S

    Lpos = beta * S * ((I + theta) / (N + npass)) ** alpha  #Number of new cases
    self.parentSite.totalcases += Lpos  #update number of cases
    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + B - Lpos
    Rpos = N - (Spos + Ipos)
    # Updating stats
    self.parentSite.incidence.append(Lpos)
    # Raises site infected flag and adds parent site to the epidemic history list.
    if not self.parentSite.infected:
        if Lpos > 0:
            #if not self.parentSite.infected:
            self.parentSite.infected = self.parentSite.parentGraph.simstep
            self.parentSite.parentGraph.epipath.append(
                (self.parentSite.parentGraph.simstep, self.parentSite, self.parentSite.infector))
    #Migrating infecctious
    self.parentSite.migInf.append(Ipos)

    return [0, Ipos, Spos]
