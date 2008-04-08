# This is a custom model to used in place of Epigrass' built-in models. Custom
# models must always be on a file named CustomModel.py and contain at least 
# a function named Model. Both the File name and the function Names are case-sensitive,
# so be careful. Please refer to the manual for intructions on how to write your 
# own custom models.

def Model(self,vars,par,theta=0, npass=0):
        """
        Calculates the model SIR, and return its values.
        - inits = (E,I,S)
        - par = (Beta, alpha, E,r,delta,B, w, p) see docs.
        - theta = infectious individuals from neighbor sites (CONSIDERANDO QUE CHEGUE COMO UMA lista         'Ip0','Ip2','Ip10','Ip15','Ip20','Ip40','Is0','Is2','Is10','Is15','Is20','Is40'
        - npass deve ser tb um vetor com populacao por faixa etaria
        """
        #Initializing

        self.parentSite.vnames = ('S0','S2','S10','S15','S20','S40',
                'Ip0','Ip2','Ip10','Ip15','Ip20','Ip40',
                'Is0','Is2','Is10','Is15','Is20','Is40',
                'Rmax0','Rmax2','Rmax10','Rmax15','Rmax20','Rmax40',
                'Rmed0','Rmed2','Rmed10','Rmed15','Rmed20','Rmed40',
                'Rmin0','Rmin2','Rmin10','Rmin15','Rmin20','Rmin40',
                'Vmax0','Vmax2','Vmax10','Vmax15','Vmax20','Vmax40',
                'Vmed0','Vmed2','Vmed10','Vmed15','Vmed20','Vmed40',
                'Vmin0','Vmin2','Vmin10','Vmin15','Vmin20','Vmin40')
 
        #print self.bi
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            #E,I,S = (self.bi['S0'],self.bi['S2'],self.bi['s'])
            S0,S2,S10,S15,S20,S40 = (self.bi['s0'],self.bi['s2'],self.bi['s10'],self.bi['s15'],self.bi['s20'],self.bi['s40'])
            Ip0,Ip2,Ip10,Ip15,Ip20,Ip40 = (self.bi['ip0'],self.bi['ip2'],self.bi['ip10'],self.bi['ip15'],self.bi['ip20'],self.bi['ip40'])
            Is0,Is2,Is10,Is15,Is20,Is40 = (self.bi['is0'],self.bi['is2'],self.bi['is10'],self.bi['is15'],self.bi['is20'],self.bi['is40'])
            Rmax0,Rmax2,Rmax10,Rmax15,Rmax20,Rmax40=(self.bi['rmax0'],self.bi['rmax2'],self.bi['rmax10'],self.bi['rmax15'],self.bi['rmax20'],self.bi['rmax40'])
            Rmed0,Rmed2,Rmed10,Rmed15,Rmed20,Rmed40=(self.bi['rmed0'],self.bi['rmed2'],self.bi['rmed10'],self.bi['rmed15'],self.bi['rmed20'],self.bi['rmed40'])
            Rmin0,Rmin2,Rmin10,Rmin15,Rmin20,Rmin40=(self.bi['rmin0'],self.bi['rmin2'],self.bi['rmin10'],self.bi['rmin15'],self.bi['rmin20'],self.bi['rmin40'])
            Vmax0,Vmax2,Vmax10,Vmax15,Vmax20,Vmax40=(self.bi['vmax0'],self.bi['vmax2'],self.bi['vmax10'],self.bi['vmax15'],self.bi['vmax20'],self.bi['vmax40'])
            Vmed0,Vmed2,Vmed10,Vmed15,Vmed20,Vmed40=(self.bi['vmed0'],self.bi['vmed2'],self.bi['vmed10'],self.bi['vmed15'],self.bi['vmed20'],self.bi['vmed40'])
            Vmin0,Vmin2,Vmin10,Vmin15,Vmin20,Vmin40=(self.bi['vmin0'],self.bi['vmin2'],self.bi['vmin10'],self.bi['vmin15'],self.bi['vmin20'],self.bi['vmin40'])

        else:
            S0,S2,S10,S15,S20,S40,Ip0,Ip2,Ip10,Ip15,Ip20,Ip40,Is0,Is2,Is10,Is15,Is20,Is40,Rmax0,Rmax2,Rmax10,Rmax15,Rmax20,Rmax40,Rmed0,Rmed2,Rmed10,Rmed15,Rmed20,Rmed40,Rmin0,Rmin2,Rmin10,Rmin15,Rmin20,Rmin40,Vmax0,Vmax2,Vmax10,Vmax15,Vmax20,Vmax40,Vmed0,Vmed2,Vmed10,Vmed15,Vmed20,Vmed40,Vmin0,Vmin2,Vmin10,Vmin15,Vmin20,Vmin40= vars
        N = self.parentSite.totpop
        
        # Visitantes infectados e totais:
        Mp0,Mp2,Mp10,Mp15,Mp20,Mp40,Ms0,Ms2,Ms10,Ms15,Ms20,Ms40 = 0,0,0,0,0,0,0,0,0,0,0,0
        npass0,npass2,npass10,npass15,npass20,npass40= 0,0,0,0,0,0
        totpass=npass0+npass2+npass10+npass15+npass20+npass40
        

        # Parametros
        #beta,alpha,e,r,delta,B,w,p = par
        
        pp, ps, sp, ss = (self.bp['pp'],self.bp['ps'],self.bp['sp'],self.bp['ss'])
        pv, e, gp, gs, a, r = (self.bp['pv'],self.bp['e'],self.bp['gp'],self.bp['gs'],self.bp['a'],self.bp['r'],) 
        ca, cm, cb, n0 = (self.bp['ca'],self.bp['cm'],self.bp['cb'],self.bp['n0'])
        n2, n10, n15, n20, n40 = (self.bp['n2'],self.bp['n10'],self.bp['n15'],self.bp['n20'],self.bp['n40'])

        #Vacination event  # apenas na primeira faixa etaria
        if self.parentSite.vaccineNow:
            S0 -= self.parentSite.vaccov*S0
            Vmax0 += self.parentSite.vaccov*S0
        
        # numero de pessoas com infeccao primaria (locais e visitas)
        Iptot = Ip0+Ip2+Ip10+Ip15+Ip20+Ip40+Mp0+Mp2+Mp10+Mp15+Mp20+Mp40
        Istot = Is0+Is2+Is10+Is15+Is20+Is40+Ms0+Ms2+Ms10+Ms15+Ms20+Ms40

        # probabilidade de infeccao por contato
        #print N, totpass, cb,pp,Ip0,Ip10,Ip15,Mp0,Mp10,Mp15,ps,Is0,Is10,Is15,Ms0,Ms10,Ms15,cm,Ip20,Ip40,Mp20,Mp40,Is20,Is40,Ms20,Ms40,ca,Ip2,Mp2,Ip2,Mp2

        p0 =  (1/(N+totpass))*(cb*(pp*(Ip0+Ip2+Mp0+Mp2)    +ps*(Is0+Is2+Ms0+Ms2))    +cm*(pp*(Ip10+Ip40+Mp10+Mp40) +ps*(Is10+Is40+Ms10+Ms40)) +ca*(pp*(Ip15+Ip20+Mp15+Mp20)  +ps*(Is15+Is20+Ms15+Ms20)))
        p2 =  (1/(N+totpass))*(cb*(pp*(Ip0+Ip10+Mp0+Mp10)  +ps*(Is0+Is10+Ms0+Ms10))  +cm*(pp*(Ip15+Ip20+Mp15+Mp20) +ps*(Is15+Is20+Ms15+Ms20)) +ca*(pp*(Ip2+Ip20+Mp2+Mp20)    +ps*(Is2+Is20+Ms2+Ms20)))
        p10 = (1/(N+totpass))*(cb*(pp*(Ip0+Mp0+Ip2+Mp2)    +ps*(Is0+Ms0+Is2+Ms2))    +cm*(pp*(Ip15+Ip40+Mp15+Mp40) +ps*(Is15+Is40+Ms15+Ms40)) +ca*(pp*(Ip10+Mp10+Ip20+Mp20)  +ps*(Is10+Ms10+Is20+Ms20)))
        p15 = (1/(N+totpass))*(cb*(pp*(Ip0+Mp0+Ip2+Mp2)    +ps*(Ip0+Mp0+Ip2+Mp2))    +cm*(pp*(Ip10+Ip40+Mp10+Mp40) +ps*(Is10+Is40+Ms10+Ms40)) +ca*(pp*(Ip20+Ip15+Mp20+Mp15)  +ps*(Is20+Is15+Ms20+Ms15)))
        p20 = (1/(N+totpass))*(cb*(pp*(Ip10+Mp10+Ip15+Mp15)+ps*(Is10+Ms10+Is15+Ms15))+cm*(pp*(Ip2+Ip40+Mp2+Mp40)   +ps*(Is2+Is40+Ms2+Ms40))   +ca*(pp*(Ip0+Ip20+Mp0+Mp20)    +ps*(Is0+Is20+Ms0+Ms20)))
        p40 = (1/(N+totpass))*(cb*(pp*(Ip0+Mp0+Ip15+Mp15)  +ps*(Is0+Ms0+Is15+Ms15))  +cm*(pp*(Ip2+Ip10+Mp2+Mp10)   +ps*(Is2+Is10+Ms2+Ms10))   +ca*(pp*(Ip20+Ip40+Mp20+Mp40)  +ps*(Is20+Is40+Ms20+Ms40)))
        
        # Incidencia (Nos nao estatmos ocnsiderando o risco da pessoa suscetivel pegar infeccao fora de casa)
        #Lpos = sp*S*((I+theta)/(N+npass))**alpha #Number of new cases
        Lp0 = sp*S0*(1-(1-p0)**n0)
        Ls0 = ss*(Rmin0+Vmin0)*(1-(1-p0)**n0)
        Lp2 = sp*S2*(1-(1-p2)**n2)
        Ls2 = ss*(Rmin2+Vmin2)*(1-(1-p2)**n2)
        Lp10 = sp*S10*(1-(1-p10)**n10)
        #print 'Lp10=%s'%Lp10
        Ls10 = ss*(Rmin10+Vmin10)*(1-(1-p10)**n10)
        Lp15 = sp*S15*(1-(1-p15)**n15)
        Ls15 = ss*(Rmin15+Vmin15)*(1-(1-p15)**n15)
        Lp20 = sp*S20*(1-(1-p20)**n20)
        Ls20 = ss*(Rmin20+Vmin20)*(1-(1-p20)**n20)
        Lp40 = sp*S40*(1-(1-p40)**n40)
        Ls40 = ss*(Rmin40+Vmin40)*(1-(1-p40)**n40)
        
        Lposp = Lp0+Lp2+Lp10+Lp15+Lp20+Lp40
        Lposs = Ls0+Ls2+Ls10+Ls15+Ls20+Ls40
        Lpos = Lposp+Lposs
        
        #print Lposp, Lposs
        self.parentSite.totalcases += Lpos #update number of cases (DA PARA FAZER MAIS DETALHADO?)
        
        # Model (vacina entra por fora).  e sem progressao etaria!
        S0pos = S0 -  Lp0
        Ip0pos = Ip0 + Lp0 - gp * Ip0
        Rmax0pos = Rmax0 + gp * Ip0 + gs * Is0 - a * Rmax0
        Rmed0pos = Rmed0 + a * Rmax0 - a * Rmed0
        Rmin0pos = Rmin0 + a * Rmed0 - Ls0 * Rmin0
        Is0pos = Is0 + Ls0 - gs * Is0
        Vmax0pos = (1- r) * Vmax0
        Vmed0pos = (1-r) * Vmed0 + r*Vmax0
        Vmin0pos =  Vmin0 + r*Vmed0 
        
        S2pos = S2 -  Lp2
        Ip2pos = Ip2 + Lp2 - gp * Ip2
        Rmax2pos = Rmax2 + gp * Ip2 + gs * Is2 - a * Rmax2
        Rmed2pos = Rmed2 + a * Rmax2 - a * Rmed2
        Rmin2pos = Rmin2 + a * Rmed2 - Ls2 * Rmin2
        Is2pos = Is2 + Ls2 - gs * Is2
        Vmax2pos = (1- r) * Vmax2
        Vmed2pos = (1-r) * Vmed2 + r*Vmax2
        Vmin2pos =  Vmin2 + r*Vmed2 
        
        S10pos = S10 -  Lp10
        Ip10pos = Ip10 + Lp10 - gp * Ip10
        Rmax10pos = Rmax10 + gp * Ip10 + gs * Is10 - a * Rmax10
        Rmed10pos = Rmed10 + a * Rmax10 - a * Rmed10
        Rmin10pos = Rmin10 + a * Rmed10 - Ls10 * Rmin10
        Is10pos = Is10 + Ls10 - gs * Is10
        Vmax10pos = (1- r) * Vmax10
        Vmed10pos = (1-r) * Vmed10 + r*Vmax10
        Vmin10pos =  Vmin10 + r*Vmed10
       
        S15pos = S15 -  Lp15
        Ip15pos = Ip15 + Lp15 - gp * Ip15
        Rmax15pos = Rmax15 + gp * Ip15 + gs * Is15 - a * Rmax15
        Rmed15pos = Rmed15 + a * Rmax15 - a * Rmed15
        Rmin15pos = Rmin15 + a * Rmed15 - Ls15 * Rmin15
        Is15pos = Is15 + Ls15 - gs * Is15
        Vmax15pos = (1- r) * Vmax15
        Vmed15pos = (1-r) * Vmed15 + r*Vmax15
        Vmin15pos =  Vmin15 + r*Vmed15  
        
        S20pos = S20 -  Lp20
        Ip20pos = Ip20 + Lp20 - gp * Ip20
        Rmax20pos = Rmax20 + gp * Ip20 + gs * Is20 - a * Rmax20
        Rmed20pos = Rmed20 + a * Rmax20 - a * Rmed20
        Rmin20pos = Rmin20 + a * Rmed20 - Ls20 * Rmin20
        Is20pos = Is20 + Ls20 - gs * Is20
        Vmax20pos = (1- r) * Vmax20
        Vmed20pos = (1-r) * Vmed20 + r*Vmax20
        Vmin20pos =  Vmin20 + r*Vmed20 
        
        S40pos = S40 -  Lp40
        Ip40pos = Ip40 + Lp40 - gp * Ip40
        Rmax40pos = Rmax40 + gp * Ip40 + gs * Is40 - a * Rmax40
        Rmed40pos = Rmed40 + a * Rmax40 - a * Rmed40
        Rmin40pos = Rmin40 + a * Rmed40 - Ls40 * Rmin40
        Is40pos = Is40 + Ls40 - gs * Is40
        Vmax40pos = (1- r) * Vmax40
        Vmed40pos = (1-r) * Vmed40 + r*Vmax40
        Vmin40pos =  Vmin40 + r*Vmed40 
        
        
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                print 'infected',self.parentSite.sitename
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infectious
        Ipos = Ip0pos+Is0pos+Ip2pos+Is2pos+Ip10pos+Is10pos+Ip15pos+Is15pos+Ip20pos+Is20pos+Ip40pos+Is40pos
        self.parentSite.migInf.append(Ipos)
        
        #return [0,Ipos,Spos]
        return [S0pos,S2pos,S10pos,S15pos,S20pos,S40pos,
                Ip0pos,Ip2pos,Ip10pos,Ip15pos,Ip20pos,Ip40pos,
                Is0pos,Is2pos,Is10pos,Is15pos,Is20pos,Is40pos,
                Rmax0pos,Rmax2pos,Rmax10pos,Rmax15pos,Rmax20pos,Rmax40pos,
                Rmed0pos,Rmed2pos,Rmed10pos,Rmed15pos,Rmed20pos,Rmed40pos,
                Rmin0pos,Rmin2pos,Rmin10pos,Rmin15pos,Rmin20pos,Rmin40pos,
                Vmax0pos,Vmax2pos,Vmax10pos,Vmax15pos,Vmax20pos,Vmax40pos,
                Vmed0pos,Vmed2pos,Vmed10pos,Vmed15pos,Vmed20pos,Vmed40pos,
                Vmin0pos,Vmin2pos,Vmin10pos,Vmin15pos,Vmin20pos,Vmin40pos]
                
