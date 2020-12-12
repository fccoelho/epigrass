# This is a custom model to used in place of Epigrass' built-in models. Custom
# models must always be on a file named CustomModel.py and contain at least 
# a function named Model. Both the File name and the function Names are case-sensitive,
# so be careful. Please refer to the manual for intructions on how to write your 
# own custom models.


##### Defining variable names to appear in the database
# Must be listed in the same order of variables they are returned by the model
vnames = ['Exposed', 'Infectious', 'Susceptible']


def Model(inits, simstep, totpop, theta=0, npass=0, bi={}, bp={}, values=(), model=None):
    """
    This function implements the SIR model
    - inits = (E,I,S)
    - theta = infectious individuals from neighbor sites
    :param inits: Initial conditions
    :param simstep: Simulation step
    :param totpop: Total population on node
    :param theta: number of infectious arriving
    :param npass: total number of individual arriving
    :param bi: state variables (dict)
    :param bp: parameters (dict)
    :param values: Extra variables passed on nodes.csv
    :param model: reference to model instance
    :return:
    """

    ##### Get state variables' current values
    if simstep == 0:  # get initial values
        E, I, S = (bi[b'e'], bi[b'i'], bi[b's'])
    else:  # get last value
        E, I, S = inits

    ##### Defining N, the total population
    N = totpop

    ##### Getting values for the model parameters
    beta, alpha, e, r, delta, B, w, p = (
    bp[b'beta'], bp[b'alpha'], bp[b'e'], bp[b'r'], bp[b'delta'], bp[b'b'], bp[b'w'], bp[b'p'])

    ##### Defining a Vacination event (optional)
    if bp[b'vaccineNow']:
        S -= bp[b'vaccov'] * S

    ##### Modeling the number of new cases (incidence function)
    Lpos = beta * S * ((I + theta) / (N + npass)) ** alpha  # Number of new cases

    ##### Epidemiological model (SIR)
    Ipos = (1 - r) * I + Lpos
    Spos = S + B - Lpos
    Rpos = N - (Spos + Ipos)

    # Number of infectious individuals commuting.
    migInf = Ipos

    return [0, Ipos, Spos], Lpos, migInf
