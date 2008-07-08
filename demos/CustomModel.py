# This is a custom model to used in place of Epigrass' built-in models. Custom
# models must always be on a file named CustomModel.py and contain at least 
# a function named Model. Both the File name and the function Names are case-sensitive,
# so be careful. Please refer to the manual for intructions on how to write your 
# own custom models.

def Model(self,vars,par,theta=0, npass=0):
        """
        This function implements the SIR model
        - inits = (E,I,S)
        - par = (Beta, alpha, E,r,delta,B, w, p) see docs.
        - theta = infectious individuals from neighbor sites
        """
        ##### Defining variable names to appear in the database
        # Must be listed in the same order of variables in the model 
        self.parentSite.vnames = ('Exposed','Infectious','Susceptible')
        
        ##### Get state variables' current values
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else: # get last value
            E,I,S = vars
            
        ##### Defining N, the total population     
        N = self.parentSite.totpop
        
        ##### Getting values for the model parameters
        beta,alpha,e,r,delta,B,w,p = (self.bp['beta'],self.bp['alpha'],self.bp['e'],self.bp['r'],self.bp['delta'],self.bp['b'],self.bp['w'],self.bp['p'])
        
        ##### Defining a Vacination event (optional)
        if self.parentSite.vaccineNow:
            S -= self.parentSite.vaccov*S
        
        ##### Modeling the number of new cases (incidence function)
        Lpos = beta*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        ##### Epidemiological model (SIR)
        Ipos = (1-r)*I + Lpos
        Spos = S + B - Lpos
        Rpos = N-(Spos+Ipos)
        
        ##### Updating stats
        self.parentSite.incidence.append(Lpos) # incidence time series 
        self.parentSite.totalcases += Lpos  # total cases so far
        
        #### If parentSite was not infected before and now it is... 
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep   # store the time of first infection
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        # Store the number of infectious individuals commuting to parentSite.
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