def getPass(self):
    '''
    This function substitutes the built-in transport model.
    It access the neighbors of self and get the number of persons and infected persons arriving by age group
    '''                    
    # pessoas infectadas viajando
    Mp0,Mp2,Mp10,Mp15,Mp20,Mp40,Ms0,Ms2,Ms10,Ms15,Ms20,Ms40 = 0,0,0,0,0,0,0,0,0,0,0,0
   
   # pessoas viajando
    npass0,npass2,npass10,npass15,npass20,npass40= 0,0,0,0,0,0
   
    
   # Pegando os vizinhos na forma de dicionario com chave = neig e valor = faixa etaria
   # ex. neig={'caxambi':2,'caxambi':4}
    neig = self.parentSite.getNeighbors()
    
        
    for zt,fe in neig.iteritems():
            S0,S2,S10,S15,S20,S40,Ip0,Ip2,Ip10,Ip15,Ip20,Ip40,Is0,Is2,Is10,Is15,Is20,Is40,Rmax0,Rmax2,Rmax10,Rmax15,Rmax20,Rmax40,Rmed0,Rmed2,Rmed10,Rmed15,Rmed20,Rmed40,Rmin0,Rmin2,Rmin10,Rmin15,Rmin20,Rmin40,Vmax0,Vmax2,Vmax10,Vmax15,Vmax20,Vmax40,Vmed0,Vmed2,Vmed10,Vmed15,Vmed20,Vmed40,Vmin0,Vmin2,Vmin10,Vmin15,Vmin20,Vmin40= zt.ts[-1]
            
            npass0 += zt.S0 + zt.Ip0
            
            if fe==0: 
                Mp0 += zt.ts[-1]
    
    
    
