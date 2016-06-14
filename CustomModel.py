# This is a custom model to used in place of Epigrass' built-in models. Custom
# models must always be on a file named CustomModel.py and contain at least 
# a function named Model. Both the File name and the function Names are case-sensitive,
# so be careful. Please refer to the manual for intructions on how to write your 
# own custom models.
from numpy.random import poisson,  multinomial
from numpy import *


def Model(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None):
        """
        Calculates the model SIR, and return its values.
        - inits = (E,I,S)
        - par = (Beta, alpha, E,r,delta,B, w, p) see docs.
        - theta = infectious individuals from neighbor sites (CONSIDERANDO QUE CHEGUE COMO UMA lista
            'Ip0','Ip2','Ip10','Ip15','Ip20','Ip40','Is0','Is2','Is10','Is15','Is20','Is40'
        - npass deve ser tb um vetor com populacao por faixa etaria
        """
        #Initializing

        vnames = ('S0','S2','S10','S15','S20','S40',
                'Ep0','Ep2','Ep10','Ep15','Ep20','Ep40',                  
                'Ip0','Ip2','Ip10','Ip15','Ip20','Ip40',
                'Es0','Es2','Es10','Es15','Es20','Es40',
                'Is0','Is2','Is10','Is15','Is20','Is40',
                'Rmax0','Rmax2','Rmax10','Rmax15','Rmax20','Rmax40',
                'Rmed0','Rmed2','Rmed10','Rmed15','Rmed20','Rmed40',
                'Rmin0','Rmin2','Rmin10','Rmin15','Rmin20','Rmin40',
                'Vmax0','Vmax2','Vmax10','Vmax15','Vmax20','Vmax40',
                'Vmed0','Vmed2','Vmed10','Vmed15','Vmed20','Vmed40',
                'Vmin0','Vmin2','Vmin10','Vmin15','Vmin20','Vmin40')
 
        # A distribuicao etaria e sitio-especificas
        if simstep == 1: #get initial values
            S0,S2,S10,S15,S20,S40 = (self.bi['s0'],self.bi['s2'], self.bi['s10'],self.bi['s15'],self.bi['s20'],self.bi['s40'])
            Ep0,Ep2,Ep10,Ep15,Ep20,Ep40 = (self.bi['ep0'],self.bi['ep2'],self.bi['ep10'],self.bi['ep15'],self.bi['ep20'],self.bi['ep40'])
            Ip0,Ip2,Ip10,Ip15,Ip20,Ip40 = (self.bi['ip0'],self.bi['ip2'],self.bi['ip10'],self.bi['ip15'],self.bi['ip20'],self.bi['ip40'])
            Es0,Es2,Es10,Es15,Es20,Es40 = (self.bi['es0'],self.bi['es2'],self.bi['es10'],self.bi['es15'],self.bi['es20'],self.bi['es40'])
            Is0,Is2,Is10,Is15,Is20,Is40 = (self.bi['is0'],self.bi['is2'],self.bi['is10'],self.bi['is15'],self.bi['is20'],self.bi['is40'])
            Rmax0,Rmax2,Rmax10,Rmax15,Rmax20,Rmax40=(self.bi['rmax0'],self.bi['rmax2'],self.bi['rmax10'],self.bi['rmax15'],self.bi['rmax20'],self.bi['rmax40'])
            Rmed0,Rmed2,Rmed10,Rmed15,Rmed20,Rmed40=(self.bi['rmed0'],self.bi['rmed2'],self.bi['rmed10'],self.bi['rmed15'],self.bi['rmed20'],self.bi['rmed40'])
            Rmin0,Rmin2,Rmin10,Rmin15,Rmin20,Rmin40=(self.bi['rmin0'],self.bi['rmin2'],self.bi['rmin10'],self.bi['rmin15'],self.bi['rmin20'],self.bi['rmin40'])
            Vmax0,Vmax2,Vmax10,Vmax15,Vmax20,Vmax40=(self.bi['vmax0'],self.bi['vmax2'],self.bi['vmax10'],self.bi['vmax15'],self.bi['vmax20'],self.bi['vmax40'])
            Vmed0,Vmed2,Vmed10,Vmed15,Vmed20,Vmed40=(self.bi['vmed0'],self.bi['vmed2'],self.bi['vmed10'],self.bi['vmed15'],self.bi['vmed20'],self.bi['vmed40'])
            Vmin0,Vmin2,Vmin10,Vmin15,Vmin20,Vmin40=(self.bi['vmin0'],self.bi['vmin2'],self.bi['vmin10'],self.bi['vmin15'],self.bi['vmin20'],self.bi['vmin40'])

            # sem fluxo no primeiro dia
            Mp0,Mp2,Mp10,Mp15,Mp20,Mp40,Ms0,Ms2,Ms10,Ms15,Ms20,Ms40=0,0,0,0,0,0,0,0,0,0,0,0

            # calculando o dicionario de fluxos:
            self.parentSite.pdest = setPassDest(self)
            npass0, npass2, npass10, npass15, npass20, npass40 = npass
            
            
        else:
            S0,S2,S10,S15,S20,S40,Ep0,Ep2,Ep10,Ep15,Ep20,Ep40,Ip0,Ip2,Ip10,Ip15,Ip20,Ip40,Es0,Es2,Es10,Es15,Es20,Es40,Is0,Is2,Is10,Is15,Is20,Is40,Rmax0,Rmax2,Rmax10,Rmax15,Rmax20,Rmax40,Rmed0,Rmed2,Rmed10,Rmed15,Rmed20,Rmed40,Rmin0,Rmin2,Rmin10,Rmin15,Rmin20,Rmin40,Vmax0,Vmax2,Vmax10,Vmax15,Vmax20,Vmax40,Vmed0,Vmed2,Vmed10,Vmed15,Vmed20,Vmed40,Vmin0,Vmin2,Vmin10,Vmin15,Vmin20,Vmin40 = inits
            # obtendo os visitantes
            Mp0,Mp2,Mp10,Mp15,Mp20,Mp40,Ms0,Ms2,Ms10,Ms15,Ms20,Ms40 = self.parentSite.infectedvisiting
            npass0,npass2,npass10,npass15,npass20,npass40 = npass
            # resetando os visitantes:
            self.parentSite.infectedvisiting=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        totpass=npass0+npass2+npass10+npass15+npass20+npass40
        N = totpop
        # Parametros
        #beta,alpha,e,r,delta,B,w,p = par
        
        pp, ps, sp, ss = (self.bp['pp'],self.bp['ps'],self.bp['sp'],self.bp['ss'])
        pv, e, gp, gs, a, r = (self.bp['pv'],self.bp['e'],self.bp['gp'],self.bp['gs'],self.bp['a'],self.bp['r'],) 
        ep, es = (self.bp['ep'],self.bp['es'])
        c0, c1, c2, c3, c4, c5= (self.bp['c0'],self.bp['c1'],self.bp['c2'],self.bp['c3'],self.bp['c4'],self.bp['c5'])
        n0, n2, n10, n15, n20, n40 = (self.bp['n0'], self.bp['n2'],self.bp['n10'],self.bp['n15'],self.bp['n20'],self.bp['n40'])

        #Vacination event  # apenas na primeira faixa etaria
        if self.parentSite.vaccineNow:
            S0 -= self.parentSite.vaccov*S0
            Vmax0 += self.parentSite.vaccov*S0
        
        # numero de pessoas com infeccao primaria (locais e visitas)
        Ip=array([Ip0+Mp0, Ip2+Mp2, Ip10+Mp10, Ip15+Mp15, Ip20+Mp20, Ip40+Mp40])
        Is=array([Is0+Ms0, Is2+Ms2, Is10+Ms10, Is15+Ms15, Is20+Ms20, Is40+Ms40])
        Iptot = sum(Ip)
        Istot = sum(Is)
        
        # distribuicao dos contatos
        matriz = 'delvalle'
        if (matriz =='luz'):
            mc0 = array([c0, c0, c3, c5, c5, c3])
            mc2 = array([c0, c5, c0, c3, c5, c3])
            mc10 =array([c0, c0, c5, c3, c5, c3])
            mc15=array([c0, c0, c3, c5, c5, c3])
            mc20=array([c5, c3, c0, c0, c5, c3])
            mc40=array([c0, c3, c3, c0, c5, c5])
        
        if (matriz =='delvalle'):
            
            mc0 = array([c0, c2, c2, c1, c1, c0])
            mc2 = array([c2, c5, c5, c1, c1, c0])
            mc10 =array([c2, c5, c5, c1, c1, c0])
            mc15=array([c1, c1, c3, c3, c2, c1])
            mc20=array([c1, c1, c0, c2, c5, c2])
            mc40=array([c0, c0, c1, c2, c2, c1])
        
        # probabilidade de infeccao por contato (a divisao e para padronizar os vetores de contato)
        x = (1/(N+totpass))*(pp*Ip+ps*Is)
        p0 = sum(x*mc0/sum(mc0))
        p2 = sum(x*mc2/sum(mc2))
        p10 = sum(x*mc10/sum(mc10))
        p15 = sum(x*mc15/sum(mc15))
        p20 = sum(x*mc20/sum(mc20))
        p40 = sum(x*mc40/sum(mc40))
        
       
        # calculando a incidencia
        
        Lp0 = min(poisson(sp*S0*(1-(1-p0)**n0), 1)[0], S0)
        Ls0r = min(poisson(ss*Rmin0*(1-(1-p0)**n0), 1)[0], Rmin0)
        Ls0v = min(poisson(ss*Vmin0*(1-(1-p0)**n0), 1)[0], Vmin0)
        
        Lp2 = min(poisson(sp*S2*(1-(1-p2)**n0), 1)[0], S2)
        Ls2r = min(poisson(ss*Rmin2*(1-(1-p2)**n2), 1)[0], Rmin2)
        Ls2v = min(poisson(ss*Vmin2*(1-(1-p2)**n2), 1)[0], Vmin2)
        
        Lp10 = min(poisson(sp*S10*(1-(1-p10)**n10), 1)[0], S10)
        Ls10r = min(poisson(ss*Rmin10*(1-(1-p10)**n10), 1)[0], Rmin10)
        Ls10v = min(poisson(ss*Vmin10*(1-(1-p10)**n10), 1)[0], Vmin10)
        
        Lp15 = min(poisson(sp*S15*(1-(1-p15)**n15), 1)[0], S15)
        Ls15r = min(poisson(ss*Rmin15*(1-(1-p15)**n15), 1)[0], Rmin15)
        Ls15v = min(poisson(ss*Vmin15*(1-(1-p15)**n15), 1)[0], Vmin15)
        
        Lp20 = min(poisson(sp*S20*(1-(1-p20)**n20), 1)[0], S20)
        Ls20r = min(poisson(ss*Rmin20*(1-(1-p20)**n20), 1)[0], Rmin20)
        Ls20v = min(poisson(ss*Vmin20*(1-(1-p20)**n20), 1)[0], Vmin20)
        
        Lp40 = min(poisson(sp*S40*(1-(1-p40)**n40), 1)[0], S40)
        Ls40r = min(poisson(ss*Rmin40*(1-(1-p40)**n40), 1)[0], Rmin40)
        Ls40v = min(poisson(ss*Vmin40*(1-(1-p40)**n40), 1)[0], Vmin40)
            
        Lposp = Lp0+Lp2+Lp10+Lp15+Lp20+Lp40
        Lposs = Ls0r+Ls2r+Ls10r+Ls15r+Ls20r+Ls40r+Ls0v+Ls2v+Ls10v+Ls15v+Ls20v+Ls40v
        Lpos = Lposp+Lposs
        
        self.parentSite.totalcases += Lpos #update number of cases (DA PARA FAZER MAIS DETALHADO?)
        
        # Model (vacina entra por fora).  e sem progressao etaria! tirei a infeccao secundaria tb porque estava errado, e preciso repensar esta parte : a entrada do Ls no modelo, acrescentei classe com latencia
            
        S0pos = S0 -  Lp0
        Ep0pos = (1-ep) * Ep0 + Lp0
        Ip0pos = (1-gp) * Ip0 + ep*Ep0
        Rmax0pos = (1-a) * Rmax0 + gp * Ip0 + gs * Is0
        Rmed0pos = (1-a) * Rmed0 + a * Rmax0
        Rmin0pos = Rmin0 + a * Rmed0 - Ls0r
        Es0pos = (1-es)*Es0 + Ls0r + Ls0v 
        Is0pos = (1-gs)*Is0 + es*Es0
        Vmax0pos = (1- r) * Vmax0
        Vmed0pos = (1-r) * Vmed0 + r*Vmax0
        Vmin0pos =  Vmin0 + r*Vmed0 - Ls0v
        
        S2pos = S2 -  Lp2
        Ep2pos = (1-ep) * Ep2 + Lp2
        Ip2pos = (1-gp) * Ip2 + ep*Ep2
        Rmax2pos = (1-a) * Rmax2 + gp * Ip2 + gs * Is2
        Rmed2pos = (1-a) * Rmed2 + a * Rmax2
        Rmin2pos = Rmin2 + a * Rmed2 - Ls2r
        Es2pos = (1-es)*Es2 + Ls2r + Ls2v 
        Is2pos = (1-gs)*Is2 + es*Es2
        Vmax2pos = (1- r) * Vmax2
        Vmed2pos = (1-r) * Vmed2 + r*Vmax2
        Vmin2pos =  Vmin2 + r*Vmed2 - Ls2v
        
        S10pos = S10 -  Lp10
        Ep10pos = (1-ep) * Ep10 + Lp10
        Ip10pos = (1-gp) * Ip10 + ep*Ep10
        Rmax10pos = (1-a) * Rmax10 + gp * Ip10 + gs * Is10
        Rmed10pos = (1-a) * Rmed10 + a * Rmax10
        Rmin10pos = Rmin10 + a * Rmed10 - Ls10r
        Es10pos = (1-es)*Es10 + Ls10r + Ls10v 
        Is10pos = (1-gs)*Is10 + es*Es10
        Vmax10pos = (1- r) * Vmax10
        Vmed10pos = (1-r) * Vmed10 + r*Vmax10
        Vmin10pos =  Vmin10 + r*Vmed10 - Ls10v
        
        S15pos = S15 -  Lp15
        Ep15pos = (1-ep) * Ep15 + Lp15
        Ip15pos = (1-gp) * Ip15 + ep*Ep15
        Rmax15pos = (1-a) * Rmax15 + gp * Ip15 + gs * Is15
        Rmed15pos = (1-a) * Rmed15 + a * Rmax15
        Rmin15pos = Rmin15 + a * Rmed15 - Ls15r
        Es15pos = (1-es)*Es15 + Ls15r + Ls15v 
        Is15pos = (1-gs)*Is15 + es*Es15
        Vmax15pos = (1- r) * Vmax15
        Vmed15pos = (1-r) * Vmed15 + r*Vmax15
        Vmin15pos =  Vmin15 + r*Vmed15 - Ls15v
        
        S20pos = S20 -  Lp20
        Ep20pos = (1-ep) * Ep20 + Lp20
        Ip20pos = (1-gp) * Ip20 + ep*Ep20
        Rmax20pos = (1-a) * Rmax20 + gp * Ip20 + gs * Is20
        Rmed20pos = (1-a) * Rmed20 + a * Rmax20
        Rmin20pos = Rmin20 + a * Rmed20 - Ls20r
        Es20pos = (1-es)*Es20 + Ls20r + Ls20v 
        Is20pos = (1-gs)*Is20 + es*Es20
        Vmax20pos = (1- r) * Vmax20
        Vmed20pos = (1-r) * Vmed20 + r*Vmax20
        Vmin20pos =  Vmin20 + r*Vmed20 - Ls20v
        
        S40pos = S40 -  Lp40
        Ep40pos = (1-ep) * Ep40 + Lp40
        Ip40pos = (1-gp) * Ip40 + ep*Ep40
        Rmax40pos = (1-a) * Rmax40 + gp * Ip40 + gs * Is40
        Rmed40pos = (1-a) * Rmed40 + a * Rmax40
        Rmin40pos = Rmin40 + a * Rmed40 - Ls40r
        Es40pos = (1-es)*Es40 + Ls40r + Ls40v 
        Is40pos = (1-gs)*Is40 + es*Es40
        Vmax40pos = (1- r) * Vmax40
        Vmed40pos = (1-r) * Vmed40 + r*Vmax40
        Vmin40pos =  Vmin40 + r*Vmed40 - Ls40v

           
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                print 'infected', self.parentSite.sitename
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
                #print self.parentSite.ftheta
        #infectious
        Ipos = Ip0pos+Is0pos+Ip2pos+Is2pos+Ip10pos+Is10pos+Ip15pos+Is15pos+Ip20pos+Is20pos+Ip40pos+Is40pos
        self.parentSite.migInf.append(Ipos)
        
        # send infected to others! 
        if (Ipos>0):
            tot0 = (S0pos+Ep0pos+Es0pos+Ip0pos+ Is0pos+Rmax0pos+Rmed0pos+Rmin0pos+Vmax0pos+Vmed0pos+Vmin0pos)
            tot2 = (S2pos+Ep2pos+Es2pos+Ip2pos+ Is2pos+Rmax2pos+Rmed2pos+Rmin2pos+Vmax2pos+Vmed2pos+Vmin2pos)
            tot10 = (S10pos+Ep10pos+Es10pos+Ip10pos+ Is10pos+Rmax10pos+Rmed10pos+Rmin10pos+Vmax10pos+Vmed10pos+Vmin10pos)
            tot15 = (S15pos+Ep15pos+Es15pos+Ip15pos+ Is15pos+Rmax15pos+Rmed15pos+Rmin15pos+Vmax15pos+Vmed15pos+Vmin15pos)
            tot20 = (S20pos+Ep20pos+Es20pos+Ip20pos+ Is20pos+Rmax20pos+Rmed20pos+Rmin20pos+Vmax20pos+Vmed20pos+Vmin20pos)
            tot40 = (S40pos+Ep40pos+Es40pos+Ip40pos+ Is40pos+Rmax40pos+Rmed40pos+Rmin40pos+Vmax40pos+Vmed40pos+Vmin40pos)
            
            infmig = [npass0*(Ip0pos/tot0),npass2*(Ip2pos/tot2),npass10*(Ip10pos/tot10),npass15*(Ip15pos/tot15),npass20*(Ip20pos/tot20),npass40*(Ip40pos/tot40),npass0*(Is0pos/tot0),npass2*(Is2pos/tot2),npass10*(Is10pos/tot10),npass15*(Is15pos/tot15),npass20*(Is20pos/tot20),npass40*(Is40pos/tot40)]
            sendInfectedPass(self, infmig, self.parentSite.pdest)
            #print self.parentSite.sitename,  self.parentSite.ts

        return [S0pos,S2pos,S10pos,S15pos,S20pos,S40pos,
                Ep0pos,Ep2pos,Ep10pos,Ep15pos,Ep20pos,Ep40pos,
                Ip0pos,Ip2pos,Ip10pos,Ip15pos,Ip20pos,Ip40pos,
                Es0pos,Es2pos,Es10pos,Es15pos,Es20pos,Es40pos,
                Is0pos,Is2pos,Is10pos,Is15pos,Is20pos,Is40pos,
                Rmax0pos,Rmax2pos,Rmax10pos,Rmax15pos,Rmax20pos,Rmax40pos,
                Rmed0pos,Rmed2pos,Rmed10pos,Rmed15pos,Rmed20pos,Rmed40pos,
                Rmin0pos,Rmin2pos,Rmin10pos,Rmin15pos,Rmin20pos,Rmin40pos,
                Vmax0pos,Vmax2pos,Vmax10pos,Vmax15pos,Vmax20pos,Vmax40pos,
                Vmed0pos,Vmed2pos,Vmed10pos,Vmed15pos,Vmed20pos,Vmed40pos,
                Vmin0pos,Vmin2pos,Vmin10pos,Vmin15pos,Vmin20pos,Vmin40pos]
                

