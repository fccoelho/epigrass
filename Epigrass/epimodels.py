"""
Library of discrete time Epidemic models

copyright 2012 Flávio Codeco Coelho
License: GPL-v3
"""

__author__ = 'fccoelho'

from numpy.random import poisson, negative_binomial
from numpy import inf, nan, nan_to_num
import sys
import redis
import cython

redisclient = redis.StrictRedis()

vnames = {
    'SIR': ['Exposed', 'Infectious', 'Susceptible'],
    'SIR_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SIS': ['Exposed', 'Infectious', 'Susceptible'],
    'SIS_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIS': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIS_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIR': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIR_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SIpRpS': ['Exposed', 'Infectious', 'Susceptible'],
    'SIpRpS_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIpRpS': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIpRpS_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIpR': ['Exposed', 'Infectious', 'Susceptible'],
    'SEIpR_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SIpR': ['Exposed', 'Infectious', 'Susceptible'],
    'SIpR_s': ['Exposed', 'Infectious', 'Susceptible'],
    'SIRS': ['Exposed', 'Infectious', 'Susceptible'],
    'SIRS_s': ['Exposed', 'Infectious', 'Susceptible'],
    'Custom': ['Exposed', 'Infectious', 'Susceptible'],
    'Influenza': ('Susc_age1', 'Incub_age1', 'Subc_age1', 'Sympt_age1', 'Comp_age1',
                  'Susc_age2', 'Incub_age2', 'Subc_age2', 'Sympt_age2', 'Comp_age2',
                  'Susc_age3', 'Incub_age3', 'Subc_age3', 'Sympt_age3', 'Comp_age3',
                  'Susc_age4', 'Incub_age4', 'Subc_age4', 'Sympt_age4', 'Comp_age4',),
}


class Epimodel(object):
    """
    Defines a library of discrete time population models
    """

    @cython.locals(geocode='long', modtype='bytes', parallel='bint')
    def __init__(self, geocode, modtype=b'', parallel=True):
        """
        Defines which models a given site will use
        and set variable names accordingly.
        :param modtype:
        """
        self.step = selectModel(modtype)
        self.geocode = geocode
        self.parallel = parallel

    def __call__(self, *args, **kwargs):
        args = self.get_args_from_redis()
        res = self.step(*(list(args)+[self]))
        self.update_redis(res)
        # return res

    @cython.locals(simstep='long', totpop='long', theta='double', npass='double')
    def get_args_from_redis(self):
        """
        Get updated parameters from the redis database.
        """
        sinits = redisclient.lrange("{}:inits".format(self.geocode),-1,-1)
        # print(sinits)
        inits = eval(sinits[0])
        simstep = int(redisclient.get("simstep"))
        totpop = int(float(redisclient.get("{}:totpop".format(self.geocode))))
        theta = int(nan_to_num(float(redisclient.get("{}:theta".format(self.geocode)))))
        npass = int(float(redisclient.get("{}:npass".format(self.geocode))))
        bi = redisclient.hgetall("{}:bi".format(self.geocode))
        bi = {k: float(v) for k, v in bi.items()}
        bp = redisclient.hgetall("{}:bp".format(self.geocode))
        bp = {k: float(v) for k, v in bp.items()}
        values = [float(i) for i in redisclient.lrange("{}:values".format(self.geocode), 0, -1)]
        return inits, simstep, totpop, theta, npass, bi, bp, values

    def update_redis(self, results):
        """
        Update redis database with the results of the model
        :param results: results tuple.
        """
        # Site state
        state, Lpos, migInf = results
        # print("Updating redis: ", state, migInf)
        redisclient.rpush("{}:inits".format(self.geocode), str(state))  # updating inits
        redisclient.rpush('{}:ts'.format(self.geocode), str(state))
        redisclient.set('{}:Lpos'.format(self.geocode), Lpos)
        totc = int(nan_to_num(float(redisclient.get('{}:totalcases'.format(self.geocode)))))
        redisclient.set('{}:totalcases'.format(self.geocode), Lpos + totc)
        redisclient.rpush('{}:incidence'.format(self.geocode), Lpos)
        redisclient.set('{}:migInf'.format(self.geocode), migInf)

        # Graph state
        if Lpos > 0:
            infected = int(redisclient.get("simstep"))
            redisclient.rpush("epipath", str((infected, self.geocode, {})))  # TODO: replace empty dict with infectors
            # self.parentGraph.epipath.append((self.parentGraph.simstep, self.geocode, self.infector))
            # TODO: have infector be stated in terms of geocodes


@cython.locals(Type='bytes')
def selectModel(modtype):
    """
    Sets the model engine
    """
    if isinstance(modtype, str):
        modtype = bytes(modtype, 'utf8')
    if modtype == b'SIR':
        return stepSIR
    elif modtype == b'SIR_s':
        return stepSIR_s
    elif modtype == b'SIS':
        return stepSIS
    elif modtype == b'SIS_s':
        return stepSIS_s
    elif modtype == b'SEIS':
        return stepSEIS
    elif modtype == b'SEIS_s':
        return stepSEIS_s
    elif modtype == b'SEIR':
        return stepSEIR
    elif modtype == b'SEIR_s':
        return stepSEIR_s
    elif modtype == b'SIpRpS':
        return stepSIpRpS
    elif modtype == b'SIpRpS_s':
        return stepSIpRpS_s
    elif modtype == b'SEIpRpS':
        return stepSEIpRpS
    elif modtype == b'SEIpRpS_s':
        return stepSEIpRpS_s
    elif modtype == b'SIpR':
        return stepSIpR
    elif modtype == b'SIpR_s':
        return stepSIpR_s
    elif modtype == b'SEIpR':
        return stepSEIpR
    elif modtype == b'SEIpR_s':
        return stepSEIpR_s
    elif modtype == b'SIRS':
        return stepSIRS
    elif modtype == b'SIRS_s':
        return stepSIRS_s
    elif modtype == b'Influenza':
        return stepFlu
    elif modtype == b'Custom':
        # adds the user model as a method of instance self
        try:
            # TODO: move this import to the graph level
            import CustomModel

            return CustomModel.Model
        except ImportError:
            print("You have to Create a CustomModel.py file before you can select\nthe Custom model type")
    else:
        sys.exit('Model type specified in .epg file is invalid')


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepFlu(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    Flu model with classes S,E,I subclinical, I mild, I medium, I serious, deaths
    """
    # Variable long names to be used in the database output.
    vnames = ('Susc_age1', 'Incub_age1', 'Subc_age1', 'Sympt_age1', 'Comp_age1',
              'Susc_age2', 'Incub_age2', 'Subc_age2', 'Sympt_age2', 'Comp_age2',
              'Susc_age3', 'Incub_age3', 'Subc_age3', 'Sympt_age3', 'Comp_age3',
              'Susc_age4', 'Incub_age4', 'Subc_age4', 'Sympt_age4', 'Comp_age4',)
    if simstep == 1:  # get initial values
        S1, E1, Is1, Ic1, Ig1 = (bi[b'susc_age1'], bi[b'incub_age1'], bi[b'subc_age1'], bi[b'sympt_age1'], bi[b'comp_age1'])
        S2, E2, Is2, Ic2, Ig2 = (bi[b'susc_age2'], bi[b'incub_age2'], bi[b'subc_age2'], bi[b'sympt_age2'], bi[b'comp_age2'])
        S3, E3, Is3, Ic3, Ig3 = (bi[b'susc_age3'], bi[b'incub_age3'], bi[b'subc_age3'], bi[b'sympt_age3'], bi[b'comp_age3'])
        S4, E4, Is4, Ic4, Ig4 = (bi[b'susc_age4'], bi[b'incub_age4'], bi[b'subc_age4'], bi[b'sympt_age4'], bi[b'comp_age4'])
    else:  # get values from last time step
        S1, E1, Is1, Ic1, Ig1, S2, E2, Is2, Ic2, Ig2, S3, E3, Is3, Ic3, Ig3, S4, E4, Is4, Ic4, Ig4 = inits
    N = totpop

    # for k, v in bp.items():
    #     exec ('%s = %s' % (k, v))
    alpha = bp[b'alpha']
    beta = bp[b'beta']
    r = bp[b'r']
    e = bp[b'e']
    c = bp[b'c']
    g = bp[b'g']
    d = bp[b'd']
    pc1 = bp[b'pc1']
    pc2 = bp[b'pc2']
    pc3 = bp[b'pc3']
    pc4 = bp[b'pc4']
    pp1 = bp[b'pp1']
    pp2 = bp[b'pp2']
    pp3 = bp[b'pp3']
    pp4 = bp[b'pp4']
    b = bp[b'b']

    # Vacination event

    if 'vaccineNow' in bp:  # TODO: add to bp when creating model
        vaccineNow = bp['vaccineNow']
        vaccov = bp['vaccov']
        S1 -= vaccov * S1
        S2 -= vaccov * S2
        S3 -= vaccov * S3
        S4 -= vaccov * S4

    # New cases by age class
    # beta=eval(values[2])

    Infectantes = Ig1 + Ig2 + Ig3 + Ig4 + Ic1 + Ic2 + Ic3 + Ic4 + 0.5 * (Is1 + Is2 + Is3 + Is4) + theta
    L1pos = float(beta) * S1 * (Infectantes / (N + npass)) ** alpha
    L2pos = float(beta) * S2 * (Infectantes / (N + npass)) ** alpha
    L3pos = float(beta) * S3 * (Infectantes / (N + npass)) ** alpha
    L4pos = float(beta) * S4 * (Infectantes / (N + npass)) ** alpha

    ######################
    Lpos = L1pos + L2pos + L3pos + L4pos
    # Model
    # 0-2 years old
    E1pos = L1pos + (1 - e) * E1
    Is1pos = (1 - (pc1 * c + (1 - pc1) * r)) * Is1 + e * E1
    Ic1pos = (1 - (pp1 * g + (1 - pp1) * r)) * Ic1 + pc1 * c * Is1
    Ig1pos = (1 - d) * Ig1 + pp1 * g * Ic1
    S1pos = b + S1 - L1pos
    # 3-14 years old
    E2pos = L2pos + (1 - e) * E2
    Is2pos = (1 - (pc2 * c + (1 - pc2) * r)) * Is2 + e * E2
    Ic2pos = (1 - (pp2 * g + (1 - pp2) * r)) * Ic2 + pc2 * c * Is2
    Ig2pos = (1 - d) * Ig2 + pp2 * g * Ic2
    S2pos = b + S2 - L2pos
    # 15-59 years old
    E3pos = L3pos + (1 - e) * E3
    Is3pos = (1 - (pc3 * c + (1 - pc3) * r)) * Is3 + e * E3
    Ic3pos = (1 - (pp3 * g + (1 - pp3) * r)) * Ic3 + pc3 * c * Is3
    Ig3pos = (1 - d) * Ig3 + pp3 * g * Ic3
    S3pos = b + S3 - L3pos
    # >60 years old
    E4pos = L4pos + (1 - e) * E4
    Is4pos = (1 - (pc4 * c + (1 - pc4) * r)) * Is4 + e * E4
    Ic4pos = (1 - (pp4 * g + (1 - pp4) * r)) * Ic4 + pc4 * c * Is4
    Ig4pos = (1 - d) * Ig4 + pp4 * g * Ic4
    S4pos = b + S4 - L4pos

    # Migrating infecctious
    migInf = (
            Ig1pos + Ig2pos + Ig3pos + Ig4pos + Ic1pos + Ic2pos + Ic3pos + Ic4pos + 0.5 * (
            Is1pos + Is2pos + Is3pos + Is4pos))
    # Return variable values

    return [S1pos, E1pos, Is1pos, Ic1pos, Ig1pos, S2pos, E2pos, Is2pos,
            Ic2pos, Ig2pos, S3pos, E3pos, Is3pos, Ic3pos, Ig3pos, S4pos,
            E4pos, Is4pos, Ic4pos, Ig4pos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIS(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    calculates the model SIS, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    :param inits: tuple with initial conditions
    :param simstep: step of the simulation
    :param totpop: total population
    :param theta: inflow of infectives parameter
    :param npass: total inflow
    :param bi: dictionary with state
    :param bp: dictionary with parameter values
    :param values: tuple of extra values
    :return:
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop

    beta = bp['beta'];
    alpha = bp['alpha'];
    r = bp['r'];
    b = bp['b']

    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases
    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos + r * I

    # Migrating infecctious
    migInf = (Ipos)
    return [0, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIS_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SIS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits

    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos + r * I

    # Migrating infecctious
    migInf = (Ipos)

    return [0, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIR(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    calculates the model SIR, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    # print(inits)
    if simstep == 1:  # get initial values
        E, I, S = (bi.get(b'e', 0), bi[b'i'], bi[b's'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp[b'beta'];
    alpha = bp[b'alpha'];
    # e = bp['e'];
    r = bp[b'r'];
    # delta = bp['delta'];
    b = bp[b'b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos
    Rpos = N - (Spos + Ipos)

    # Migrating infecctious
    migInf = Ipos

    return (0, Ipos, Spos), Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIR_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SIR:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos
    Rpos = N - (Spos + Ipos)

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIS(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    Defines the model SEIS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    # Model
    Epos = (1 - e) * E + Lpos
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos + r * I

    # Migrating infecctious
    migInf = Ipos

    return [Epos, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIS_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SEIS:
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # converting between parameterizations
        Lpos = negative_binomial(I, prob)

    Epos = (1 - e) * E + Lpos
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos + r * I

    # Migrating infecctious
    migInf = Ipos

    return [Epos, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIR(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    Defines the model SEIR:
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    # Model
    Epos = (1 - e) * E + Lpos
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos
    Rpos = N - (Spos + Epos + Ipos)

    # Migrating infecctious
    migInf = Ipos

    return [Epos, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIR_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SEIR:
    - inits = (E,I,S)
    - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)  # poisson(Lpos_esp)
    ##            if theta == 0 and Lpos_esp == 0 and Lpos > 0:
    ##                print Lpos,Lpos_esp,S,I,theta,N,parentSite.sitename
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)

    Epos = (1 - e) * E + Lpos
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos
    Rpos = N - (Spos + Epos + Ipos)

    # Migrating infecctious
    migInf = Ipos

    return [Epos, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIpRpS(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    calculates the model SIpRpS, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos + (1 - delta) * r * I
    Rpos = N - (Spos + Ipos) + delta * r * I

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIpRpS_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SIpRpS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos + (1 - delta) * r * I
    Rpos = N - (Spos + Ipos) + delta * r * I

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIpRpS(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    Defines the model SEIpRpS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']

    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    Epos = (1 - e) * E + Lpos
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos + (1 - delta) * r * I
    Rpos = N - (Spos + Epos + Ipos) + delta * r * I

    # Migrating infecctious
    migInf = Ipos

    return [Epos, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIpRpS_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SEIpRpS:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)

    Epos = (1 - e) * E + Lpos
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos + (1 - delta) * r * I
    Rpos = N - (Spos + Epos + Ipos) + delta * r * I

    # Migrating infecctious
    migInf = Ipos

    return [Epos, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIpR(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    calculates the model SIpR, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    R = N - E - I - S
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    p = bp['p']
    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases
    Lpos2 = p * float(beta) * R * ((I + theta) / (N + npass)) ** alpha  # number of secondary Infections

    # Model
    Ipos = (1 - r) * I + Lpos + Lpos2
    Spos = S + b - Lpos
    Rpos = N - (Spos + Ipos) - Lpos2

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos + Lpos2, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIpR_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SIpRs:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    p = bp['p']
    R = N - E - I - S

    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases
    Lpos2_esp = p * float(beta) * R * ((I + theta) / (N + npass)) ** alpha  # number of secondary Infections

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
        Lpos2 = poisson(Lpos2_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)
        prob = I / (I + Lpos2_esp)  # convertin between parameterizations
        Lpos2 = negative_binomial(I, prob)

    # Model
    Ipos = (1 - r) * I + Lpos + Lpos2
    Spos = S + b - Lpos
    Rpos = N - (Spos + Ipos) - Lpos2

    # Migrating infecctious
    migInf = Ipos
    return [0, Ipos, Spos], Lpos + Lpos2, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIpR(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    calculates the model SEIpR, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    R = N - E - I - S
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    p = bp['p']

    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases
    Lpos2 = p * float(beta) * R * ((I + theta) / (N + npass)) ** alpha  # secondary infections

    # Model
    Epos = (1 - e) * E + Lpos + Lpos2
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos
    Rpos = N - (Spos + Ipos) - Lpos2

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos + Lpos2, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSEIpR_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SEIpRs:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    beta = bp['beta'];
    alpha = bp['alpha'];
    e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    # w = bp['w'];
    p = bp['p']
    R = N - E - I - S

    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases
    Lpos2_esp = p * float(beta) * R * ((I + theta) / (N + npass)) ** alpha  # secondary infections

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
        Lpos2 = poisson(Lpos2_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # converting between parameterizations
        Lpos = negative_binomial(I, prob)
        prob = I / (I + Lpos2_esp)  # converting between parameterizations
        Lpos2 = negative_binomial(I, prob)

    # Model
    Epos = (1 - e) * E + Lpos + Lpos2
    Ipos = e * E + (1 - r) * I
    Spos = S + b - Lpos
    Rpos = N - (Spos + Ipos) - Lpos2

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos + Lpos2, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIRS(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None):
    """
    calculates the model SIRS, and return its values (no demographics)
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    R = N - (E + I + S)
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    w = bp['w'];
    # p = bp['p']
    Lpos = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos + w * R
    Rpos = N - (Spos + Ipos) - w * R

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos, migInf


@cython.locals(inits='object', simstep='long', totpop='long', theta='double', npass='double',
               beta='double', alpha='double', E='double', I='double', S='double', N='long',
               r='double', b='double', w='double', Lpos='double', Lpos_esp='double', R='double',
               Ipos='double', Spos='double', Rpos='double')
def stepSIRS_s(inits, simstep, totpop, theta=0, npass=0, bi=None, bp=None, values=None, model=None, dist='poisson'):
    """
    Defines an stochastic model SIR:
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    """
    if simstep == 1:  # get initial values
        E, I, S = (bi['e'], bi['i'], bi['s'])
    else:
        E, I, S = inits
    N = totpop
    R = N - (E + I + S)
    beta = bp['beta'];
    alpha = bp['alpha'];
    # e = bp['e'];
    r = bp['r'];
    # delta = bp['delta'];
    b = bp['b'];
    w = bp['w'];
    # p = bp['p']
    Lpos_esp = float(beta) * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    if dist == 'poisson':
        Lpos = poisson(Lpos_esp)
    elif dist == 'negbin':
        prob = I / (I + Lpos_esp)  # convertin between parameterizations
        Lpos = negative_binomial(I, prob)

    # Model
    Ipos = (1 - r) * I + Lpos
    Spos = S + b - Lpos + w * R
    Rpos = N - (Spos + Ipos) - w * R

    # Migrating infecctious
    migInf = Ipos

    return [0, Ipos, Spos], Lpos, migInf