def getNPass(self):
    '''
    Calculando quantos passageiros chegam ao site por dia
    '''
    npass = [0, 0, 0, 0, 0, 0]
    fes = [0, 2, 10, 15, 20, 40]
    for e in self.parentSite.getInEdges():
        fe = fes.index(e.length)
        npass[fe]+=e.fmig
    
    return npass
    
def setPassDest(self):
    '''
    Define, para cada ZT, os destinos possiveis e a probabilidade de cada um deles por faixa etaria
    '''
    
    # criando uma lista de dicts, um para cada FE, contendo os outedges e of fluxos
    dests = [{}, {}, {}, {}, {}, {}]
    fes = [0, 2, 10, 15, 20, 40]
    
    for e in self.parentSite.getOutEdges():
        fe = fes.index(e.length)
        dests[fe][e]=e.fmig
    
    # transformando os fluxos em probabilidade de destino
    pdests = dests
    for i in xrange(6):
        tot=sum(dests[i].values())
        di = dests[i]
        for k, v in di.iteritems():
            pdests[i][k]=v/tot
            
    
            
    return pdests

    
def sendInfectedPass(self, infgroup, pdests):
    '''
    if there is people infected, check where they are going to...
    inf = [Ip0pos,Ip2pos,Ip10pos,Ip15pos,Ip20pos,Ip40pos,Is0pos,Is2pos,Is10pos,Is15pos,Is20pos,Is40pos]
    '''
    # Quantos vao sair?
    
    a = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
    if (pdests):
        n = 0 # indexador do inf 
        for i in infgroup:
            posdest = a[n]
            #print 'posdest=', posdest
            #print 'enviando %s para os destinos:'%i , pdests[posdest]
            if (int(i) & len(pdests[posdest])):
                destlist = pdests[posdest]
                #print 'destinos gerais de %s:'%a[n], destlist
                choosedest = multinomial(int(i),destlist.values())
                k=0
                for j in destlist: # enviando os infectados para seus destinos
                    j.dest.infectedvisiting[n] += choosedest[k]
                    k+=1
            n+=1

    return 1
    
